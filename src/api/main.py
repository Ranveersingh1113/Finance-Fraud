"""
FastAPI backend for the Financial Intelligence Platform.
Phase 1 implementation with basic RAG endpoints.
"""
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import uvicorn

from src.core.config import settings
from src.core.rag_engine import BaselineRAGEngine
from src.data.ingestion import DataIngestion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Financial Intelligence Platform API",
    description="API for financial fraud detection and analysis",
    version="1.0.0"
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


class SearchRequest(BaseModel):
    """Request model for search queries."""
    query: str
    n_results: int = 5
    collection: Optional[str] = None  # 'transactions', 'sebi_orders', or None for all


class SearchResponse(BaseModel):
    """Response model for search results."""
    query: str
    results: Dict[str, List[Dict[str, Any]]]
    total_results: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    database_stats: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global rag_engine, data_ingestion
    
    try:
        logger.info("Initializing Financial Intelligence Platform...")
        
        # Initialize components
        rag_engine = BaselineRAGEngine(settings.chroma_persist_directory)
        data_ingestion = DataIngestion(settings.data_directory)
        
        # Load and index data
        logger.info("Loading and indexing data...")
        all_data = data_ingestion.get_all_data()
        
        if not all_data['ieee_cis'].empty:
            rag_engine.add_transaction_data(all_data['ieee_cis'])
            logger.info("Transaction data indexed")
        
        if not all_data['sebi'].empty:
            rag_engine.add_sebi_data(all_data['sebi'])
            logger.info("SEBI data indexed")
        
        logger.info("Application startup completed successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "message": "Financial Intelligence Platform API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        stats = rag_engine.get_collection_stats() if rag_engine else {}
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            database_stats=stats
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for relevant documents using semantic similarity.
    
    Args:
        request: Search request with query and parameters
        
    Returns:
        Search results with relevant documents and metadata
    """
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        # Perform search based on collection preference
        if request.collection == "transactions":
            results = {
                "transactions": rag_engine.search_transactions(request.query, request.n_results),
                "sebi_orders": []
            }
        elif request.collection == "sebi_orders":
            results = {
                "transactions": [],
                "sebi_orders": rag_engine.search_sebi_orders(request.query, request.n_results)
            }
        else:
            # Search all collections
            results = rag_engine.search_all(request.query, request.n_results)
        
        total_results = sum(len(collection_results) for collection_results in results.values())
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=total_results
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/search/transactions")
async def search_transactions(
    query: str = Query(..., description="Search query"),
    n_results: int = Query(5, description="Number of results to return")
):
    """Search only transaction data."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        results = rag_engine.search_transactions(query, n_results)
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Transaction search error: {e}")
        raise HTTPException(status_code=500, detail=f"Transaction search failed: {str(e)}")


@app.get("/search/sebi")
async def search_sebi_orders(
    query: str = Query(..., description="Search query"),
    n_results: int = Query(5, description="Number of results to return")
):
    """Search only SEBI orders data."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        results = rag_engine.search_sebi_orders(query, n_results)
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"SEBI search error: {e}")
        raise HTTPException(status_code=500, detail=f"SEBI search failed: {str(e)}")


@app.get("/stats")
async def get_database_stats():
    """Get database statistics."""
    try:
        if not rag_engine:
            raise HTTPException(status_code=500, detail="RAG engine not initialized")
        
        stats = rag_engine.get_collection_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats retrieval failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
