"""
Test GPU configuration for Financial Intelligence Platform.
Verifies that GPU is properly detected and being used by all components.
"""
import sys
from pathlib import Path
import os

# Set UTF-8 encoding for console output (Windows compatibility)
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import torch
from src.core.device_config import device_manager, get_device_string, is_cuda_available

print("=" * 70)
print("GPU Configuration Test")
print("=" * 70)

# Test 1: PyTorch CUDA availability
print("\n[Test 1] PyTorch CUDA Detection")
print(f"  PyTorch Version: {torch.__version__}")
print(f"  CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  CUDA Version: {torch.version.cuda}")
    print(f"  cuDNN Version: {torch.backends.cudnn.version()}")
    print(f"  GPU Count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"    Total Memory: {props.total_memory / 1024**3:.2f} GB")
        print(f"    Compute Capability: {props.major}.{props.minor}")
else:
    print("  ⚠ No CUDA-capable GPU detected")
    print("\n  To enable GPU support:")
    print("  1. Ensure you have an NVIDIA GPU with CUDA support")
    print("  2. Install NVIDIA GPU drivers: https://www.nvidia.com/download/index.aspx")
    print("  3. Install PyTorch with CUDA:")
    print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")

# Test 2: Device Manager
print("\n[Test 2] Device Manager")
print(f"  Device: {device_manager.device_name}")
print(f"  Device Type: {device_manager.device}")
print(f"  Is CUDA: {device_manager.is_cuda}")
print(f"  Device String: {get_device_string()}")

if is_cuda_available():
    gpu_info = device_manager.get_gpu_memory_info()
    print(f"\n  GPU Memory Info:")
    print(f"    Total: {gpu_info['total_memory_gb']:.2f} GB")
    print(f"    Allocated: {gpu_info['allocated_memory_gb']:.2f} GB")
    print(f"    Cached: {gpu_info['cached_memory_gb']:.2f} GB")
    print(f"    Free: {gpu_info['free_memory_gb']:.2f} GB")

# Test 3: SentenceTransformer with GPU
print("\n[Test 3] SentenceTransformer GPU Usage")
try:
    from sentence_transformers import SentenceTransformer
    
    device = get_device_string()
    print(f"  Loading model on: {device}")
    
    model = SentenceTransformer('all-MiniLM-L12-v2', device=device)
    print(f"  Model device: {model.device}")
    
    # Test encoding
    test_text = "This is a test sentence for GPU acceleration."
    embedding = model.encode(test_text)
    print(f"  Embedding shape: {embedding.shape}")
    print(f"  ✓ SentenceTransformer successfully using {device}")
    
except Exception as e:
    print(f"  ✗ Error loading SentenceTransformer: {e}")

# Test 4: FlagReranker with GPU
print("\n[Test 4] FlagReranker GPU Usage")
try:
    from FlagEmbedding import FlagReranker
    
    if is_cuda_available():
        print(f"  Loading reranker on GPU (device 0)")
        reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=True, device=0)
        print(f"  ✓ FlagReranker successfully using GPU")
    else:
        print(f"  Loading reranker on CPU (device -1)")
        reranker = FlagReranker('BAAI/bge-reranker-base', use_fp16=False, device=-1)
        print(f"  ✓ FlagReranker successfully using CPU")
    
    # Test reranking
    scores = reranker.compute_score([('test query', 'test document')])
    print(f"  Reranker test score: {scores}")
    
except ImportError:
    print(f"  ⚠ FlagEmbedding not installed. Run: pip install FlagEmbedding")
except Exception as e:
    print(f"  ✗ Error loading FlagReranker: {e}")

# Test 5: RAG Engine with GPU
print("\n[Test 5] RAG Engine GPU Integration")
try:
    from src.core.rag_engine import BaselineRAGEngine
    
    print(f"  Initializing BaselineRAGEngine...")
    rag = BaselineRAGEngine()
    print(f"  Embedding model device: {rag.embedding_model.device}")
    print(f"  ✓ BaselineRAGEngine initialized with {get_device_string()}")
    
except Exception as e:
    print(f"  ✗ Error initializing RAG engine: {e}")

# Test 6: Advanced RAG Engine with GPU
print("\n[Test 6] Advanced RAG Engine GPU Integration")
try:
    from src.core.advanced_rag_engine import AdvancedRAGEngine
    
    print(f"  Initializing AdvancedRAGEngine...")
    advanced_rag = AdvancedRAGEngine()
    
    stats = advanced_rag.get_advanced_stats()
    device_info = stats.get('device_info', {})
    
    print(f"  Device: {device_info.get('device', 'Unknown')}")
    print(f"  Using GPU: {device_info.get('using_gpu', False)}")
    
    if device_info.get('gpu_memory'):
        gpu_mem = device_info['gpu_memory']
        if gpu_mem.get('available'):
            print(f"  GPU Memory: {gpu_mem.get('free_memory_gb', 0):.2f} GB free")
    
    print(f"  ✓ AdvancedRAGEngine initialized")
    
except Exception as e:
    print(f"  ✗ Error initializing Advanced RAG engine: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 70)
print("Summary")
print("=" * 70)

if is_cuda_available():
    print("✓ GPU acceleration is ENABLED")
    print(f"  Device: {device_manager.device_name}")
    gpu_info = device_manager.get_gpu_memory_info()
    print(f"  Available Memory: {gpu_info['free_memory_gb']:.2f} GB")
    print("\n  Your models will run significantly faster!")
else:
    print("⚠ GPU acceleration is DISABLED (using CPU)")
    print("\n  To enable GPU acceleration:")
    print("  1. Install NVIDIA drivers")
    print("  2. Install PyTorch with CUDA:")
    print("     pip uninstall torch")
    print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("  3. (Optional) Install faiss-gpu for faster vector search:")
    print("     pip uninstall faiss-cpu")
    print("     pip install faiss-gpu")

print("\n" + "=" * 70)

