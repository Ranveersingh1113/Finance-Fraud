"""
Data ingestion module for processing financial fraud datasets.
Supports IEEE-CIS transaction data and SEBI orders/reports.
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import pickle
import warnings
warnings.filterwarnings('ignore')

# Import SEBI modules
try:
    from .sebi_file_processor import SEBIFileProcessor, SEBIDocument
    from .sebi_processor import SEBIProcessor, ProcessedChunk
except ImportError:
    from sebi_file_processor import SEBIFileProcessor, SEBIDocument
    from sebi_processor import SEBIProcessor, ProcessedChunk

logger = logging.getLogger(__name__)


class DataIngestion:
    """Handles data ingestion and preprocessing for financial fraud datasets."""
    
    def __init__(self, data_directory: str = "./data"):
        self.data_directory = Path(data_directory)
        self.ieee_cis_path = self.data_directory / "ieee_cis"
        self.sebi_path = self.data_directory / "sebi"
        
        # V-feature clustering components
        self.v_feature_clusterer = None
        self.v_feature_scaler = None
        self.v_feature_imputer = None
        self.behavioral_cluster_names = {}
        self.v_features_columns = [f"V{i}" for i in range(1, 340)]
        
        # SEBI components
        self.sebi_file_processor = None
        self.sebi_processor = None
        self.sebi_documents = []
        self.sebi_chunks = []
        
    def load_ieee_cis_transaction_data(self, is_train: bool = True, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load IEEE-CIS transaction data with efficient memory usage.
        
        Args:
            is_train: Whether to load training data (includes isFraud column)
            sample_size: If provided, load only a sample of the data
            
        Returns:
            Processed DataFrame with transaction data
        """
        file_name = "train_transaction.csv" if is_train else "test_transaction.csv"
        file_path = self.ieee_cis_path / file_name
        
        if not file_path.exists():
            logger.warning(f"IEEE-CIS {file_name} not found. Creating sample data.")
            return self._create_sample_ieee_cis_data()
        
        try:
            # Load data with memory optimization
            if sample_size:
                df = pd.read_csv(file_path, nrows=sample_size)
                logger.info(f"Loaded IEEE-CIS {file_name} sample: {len(df)} records")
            else:
                # Use chunking for large files
                df = pd.read_csv(file_path, low_memory=False)
                logger.info(f"Loaded IEEE-CIS {file_name}: {len(df)} records")
            
            return self._preprocess_ieee_cis_transaction_data(df)
        except Exception as e:
            logger.error(f"Error loading IEEE-CIS {file_name}: {e}")
            return self._create_sample_ieee_cis_data()
    
    def load_ieee_cis_identity_data(self, is_train: bool = True, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load IEEE-CIS identity data with column name normalization.
        
        Args:
            is_train: Whether to load training data
            sample_size: If provided, load only a sample of the data
            
        Returns:
            Processed DataFrame with identity data
        """
        file_name = "train_identity.csv" if is_train else "test_identity.csv"
        file_path = self.ieee_cis_path / file_name
        
        if not file_path.exists():
            logger.warning(f"IEEE-CIS {file_name} not found. Returning empty DataFrame.")
            return pd.DataFrame()
        
        try:
            if sample_size:
                df = pd.read_csv(file_path, nrows=sample_size)
                logger.info(f"Loaded IEEE-CIS {file_name} sample: {len(df)} records")
            else:
                df = pd.read_csv(file_path, low_memory=False)
                logger.info(f"Loaded IEEE-CIS {file_name}: {len(df)} records")
            
            return self._preprocess_ieee_cis_identity_data(df)
        except Exception as e:
            logger.error(f"Error loading IEEE-CIS {file_name}: {e}")
            return pd.DataFrame()
    
    def load_ieee_cis_combined_data(self, is_train: bool = True, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load and combine IEEE-CIS transaction and identity data.
        
        Args:
            is_train: Whether to load training data
            sample_size: If provided, load only a sample of the data
            
        Returns:
            Combined DataFrame with transaction and identity data
        """
        # Load transaction data
        transaction_df = self.load_ieee_cis_transaction_data(is_train, sample_size)
        
        # Load identity data
        identity_df = self.load_ieee_cis_identity_data(is_train, sample_size)
        
        if identity_df.empty:
            logger.warning("No identity data available, returning transaction data only")
            return transaction_df
        
        # Merge on TransactionID
        combined_df = transaction_df.merge(
            identity_df, 
            on='TransactionID', 
            how='left',
            suffixes=('_trans', '_id')
        )
        
        logger.info(f"Combined IEEE-CIS data: {len(combined_df)} records")
        return combined_df
    
    def train_v_feature_clusters(self, df: pd.DataFrame, n_clusters: int = 5, 
                                sample_size: int = 50000) -> None:
        """
        Train K-means clustering on V-features to create behavioral archetypes.
        
        Args:
            df: DataFrame with V-features
            n_clusters: Number of behavioral clusters to create
            sample_size: Number of samples to use for training (for memory efficiency)
        """
        logger.info(f"Training V-feature clustering with {n_clusters} clusters...")
        
        # Extract V-features
        v_features = df[self.v_features_columns].copy()
        
        # Sample data if too large
        if len(v_features) > sample_size:
            v_features = v_features.sample(n=sample_size, random_state=42)
            logger.info(f"Sampled {sample_size} records for clustering")
        
        # Handle missing values
        self.v_feature_imputer = SimpleImputer(strategy='median')
        v_features_imputed = self.v_feature_imputer.fit_transform(v_features)
        
        # Scale features
        self.v_feature_scaler = StandardScaler()
        v_features_scaled = self.v_feature_scaler.fit_transform(v_features_imputed)
        
        # Train K-means
        self.v_feature_clusterer = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = self.v_feature_clusterer.fit_predict(v_features_scaled)
        
        # Define behavioral cluster names based on fraud patterns
        self.behavioral_cluster_names = self._define_cluster_names(
            v_features, cluster_labels, n_clusters
        )
        
        logger.info(f"V-feature clustering trained with {n_clusters} behavioral clusters")
        logger.info(f"Cluster names: {self.behavioral_cluster_names}")
    
    def predict_behavioral_clusters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict behavioral clusters for new data using trained models.
        
        Args:
            df: DataFrame with V-features
            
        Returns:
            DataFrame with added 'behavioral_cluster' column
        """
        if self.v_feature_clusterer is None:
            logger.warning("V-feature clusterer not trained. Training on current data...")
            self.train_v_feature_clusters(df)
        
        # Extract V-features
        v_features = df[self.v_features_columns].copy()
        
        # Handle missing values
        v_features_imputed = self.v_feature_imputer.transform(v_features)
        
        # Scale features
        v_features_scaled = self.v_feature_scaler.transform(v_features_imputed)
        
        # Predict clusters
        cluster_labels = self.v_feature_clusterer.predict(v_features_scaled)
        
        # Add behavioral cluster names
        df = df.copy()
        df['behavioral_cluster'] = [self.behavioral_cluster_names.get(label, f"Cluster_{label}") 
                                   for label in cluster_labels]
        
        logger.info(f"Predicted behavioral clusters for {len(df)} records")
        return df
    
    def _define_cluster_names(self, v_features: pd.DataFrame, cluster_labels: np.ndarray, 
                            n_clusters: int) -> Dict[int, str]:
        """
        Define meaningful names for behavioral clusters based on fraud patterns.
        
        Args:
            v_features: V-features used for clustering
            cluster_labels: Cluster assignments
            n_clusters: Number of clusters
            
        Returns:
            Dictionary mapping cluster numbers to names
        """
        cluster_names = {}
        
        # Analyze each cluster to define meaningful names
        for cluster_id in range(n_clusters):
            cluster_mask = cluster_labels == cluster_id
            cluster_size = cluster_mask.sum()
            
            if cluster_size == 0:
                cluster_names[cluster_id] = f"Empty_Cluster_{cluster_id}"
                continue
            
            # Analyze V-feature statistics for this cluster
            cluster_v_features = v_features[cluster_mask]
            
            # Calculate cluster characteristics
            non_null_ratio = cluster_v_features.notna().mean().mean()
            mean_values = cluster_v_features.mean().mean()
            std_values = cluster_v_features.std().mean()
            
            # Define cluster based on characteristics
            if non_null_ratio < 0.3:
                cluster_names[cluster_id] = "Sparse_Data_Cluster"
            elif std_values > 2.0:
                cluster_names[cluster_id] = "High_Variance_Anomalous_Activity"
            elif mean_values > 1.5:
                cluster_names[cluster_id] = "Elevated_Risk_Pattern"
            elif mean_values < -1.0:
                cluster_names[cluster_id] = "Low_Risk_Standard_Pattern"
            else:
                cluster_names[cluster_id] = "Typical_Transaction_Profile"
        
        return cluster_names
    
    def load_sebi_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """
        Load SEBI orders and reports data.
        
        Args:
            file_path: Path to the CSV file. If None, looks for default files.
            
        Returns:
            Processed DataFrame with SEBI data
        """
        if file_path is None:
            possible_files = list(self.sebi_path.glob("*.csv"))
            if not possible_files:
                logger.warning("No SEBI data files found. Creating sample data.")
                return self._create_sample_sebi_data()
            file_path = possible_files[0]
        
        try:
            df = pd.read_csv(file_path)
            logger.info(f"Loaded SEBI data: {len(df)} records")
            return self._preprocess_sebi_data(df)
        except Exception as e:
            logger.error(f"Error loading SEBI data: {e}")
            return self._create_sample_sebi_data()
    
    def _preprocess_ieee_cis_transaction_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess IEEE-CIS transaction data."""
        logger.info(f"Preprocessing IEEE-CIS transaction data: {len(df)} records")
        
        # Handle missing values for key columns
        df = df.fillna({
            'TransactionAmt': 0,
            'ProductCD': 'unknown',
            'card4': 'unknown',
            'card6': 'unknown'
        })
        
        # Handle isFraud column (only exists in training data)
        if 'isFraud' in df.columns:
            df['isFraud'] = df['isFraud'].fillna(0).astype(int)
        
        # Convert categorical variables
        categorical_cols = ['ProductCD', 'card4', 'card6']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        # Convert TransactionDT to datetime (relative to reference date)
        if 'TransactionDT' in df.columns:
            # TransactionDT is timedelta from reference datetime
            reference_date = pd.Timestamp('2017-12-01 00:00:00')
            df['TransactionDateTime'] = reference_date + pd.to_timedelta(df['TransactionDT'], unit='s')
        
        # Create text descriptions for RAG
        df['transaction_description'] = self._create_transaction_descriptions(df)
        
        return df
    
    def _preprocess_ieee_cis_identity_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess IEEE-CIS identity data."""
        logger.info(f"Preprocessing IEEE-CIS identity data: {len(df)} records")
        
        # Normalize column names (handle underscore vs dash inconsistency)
        column_mapping = {}
        for col in df.columns:
            if col.startswith('id-'):
                new_col = col.replace('id-', 'id_')
                column_mapping[col] = new_col
        df = df.rename(columns=column_mapping)
        
        # Handle missing values
        df = df.fillna({
            'DeviceType': 'unknown',
            'DeviceInfo': 'unknown'
        })
        
        # Convert categorical variables
        categorical_cols = ['DeviceType', 'DeviceInfo']
        for col in categorical_cols:
            if col in df.columns:
                df[col] = df[col].astype('category')
        
        return df
    
    def _preprocess_sebi_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess SEBI orders and reports data."""
        # Handle missing values
        df = df.fillna({
            'penalty_amount': 0,
            'violation_type': 'unknown'
        })
        
        # Convert date columns
        date_cols = ['order_date', 'violation_date']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Create text descriptions for RAG
        df['order_description'] = self._create_order_descriptions(df)
        
        return df
    
    def _create_transaction_descriptions(self, df: pd.DataFrame) -> List[str]:
        """Create human-readable descriptions of transactions for RAG."""
        descriptions = []
        for _, row in df.iterrows():
            desc = f"Transaction ID {row.get('TransactionID', 'unknown')}: "
            desc += f"Amount ${row.get('TransactionAmt', 0):.2f}, "
            desc += f"Product {row.get('ProductCD', 'unknown')}, "
            desc += f"Card type {row.get('card4', 'unknown')}"
            
            # Add device information if available
            if 'DeviceType' in row and pd.notna(row['DeviceType']):
                desc += f", Device: {row['DeviceType']}"
            
            # Add behavioral cluster information if available
            if 'behavioral_cluster' in row and pd.notna(row['behavioral_cluster']):
                desc += f", Behavioral Profile: {row['behavioral_cluster']}"
            
            # Add fraud label if available
            if row.get('isFraud', 0) == 1:
                desc += " [FRAUD DETECTED]"
            
            descriptions.append(desc)
        return descriptions
    
    def _create_order_descriptions(self, df: pd.DataFrame) -> List[str]:
        """Create human-readable descriptions of SEBI orders for RAG."""
        descriptions = []
        for _, row in df.iterrows():
            desc = f"SEBI Order {row.get('order_id', 'unknown')}: "
            desc += f"Entity {row.get('entity_name', 'unknown')}, "
            desc += f"Violation: {row.get('violation_type', 'unknown')}, "
            desc += f"Penalty: ₹{row.get('penalty_amount', 0):,.2f}"
            descriptions.append(desc)
        return descriptions
    
    def _create_sample_ieee_cis_data(self) -> pd.DataFrame:
        """Create sample IEEE-CIS data for demonstration."""
        np.random.seed(42)
        n_samples = 1000
        
        data = {
            'TransactionID': range(1, n_samples + 1),
            'TransactionAmt': np.random.exponential(50, n_samples),
            'ProductCD': np.random.choice(['W', 'C', 'R', 'S', 'H'], n_samples),
            'card1': [f"card_{i%100}" for i in range(n_samples)],
            'card2': [f"type_{i%10}" for i in range(n_samples)],
            'card4': np.random.choice(['visa', 'mastercard', 'discover', 'american express'], n_samples),
            'card6': np.random.choice(['debit', 'credit'], n_samples),
            'isFraud': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
        }
        
        df = pd.DataFrame(data)
        df['transaction_description'] = self._create_transaction_descriptions(df)
        logger.info("Created sample IEEE-CIS data")
        return df
    
    def _create_sample_sebi_data(self) -> pd.DataFrame:
        """Create sample SEBI data for demonstration."""
        np.random.seed(42)
        n_samples = 200
        
        violation_types = [
            'Insider Trading', 'Market Manipulation', 'Disclosure Violation',
            'Corporate Governance', 'Accounting Fraud', 'Money Laundering'
        ]
        
        data = {
            'order_id': [f"SEBI/ORDER/{i:06d}" for i in range(1, n_samples + 1)],
            'entity_name': [f"Entity_{i%50}" for i in range(n_samples)],
            'violation_type': np.random.choice(violation_types, n_samples),
            'penalty_amount': np.random.exponential(100000, n_samples),
            'order_date': pd.date_range('2020-01-01', periods=n_samples, freq='D')
        }
        
        df = pd.DataFrame(data)
        df['order_description'] = self._create_order_descriptions(df)
        logger.info("Created sample SEBI data")
        return df
    
    def process_ieee_cis_pipeline(self, is_train: bool = True, sample_size: Optional[int] = None,
                                 train_clusters: bool = True, n_clusters: int = 5) -> pd.DataFrame:
        """
        Complete IEEE-CIS data processing pipeline with V-feature clustering.
        
        Args:
            is_train: Whether to process training data
            sample_size: If provided, process only a sample of the data
            train_clusters: Whether to train V-feature clusters
            n_clusters: Number of behavioral clusters to create
            
        Returns:
            Fully processed DataFrame with behavioral clusters
        """
        logger.info(f"Starting IEEE-CIS pipeline for {'training' if is_train else 'test'} data...")
        
        # Load combined data
        df = self.load_ieee_cis_combined_data(is_train, sample_size)
        
        if df.empty:
            logger.warning("No data loaded, returning empty DataFrame")
            return df
        
        # Train V-feature clusters on training data
        if train_clusters and is_train:
            self.train_v_feature_clusters(df, n_clusters)
        
        # Predict behavioral clusters
        if self.v_feature_clusterer is not None:
            df = self.predict_behavioral_clusters(df)
        else:
            logger.warning("V-feature clusterer not available, skipping behavioral clustering")
        
        # Regenerate transaction descriptions with behavioral clusters
        df['transaction_description'] = self._create_transaction_descriptions(df)
        
        logger.info(f"IEEE-CIS pipeline completed: {len(df)} records processed")
        return df
    
    def save_clustering_models(self, filepath: str) -> None:
        """Save trained clustering models for later use."""
        if self.v_feature_clusterer is None:
            logger.warning("No clustering models to save")
            return
        
        models = {
            'clusterer': self.v_feature_clusterer,
            'scaler': self.v_feature_scaler,
            'imputer': self.v_feature_imputer,
            'cluster_names': self.behavioral_cluster_names
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(models, f)
        
        logger.info(f"Clustering models saved to {filepath}")
    
    def load_clustering_models(self, filepath: str) -> None:
        """Load previously trained clustering models."""
        try:
            with open(filepath, 'rb') as f:
                models = pickle.load(f)
            
            self.v_feature_clusterer = models['clusterer']
            self.v_feature_scaler = models['scaler']
            self.v_feature_imputer = models['imputer']
            self.behavioral_cluster_names = models['cluster_names']
            
            logger.info(f"Clustering models loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading clustering models: {e}")
    
    def initialize_sebi_components(self) -> None:
        """Initialize SEBI file processor and document processor components."""
        self.sebi_file_processor = SEBIFileProcessor(
            sebi_directory=str(self.sebi_path)
        )
        self.sebi_processor = SEBIProcessor()
        logger.info("SEBI components initialized")
    
    def load_sebi_data_from_files(self) -> List[SEBIDocument]:
        """
        Load SEBI data from manually downloaded files.
        
        Returns:
            List of SEBI documents
        """
        if not self.sebi_file_processor:
            self.initialize_sebi_components()
        
        logger.info("Starting SEBI data loading from files...")
        documents = self.sebi_file_processor.process_all_files()
        
        # Store documents
        self.sebi_documents = documents
        logger.info(f"Loaded {len(documents)} SEBI documents from files")
        
        return documents
    
    def process_sebi_documents(self, documents: Optional[List[SEBIDocument]] = None) -> List[ProcessedChunk]:
        """
        Process SEBI documents into chunks for RAG.
        
        Args:
            documents: List of SEBI documents to process. If None, uses stored documents.
            
        Returns:
            List of processed chunks
        """
        if not self.sebi_processor:
            self.initialize_sebi_components()
        
        if documents is None:
            documents = self.sebi_documents
        
        if not documents:
            logger.warning("No SEBI documents to process")
            return []
        
        # Convert SEBIDocument objects to dictionaries for processing
        doc_dicts = []
        for doc in documents:
            doc_dict = {
                'document_id': doc.document_id,
                'title': doc.title,
                'document_type': doc.document_type,
                'url': getattr(doc, 'url', None) or doc.file_path,
                'date': doc.date.isoformat() if doc.date else None,
                'content': doc.content,
                'metadata': doc.metadata
            }
            doc_dicts.append(doc_dict)
        
        logger.info(f"Processing {len(doc_dicts)} SEBI documents...")
        chunks = self.sebi_processor.process_documents(doc_dicts)
        
        # Store processed chunks
        self.sebi_chunks = chunks
        
        # Save processed chunks
        if chunks:
            output_path = self.sebi_path / "processed_sebi_chunks.csv"
            self.sebi_processor.save_processed_chunks(chunks, str(output_path))
            
            # Create and save document summary
            summary = self.sebi_processor.create_document_summary(chunks)
            summary_path = self.sebi_path / "sebi_document_summary.json"
            import json
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Processed {len(chunks)} SEBI document chunks")
        return chunks
    
    def load_processed_sebi_chunks(self) -> List[ProcessedChunk]:
        """Load previously processed SEBI chunks from CSV."""
        chunks_path = self.sebi_path / "processed_sebi_chunks.csv"
        
        if not chunks_path.exists():
            logger.warning("No processed SEBI chunks found")
            return []
        
        try:
            df = pd.read_csv(chunks_path)
            chunks = []
            
            for _, row in df.iterrows():
                chunk = ProcessedChunk(
                    chunk_id=row['chunk_id'],
                    document_id=row['document_id'],
                    document_type=row['document_type'],
                    title=row['title'],
                    content=row['content'],
                    chunk_index=row['chunk_index'],
                    metadata=eval(row['metadata']) if pd.notna(row['metadata']) else {},
                    keywords=row['keywords'].split(', ') if pd.notna(row['keywords']) else [],
                    entities=row['entities'].split(', ') if pd.notna(row['entities']) else [],
                    violation_types=row['violation_types'].split(', ') if pd.notna(row['violation_types']) else []
                )
                chunks.append(chunk)
            
            self.sebi_chunks = chunks
            logger.info(f"Loaded {len(chunks)} processed SEBI chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Error loading processed SEBI chunks: {e}")
            return []
    
    def run_sebi_pipeline(self, load_from_files: bool = True) -> Dict[str, Any]:
        """
        Run complete SEBI data pipeline: file loading, processing, and chunking.
        
        Args:
            load_from_files: Whether to load data from manually downloaded files
            
        Returns:
            Dictionary containing pipeline results
        """
        logger.info("Starting SEBI data pipeline...")
        
        results = {
            'loaded_documents': [],
            'processed_chunks': [],
            'summary': {}
        }
        
        try:
            # Step 1: Load data from files (if requested)
            if load_from_files:
                logger.info("Step 1: Loading SEBI data from files...")
                documents = self.load_sebi_data_from_files()
                results['loaded_documents'] = documents
            else:
                # Try to load existing processed chunks
                logger.info("Step 1: Loading existing processed SEBI chunks...")
                chunks = self.load_processed_sebi_chunks()
                if chunks:
                    results['processed_chunks'] = chunks
                    return results
            
            # Step 2: Process documents into chunks
            logger.info("Step 2: Processing SEBI documents...")
            chunks = self.process_sebi_documents()
            results['processed_chunks'] = chunks
            
            # Step 3: Create summary
            if chunks:
                logger.info("Step 3: Creating document summary...")
                summary = self.sebi_processor.create_document_summary(chunks)
                results['summary'] = summary
            elif documents:
                logger.info("Step 3: Creating file processing summary...")
                summary = self.sebi_file_processor.get_processing_summary(documents)
                results['summary'] = summary
            
            logger.info("SEBI data pipeline completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in SEBI data pipeline: {e}")
            return results
    
    def get_sebi_insights(self, violation_type: Optional[str] = None, 
                         document_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get insights from SEBI data based on filters.
        
        Args:
            violation_type: Filter by violation type (e.g., 'insider_trading')
            document_type: Filter by document type (e.g., 'enforcement_order')
            
        Returns:
            Dictionary containing filtered insights
        """
        if not self.sebi_chunks:
            logger.warning("No SEBI chunks available. Run SEBI pipeline first.")
            return {}
        
        # Apply filters
        filtered_chunks = self.sebi_chunks.copy()
        
        if violation_type:
            filtered_chunks = [chunk for chunk in filtered_chunks 
                             if violation_type in chunk.violation_types]
        
        if document_type:
            filtered_chunks = [chunk for chunk in filtered_chunks 
                             if chunk.document_type == document_type]
        
        if not filtered_chunks:
            return {'message': 'No chunks match the specified filters'}
        
        # Extract insights
        insights = {
            'total_chunks': len(filtered_chunks),
            'document_types': {},
            'violation_types': {},
            'top_entities': {},
            'penalty_mentions': [],
            'key_findings': []
        }
        
        # Aggregate statistics
        for chunk in filtered_chunks:
            # Document type distribution
            doc_type = chunk.document_type
            insights['document_types'][doc_type] = insights['document_types'].get(doc_type, 0) + 1
            
            # Violation type distribution
            for violation in chunk.violation_types:
                insights['violation_types'][violation] = insights['violation_types'].get(violation, 0) + 1
            
            # Entity distribution
            for entity in chunk.entities:
                insights['top_entities'][entity] = insights['top_entities'].get(entity, 0) + 1
            
            # Extract penalty information
            penalty_info = chunk.metadata.get('penalty_info', {})
            if penalty_info:
                insights['penalty_mentions'].extend(penalty_info.get('amounts', []))
        
        # Sort top entities
        insights['top_entities'] = dict(sorted(insights['top_entities'].items(), 
                                             key=lambda x: x[1], reverse=True)[:10])
        
        return insights

    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all available datasets."""
        return {
            'ieee_cis_train': self.process_ieee_cis_pipeline(is_train=True, sample_size=10000),
            'ieee_cis_test': self.process_ieee_cis_pipeline(is_train=False, sample_size=10000),
            'sebi': self.load_sebi_data()
        }
