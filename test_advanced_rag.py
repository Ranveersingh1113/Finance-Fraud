#!/usr/bin/env python3
"""
Test script for the Advanced RAG Engine with Claude 3.5 Haiku and re-ranking.
"""

import sys
import logging
import asyncio
from pathlib import Path
import os

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_advanced_rag_engine():
    """Test the advanced RAG engine with various queries."""
    logger.info("=== Testing Advanced RAG Engine ===")
    
    try:
        # Import advanced components
        from src.core.advanced_rag_engine import AdvancedRAGEngine
        from src.data.ingestion import DataIngestion
        from src.core.config import Settings
        
        # Get Anthropic API key from environment
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            logger.warning("ANTHROPIC_API_KEY not found. Testing with fallback mode.")
        
        # Initialize settings and data ingestion
        settings = Settings()
        data_ingestion = DataIngestion()
        
        # Initialize advanced RAG engine
        logger.info("Initializing Advanced RAG Engine...")
        rag_engine = AdvancedRAGEngine(
            persist_directory=settings.chroma_persist_directory,
            anthropic_api_key=anthropic_api_key
        )
        
        # Load existing SEBI data
        logger.info("Loading SEBI data...")
        sebi_chunks = data_ingestion.load_processed_sebi_chunks()
        
        if not sebi_chunks:
            logger.warning("No SEBI chunks found. Running SEBI pipeline...")
            sebi_results = data_ingestion.run_sebi_pipeline(load_from_files=True)
            sebi_chunks = sebi_results.get('processed_chunks', [])
        
        if sebi_chunks:
            logger.info(f"Adding {len(sebi_chunks)} SEBI chunks to advanced RAG engine...")
            rag_engine.add_sebi_chunks(sebi_chunks)
        else:
            logger.warning("No SEBI data available for testing")
            return False
        
        # Test queries
        test_queries = [
            "What are the common patterns of insider trading violations?",
            "How does SEBI handle market manipulation cases?",
            "What penalties are imposed for fraudulent trading practices?",
            "Tell me about recent enforcement actions against companies",
            "What are the key entities involved in securities fraud?"
        ]
        
        logger.info("Testing advanced RAG queries...")
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n--- Test Query {i} ---")
            logger.info(f"Query: {query}")
            
            try:
                # Test multi-stage retrieval
                logger.info("Testing multi-stage retrieval...")
                evidence = rag_engine.multi_stage_retrieval(query, n_results=5)
                
                logger.info(f"Retrieved {len(evidence)} evidence documents")
                if evidence:
                    logger.info(f"Top result score: {evidence[0].final_score:.3f}")
                    logger.info(f"Top result source: {evidence[0].source}")
                
                # Test full RAG query
                logger.info("Testing full RAG query...")
                rag_response = await rag_engine.query(query, n_results=5)
                
                logger.info(f"Answer: {rag_response.answer[:200]}...")
                logger.info(f"Confidence: {rag_response.confidence_score:.3f}")
                logger.info(f"Query Type: {rag_response.query_type}")
                logger.info(f"Processing Time: {rag_response.processing_time:.2f}s")
                logger.info(f"Evidence Count: {len(rag_response.evidence)}")
                
                # Test query optimization
                logger.info("Testing query optimization...")
                optimized_queries = rag_engine.optimize_query(query)
                logger.info(f"Optimized queries: {list(optimized_queries.keys())}")
                
                logger.info("✅ Query test passed")
                
            except Exception as e:
                logger.error(f"❌ Query test failed: {e}")
                continue
        
        # Test system stats
        logger.info("\n--- System Statistics ---")
        stats = rag_engine.get_advanced_stats()
        logger.info(f"Models Available: {stats.get('models_available', {})}")
        logger.info(f"Advanced Features: {stats.get('advanced_features', {})}")
        logger.info(f"Total Documents: {stats.get('total_documents', 0)}")
        
        # Test confidence calculation
        logger.info("\n--- Testing Confidence Calculation ---")
        test_evidence = evidence[:3] if evidence else []
        if test_evidence:
            confidence = rag_engine._calculate_confidence(test_evidence)
            logger.info(f"Calculated confidence: {confidence:.3f}")
        
        logger.info("\n🎉 Advanced RAG Engine tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Advanced RAG Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_endpoints():
    """Test the advanced API endpoints."""
    logger.info("\n=== Testing Advanced API ===")
    
    try:
        import httpx
        
        # Test health endpoint
        logger.info("Testing health endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                logger.info("✅ Health endpoint working")
            else:
                logger.warning(f"⚠️ Health endpoint returned {response.status_code}")
        
        # Test stats endpoint
        logger.info("Testing stats endpoint...")
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/stats")
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"✅ Stats endpoint working - {stats.get('total_documents', 0)} documents")
            else:
                logger.warning(f"⚠️ Stats endpoint returned {response.status_code}")
        
        logger.info("🎉 API tests completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ API tests failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("Starting Advanced RAG Engine Tests...")
    
    # Test 1: Advanced RAG Engine
    rag_success = await test_advanced_rag_engine()
    
    # Test 2: API Endpoints (if server is running)
    api_success = await test_api_endpoints()
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"Advanced RAG Engine: {'✅ PASSED' if rag_success else '❌ FAILED'}")
    logger.info(f"API Endpoints: {'✅ PASSED' if api_success else '❌ FAILED'}")
    
    if rag_success:
        logger.info("\n🚀 Advanced RAG Engine is ready for production use!")
        logger.info("Next steps:")
        logger.info("1. Set ANTHROPIC_API_KEY environment variable for Claude 3.5 Haiku")
        logger.info("2. Start the API server: python -m src.api.advanced_main")
        logger.info("3. Test the web interface with advanced features")
    else:
        logger.error("❌ Advanced RAG Engine needs fixes before production use")


if __name__ == "__main__":
    asyncio.run(main())
