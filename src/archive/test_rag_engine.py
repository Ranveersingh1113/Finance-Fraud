"""
Tests for the RAG engine functionality.
"""
import pytest
import pandas as pd
import tempfile
import shutil
from pathlib import Path

from src.core.rag_engine import BaselineRAGEngine
from src.data.ingestion import DataIngestion


class TestBaselineRAGEngine:
    """Test cases for BaselineRAGEngine."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def rag_engine(self, temp_dir):
        """Create a RAG engine instance for testing."""
        return BaselineRAGEngine(persist_directory=temp_dir)
    
    @pytest.fixture
    def sample_transaction_data(self):
        """Create sample transaction data for testing."""
        return pd.DataFrame({
            'TransactionID': [1, 2, 3],
            'TransactionAmt': [100.0, 250.0, 50.0],
            'ProductCD': ['W', 'C', 'R'],
            'card4': ['visa', 'mastercard', 'visa'],
            'isFraud': [0, 1, 0],
            'transaction_description': [
                'Transaction ID 1: Amount $100.00, Product W, Card type visa',
                'Transaction ID 2: Amount $250.00, Product C, Card type mastercard [FRAUD DETECTED]',
                'Transaction ID 3: Amount $50.00, Product R, Card type visa'
            ]
        })
    
    @pytest.fixture
    def sample_sebi_data(self):
        """Create sample SEBI data for testing."""
        return pd.DataFrame({
            'order_id': ['SEBI/ORDER/001', 'SEBI/ORDER/002'],
            'entity_name': ['Entity_A', 'Entity_B'],
            'violation_type': ['Insider Trading', 'Market Manipulation'],
            'penalty_amount': [100000, 250000],
            'order_description': [
                'SEBI Order SEBI/ORDER/001: Entity Entity_A, Violation: Insider Trading, Penalty: ₹100,000.00',
                'SEBI Order SEBI/ORDER/002: Entity Entity_B, Violation: Market Manipulation, Penalty: ₹250,000.00'
            ]
        })
    
    def test_rag_engine_initialization(self, rag_engine):
        """Test RAG engine initialization."""
        assert rag_engine is not None
        assert rag_engine.embedding_model is not None
        assert rag_engine.chroma_client is not None
    
    def test_add_transaction_data(self, rag_engine, sample_transaction_data):
        """Test adding transaction data to the vector database."""
        # This should not raise an exception
        rag_engine.add_transaction_data(sample_transaction_data)
        
        # Check that data was added
        stats = rag_engine.get_collection_stats()
        assert stats['transaction_count'] > 0
    
    def test_add_sebi_data(self, rag_engine, sample_sebi_data):
        """Test adding SEBI data to the vector database."""
        # This should not raise an exception
        rag_engine.add_sebi_data(sample_sebi_data)
        
        # Check that data was added
        stats = rag_engine.get_collection_stats()
        assert stats['sebi_count'] > 0
    
    def test_search_transactions(self, rag_engine, sample_transaction_data):
        """Test searching transaction data."""
        # Add data first
        rag_engine.add_transaction_data(sample_transaction_data)
        
        # Search for fraud-related transactions
        results = rag_engine.search_transactions("fraudulent transaction", n_results=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        
        # Check result structure
        if results:
            result = results[0]
            assert 'document' in result
            assert 'metadata' in result
            assert 'similarity_score' in result
    
    def test_search_sebi_orders(self, rag_engine, sample_sebi_data):
        """Test searching SEBI orders."""
        # Add data first
        rag_engine.add_sebi_data(sample_sebi_data)
        
        # Search for insider trading
        results = rag_engine.search_sebi_orders("insider trading", n_results=2)
        
        assert isinstance(results, list)
        assert len(results) <= 2
        
        # Check result structure
        if results:
            result = results[0]
            assert 'document' in result
            assert 'metadata' in result
            assert 'similarity_score' in result
    
    def test_search_all(self, rag_engine, sample_transaction_data, sample_sebi_data):
        """Test searching across all collections."""
        # Add both datasets
        rag_engine.add_transaction_data(sample_transaction_data)
        rag_engine.add_sebi_data(sample_sebi_data)
        
        # Search all collections
        results = rag_engine.search_all("fraud", n_results=5)
        
        assert isinstance(results, dict)
        assert 'transactions' in results
        assert 'sebi_orders' in results
        
        # Check that we have results from both collections
        total_results = len(results['transactions']) + len(results['sebi_orders'])
        assert total_results > 0
    
    def test_get_collection_stats(self, rag_engine, sample_transaction_data, sample_sebi_data):
        """Test getting collection statistics."""
        # Initial stats should show zero
        initial_stats = rag_engine.get_collection_stats()
        assert initial_stats['transaction_count'] == 0
        assert initial_stats['sebi_count'] == 0
        
        # Add data
        rag_engine.add_transaction_data(sample_transaction_data)
        rag_engine.add_sebi_data(sample_sebi_data)
        
        # Check updated stats
        updated_stats = rag_engine.get_collection_stats()
        assert updated_stats['transaction_count'] > 0
        assert updated_stats['sebi_count'] > 0
        assert updated_stats['total_documents'] > 0


class TestDataIngestion:
    """Test cases for DataIngestion."""
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create a temporary data directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def data_ingestion(self, temp_data_dir):
        """Create a DataIngestion instance for testing."""
        return DataIngestion(data_directory=temp_data_dir)
    
    def test_data_ingestion_initialization(self, data_ingestion):
        """Test DataIngestion initialization."""
        assert data_ingestion is not None
        assert data_ingestion.data_directory is not None
    
    def test_create_sample_ieee_cis_data(self, data_ingestion):
        """Test creating sample IEEE-CIS data."""
        df = data_ingestion._create_sample_ieee_cis_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'transaction_description' in df.columns
        assert 'TransactionID' in df.columns
        assert 'isFraud' in df.columns
    
    def test_create_sample_sebi_data(self, data_ingestion):
        """Test creating sample SEBI data."""
        df = data_ingestion._create_sample_sebi_data()
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert 'order_description' in df.columns
        assert 'order_id' in df.columns
        assert 'violation_type' in df.columns
    
    def test_get_all_data(self, data_ingestion):
        """Test getting all data."""
        all_data = data_ingestion.get_all_data()
        
        assert isinstance(all_data, dict)
        assert 'ieee_cis' in all_data
        assert 'sebi' in all_data
        
        # Should return DataFrames
        assert isinstance(all_data['ieee_cis'], pd.DataFrame)
        assert isinstance(all_data['sebi'], pd.DataFrame)
