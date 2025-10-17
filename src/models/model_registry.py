"""
Model registry for managing different AI models used in the platform.
Phase 1: Baseline models, Phase 2: Production models with fine-tuning.
"""
from enum import Enum
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """Enumeration of model types."""
    EMBEDDING = "embedding"
    GENERATIVE = "generative"
    RERANKER = "reranker"
    FINE_TUNED = "fine_tuned"


class ModelPhase(Enum):
    """Enumeration of implementation phases."""
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"


class ModelRegistry:
    """Registry for managing AI models across different phases."""
    
    def __init__(self):
        self.models = {
            # Phase 1 Models
            "all-MiniLM-L12-v2": {
                "name": "all-MiniLM-L12-v2",
                "type": ModelType.EMBEDDING,
                "phase": ModelPhase.PHASE_1,
                "description": "Baseline embedding model for semantic search",
                "fine_tuned": False,
                "model_path": "sentence-transformers/all-MiniLM-L12-v2",
                "max_tokens": 512,
                "dimension": 384
            },
            
            # Phase 2 Models (to be implemented)
            "llama3": {
                "name": "llama3",
                "type": ModelType.GENERATIVE,
                "phase": ModelPhase.PHASE_2,
                "description": "Generative LLM for text generation",
                "fine_tuned": False,
                "model_path": "llama3",
                "max_tokens": 4096,
                "context_length": 8192
            },
            
            "bge-reranker-large": {
                "name": "bge-reranker-large",
                "type": ModelType.RERANKER,
                "phase": ModelPhase.PHASE_2,
                "description": "Cross-encoder for re-ranking search results",
                "fine_tuned": False,
                "model_path": "BAAI/bge-reranker-large",
                "max_tokens": 512
            },
            
            "fin-e5": {
                "name": "fin-e5",
                "type": ModelType.FINE_TUNED,
                "phase": ModelPhase.PHASE_2,
                "description": "Fine-tuned embedding model for financial domain",
                "fine_tuned": True,
                "model_path": "sentence-transformers/all-MiniLM-L12-v2",  # Base model
                "fine_tuned_path": "./models/fin-e5-finetuned",
                "max_tokens": 512,
                "dimension": 384
            }
        }
    
    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get model configuration by name."""
        return self.models.get(model_name)
    
    def get_models_by_phase(self, phase: ModelPhase) -> Dict[str, Dict[str, Any]]:
        """Get all models for a specific phase."""
        return {
            name: config for name, config in self.models.items()
            if config["phase"] == phase
        }
    
    def get_models_by_type(self, model_type: ModelType) -> Dict[str, Dict[str, Any]]:
        """Get all models of a specific type."""
        return {
            name: config for name, config in self.models.items()
            if config["type"] == model_type
        }
    
    def list_available_models(self) -> Dict[str, Dict[str, Any]]:
        """List all available models."""
        return self.models.copy()
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available."""
        return model_name in self.models
    
    def get_phase_1_models(self) -> Dict[str, Dict[str, Any]]:
        """Get Phase 1 models (baseline)."""
        return self.get_models_by_phase(ModelPhase.PHASE_1)
    
    def get_phase_2_models(self) -> Dict[str, Dict[str, Any]]:
        """Get Phase 2 models (production)."""
        return self.get_models_by_phase(ModelPhase.PHASE_2)


# Global model registry instance
model_registry = ModelRegistry()
