"""
Device Configuration for GPU acceleration.
Detects and manages GPU/CPU device usage across the platform.
"""
import torch
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manage device configuration for GPU/CPU acceleration."""
    
    _instance = None
    _device = None
    _device_name = None
    
    def __new__(cls):
        """Singleton pattern to ensure consistent device across application."""
        if cls._instance is None:
            cls._instance = super(DeviceManager, cls).__new__(cls)
            cls._instance._initialize_device()
        return cls._instance
    
    def _initialize_device(self):
        """Initialize and detect the best available device."""
        if torch.cuda.is_available():
            self._device = torch.device("cuda")
            self._device_name = torch.cuda.get_device_name(0)
            logger.info(f"✓ GPU detected: {self._device_name}")
            logger.info(f"  CUDA Version: {torch.version.cuda}")
            logger.info(f"  Total GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            self._device = torch.device("cpu")
            self._device_name = "CPU"
            logger.warning("⚠ No GPU detected. Using CPU. Performance will be slower.")
            logger.info("  To enable GPU:")
            logger.info("  1. Install PyTorch with CUDA: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            logger.info("  2. Ensure NVIDIA GPU drivers are installed")
    
    @property
    def device(self) -> torch.device:
        """Get the current device."""
        return self._device
    
    @property
    def device_name(self) -> str:
        """Get the device name."""
        return self._device_name
    
    @property
    def is_cuda(self) -> bool:
        """Check if CUDA is available and being used."""
        return self._device.type == "cuda"
    
    @property
    def device_string(self) -> str:
        """Get device as string for compatibility with sentence-transformers."""
        return "cuda" if self.is_cuda else "cpu"
    
    def get_gpu_memory_info(self) -> dict:
        """Get GPU memory information."""
        if not self.is_cuda:
            return {"available": False}
        
        return {
            "available": True,
            "device_name": self._device_name,
            "total_memory_gb": torch.cuda.get_device_properties(0).total_memory / 1024**3,
            "allocated_memory_gb": torch.cuda.memory_allocated(0) / 1024**3,
            "cached_memory_gb": torch.cuda.memory_reserved(0) / 1024**3,
            "free_memory_gb": (torch.cuda.get_device_properties(0).total_memory - 
                              torch.cuda.memory_allocated(0)) / 1024**3
        }
    
    def clear_gpu_cache(self):
        """Clear GPU cache to free memory."""
        if self.is_cuda:
            torch.cuda.empty_cache()
            logger.info("GPU cache cleared")
    
    def set_device(self, device: str):
        """
        Manually set device (for testing or special cases).
        
        Args:
            device: Device string ('cuda', 'cpu', 'cuda:0', etc.)
        """
        if device.startswith('cuda') and not torch.cuda.is_available():
            logger.warning(f"CUDA requested but not available. Falling back to CPU.")
            self._device = torch.device("cpu")
            self._device_name = "CPU"
        else:
            self._device = torch.device(device)
            if device.startswith('cuda'):
                self._device_name = torch.cuda.get_device_name(int(device.split(':')[1]) if ':' in device else 0)
            else:
                self._device_name = "CPU"
            logger.info(f"Device manually set to: {self._device_name}")
    
    def log_device_info(self):
        """Log detailed device information."""
        logger.info("=" * 60)
        logger.info("Device Configuration")
        logger.info("=" * 60)
        logger.info(f"Device: {self._device_name}")
        logger.info(f"Type: {'GPU (CUDA)' if self.is_cuda else 'CPU'}")
        
        if self.is_cuda:
            mem_info = self.get_gpu_memory_info()
            logger.info(f"Total Memory: {mem_info['total_memory_gb']:.2f} GB")
            logger.info(f"Free Memory: {mem_info['free_memory_gb']:.2f} GB")
            logger.info(f"CUDA Version: {torch.version.cuda}")
            logger.info(f"cuDNN Version: {torch.backends.cudnn.version()}")
        
        logger.info("=" * 60)


# Global device manager instance
device_manager = DeviceManager()


def get_device() -> torch.device:
    """Get the current device."""
    return device_manager.device


def get_device_string() -> str:
    """Get device as string for sentence-transformers compatibility."""
    return device_manager.device_string


def is_cuda_available() -> bool:
    """Check if CUDA is available."""
    return device_manager.is_cuda


def get_gpu_memory_info() -> dict:
    """Get GPU memory information."""
    return device_manager.get_gpu_memory_info()


def clear_gpu_cache():
    """Clear GPU cache."""
    device_manager.clear_gpu_cache()

