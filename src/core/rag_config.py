"""
Configuration constants for the Unified GraphRAG Engine.
Centralizes all magic numbers and configuration parameters.
"""
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class RAGConfig:
    """Configuration constants for RAG engine."""
    
    # Display limits
    MAX_SEBI_RESULTS_DISPLAY: int = 3
    MAX_AMLSIM_RESULTS_DISPLAY: int = 3
    MAX_EVIDENCE_RESULTS: int = 5
    MAX_TRANSACTION_RESULTS: int = 3
    
    # Graph traversal
    MAX_GRAPH_HOPS: int = 2
    FAN_OUT_THRESHOLD: int = 5
    FAN_IN_THRESHOLD: int = 5
    MAX_SIMILAR_CASES: int = 5
    
    # Retrieval
    RETRIEVAL_OVERSAMPLING_FACTOR: int = 2
    DEFAULT_N_RESULTS: int = 10
    MAX_QUERY_VARIATIONS: int = 2
    
    # Caching
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    MAX_CACHE_SIZE: int = 100
    SEMANTIC_SIMILARITY_THRESHOLD: float = 0.85
    STATS_CACHE_TTL: int = 3600  # 1 hour
    
    # Pattern matching
    HIGH_VALUE_THRESHOLD: int = 100000
    VERY_HIGH_VALUE_THRESHOLD: int = 500000
    CRITICAL_VALUE_THRESHOLD: int = 200000
    FAN_OUT_RISK_THRESHOLD: int = 15
    FAN_IN_RISK_THRESHOLD: int = 15
    LAYERING_MIN_THRESHOLD: int = 5
    
    # Risk scoring
    RISK_SCORE_FAN_OUT_HIGH: int = 40
    RISK_SCORE_FAN_IN_HIGH: int = 40
    RISK_SCORE_LAYERING: int = 35
    RISK_SCORE_HIGH_OUTFLOW: int = 30
    RISK_SCORE_MEDIUM_OUTFLOW: int = 15
    RISK_SCORE_LARGE_NET_FLOW: int = 20
    RISK_SCORE_FRAUD_FLAG: int = 50
    RISK_SCORE_SUSPICIOUS_FLAG: int = 30
    
    RISK_LEVEL_CRITICAL: int = 80
    RISK_LEVEL_HIGH: int = 50
    RISK_LEVEL_MEDIUM: int = 25
    
    # LLM parameters
    LLM_MAX_TOKENS: int = 1200
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_CONTEXT_LENGTH: int = 2000
    OLLAMA_NUM_PREDICT: int = 800
    
    # Circuit breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60
    
    # Retry logic
    MAX_RETRY_ATTEMPTS: int = 3
    RETRY_MIN_WAIT: int = 1
    RETRY_MAX_WAIT: int = 10
    
    # Parallel execution
    MAX_WORKERS: int = 3
    CACHE_REFRESH_INTERVAL: int = 3600  # 1 hour
    
    # Document boosting
    REGULATION_BOOST_REGULATORY: float = 0.5
    REGULATION_PENALTY_REGULATORY: float = -0.1
    TRANSACTION_BOOST: float = 0.3
    REGULATION_BOOST_COMBINED: float = 0.2
    
    # Diversity
    MAX_REGULATIONS_IN_RESULTS: int = 7
    
    # Cross-domain pattern confidence
    FAN_OUT_TO_FRAUD_CONFIDENCE: float = 0.85
    FAN_IN_TO_ML_CONFIDENCE: float = 0.82
    GENERAL_SUSPICIOUS_CONFIDENCE: float = 0.70
    
    # Top patterns display
    MAX_PATTERNS_DISPLAY: int = 10
    MAX_CROSS_DOMAIN_PATTERNS: int = 3
    
    # Transaction trace
    MIN_FAN_OUT_PATTERN: int = 10
    MIN_FAN_IN_PATTERN: int = 10
    TOP_TRANSACTIONS_DISPLAY: int = 5
    TRACE_MAX_HOPS: int = 3
    
    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('_') and not callable(value)
        }
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return getattr(cls, key, default)

