"""
Advanced FastAPI backend for the Financial Intelligence Platform.
Phase 3 implementation with production-grade RAG engine and Ollama integration.
"""
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import uvicorn
import asyncio
from datetime import datetime

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

# Valid API keys (in production, use database or environment variables)
VALID_API_KEYS = {
    settings.api_key,  # From config/env
    "dev-api-key",     # Development key
    "analyst-key-001"  # Analyst key
}

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
rag_engine = None
data_ingestion = None
case_manager = None


class QueryRequest(BaseModel):
    """Request model for RAG queries."""
    query: str
    n_results: int = 5
    collection: Optional[str] = None  # 'transactions', 'sebi_documents', or None for all
    include_metadata: bool = True


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
    case_id: str
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
    global rag_engine, data_ingestion, case_manager
    
    try:
        logger.info("Initializing Advanced Financial Intelligence Platform...")
        
        # Initialize advanced components
        rag_engine = AdvancedRAGEngine(
            persist_directory=settings.chroma_persist_directory,
            ollama_model="llama3.1:8b",
            ollama_host="http://localhost:11434"
        )
        
        data_ingestion = DataIngestion()
        
        # Initialize case manager
        case_manager = CaseManager(db_path="./data/cases.db")
        logger.info("Case manager initialized")
        
        # Load existing SEBI data
        logger.info("Loading SEBI data...")
        sebi_chunks = data_ingestion.load_processed_sebi_chunks()
        
        if sebi_chunks:
            logger.info(f"Adding {len(sebi_chunks)} SEBI chunks to advanced RAG engine...")
            rag_engine.add_sebi_chunks(sebi_chunks)
            logger.info("SEBI data indexed successfully")
        else:
            logger.warning("No SEBI data found. Please run the data pipeline first.")
        
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
async def query_rag_engine(request: QueryRequest, api_key: str = Depends(get_api_key)):
    """
    Query the advanced RAG engine with Ollama-powered generation.
    
    Requires API key authentication.
    
    Args:
        request: Query request with parameters
        api_key: API key for authentication
        
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
                "embedding_model": "all-MiniLM-L12-v2"
            }
        )
        
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


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
        
        # Perform analysis
        rag_response = await rag_engine.query(query, n_results=10)
        
        # Save query to case
        evidence_list = [
            {
                'rank': i + 1,
                'score': result.final_score or result.similarity_score,
                'document': result.document[:500],
                'source': result.source,
                'metadata': result.metadata
            }
            for i, result in enumerate(rag_response.evidence)
        ]
        
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


async def log_case_creation(case_id: str, description: str):
    """Background task to log case creation."""
    logger.info(f"Case {case_id} created: {description}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api.advanced_main:app",
        host="127.0.0.1",
        port=8001,
        reload=False
    )