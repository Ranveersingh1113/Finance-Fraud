#!/usr/bin/env python3
"""
Test script for SEBI file processing (manually downloaded files).
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_sebi_file_processor():
    """Test the SEBI file processor with manually downloaded files."""
    logger.info("Testing SEBI file processor...")
    
    try:
        from src.data.sebi_file_processor import SEBIFileProcessor
        
        # Initialize processor
        processor = SEBIFileProcessor(sebi_directory="./data/sebi")
        
        # Check if there are any files to process
        files = processor.scan_sebi_files()
        logger.info(f"Found {len(files)} files to process")
        
        if not files:
            logger.warning("No SEBI files found in ./data/sebi directory")
            logger.info("Please manually download SEBI documents and place them in ./data/sebi/")
            logger.info("Supported formats: .pdf, .txt, .doc, .docx")
            return True
        
        # Process all files
        documents = processor.process_all_files()
        logger.info(f"Successfully processed {len(documents)} documents")
        
        if documents:
            # Save to CSV
            processor.save_documents_to_csv(documents, "processed_sebi_documents.csv")
            
            # Display summary
            summary = processor.get_processing_summary(documents)
            logger.info("Processing Summary:")
            logger.info(f"Total documents: {summary.get('total_documents', 0)}")
            logger.info(f"Document types: {summary.get('document_types', {})}")
            logger.info(f"Violation types: {summary.get('violation_types', {})}")
            logger.info(f"Date range: {summary.get('date_range', {})}")
            
            # Display sample documents
            for i, doc in enumerate(documents[:3]):
                logger.info(f"Sample {i+1}: {doc.title}")
                logger.info(f"  Type: {doc.document_type}")
                logger.info(f"  Date: {doc.date}")
                logger.info(f"  Violations: {doc.metadata.get('violation_types', [])}")
                logger.info(f"  Content length: {len(doc.content)} chars")
                logger.info("---")
        
        logger.info("SEBI file processor test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"SEBI file processor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_full_pipeline():
    """Test the full SEBI data pipeline."""
    logger.info("Testing full SEBI data pipeline...")
    
    try:
        from src.data.ingestion import DataIngestion
        
        # Initialize data ingestion
        data_ingestion = DataIngestion()
        
        # Run SEBI pipeline
        results = data_ingestion.run_sebi_pipeline(load_from_files=True)
        
        logger.info("Pipeline Results:")
        logger.info(f"Loaded documents: {len(results.get('loaded_documents', []))}")
        logger.info(f"Processed chunks: {len(results.get('processed_chunks', []))}")
        logger.info(f"Summary keys: {list(results.get('summary', {}).keys())}")
        
        logger.info("Full SEBI pipeline test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Full pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    logger.info("=== SEBI File Processing Test ===")
    
    # Test file processor
    success1 = test_sebi_file_processor()
    
    if success1:
        # Test full pipeline
        success2 = test_full_pipeline()
        
        if success1 and success2:
            logger.info("All tests passed! ✅")
            return True
        else:
            logger.error("Some tests failed! ❌")
            return False
    else:
        logger.error("File processor test failed! ❌")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

