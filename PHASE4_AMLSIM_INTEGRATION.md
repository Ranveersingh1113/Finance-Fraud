# Phase 4: AMLSim Integration Strategy

**Status:** Planning Phase  
**Timeline:** Week 3-4  
**Purpose:** Replace IEEE-CIS with AMLSim for transaction network graph

---

## 🎯 Why AMLSim Instead of IEEE-CIS?

### **AMLSim Advantages for Knowledge Graph:**

| Feature | IEEE-CIS | AMLSim | Winner |
|---------|----------|--------|--------|
| **Built-in Relationships** | ❌ No | ✅ Yes | AMLSim ✅ |
| **Account Networks** | ❌ Inferred | ✅ Explicit | AMLSim ✅ |
| **Money Laundering Patterns** | ❌ Generic fraud | ✅ Specific AML | AMLSim ✅ |
| **Transaction Chains** | ❌ Independent | ✅ Connected | AMLSim ✅ |
| **Alert Types** | ❌ None | ✅ Labeled | AMLSim ✅ |
| **Graph-Ready** | ❌ Requires inference | ✅ Native graph structure | AMLSim ✅ |

**AMLSim is PERFECT for GraphRAG because:**
- ✅ Designed for network analysis (account-to-account)
- ✅ Has explicit transaction relationships
- ✅ Includes labeled suspicious patterns
- ✅ Better aligns with SEBI enforcement (regulatory + AML)

---

## 📊 AMLSim Data Structure

### **Core Files**
```
AMLSim typically provides:
1. accounts.csv          - Account information
   - account_id, account_type, balance, is_sar

2. transactions.csv      - Transaction records  
   - transaction_id, orig_account, dest_account, amount, timestamp

3. alert_accounts.csv    - Suspicious accounts
   - account_id, alert_type, sar_flag

4. patterns.csv (optional) - Money laundering patterns
   - pattern_id, pattern_type, accounts_involved
```

### **Key Advantages:**
- ✅ **Explicit relationships:** orig_account → dest_account (perfect for graphs!)
- ✅ **Network structure:** Can trace money flow chains
- ✅ **Alert labels:** Know which patterns are suspicious
- ✅ **Real ML patterns:** Fan-out, fan-in, cycles, layering

---

## 🏗️ AMLSim Graph Schema Design

### **Node Types:**

```python
Node Types in AMLSim Graph:
├─ Account (Primary)
│  Properties: account_id, balance, account_type, is_sar, risk_score
│
├─ Transaction
│  Properties: txn_id, amount, timestamp, pattern_type
│
├─ Alert
│  Properties: alert_id, alert_type, sar_flag, severity
│
└─ Pattern
   Properties: pattern_id, pattern_name, typology
```

### **Relationship Types:**

```python
Relationships in AMLSim Graph:
├─ SENT_TO (Account → Account via Transaction)
│  Properties: amount, timestamp, transaction_id
│
├─ RECEIVED_FROM (Account → Account)
│  Properties: amount, timestamp
│
├─ TRIGGERED (Transaction → Alert)
│  Properties: confidence_score, alert_type
│
├─ PARTICIPATES_IN (Account → Pattern)
│  Properties: role (sender/receiver/intermediary)
│
└─ PART_OF (Transaction → Pattern)
   Properties: pattern_type (fan-out, layering, cycle)
```

---

## 🔍 Money Laundering Patterns to Detect

### **Pattern 1: Fan-Out (Placement)**
```
           ┌─> Account B ($10K)
Account A ─┼─> Account C ($10K)
           └─> Account D ($10K)

Detection: Single source → Multiple destinations
Risk: Breaking large amounts into smaller transfers
```

### **Pattern 2: Fan-In (Integration)**
```
Account A ─┐
Account B ─┼─> Account D
Account C ─┘

Detection: Multiple sources → Single destination
Risk: Consolidating illicit funds
```

### **Pattern 3: Cycle/Round-Tripping (Layering)**
```
Account A → Account B → Account C → Account A

Detection: Circular transaction chains
Risk: Obscuring money origin through layers
```

### **Pattern 4: Structuring (Smurfing)**
```
Account A: $9,900 (repeated 20 times)

Detection: Just below reporting threshold ($10K)
Risk: Avoiding regulatory reporting
```

---

## 📋 Implementation Plan

### **Week 3: AMLSim Data Integration**

#### **Task 1: Obtain/Generate AMLSim Data**
```bash
Options:
A. Download AMLSim from GitHub
   https://github.com/IBM/AMLSim

B. Generate synthetic data using AMLSim
   - Install AMLSim
   - Configure parameters
   - Generate transaction network

C. Use pre-generated AMLSim dataset
   - Find public AMLSim dataset
   - Download and place in ./data/amlsim/
```

#### **Task 2: Create AMLSim Loader**
```python
# src/data/amlsim_loader.py

class AMLSimLoader:
    """Load and parse AMLSim data files."""
    
    def load_accounts(self) -> pd.DataFrame:
        """Load accounts.csv"""
        
    def load_transactions(self) -> pd.DataFrame:
        """Load transactions.csv"""
        
    def load_alerts(self) -> pd.DataFrame:
        """Load alert_accounts.csv"""
        
    def merge_data(self) -> pd.DataFrame:
        """Merge all AMLSim data"""
```

#### **Task 3: Create Document Generator**
```python
# src/data/amlsim_document_generator.py

def generate_transaction_document(txn_row):
    """
    Convert AMLSim transaction to natural language.
    
    Example Output:
    --------------
    Transaction ID: TXN_12345
    
    TRANSACTION FLOW:
    - From: Account_A001 (Individual Savings)
    - To: Account_B002 (Business Checking)
    - Amount: $15,000.00
    - Date: 2024-03-15 14:23:00
    
    PATTERN ANALYSIS:
    - Pattern Type: Fan-Out (Placement)
    - Risk Score: HIGH
    - Alert Triggered: SAR_SUSPICIOUS_ACTIVITY
    
    CONTEXT:
    This transaction is part of a fan-out pattern where
    Account_A001 sent funds to 15 different accounts within
    24 hours, indicating potential structuring activity.
    """
```

---

### **Week 4: AMLSim Knowledge Graph Construction**

#### **Task 1: Create AMLSim Graph Manager**
```python
# src/core/amlsim_graph_manager.py

class AMLSimGraphManager(GraphManager):
    """
    Build transaction network graph from AMLSim data.
    
    Specialized for:
    - Account-to-account relationships
    - Transaction flow tracking
    - Money laundering pattern detection
    - Alert integration
    """
    
    def add_transaction_network(self, transactions_df):
        """Build graph from transaction flows"""
        
    def detect_fan_out(self, account_id, threshold=5):
        """Detect fan-out patterns (1 → many)"""
        
    def detect_fan_in(self, account_id, threshold=5):
        """Detect fan-in patterns (many → 1)"""
        
    def detect_cycles(self, max_length=5):
        """Detect circular transaction chains"""
        
    def get_transaction_chain(self, start_account, max_hops=5):
        """Trace money flow chains"""
```

---

## 🎯 AMLSim vs SEBI Graph: Complementary Intelligence

### **SEBI Graph (Regulatory)**
```
Purpose: "What does the law say about this violation?"

Queries:
- "What penalties were imposed for money laundering?"
- "Show me SEBI enforcement actions for layering"
- "Find similar regulatory cases"

Output: Legal precedents, penalties, enforcement actions
```

### **AMLSim Graph (Transactional)**
```
Purpose: "Is this transaction pattern suspicious?"

Queries:
- "Does this account show fan-out behavior?"
- "Trace money flow from Account A"
- "Find circular transaction patterns"

Output: Transaction networks, suspicious patterns, money trails
```

### **Combined Power (GraphRAG)**
```
Purpose: "Is this transaction illegal AND matches known patterns?"

Query: "Analyze Account X for money laundering"

System Response:
1. AMLSim Graph: "Account X shows fan-out to 15 accounts"
2. SEBI Graph: "Similar pattern in SEBI Case #2020-042 (penalty: ₹50L)"
3. RAG: Retrieves both regulatory text + transaction data
4. LLM: "Account X exhibits layering behavior matching SEBI
         enforcement precedent. Pattern: placement via fan-out,
         similar to Case #2020-042 which resulted in ₹50L penalty."
```

---

## 📊 Expected Graph Size

### **AMLSim Graph Estimates:**
```
Typical AMLSim Dataset:
- Accounts: 1,000 - 10,000 nodes
- Transactions: 10,000 - 100,000 edges
- Alerts: 100 - 1,000 nodes
- Patterns: 10-50 distinct patterns

Processing Time Estimate:
- 10K transactions: ~2-5 minutes
- Graph construction: Fast (already structured)
- Pattern detection: ~1-2 minutes
```

---

## 🚀 Benefits for Your Platform

### **1. Natural Graph Structure**
```
IEEE-CIS:
- Had to infer relationships (Card → Device)
- Guesswork on connections
- No explicit money flow

AMLSim:
- Native account relationships ✅
- Explicit transaction flows ✅
- Money trail tracking ✅
```

### **2. Better Alignment with SEBI**
```
SEBI enforces:
- Money laundering regulations
- Layering detection
- Structuring violations

AMLSim provides:
- Money laundering patterns
- Layering chains
- Structuring examples

Perfect match! ✅
```

### **3. Client Value**
```
For Banks/Financial Institutions:
✅ Detect suspicious account networks
✅ Trace money laundering chains
✅ Identify high-risk accounts
✅ Generate alerts with regulatory context
✅ SAR reports with transaction flow diagrams
```

---

## 📋 Next Immediate Steps

### **Step 1: Research AMLSim** (1-2 hours)
- [ ] Review AMLSim documentation
- [ ] Understand data schema
- [ ] Identify best data source (GitHub, public dataset, or generate)

### **Step 2: Obtain AMLSim Data** (2-4 hours)
- [ ] Download/generate AMLSim dataset
- [ ] Place in `./data/amlsim/` directory
- [ ] Verify data quality and completeness

### **Step 3: Create AMLSim Loader** (4-6 hours)
- [ ] Implement data loading functions
- [ ] Test data parsing
- [ ] Validate relationships

### **Step 4: Build AMLSim Graph** (6-8 hours)
- [ ] Create `AMLSimGraphManager`
- [ ] Build account network
- [ ] Implement pattern detection
- [ ] Test queries

**Total Estimate:** 2-3 days for complete AMLSim integration

---

## ✅ Decision Summary

**IEEE-CIS → AMLSim Switch:**
- ✅ Better for knowledge graph construction
- ✅ Native transaction relationships
- ✅ Money laundering focused
- ✅ Aligns with SEBI regulatory context
- ✅ Cleaner client value proposition

**Next Action:** Research and obtain AMLSim data

---

**Ready to research AMLSim and begin integration?** 🚀

