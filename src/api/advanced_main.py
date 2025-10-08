"""
Advanced FastAPI backend for the Financial Intelligence Platform.
Phase 3 implementation with production-grade RAG engine and Ollama integration.
"""
from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
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
from src.data.ingestion import DataIngestion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

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
    global rag_engine, data_ingestion
    
    try:
        logger.info("Initializing Advanced Financial Intelligence Platform...")
        
        # Initialize advanced components
        rag_engine = AdvancedRAGEngine(
            persist_directory=settings.chroma_persist_directory,
            ollama_model="llama3.1:8b",
            ollama_host="http://localhost:11434"
        )
        
        data_ingestion = DataIngestion()
        
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
async def query_rag_engine(request: QueryRequest):
    """
    Query the advanced RAG engine with Ollama-powered generation.
    
    Args:
        request: Query request with parameters
        
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
async def create_case(request: CaseRequest, background_tasks: BackgroundTasks):
    """
    Create a new investigation case.
    
    Args:
        request: Case creation request
        background_tasks: FastAPI background tasks
        
    Returns:
        Case creation response
    """
    try:
        # TODO: Implement actual case storage (JSON/SQLite)
        # For now, just return a mock response
        
        background_tasks.add_task(log_case_creation, request.case_id, request.description)
        
        return CaseResponse(
            case_id=request.case_id,
            status="created",
            created_at=datetime.now().isoformat(),
            message=f"Case {request.case_id} created successfully"
        )
        
    except Exception as e:
        logger.error(f"Case creation error: {e}")
        raise HTTPException(status_code=500, detail=f"Case creation failed: {str(e)}")


@app.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get case details."""
    try:
        # TODO: Implement actual case retrieval
        return {
            "case_id": case_id,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "message": "Case retrieval not yet implemented"
        }
        
    except Exception as e:
        logger.error(f"Case retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Case retrieval failed: {str(e)}")


@app.post("/cases/{case_id}/analyze")
async def analyze_case(case_id: str, query: str = Query(..., description="Analysis query")):
    """
    Analyze a case using the RAG engine.
    
    Args:
        case_id: Case identifier
        query: Analysis query
        
    Returns:
        Analysis results
    """
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        # Perform analysis
        rag_response = await rag_engine.query(query, n_results=10)
        
        return {
            "case_id": case_id,
            "analysis_query": query,
            "analysis": rag_response.answer,
            "confidence": rag_response.confidence_score,
            "evidence_count": len(rag_response.evidence),
            "query_type": rag_response.query_type
        }
        
    except Exception as e:
        logger.error(f"Case analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Case analysis failed: {str(e)}")


@app.get("/stats")
async def get_system_stats():
    """Get comprehensive system statistics."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        stats = rag_engine.get_advanced_stats()
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