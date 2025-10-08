#!/usr/bin/env python3
"""
Test script for complete SEBI pipeline: file processing, chunking, and RAG integration.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_pipeline():
    """Test the complete SEBI pipeline from file processing to RAG integration."""
    logger.info("=== Testing Complete SEBI Pipeline ===")
    
    try:
        # Step 1: Load and process SEBI documents
        logger.info("Step 1: Loading SEBI documents...")
        from src.data.ingestion import DataIngestion
        
        data_ingestion = DataIngestion()
        documents = data_ingestion.load_sebi_data_from_files()
        logger.info(f"✅ Loaded {len(documents)} SEBI documents")
        
        # Step 2: Process documents into chunks
        logger.info("Step 2: Processing documents into chunks...")
        chunks = data_ingestion.process_sebi_documents(documents)
        logger.info(f"✅ Generated {len(chunks)} chunks from {len(documents)} documents")
        
        if chunks:
            # Step 3: Save processed chunks
            logger.info("Step 3: Saving processed chunks...")
            from src.data.sebi_processor import SEBIProcessor
            processor = SEBIProcessor()
            processor.save_processed_chunks(chunks, "./data/sebi/processed_chunks.csv")
            logger.info("✅ Saved processed chunks to CSV")
            
            # Step 4: Test RAG integration
            logger.info("Step 4: Testing RAG integration...")
            from src.core.rag_engine import BaselineRAGEngine
            
            rag_engine = BaselineRAGEngine()
            rag_engine.add_sebi_chunks(chunks)
            logger.info("✅ Added SEBI chunks to RAG engine")
            
            # Step 5: Test semantic search
            logger.info("Step 5: Testing semantic search...")
            test_queries = [
                "insider trading penalties",
                "market manipulation cases",
                "fraudulent trade practices",
                "monetary penalties imposed",
                "research analyst violations"
            ]
            
            for query in test_queries:
                results = rag_engine.search_sebi_documents(query, n_results=3)
                logger.info(f"Query: '{query}' -> Found {len(results)} results")
                if results:
                    logger.info(f"  Top result: {results[0].get('metadata', {}).get('document_title', 'No title')[:60]}...")
            
            # Step 6: Get collection statistics
            logger.info("Step 6: Getting collection statistics...")
            stats = rag_engine.get_collection_stats()
            logger.info(f"✅ RAG Engine Statistics: {stats}")
            
            # Step 7: Test filtered search
            logger.info("Step 7: Testing filtered search...")
            filtered_results = rag_engine.search_sebi_documents(
                "insider trading",
                n_results=5,
                document_type="adjudication_order",
                violation_type="insider_trading"
            )
            logger.info(f"✅ Filtered search found {len(filtered_results)} insider trading cases")
            
            logger.info("🎉 Complete SEBI pipeline test PASSED!")
            return True
            
        else:
            logger.warning("No chunks generated - pipeline incomplete")
            return False
            
    except Exception as e:
        logger.error(f"❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chunk_quality():
    """Test the quality of generated chunks."""
    logger.info("=== Testing Chunk Quality ===")
    
    try:
        # Load a few sample chunks
        import pandas as pd
        chunks_df = pd.read_csv("./data/sebi/processed_chunks.csv")
        
        logger.info(f"Total chunks: {len(chunks_df)}")
        logger.info(f"Average chunk length: {chunks_df['content_length'].mean():.0f} characters")
        logger.info(f"Chunk length range: {chunks_df['content_length'].min()} - {chunks_df['content_length'].max()}")
        
        # Check metadata quality
        violation_types = chunks_df['violation_types'].dropna()
        entities = chunks_df['entities'].dropna()
        
        logger.info(f"Chunks with violation types: {len(violation_types)}/{len(chunks_df)}")
        logger.info(f"Chunks with entities: {len(entities)}/{len(chunks_df)}")
        
        # Sample chunk analysis
        sample_chunk = chunks_df.iloc[0]
        logger.info(f"Sample chunk metadata:")
        logger.info(f"  Document: {sample_chunk['title'][:50]}...")
        logger.info(f"  Type: {sample_chunk['document_type']}")
        logger.info(f"  Length: {sample_chunk['content_length']} chars")
        logger.info(f"  Violations: {sample_chunk['violation_types']}")
        
        logger.info("✅ Chunk quality analysis completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Chunk quality test failed: {e}")
        return False

def main():
    """Main test function."""
    logger.info("🚀 Starting SEBI Pipeline Validation")
    
    # Test 1: Complete pipeline
    pipeline_success = test_complete_pipeline()
    
    # Test 2: Chunk quality
    quality_success = test_chunk_quality()
    
    if pipeline_success and quality_success:
        logger.info("🎉 ALL TESTS PASSED! SEBI Pipeline is ready for production!")
        return True
    else:
        logger.error("❌ Some tests failed. Please check the logs.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
