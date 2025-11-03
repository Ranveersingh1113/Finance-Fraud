# Security Guidelines and Implementation Roadmap

## Current Security Status

**Overall Grade: C+ (75/100)**

This document outlines current security gaps and provides implementation roadmap for production deployment.

---

## Critical Security Gaps Identified

### 1. Authentication & Authorization ⚠️ CRITICAL

**Current State:**
```python
# src/api/advanced_main.py lines 38-43
VALID_API_KEYS = {
    settings.api_key,
    "dev-api-key",     # ❌ Hard-coded, shared key
    "analyst-key-001"  # ❌ Hard-coded, shared key
}
```

**Issues:**
- No OAuth2/SAML integration
- Hard-coded API keys in source code
- No role-based access control (RBAC)
- No multi-factor authentication (MFA)
- No session management

**Production Requirements:**
```python
# RECOMMENDED: Use OAuth2 with Auth0/Okta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from authlib.integrations.fastapi_oauth2 import AuthorizationServer
from jose import JWTError, jwt

# Recommended: Store API keys in environment variables or secrets manager
import os
from azure.keyvault.secrets import SecretClient  # Azure
from google.cloud import secretmanager  # GCP
from boto3 import client as boto3_client  # AWS

# Store keys in:
# - Azure Key Vault
# - AWS Secrets Manager
# - HashiCorp Vault
# - Environment variables (minimum for development)
```

**Implementation Priority:** 🔴 HIGH (Week 1-2)

---

### 2. Data Encryption ⚠️ CRITICAL

**Current State:**
```python
# Data stored in plain SQLite
cases.db  # ❌ Unencrypted PII and sensitive data
chroma_db/  # ❌ Unencrypted embeddings and documents
```

**Issues:**
- No field-level encryption
- No encryption at rest for databases
- No key management system (KMS/HSM)
- Sensitive PII exposure risk

**Production Requirements:**
```python
# RECOMMENDED: Field-level encryption for PII
from cryptography.fernet import Fernet
import os

class EncryptedField:
    """Field-level encryption wrapper."""
    
    def __init__(self, value: str):
        # Use AWS KMS, Azure Key Vault, or GCP KMS
        self.encrypted_value = encrypt_with_kms(value)
    
    def decrypt(self) -> str:
        return decrypt_with_kms(self.encrypted_value)

# Database encryption
# Option 1: SQLCipher (SQLite encrypted)
# Option 2: PostgreSQL with encrypted columns
# Option 3: Cloud managed databases with encryption

# Configuration example:
DATABASE_ENCRYPTION = {
    'method': 'aes256_gcm',  # AES-256-GCM encryption
    'key_rotation_days': 90,
    'master_key': os.getenv('DB_MASTER_KEY'),  # From secrets manager
}

# ChromaDB encryption
# Use encrypted volumes (LUKS for Linux, BitLocker for Windows)
# Or use ChromaDB on encrypted cloud storage (S3 with encryption)
```

**Implementation Priority:** 🔴 HIGH (Week 2-3)

---

### 3. Audit Logging & Compliance ⚠️ CRITICAL

**Current State:**
```python
# Basic Python logging only
logging.basicConfig(level=logging.INFO)
logger.info("Query processed")  # ❌ Not tamper-proof
```

**Issues:**
- No tamper-proof audit logs
- No audit trail for data access
- No compliance with SOX, GDPR, RBI requirements
- No evidence preservation for legal cases

**Production Requirements:**
```python
# RECOMMENDED: Immutable audit logging
from auditlogging import AuditLogger, AuditEvent
import hashlib
from datetime import datetime

class ComplianceAuditLogger:
    """Tamper-proof audit logger for compliance."""
    
    def log_data_access(self, user_id: str, resource: str, 
                       action: str, result: str):
        """Log all data access with cryptographic proof."""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'result': result,
            'ip_address': get_client_ip(),
            'session_id': get_session_id(),
        }
        
        # Generate cryptographic hash for tamper detection
        event['hash'] = self._generate_hash(event)
        
        # Write to immutable log storage (WORM - Write Once Read Many)
        self._write_to_immutable_storage(event)
    
    def _generate_hash(self, event: dict) -> str:
        """Generate SHA-256 hash of event data."""
        event_str = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()

# Use WORM storage:
# - AWS Glacier with legal holds
# - Azure Blob with immutable storage
# - Google Cloud Storage with bucket locks

# Audit retention:
# - SOX: 7 years
# - GDPR: Based on legal hold requirements
# - RBI: 10 years for certain records
```

**Implementation Priority:** 🔴 HIGH (Week 3-4)

---

### 4. Input Validation & Injection Prevention ⚠️ MEDIUM

**Current State:**
```python
# Basic Pydantic validation
class QueryRequest(BaseModel):
    query: str  # ❌ No length limits or sanitization
    n_results: int = 5  # ❌ Could be huge number
```

**Issues:**
- No query length limits
- Potential SQL injection if database queries used
- No input sanitization
- Potential for prompt injection attacks on LLM

**Production Requirements:**
```python
# RECOMMENDED: Enhanced input validation
from pydantic import BaseModel, validator, Field
import re

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    n_results: int = Field(5, ge=1, le=100)
    collection: Optional[str] = None
    
    @validator('query')
    def sanitize_query(cls, v):
        """Sanitize query to prevent injection attacks."""
        # Remove special SQL chars
        v = re.sub(r'[;\'"\\]', '', v)
        
        # Block prompt injection attempts
        blocked_patterns = [
            r'ignore.*previous.*instructions',
            r'system.*prompt',
            r'you are.*jailbreak',
        ]
        
        for pattern in blocked_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")
        
        return v.strip()
    
    @validator('n_results')
    def validate_n_results(cls, v):
        """Prevent resource exhaustion."""
        if v > 100:
            raise ValueError("n_results cannot exceed 100")
        return v

# Add rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/query")
@limiter.limit("20/minute")  # 20 queries per minute per IP
async def query_endpoint(request: Request, query_req: QueryRequest):
    ...
```

**Implementation Priority:** 🟡 MEDIUM (Week 4-5)

---

### 5. Secrets Management ⚠️ CRITICAL

**Current State:**
```python
# API keys in plain Python files
API_KEY = "dev-api-key"  # ❌ Hard-coded in source

# Environment variables manually loaded
from dotenv import load_dotenv
load_dotenv()
```

**Issues:**
- Secrets in source code
- No secret rotation
- No secret versioning
- Risk of secrets in git history

**Production Requirements:**
```python
# RECOMMENDED: Use secrets manager
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

class SecretsManager:
    """Unified secrets management."""
    
    def __init__(self):
        # Use cloud provider's secrets manager
        self.vault_url = os.getenv('AZURE_VAULT_URL')
        credential = DefaultAzureCredential()
        self.client = SecretClient(
            vault_url=self.vault_url,
            credential=credential
        )
    
    def get_secret(self, name: str) -> str:
        """Retrieve secret from vault."""
        secret = self.client.get_secret(name)
        return secret.value
    
    def rotate_secret(self, name: str):
        """Rotate secret periodically."""
        # Implement secret rotation logic
        new_secret = generate_random_secret()
        self.client.set_secret(name, new_secret)
        # Old version kept for rollback

# Configuration
SECRETS = {
    'anthropic_api_key': secrets_mgr.get_secret('ANTHROPIC_API_KEY'),
    'database_password': secrets_mgr.get_secret('DB_PASSWORD'),
    'jwt_secret': secrets_mgr.get_secret('JWT_SECRET'),
}

# Development fallback
if os.getenv('ENVIRONMENT') == 'development':
    SECRETS['anthropic_api_key'] = os.getenv('ANTHROPIC_API_KEY')
```

**Implementation Priority:** 🔴 HIGH (Week 1)

---

### 6. Network Security ⚠️ MEDIUM

**Current State:**
```python
# CORS: Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ Too permissive
    ...
)
```

**Issues:**
- CORS allows all origins
- No WAF (Web Application Firewall)
- No DDoS protection
- No network segmentation

**Production Requirements:**
```python
# RECOMMENDED: Restrict CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.fraudanalytics.com",
        "https://intranet.company.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Use WAF
# - Cloudflare WAF
# - AWS WAF
# - Azure Application Gateway WAF

# Network security
# - Private subnets for databases
# - VPC peering for services
# - VPN for analyst access
# - DDoS protection (AWS Shield, Azure DDoS)
```

**Implementation Priority:** 🟡 MEDIUM (Week 5-6)

---

## Security Implementation Roadmap

### Phase 1: Critical Security (Weeks 1-4) 🔴

**Week 1: Secrets & Authentication**
- [ ] Migrate to secrets manager (Azure Key Vault / AWS Secrets Manager)
- [ ] Implement OAuth2 authentication
- [ ] Remove hard-coded API keys from codebase
- [ ] Add environment-based configuration

**Week 2: Data Encryption**
- [ ] Implement field-level encryption for PII
- [ ] Configure database encryption at rest
- [ ] Set up key rotation schedule
- [ ] Encrypt ChromaDB storage

**Week 3: Audit Logging**
- [ ] Implement tamper-proof audit logging
- [ ] Configure immutable log storage
- [ ] Add data access tracking
- [ ] Set retention policies

**Week 4: Compliance Baseline**
- [ ] GDPR compliance (right to access, deletion)
- [ ] SOX audit trail requirements
- [ ] RBI reporting compliance
- [ ] Data retention policies

---

### Phase 2: Enhanced Security (Weeks 5-8) 🟡

**Week 5: Input Validation**
- [ ] Enhanced input sanitization
- [ ] Rate limiting
- [ ] Anti-automation controls
- [ ] Prompt injection prevention

**Week 6: Network Security**
- [ ] WAF deployment
- [ ] DDoS protection
- [ ] Network segmentation
- [ ] VPN for secure access

**Week 7: Monitoring & Detection**
- [ ] Security event monitoring
- [ ] Anomaly detection
- [ ] Real-time alerting
- [ ] Incident response procedures

**Week 8: Testing & Documentation**
- [ ] Security penetration testing
- [ ] OWASP Top 10 remediation
- [ ] Security documentation
- [ ] Team training

---

### Phase 3: Advanced Security (Weeks 9-12) 🟢

**Week 9-10: RBAC & Advanced Auth**
- [ ] Role-based access control
- [ ] Multi-factor authentication
- [ ] SSO integration
- [ ] Privileged access management

**Week 11-12: Advanced Controls**
- [ ] Data loss prevention (DLP)
- [ ] Dynamic data masking
- [ ] Security analytics dashboard
- [ ] Compliance reporting automation

---

## Quick Wins (Can Implement Now)

### 1. Environment Variables (5 minutes)
```bash
# Create .env file
API_KEY=generate-random-key-here
DATABASE_URL=postgresql://user:pass@localhost:5432/db
ANTHROPIC_API_KEY=sk-ant-your-key

# Use python-dotenv
pip install python-dotenv
```

### 2. Input Sanitization (30 minutes)
```python
# Add to QueryRequest model
@validator('query')
def sanitize_input(cls, v):
    # Remove dangerous chars
    v = re.sub(r'[;<>\'"\\]', '', v)
    # Limit length
    if len(v) > 1000:
        raise ValueError("Query too long")
    return v.strip()
```

### 3. Rate Limiting (15 minutes)
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("20/minute")
async def query(request, query_req: QueryRequest):
    ...
```

### 4. Basic Audit Log (45 minutes)
```python
import json
from datetime import datetime

def audit_log(action: str, user: str, details: dict):
    """Basic audit logging."""
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'action': action,
        'user': user,
        'details': details,
    }
    # Append to secure log file
    with open('/var/log/audit.log', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

---

## Security Checklist for Deployment

### Pre-Production Security Review

- [ ] All secrets moved to secrets manager
- [ ] Database encryption enabled
- [ ] Authentication & authorization implemented
- [ ] Audit logging configured
- [ ] Input validation enhanced
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] WAF deployed
- [ ] DDoS protection enabled
- [ ] Security monitoring configured
- [ ] Penetration testing completed
- [ ] Compliance requirements met
- [ ] Incident response plan documented
- [ ] Team trained on security practices
- [ ] Security documentation complete

---

## References

### Standards & Frameworks
- **OWASP Top 10**: Web application security risks
- **PCI DSS**: Payment card industry security
- **SOC 2 Type II**: Trust services criteria
- **ISO 27001**: Information security management
- **NIST CSF**: Cybersecurity framework

### Tools & Services
- **Secrets**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault
- **Encryption**: AWS KMS, Azure Key Vault, GCP KMS
- **WAF**: Cloudflare, AWS WAF, Azure Application Gateway
- **Monitoring**: Splunk, ELK Stack, Azure Sentinel, AWS Security Hub
- **Auth**: Auth0, Okta, Azure AD, AWS Cognito

### Reading List
- OWASP API Security Top 10
- NIST Special Publication 800-63 (Digital Identity Guidelines)
- OWASP Application Security Verification Standard (ASVS)
- Cloud Security Alliance (CSA) guidelines

---

## Contact

For security concerns or questions, contact the security team:
- **Security Lead**: [Your Name]
- **Email**: security@yourcompany.com
- **Reporting**: Use responsible disclosure process

**Last Updated**: October 2025
**Next Review**: January 2026

