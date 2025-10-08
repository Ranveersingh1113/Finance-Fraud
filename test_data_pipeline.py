#!/usr/bin/env python3
"""
Test script for the updated IEEE-CIS data pipeline with V-feature clustering.
"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from data.ingestion import DataIngestion

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_data_pipeline():
    """Test the complete IEEE-CIS data pipeline."""
    logger.info("Starting IEEE-CIS data pipeline test...")
    
    # Initialize data ingestion
    data_ingestion = DataIngestion()
    
    try:
        # Test 1: Load a small sample of training data
        logger.info("Test 1: Loading training data sample...")
        train_sample = data_ingestion.process_ieee_cis_pipeline(
            is_train=True, 
            sample_size=1000,
            train_clusters=True,
            n_clusters=3
        )
        
        logger.info(f"Training sample loaded: {len(train_sample)} records")
        logger.info(f"Columns: {list(train_sample.columns)}")
        
        if 'behavioral_cluster' in train_sample.columns:
            logger.info(f"Behavioral clusters: {train_sample['behavioral_cluster'].value_counts().to_dict()}")
        
        # Test 2: Load a small sample of test data
        logger.info("Test 2: Loading test data sample...")
        test_sample = data_ingestion.process_ieee_cis_pipeline(
            is_train=False, 
            sample_size=1000,
            train_clusters=False  # Use trained model from training data
        )
        
        logger.info(f"Test sample loaded: {len(test_sample)} records")
        
        # Test 3: Check transaction descriptions
        logger.info("Test 3: Checking transaction descriptions...")
        sample_descriptions = train_sample['transaction_description'].head(3).tolist()
        for i, desc in enumerate(sample_descriptions):
            logger.info(f"Description {i+1}: {desc}")
        
        # Test 4: Save and load clustering models
        logger.info("Test 4: Testing model persistence...")
        model_path = "test_clustering_models.pkl"
        data_ingestion.save_clustering_models(model_path)
        
        # Create new instance and load models
        new_ingestion = DataIngestion()
        new_ingestion.load_clustering_models(model_path)
        
        logger.info("Model persistence test completed successfully")
        
        # Clean up test file
        Path(model_path).unlink(missing_ok=True)
        
        logger.info("All tests completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_pipeline()
    sys.exit(0 if success else 1)
