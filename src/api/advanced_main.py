"""
Advanced FastAPI backend for the Financial Intelligence Platform.
Phase 3 implementation with production-grade RAG engine and Ollama integration.
"""
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, Security, Request
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
import logging
import uvicorn
import asyncio
from datetime import datetime
import os
import re
import json
from pathlib import Path

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import Settings
from src.core.advanced_rag_engine import AdvancedRAGEngine
from src.core.case_manager import CaseManager
from src.data.ingestion import DataIngestion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# API Key Security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Valid API keys - Load from environment variables for security
VALID_API_KEYS = {
    settings.api_key,  # From config/env
    os.getenv('API_KEY_DEV'),     # Development key from env
    os.getenv('API_KEY_ANALYST'),  # Analyst key from env
    "dev-api-key",     # Fallback for development only
}

# Filter out None values
VALID_API_KEYS = {key for key in VALID_API_KEYS if key}

async def get_api_key(api_key: str = Security(api_key_header)):
    """Validate API key for secured endpoints."""
    if api_key in VALID_API_KEYS:
        return api_key
    raise HTTPException(
        status_code=403,
        detail="Invalid or missing API key"
    )

# Initialize FastAPI app
app = FastAPI(
    title="Financial Intelligence Platform - Advanced API",
    description="Production-grade API for financial fraud detection and analysis with Ollama integration",
    version="2.0.0"
)

# Add CORS middleware
# Parse CORS origins from environment variable (comma-separated or "*" for all)
cors_origins_list = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting (if slowapi is installed)
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    RATE_LIMITING_ENABLED = True
    logger.info("Rate limiting enabled")
except ImportError:
    limiter = None
    RATE_LIMITING_ENABLED = False
    logger.warning("Rate limiting not available (slowapi not installed)")

# Audit logging setup
AUDIT_LOG_DIR = Path("./logs")
AUDIT_LOG_DIR.mkdir(exist_ok=True)
AUDIT_LOG_FILE = AUDIT_LOG_DIR / "audit.log"

def audit_log(action: str, user: str, details: dict, request: Request = None):
    """
    Basic audit logging for compliance.
    
    Args:
        action: Action performed (e.g., 'query', 'case_create')
        user: User identifier or API key
        details: Additional details about the action
        request: FastAPI request object for IP address
    """
    try:
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'user': user if user else 'anonymous',
            'ip_address': request.client.host if request and request.client else None,
            'details': details,
        }
        
        # Append to secure log file
        with open(AUDIT_LOG_FILE, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Also log to standard logger for visibility
        logger.info(f"AUDIT: {action} by {user if user else 'anonymous'}")
        
    except Exception as e:
        logger.error(f"Audit logging failed: {e}")

# Global instances
rag_engine = None
data_ingestion = None
case_manager = None
unified_engine = None  # Unified GraphRAG engine (initialized once!)


class QueryRequest(BaseModel):
    """Request model for RAG queries with input validation."""
    query: str
    n_results: int = 5
    collection: Optional[str] = None  # 'transactions', 'sebi_documents', or None for all
    include_metadata: bool = True
    
    @validator('query')
    def sanitize_query(cls, v):
        """Sanitize query to prevent injection attacks."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        
        # Remove dangerous characters
        v = re.sub(r'[;<>\'"\\]', '', v)
        
        # Block prompt injection attempts
        blocked_patterns = [
            r'ignore.*previous.*instructions',
            r'system.*prompt',
            r'you are.*jailbreak',
        ]
        
        for pattern in blocked_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")
        
        # Limit length
        if len(v) > 1000:
            raise ValueError("Query too long (max 1000 characters)")
        
        return v.strip()
    
    @validator('n_results')
    def validate_n_results(cls, v):
        """Prevent resource exhaustion."""
        if v < 1 or v > 100:
            raise ValueError("n_results must be between 1 and 100")
        return v


class QueryResponse(BaseModel):
    """Response model for RAG query results."""
    query: str
    answer: str
    confidence_score: float
    query_type: str
    processing_time: float
    evidence: List[Dict[str, Any]]
    metadata: Dict[str, Any]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_available: Dict[str, Any]
    database_stats: Dict[str, Any]
    uptime: str


class CaseRequest(BaseModel):
    """Request model for case creation."""
    case_id: Optional[str] = None  # Optional - will be auto-generated if not provided
    description: str
    priority: str = "medium"  # low, medium, high, critical
    analyst: str
    tags: List[str] = []


class CaseResponse(BaseModel):
    """Response model for case operations."""
    case_id: str
    status: str
    created_at: str
    message: str


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global rag_engine, data_ingestion, case_manager, unified_engine
    
    try:
        logger.info("Initializing Advanced Financial Intelligence Platform...")
        
        # Initialize advanced components
        rag_engine = AdvancedRAGEngine(
            persist_directory=settings.chroma_persist_directory,
            ollama_model=settings.ollama_model,
            ollama_host=settings.ollama_host
        )
        
        data_ingestion = DataIngestion()
        
        # Initialize case manager
        case_manager = CaseManager(db_path=settings.cases_db_path)
        logger.info("Case manager initialized")
        
        # Check if SEBI data already exists in ChromaDB
        logger.info("Checking SEBI data in ChromaDB...")
        existing_count = rag_engine.sebi_collection.count()
        
        if existing_count > 0:
            logger.info(f"Found {existing_count} existing SEBI documents in ChromaDB - skipping reload")
        else:
            # Load existing SEBI data from processed chunks
            logger.info("Loading SEBI data from processed chunks...")
            sebi_chunks = data_ingestion.load_processed_sebi_chunks()
            
            if sebi_chunks:
                logger.info(f"Adding {len(sebi_chunks)} SEBI chunks to advanced RAG engine...")
                rag_engine.add_sebi_chunks(sebi_chunks)
                logger.info("SEBI data indexed successfully")
            else:
                logger.warning("No SEBI data found. Please run the data pipeline first.")
        
        # Check FIU collection
        try:
            fiu_count = rag_engine.fiu_collection.count()
            if fiu_count > 0:
                logger.info(f"✓ FIU collection initialized: {fiu_count} documents")
            else:
                logger.warning(f"⚠ FIU collection exists but is empty ({fiu_count} documents). Index FIU data to use it.")
        except Exception as e:
            logger.warning(f"FIU collection check failed: {e}")
        
        # Check Income Tax collection
        try:
            incometax_count = rag_engine.incometax_collection.count()
            if incometax_count > 0:
                logger.info(f"✓ Income Tax collection initialized: {incometax_count} documents")
            else:
                logger.warning(f"⚠ Income Tax collection exists but is empty ({incometax_count} documents). Index Income Tax data to use it.")
        except Exception as e:
            logger.warning(f"Income Tax collection check failed: {e}")
        
        # Initialize Unified GraphRAG Engine (once on startup for performance!)
        logger.info("Initializing Unified GraphRAG Engine...")
        try:
            from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
            unified_engine = UnifiedGraphRAGEngine(
                persist_directory=settings.graphs_directory,
                chroma_directory=settings.chroma_persist_directory,
                ollama_model=settings.ollama_model,
                ollama_host=settings.ollama_host
            )
            
            # Log graph status
            if unified_engine.amlsim_graph.graph:
                amlsim_nodes = len(unified_engine.amlsim_graph.graph.nodes())
                amlsim_edges = len(unified_engine.amlsim_graph.graph.edges())
                logger.info(f"AMLSim graph status: {amlsim_nodes} nodes, {amlsim_edges} edges")
            else:
                logger.warning("AMLSim graph is empty - graph visualization will not work")
            
            logger.info("Unified GraphRAG Engine initialized with cached patterns")
        except Exception as e:
            logger.warning(f"Unified engine initialization failed: {e}")
            logger.warning("Unified GraphRAG queries will not be available")
            unified_engine = None
        
        logger.info("Advanced application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Financial Intelligence Platform - Advanced API",
        "version": "2.0.0",
        "status": "running",
        "features": "Ollama + Llama 3.1 8B, BGE Reranker, Advanced RAG"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with model status."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        stats = rag_engine.get_advanced_stats()
        
        return HealthResponse(
            status="healthy",
            version="2.0.0",
            models_available=stats.get('models_available', {}),
            database_stats=stats.get('database_stats', {}),
            uptime="N/A"  # Could implement proper uptime tracking
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/query", response_model=QueryResponse)
async def query_rag_engine(
    request: QueryRequest,
    api_key: str = Depends(get_api_key),
    req: Request = None
):
    """
    Query the advanced RAG engine with Ollama-powered generation.
    
    Requires API key authentication.
    
    Args:
        request: Query request with parameters
        api_key: API key for authentication
        req: FastAPI request object for audit logging
        
    Returns:
        Comprehensive response with answer, evidence, and metadata
    """
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        start_time = datetime.now()
        
        # Perform RAG query
        rag_response = await rag_engine.query(
            query=request.query,
            n_results=request.n_results
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare evidence for response
        evidence = []
        for i, result in enumerate(rag_response.evidence):
            evidence_item = {
                "rank": i + 1,
                "score": result.final_score or result.similarity_score,
                "document": result.document[:500] + "..." if len(result.document) > 500 else result.document,
                "metadata": result.metadata if request.include_metadata else {},
                "source": result.source
            }
            evidence.append(evidence_item)
        
        # Audit log the query
        audit_log(
            action="query",
            user=api_key[-8:] if api_key else "anonymous",  # Last 8 chars for privacy
            details={
                "query_length": len(request.query),
                "n_results": request.n_results,
                "query_type": rag_response.query_type,
                "processing_time": processing_time
            },
            request=req
        )
        
        return QueryResponse(
            query=request.query,
            answer=rag_response.answer,
            confidence_score=rag_response.confidence_score,
            query_type=rag_response.query_type,
            processing_time=processing_time,
            evidence=evidence,
            metadata={
                "model_used": "ollama_llama" if rag_engine.use_ollama else "fallback",
                "reranker_used": rag_engine.use_reranker,
                "embedding_model": settings.embedding_model
            }
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@app.post("/query/unified")
async def query_unified_graphrag(request: QueryRequest, api_key: str = Depends(get_api_key)):
    """
    Query the unified GraphRAG engine (SEBI + AMLSim knowledge graphs).
    
    This endpoint combines:
    - SEBI regulatory knowledge graph
    - AMLSim transaction network graph
    - ChromaDB vector retrieval
    - LLM-powered answer generation
    - PRE-COMPUTED fraud pattern cache (instant queries!)
    
    Requires API key authentication.
    """
    try:
        if not unified_engine:
            raise HTTPException(
                status_code=503, 
                detail="Unified GraphRAG engine not initialized. Please restart the API server."
            )
        
        logger.info(f"Unified query received: {request.query}")
        start_time = datetime.now()
        
        # Execute unified query (using global cached instance - FAST!)
        result = await unified_engine.unified_query(
            query=request.query,
            use_graphs=True,
            n_results=request.n_results
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Flatten evidence for Streamlit compatibility
        evidence = []
        rank = 1
        
        # Add SEBI results
        for doc in result.get('sebi_results', [])[:5]:
            evidence.append({
                "rank": rank,
                "score": doc.get('score', 0),
                "document": doc.get('document', '')[:500] + "..." if len(doc.get('document', '')) > 500 else doc.get('document', ''),
                "source": "sebi_regulation",
                "metadata": doc.get('metadata', {})
            })
            rank += 1
        
        # Add AMLSim results
        for doc in result.get('amlsim_results', [])[:5]:
            evidence.append({
                "rank": rank,
                "score": doc.get('score', 0),
                "document": doc.get('document', '')[:500] + "..." if len(doc.get('document', '')) > 500 else doc.get('document', ''),
                "source": "amlsim_transaction",
                "metadata": doc.get('metadata', {})
            })
            rank += 1
        
        # Format response (compatible with Streamlit display)
        return {
            "query": request.query,
            "answer": result.get('answer', ''),
            "confidence_score": result.get('confidence', 0.8),
            "query_type": result.get('query_type', 'unknown'),
            "processing_time": processing_time,
            "evidence": evidence,
            "metadata": {
                "model_used": "unified_graphrag",
                "graphs_loaded": True,
                "pattern_cache_used": True,
                "cross_domain_matches": result.get('cross_domain_patterns', 0),
                "sebi_entities_found": len(result.get('sebi_entities', [])),
                "amlsim_patterns_found": len(result.get('amlsim_patterns', []))
            }
        }
        
    except Exception as e:
        logger.error(f"Unified query error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unified query failed: {str(e)}")


@app.get("/query/simple")
async def simple_query(
    query: str = Query(..., description="Search query"),
    n_results: int = Query(5, description="Number of results to return")
):
    """Simple query endpoint for quick testing."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        rag_response = await rag_engine.query(query, n_results)
        
        return {
            "query": query,
            "answer": rag_response.answer,
            "confidence": rag_response.confidence_score,
            "evidence_count": len(rag_response.evidence)
        }
        
    except Exception as e:
        logger.error(f"Simple query error: {e}")
        raise HTTPException(status_code=500, detail=f"Simple query failed: {str(e)}")


@app.post("/cases", response_model=CaseResponse)
async def create_case(request: CaseRequest, background_tasks: BackgroundTasks, api_key: str = Depends(get_api_key)):
    """
    Create a new investigation case.
    
    Requires API key authentication.
    
    Args:
        request: Case creation request
        background_tasks: FastAPI background tasks
        api_key: API key for authentication
        
    Returns:
        Case creation response
    """
    try:
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        # Generate case_id if not provided
        if not request.case_id:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            request.case_id = f"CASE_{timestamp}"
        
        # Create case in database
        case_data = case_manager.create_case(
            case_id=request.case_id,
            description=request.description,
            priority=request.priority,
            analyst=request.analyst,
            tags=request.tags
        )
        
        background_tasks.add_task(log_case_creation, request.case_id, request.description)
        
        return CaseResponse(
            case_id=case_data['case_id'],
            status="created",
            created_at=case_data['created_at'],
            message=f"Case {request.case_id} created successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Case creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Case creation failed: {str(e)}")


@app.get("/cases/{case_id}")
async def get_case(case_id: str, api_key: str = Depends(get_api_key)):
    """Get case details. Requires API key authentication."""
    try:
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        case_data = case_manager.get_case(case_id)
        
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Get associated queries
        queries = case_manager.get_case_queries(case_id)
        case_data['queries'] = queries
        case_data['query_count'] = len(queries)
        
        return case_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Case retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Case retrieval failed: {str(e)}")


@app.post("/cases/{case_id}/analyze")
async def analyze_case(case_id: str, query: str = Query(..., description="Analysis query"), 
                      api_key: str = Depends(get_api_key)):
    """
    Analyze a case using the RAG engine.
    
    Requires API key authentication.
    
    Args:
        case_id: Case identifier
        query: Analysis query
        api_key: API key for authentication
        
    Returns:
        Analysis results
    """
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        # Verify case exists
        case_data = case_manager.get_case(case_id)
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Smart routing: Detect query intent to route appropriately
        query_lower = query.lower()
        
        # Detect regulatory/SEBI queries (higher priority)
        regulatory_keywords = ['sebi', 'regulation', 'regulatory', 'compliance', 'violation', 'penalty', 
                              'precedent', 'enforcement', 'rule', 'law', 'legal', 'regulatory context']
        is_regulatory_query = any(keyword in query_lower for keyword in regulatory_keywords)
        
        # Detect transaction-related queries
        transaction_keywords = ['cash flow', 'cashflow', 'balance', 'transfer', 'payment', 
                               'deposit', 'withdrawal', 'send', 'receive', 'amount', 'money', 'fund']
        # Only consider "account" as transaction keyword if not in regulatory context
        is_transaction_query = any(keyword in query_lower for keyword in transaction_keywords) or \
                              ('account' in query_lower and not is_regulatory_query)
        
        # Use unified engine for hybrid queries (regulatory + account) or transaction queries
        # Use basic RAG for pure regulatory queries without account context
        if unified_engine and (is_regulatory_query or is_transaction_query):
            if is_regulatory_query:
                logger.info(f"Routing regulatory query to unified GraphRAG engine: {query}")
            else:
                logger.info(f"Routing transaction query to unified GraphRAG engine: {query}")
            import time
            start_time = time.time()
            
            unified_result = await unified_engine.unified_query(
                query=query,
                use_graphs=True,
                n_results=10
            )
            
            processing_time = time.time() - start_time
            
            # Convert unified result to RAG response format
            evidence = []
            
            # Prioritize based on query type
            if is_regulatory_query:
                # For regulatory queries, prioritize SEBI results
                for i, doc in enumerate(unified_result.get('sebi_results', [])[:10]):
                    evidence.append({
                        'rank': i + 1,
                        'score': doc.get('score', 0),
                        'document': doc.get('document', ''),
                        'source': 'sebi_regulation',
                        'metadata': doc.get('metadata', {})
                    })
                
                # Add transaction results for context (fewer for regulatory queries)
                for i, doc in enumerate(unified_result.get('amlsim_results', [])[:5]):
                    evidence.append({
                        'rank': len(evidence) + 1,
                        'score': doc.get('score', 0),
                        'document': doc.get('document', ''),
                        'source': 'amlsim_transaction',
                        'metadata': doc.get('metadata', {})
                    })
            else:
                # For transaction queries, prioritize transaction results
                for i, doc in enumerate(unified_result.get('amlsim_results', [])[:10]):
                    evidence.append({
                        'rank': i + 1,
                        'score': doc.get('score', 0),
                        'document': doc.get('document', ''),
                        'source': 'amlsim_transaction',
                        'metadata': doc.get('metadata', {})
                    })
                
                # Add SEBI results (fewer for transaction queries)
                for i, doc in enumerate(unified_result.get('sebi_results', [])[:3]):
                    evidence.append({
                        'rank': len(evidence) + 1,
                        'score': doc.get('score', 0),
                        'document': doc.get('document', ''),
                        'source': 'sebi_regulation',
                        'metadata': doc.get('metadata', {})
                    })
            
            # Calculate confidence based on evidence quality
            if evidence:
                avg_score = sum(d.get('score', 0) for d in evidence) / len(evidence)
                confidence = min(0.95, 0.5 + avg_score * 0.5)  # Scale to 0.5-0.95 range
            else:
                confidence = 0.3
            
            # Create RAGResponse-like structure
            rag_response = type('RAGResponse', (), {
                'answer': unified_result.get('answer', 'No answer generated'),
                'confidence_score': confidence,
                'query_type': unified_result.get('query_type', 'transaction'),
                'processing_time': processing_time,
                'evidence': evidence
            })()
        else:
            # Use basic RAG engine for regulatory/SEBI queries
            logger.info(f"Routing query to basic RAG engine: {query}")
            rag_response = await rag_engine.query(query, n_results=10)
        
        # Save query to case (handle both QueryResult objects and dict evidence)
        evidence_list = []
        for i, evidence_item in enumerate(rag_response.evidence):
            if isinstance(evidence_item, dict):
                # Already in dict format (from unified engine)
                evidence_list.append({
                    'rank': evidence_item.get('rank', i + 1),
                    'score': evidence_item.get('score', 0),
                    'document': evidence_item.get('document', '')[:500],
                    'source': evidence_item.get('source', 'unknown'),
                    'metadata': evidence_item.get('metadata', {})
                })
            else:
                # QueryResult object (from basic RAG engine)
                evidence_list.append({
                    'rank': i + 1,
                    'score': evidence_item.final_score or evidence_item.similarity_score,
                    'document': evidence_item.document[:500],
                    'source': getattr(evidence_item, 'source', 'unknown'),
                    'metadata': evidence_item.metadata
                })
        
        case_manager.add_query_to_case(
            case_id=case_id,
            query=query,
            answer=rag_response.answer,
            confidence_score=rag_response.confidence_score,
            query_type=rag_response.query_type,
            processing_time=rag_response.processing_time,
            evidence=evidence_list
        )
        
        return {
            "case_id": case_id,
            "analysis_query": query,
            "analysis": rag_response.answer,
            "confidence": rag_response.confidence_score,
            "evidence_count": len(rag_response.evidence),
            "query_type": rag_response.query_type,
            "processing_time": rag_response.processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Case analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Case analysis failed: {str(e)}")


@app.get("/cases")
async def list_cases(status: Optional[str] = None, api_key: str = Depends(get_api_key)):
    """List all cases, optionally filtered by status. Requires API key authentication."""
    try:
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        cases = case_manager.list_cases(status=status)
        return {
            "cases": cases,
            "count": len(cases),
            "filter": status
        }
        
    except Exception as e:
        logger.error(f"List cases error: {e}")
        raise HTTPException(status_code=500, detail=f"List cases failed: {str(e)}")


@app.delete("/cases/{case_id}")
async def delete_case(case_id: str, api_key: str = Depends(get_api_key)):
    """Delete a case. Requires API key authentication."""
    try:
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        success = case_manager.delete_case(case_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found or deletion failed")
        
        return {
            "case_id": case_id,
            "status": "deleted",
            "message": f"Case {case_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete case error: {e}")
        raise HTTPException(status_code=500, detail=f"Case deletion failed: {str(e)}")


@app.post("/cases/{case_id}/sar")
async def generate_sar(case_id: str, api_key: str = Depends(get_api_key)):
    """Generate SAR (Suspicious Activity Report) for a case. Requires API key authentication."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        # Get case data
        case_data = case_manager.get_case(case_id)
        if not case_data:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Get case queries for context
        queries = case_manager.get_case_queries(case_id)
        
        # Generate comprehensive SAR using RAG
        sar_query = f"""Generate a comprehensive Suspicious Activity Report (SAR) for the following case:
        
Case ID: {case_id}
Description: {case_data['description']}
Priority: {case_data['priority']}
Analyst: {case_data['analyst']}

The SAR should include:
1. Executive Summary
2. Case Overview
3. Key Findings and Evidence
4. Patterns and Red Flags Identified
5. Supporting Documentation
6. Recommendations for Further Action
7. Conclusion

Previous Analysis Queries: {len(queries)} queries performed
Latest Query Results: {queries[0]['answer'][:200] if queries else 'No previous queries'}

Please provide a detailed, professional SAR suitable for regulatory submission."""
        
        rag_response = await rag_engine.query(sar_query, n_results=15)
        
        # Save SAR to database
        sar_id = case_manager.save_sar_report(
            case_id=case_id,
            report_content=rag_response.answer,
            analyst=case_data['analyst'],
            status='draft'
        )
        
        return {
            "case_id": case_id,
            "sar_id": sar_id,
            "report_content": rag_response.answer,
            "confidence": rag_response.confidence_score,
            "generated_at": datetime.now().isoformat(),
            "status": "draft"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"SAR generation error: {e}")
        raise HTTPException(status_code=500, detail=f"SAR generation failed: {str(e)}")


@app.get("/cases/{case_id}/sar")
async def get_sar_reports(case_id: str, api_key: str = Depends(get_api_key)):
    """Get all SAR reports for a case. Requires API key authentication."""
    try:
        if not case_manager:
            raise HTTPException(status_code=500, detail="Case manager not initialized")
        
        reports = case_manager.get_sar_reports(case_id)
        
        return {
            "case_id": case_id,
            "reports": reports,
            "count": len(reports)
        }
        
    except Exception as e:
        logger.error(f"Get SAR reports error: {e}")
        raise HTTPException(status_code=500, detail=f"Get SAR reports failed: {str(e)}")


@app.get("/graph/account/{account_id}")
async def get_account_graph(
    account_id: str,
    hops: int = Query(default=2, ge=1, le=3, description="Number of hops to traverse (1-3)"),
    max_nodes: int = Query(default=200, ge=50, le=500, description="Maximum nodes to return (50-500)"),
    api_key: str = Depends(get_api_key)
):
    """
    Get ego network (local subgraph) for a specific account.
    Returns only the nodes and edges within N hops of the account.
    Requires API key authentication.
    
    Args:
        account_id: Account ID (e.g., '108' or 'account_108')
        hops: Number of hops to traverse (default 2, max 3)
        max_nodes: Maximum nodes to return for performance (default 200, max 500)
    
    Returns:
        Graph data with nodes, edges, and statistics
    """
    try:
        if not unified_engine:
            raise HTTPException(status_code=500, detail="Unified GraphRAG engine not initialized")
        
        # Check if AMLSim graph is loaded and has nodes
        if not hasattr(unified_engine.amlsim_graph, 'graph'):
            raise HTTPException(
                status_code=503, 
                detail="AMLSim graph manager not properly initialized"
            )
        
        graph = unified_engine.amlsim_graph.graph
        if not graph or len(graph.nodes()) == 0:
            # Try to reload the graph
            logger.warning("AMLSim graph appears empty, attempting to reload...")
            reloaded = unified_engine.amlsim_graph.load_graph()
            if not reloaded or len(unified_engine.amlsim_graph.graph.nodes()) == 0:
                raise HTTPException(
                    status_code=503, 
                    detail="AMLSim transaction graph is not loaded or is empty. Please build the graph first using: python build_amlsim_graph.py"
                )
            graph = unified_engine.amlsim_graph.graph
        
        # Normalize account ID format
        original_account_id = account_id
        if not account_id.startswith('account_'):
            account_id = f'account_{account_id}'
        
        # Check if account exists in graph
        if account_id not in unified_engine.amlsim_graph.graph:
            # Try to find similar accounts for helpful error message
            all_accounts = list(unified_engine.amlsim_graph.find_nodes_by_type('Account'))
            account_numbers = [acc.replace('account_', '') for acc in all_accounts[:10]]  # First 10 for reference
            
            error_msg = f"Account {original_account_id} not found in the transaction graph."
            if account_numbers:
                error_msg += f" Available accounts (sample): {', '.join(account_numbers)}"
            raise HTTPException(status_code=404, detail=error_msg)
        
        # Extract ego network from AMLSim graph
        graph_data = unified_engine.amlsim_graph.get_ego_network(
            account_id=account_id,
            max_hops=hops,
            max_nodes=max_nodes
        )
        
        if 'error' in graph_data:
            raise HTTPException(status_code=404, detail=graph_data['error'])
        
        # Check if we got any nodes
        if graph_data.get('stats', {}).get('total_nodes', 0) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Account {original_account_id} exists but has no connections within {hops} hop(s). Try increasing the number of hops."
            )
        
        logger.info(f"Graph extracted for {account_id}: {graph_data['stats']['total_nodes']} nodes, {graph_data['stats']['total_edges']} edges")
        
        return {
            "success": True,
            "account_id": account_id,
            "graph": graph_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Graph extraction error for {account_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Graph extraction failed: {str(e)}")


@app.get("/graph/status")
async def get_graph_status(api_key: str = Depends(get_api_key)):
    """
    Get graph status and diagnostics.
    Useful for debugging graph loading issues.
    """
    try:
        status = {
            "unified_engine_initialized": unified_engine is not None,
            "amlsim_graph": {},
            "sebi_graph": {}
        }
        
        if unified_engine:
            # Check AMLSim graph
            amlsim_status = {
                "manager_exists": hasattr(unified_engine, 'amlsim_graph'),
                "graph_loaded": False,
                "node_count": 0,
                "edge_count": 0,
                "sample_accounts": []
            }
            
            if hasattr(unified_engine, 'amlsim_graph'):
                if hasattr(unified_engine.amlsim_graph, 'graph'):
                    graph = unified_engine.amlsim_graph.graph
                    if graph:
                        amlsim_status["graph_loaded"] = True
                        amlsim_status["node_count"] = len(graph.nodes())
                        amlsim_status["edge_count"] = len(graph.edges())
                        
                        # Get sample account IDs
                        account_nodes = unified_engine.amlsim_graph.find_nodes_by_type('Account')
                        amlsim_status["sample_accounts"] = [
                            acc.replace('account_', '') for acc in list(account_nodes)[:20]
                        ]
            
            status["amlsim_graph"] = amlsim_status
            
            # Check SEBI graph
            sebi_status = {
                "manager_exists": hasattr(unified_engine, 'sebi_graph'),
                "graph_loaded": False,
                "node_count": 0
            }
            
            if hasattr(unified_engine, 'sebi_graph'):
                if hasattr(unified_engine.sebi_graph, 'graph'):
                    graph = unified_engine.sebi_graph.graph
                    if graph:
                        sebi_status["graph_loaded"] = True
                        sebi_status["node_count"] = len(graph.nodes())
            
            status["sebi_graph"] = sebi_status
        
        return status
        
    except Exception as e:
        logger.error(f"Graph status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Graph status check failed: {str(e)}")


@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        stats = rag_engine.get_advanced_stats()
        
        # Add case statistics if case_manager is available
        if case_manager:
            case_stats = case_manager.get_case_statistics()
            stats['case_statistics'] = case_stats
        
        return {
            "system_status": "operational",
            "rag_engine_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    avatar_url: Optional[str] = None
    department: Optional[str] = None
    joined_date: Optional[str] = None


@app.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile(api_key: str = Depends(get_api_key)):
    """
    Get current user profile information.
    
    For now, returns a default user profile. In production, this would:
    - Extract user info from JWT token or session
    - Query user database
    - Return actual user data
    
    Requires API key authentication.
    """
    try:
        # TODO: In production, extract user ID from JWT token or session
        # For now, return a default profile that can be customized
        # You can also check the API key to determine which user to return
        
        # Default user profile - can be customized based on API key or session
        default_profile = {
            "id": "user_001",
            "name": "Sarah Johnson",
            "email": "sarah.johnson@company.com",
            "role": "Senior Fraud Analyst",
            "avatar_url": None,
            "department": "Financial Intelligence Unit",
            "joined_date": "2023-01-15"
        }
        
        # In production, you would do something like:
        # user_id = get_user_id_from_token(api_key)
        # user = user_db.get_user(user_id)
        # return UserProfileResponse(**user)
        
        return UserProfileResponse(**default_profile)
        
    except Exception as e:
        logger.error(f"User profile error: {e}")
        raise HTTPException(status_code=500, detail=f"User profile retrieval failed: {str(e)}")


async def log_case_creation(case_id: str, description: str):
    """Background task to log case creation."""
    logger.info(f"Case {case_id} created: {description}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api.advanced_main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False
    )