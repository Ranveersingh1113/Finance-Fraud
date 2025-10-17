"""
Configuration management for the Financial Intelligence Platform.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=True, env="DEBUG")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_key: str = Field(default="dev-api-key", env="API_KEY")
    
    # Database Configuration
    chroma_persist_directory: str = Field(
        default="./data/chroma_db", 
        env="CHROMA_PERSIST_DIRECTORY"
    )
    neo4j_uri: str = Field(default="bolt://localhost:7687", env="NEO4J_URI")
    neo4j_username: str = Field(default="neo4j", env="NEO4J_USERNAME")
    neo4j_password: str = Field(default="password", env="NEO4J_PASSWORD")
    
    # Model Configuration
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L12-v2",
        env="EMBEDDING_MODEL"
    )
    llm_model: str = Field(default="llama3", env="LLM_MODEL")
    reranker_model: str = Field(
        default="ms-marco-MiniLM-L-12-v2",
        env="RERANKER_MODEL"
    )
    
    # Device Configuration (GPU/CPU)
    device: str = Field(
        default="auto",  # 'auto', 'cuda', 'cpu', 'cuda:0', etc.
        env="DEVICE"
    )
    use_fp16: bool = Field(
        default=True,  # Use half precision for GPU to save memory
        env="USE_FP16"
    )
    
    # HuggingFace Cache Configuration
    hf_home: str = Field(
        default=r"D:\huggingface_cache",
        env="HF_HOME"
    )
    transformers_cache: str = Field(
        default=r"D:\huggingface_cache",
        env="TRANSFORMERS_CACHE"
    )
    
    # Data Paths
    data_directory: str = Field(default="./data", env="DATA_DIRECTORY")
    ieee_cis_data_path: str = Field(
        default="./data/ieee_cis", 
        env="IEEE_CIS_DATA_PATH"
    )
    sebi_data_path: str = Field(
        default="./data/sebi", 
        env="SEBI_DATA_PATH"
    )
    
    # V-Feature Clustering Configuration
    v_feature_clusters: int = Field(default=5, env="V_FEATURE_CLUSTERS")
    clustering_sample_size: int = Field(default=50000, env="CLUSTERING_SAMPLE_SIZE")
    clustering_model_path: str = Field(
        default="./data/clustering_models.pkl",
        env="CLUSTERING_MODEL_PATH"
    )
    
    # SEBI Data Configuration
    sebi_directory: str = Field(
        default="./data/sebi",
        env="SEBI_DIRECTORY"
    )
    sebi_min_chunk_size: int = Field(default=200, env="SEBI_MIN_CHUNK_SIZE")
    sebi_max_chunk_size: int = Field(default=1000, env="SEBI_MAX_CHUNK_SIZE")
    sebi_processed_chunks_path: str = Field(
        default="./data/sebi/processed_sebi_chunks.csv",
        env="SEBI_PROCESSED_CHUNKS_PATH"
    )
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=30, 
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set HuggingFace environment variables
        os.environ['HF_HOME'] = self.hf_home
        os.environ['TRANSFORMERS_CACHE'] = self.transformers_cache
        os.environ['HF_DATASETS_CACHE'] = self.transformers_cache
        
        # Ensure data directories exist
        Path(self.data_directory).mkdir(parents=True, exist_ok=True)
        Path(self.chroma_persist_directory).mkdir(parents=True, exist_ok=True)
        Path(self.ieee_cis_data_path).mkdir(parents=True, exist_ok=True)
        Path(self.sebi_data_path).mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
