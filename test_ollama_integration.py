#!/usr/bin/env python3
"""
Test script for Ollama integration with the Advanced RAG Engine.
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


async def test_ollama_integration():
    """Test Ollama integration with the advanced RAG engine."""
    logger.info("=== Testing Ollama Integration with Advanced RAG Engine ===")
    
    try:
        # Import advanced components
        from src.core.advanced_rag_engine import AdvancedRAGEngine
        from src.data.ingestion import DataIngestion
        from src.core.config import Settings
        
        # Initialize settings and data ingestion
        settings = Settings()
        data_ingestion = DataIngestion()
        
        # Initialize advanced RAG engine with Ollama
        logger.info("Initializing Advanced RAG Engine with Ollama...")
        rag_engine = AdvancedRAGEngine(
            persist_directory=settings.chroma_persist_directory,
            ollama_model="llama3.1:8b",
            ollama_host="http://localhost:11434"
        )
        
        # Check model availability
        logger.info("Checking model availability...")
        stats = rag_engine.get_advanced_stats()
        logger.info(f"Models Available: {stats['models_available']}")
        
        if not stats['models_available']['ollama_llama']:
            logger.error("Ollama Llama model not available!")
            logger.info("Please ensure:")
            logger.info("1. Ollama is installed and running")
            logger.info("2. Llama 3.1 8B model is available")
            logger.info("3. Ollama server is running on http://localhost:11434")
            return False
        
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
        ]
        
        logger.info("Testing Ollama-powered RAG queries...")
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n--- Test Query {i} ---")
            logger.info(f"Query: {query}")
            
            try:
                # Test full RAG query with Ollama
                logger.info("Testing Ollama-powered RAG query...")
                rag_response = await rag_engine.query(query, n_results=5)
                
                logger.info(f"Answer: {rag_response.answer[:300]}...")
                logger.info(f"Confidence: {rag_response.confidence_score:.3f}")
                logger.info(f"Query Type: {rag_response.query_type}")
                logger.info(f"Processing Time: {rag_response.processing_time:.2f}s")
                logger.info(f"Evidence Count: {len(rag_response.evidence)}")
                
                # Show evidence sources
                if rag_response.evidence:
                    logger.info("Evidence Sources:")
                    for j, evidence in enumerate(rag_response.evidence[:3], 1):
                        logger.info(f"  {j}. Score: {evidence.final_score:.3f} | Source: {evidence.source}")
                
            except Exception as e:
                logger.error(f"Error testing query {i}: {e}")
                continue
        
        logger.info("\n=== Ollama Integration Test Completed ===")
        return True
        
    except Exception as e:
        logger.error(f"Error in Ollama integration test: {e}")
        return False


def check_ollama_status():
    """Check if Ollama is running and has the required model."""
    logger.info("=== Checking Ollama Status ===")
    
    try:
        import ollama
        
        # Test connection
        client = ollama.Client(host="http://localhost:11434")
        models = client.list()
        
        logger.info(f"Ollama is running on http://localhost:11434")
        model_names = [model.model for model in models.models]
        logger.info(f"Available models: {model_names}")
        
        # Check for Llama 3.1 8B
        if "llama3.1:8b" in model_names:
            logger.info("✅ Llama 3.1 8B model is available")
            return True
        else:
            logger.warning("❌ Llama 3.1 8B model not found")
            logger.info("Available models:")
            for model in model_names:
                logger.info(f"  - {model}")
            logger.info("\nTo install Llama 3.1 8B, run:")
            logger.info("  ollama pull llama3.1:8b")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ollama is not running or not accessible: {e}")
        logger.info("Please ensure Ollama is installed and running:")
        logger.info("1. Install Ollama: https://ollama.ai/")
        logger.info("2. Start Ollama service")
        logger.info("3. Pull the model: ollama pull llama3.1:8b")
        return False


async def main():
    """Main test function."""
    logger.info("Starting Ollama Integration Test...")
    
    # First check Ollama status
    if not check_ollama_status():
        logger.error("Ollama setup incomplete. Please fix the issues above.")
        return
    
    # Run the integration test
    success = await test_ollama_integration()
    
    if success:
        logger.info("✅ Ollama integration test completed successfully!")
    else:
        logger.error("❌ Ollama integration test failed!")


if __name__ == "__main__":
    asyncio.run(main())

