"""
Baseline RAG (Retrieval-Augmented Generation) engine for financial fraud detection.
Phase 1 implementation using ChromaDB and all-MiniLM-L12-v2 embeddings.
"""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
try:
    from ..data.sebi_processor import ProcessedChunk
    from .device_config import get_device_string, device_manager
except ImportError:
    from data.sebi_processor import ProcessedChunk
    from device_config import get_device_string, device_manager

logger = logging.getLogger(__name__)


class BaselineRAGEngine:
    """
    Baseline RAG engine for financial fraud detection.
    Uses ChromaDB for vector storage and all-MiniLM-L12-v2 for embeddings.
    """
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = persist_directory
        
        # Initialize embedding model with GPU support
        device = get_device_string()
        logger.info(f"Initializing embedding model on device: {device}")
        self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2', device=device)
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Get or create collections
        self.transaction_collection = self.chroma_client.get_or_create_collection(
            name="transactions",
            metadata={"description": "IEEE-CIS transaction data"}
        )
        
        self.sebi_collection = self.chroma_client.get_or_create_collection(
            name="sebi_documents",
            metadata={"description": "SEBI orders, reports, and press releases"}
        )
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        logger.info("Baseline RAG Engine initialized")
    
    def add_transaction_data(self, df: pd.DataFrame) -> None:
        """
        Add transaction data to the vector database.
        
        Args:
            df: DataFrame with transaction data including 'transaction_description' column
        """
        try:
            # Prepare documents
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in df.iterrows():
                doc_text = row['transaction_description']
                
                # Split long documents
                chunks = self.text_splitter.split_text(doc_text)
                
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id = f"txn_{row.get('TransactionID', idx)}_{chunk_idx}"
                    
                    documents.append(chunk)
                    metadatas.append({
                        'transaction_id': row.get('TransactionID', idx),
                        'amount': row.get('TransactionAmt', 0),
                        'is_fraud': row.get('isFraud', 0),
                        'product_cd': row.get('ProductCD', 'unknown'),
                        'card_type': row.get('card4', 'unknown'),
                        'chunk_index': chunk_idx,
                        'source': 'ieee_cis'
                    })
                    ids.append(doc_id)
            
            # Generate embeddings and add to collection
            embeddings = self.embedding_model.encode(documents).tolist()
            
            self.transaction_collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} transaction chunks to vector database")
            
        except Exception as e:
            logger.error(f"Error adding transaction data: {e}")
            raise
    
    def add_sebi_data(self, df: pd.DataFrame) -> None:
        """
        Add SEBI orders data to the vector database.
        
        Args:
            df: DataFrame with SEBI data including 'order_description' column
        """
        try:
            # Prepare documents
            documents = []
            metadatas = []
            ids = []
            
            for idx, row in df.iterrows():
                doc_text = row['order_description']
                
                # Split long documents
                chunks = self.text_splitter.split_text(doc_text)
                
                for chunk_idx, chunk in enumerate(chunks):
                    doc_id = f"sebi_{row.get('order_id', idx)}_{chunk_idx}"
                    
                    documents.append(chunk)
                    metadatas.append({
                        'order_id': row.get('order_id', idx),
                        'entity_name': row.get('entity_name', 'unknown'),
                        'violation_type': row.get('violation_type', 'unknown'),
                        'penalty_amount': row.get('penalty_amount', 0),
                        'order_date': str(row.get('order_date', '')),
                        'chunk_index': chunk_idx,
                        'source': 'sebi'
                    })
                    ids.append(doc_id)
            
            # Generate embeddings and add to collection
            embeddings = self.embedding_model.encode(documents).tolist()
            
            self.sebi_collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} SEBI order chunks to vector database")
            
        except Exception as e:
            logger.error(f"Error adding SEBI data: {e}")
            raise
    
    def add_sebi_chunks(self, chunks: List[ProcessedChunk]) -> None:
        """
        Add processed SEBI chunks to the vector database.
        
        Args:
            chunks: List of ProcessedChunk objects
        """
        try:
            if not chunks:
                logger.warning("No SEBI chunks to add")
                return
            
            # Prepare documents
            documents = []
            metadatas = []
            ids = []
            
            for chunk in chunks:
                documents.append(chunk.content)
                
                # Create comprehensive metadata
                metadata = {
                    'chunk_id': chunk.chunk_id,
                    'document_id': chunk.document_id,
                    'document_type': chunk.document_type,
                    'title': chunk.title,
                    'chunk_index': chunk.chunk_index,
                    'violation_types': ', '.join(chunk.violation_types),
                    'entities': ', '.join(chunk.entities),
                    'keywords': ', '.join(chunk.keywords),
                    'source': 'sebi_processed',
                    'content_length': len(chunk.content),
                    'word_count': chunk.metadata.get('chunk_word_count', 0)
                }
                
                # Add document-specific metadata
                doc_metadata = chunk.metadata
                if 'document_title' in doc_metadata:
                    metadata['document_title'] = doc_metadata['document_title']
                if 'document_date' in doc_metadata:
                    metadata['document_date'] = str(doc_metadata['document_date'])
                if 'document_url' in doc_metadata:
                    metadata['document_url'] = doc_metadata['document_url']
                
                # Add penalty information if available
                penalty_info = doc_metadata.get('penalty_info', {})
                if penalty_info:
                    if 'amounts' in penalty_info:
                        metadata['penalty_amounts'] = ', '.join(penalty_info['amounts'])
                    if 'types' in penalty_info:
                        metadata['penalty_types'] = ', '.join(penalty_info['types'])
                
                # Add financial terms
                financial_terms = doc_metadata.get('financial_terms', [])
                if financial_terms:
                    metadata['financial_terms'] = ', '.join(financial_terms)
                
                metadatas.append(metadata)
                ids.append(chunk.chunk_id)
            
            # Generate embeddings and add to collection
            embeddings = self.embedding_model.encode(documents).tolist()
            
            self.sebi_collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(documents)} processed SEBI chunks to vector database")
            
        except Exception as e:
            logger.error(f"Error adding SEBI chunks: {e}")
            raise
    
    def search_transactions(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search transaction data using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant transaction documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in transaction collection
            results = self.transaction_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching transactions: {e}")
            return []
    
    def search_sebi_documents(self, query: str, n_results: int = 5, 
                             document_type: Optional[str] = None,
                             violation_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search SEBI documents using semantic similarity with filtering.
        
        Args:
            query: Search query
            n_results: Number of results to return
            document_type: Filter by document type (enforcement_order, investigation_report, press_release)
            violation_type: Filter by violation type (insider_trading, market_manipulation, etc.)
            
        Returns:
            List of relevant SEBI document chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Build where clause for filtering
            where_clause = {}
            if document_type:
                where_clause['document_type'] = document_type
            if violation_type:
                where_clause['violation_types'] = {'$contains': violation_type}
            
            # Search in SEBI collection
            results = self.sebi_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_clause if where_clause else None,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching SEBI documents: {e}")
            return []
    
    def search_sebi_orders(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search SEBI orders data using semantic similarity.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of relevant SEBI order documents with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in SEBI collection
            results = self.sebi_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['documents'][0])):
                formatted_results.append({
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'similarity_score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching SEBI orders: {e}")
            return []
    
    def search_all(self, query: str, n_results: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search across all collections.
        
        Args:
            query: Search query
            n_results: Number of results per collection
            
        Returns:
            Dictionary with results from each collection
        """
        return {
            'transactions': self.search_transactions(query, n_results // 2),
            'sebi_documents': self.search_sebi_documents(query, n_results // 2)
        }
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collections."""
        try:
            transaction_count = self.transaction_collection.count()
            sebi_count = self.sebi_collection.count()
            
            return {
                'transaction_count': transaction_count,
                'sebi_document_count': sebi_count,
                'total_documents': transaction_count + sebi_count,
                'collections': {
                    'transactions': {
                        'name': 'transactions',
                        'description': 'IEEE-CIS transaction data',
                        'count': transaction_count
                    },
                    'sebi_documents': {
                        'name': 'sebi_documents', 
                        'description': 'SEBI orders, reports, and press releases',
                        'count': sebi_count
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'error': str(e)}
