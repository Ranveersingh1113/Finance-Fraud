#!/usr/bin/env python3
"""
Test script to verify BAAI/bge-reranker-large model loading
"""

import os
import sys
from datetime import datetime

def test_model_loading():
    """Test loading the BAAI/bge-reranker-large model"""
    print("=" * 60)
    print("BAAI/bge-reranker-large Model Loading Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print()
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  HF_HOME: {os.getenv('HF_HOME', 'Not set')}")
    print(f"  TRANSFORMERS_CACHE: {os.getenv('TRANSFORMERS_CACHE', 'Not set')}")
    print(f"  HUGGINGFACE_HUB_CACHE: {os.getenv('HUGGINGFACE_HUB_CACHE', 'Not set')}")
    print()
    
    try:
        print("1. Importing required libraries...")
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
        print("   ✅ Successfully imported transformers and torch")
        
        print("2. Loading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained('BAAI/bge-reranker-large')
        print(f"   ✅ Tokenizer loaded - Vocab size: {tokenizer.vocab_size}")
        
        print("3. Loading model...")
        model = AutoModelForSequenceClassification.from_pretrained('BAAI/bge-reranker-large')
        print(f"   ✅ Model loaded - Config: {model.config.name_or_path}")
        print(f"   ✅ Model parameters: {sum(p.numel() for p in model.parameters()):,}")
        
        print("4. Testing basic functionality...")
        # Test with sample input
        query = "What is machine learning?"
        passage = "Machine learning is a branch of artificial intelligence that focuses on algorithms."
        
        inputs = tokenizer(query, passage, return_tensors="pt", truncation=True, max_length=512)
        print(f"   ✅ Tokenization successful - Input shape: {inputs['input_ids'].shape}")
        
        # Test model inference
        with torch.no_grad():
            outputs = model(**inputs)
            scores = outputs.logits
        print(f"   ✅ Model inference successful - Output shape: {scores.shape}")
        print(f"   ✅ Relevance score: {scores.item():.4f}")
        
        print("5. Cache location check...")
        cache_dir = os.getenv('HF_HOME') or os.getenv('TRANSFORMERS_CACHE')
        if cache_dir:
            model_cache = os.path.join(cache_dir, "models--BAAI--bge-reranker-large")
            if os.path.exists(model_cache):
                print(f"   ✅ Model found in cache: {model_cache}")
            else:
                print(f"   ⚠️  Model cache not found at: {model_cache}")
        
        print()
        print("🎉 ALL TESTS PASSED! The model is working correctly.")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   Please ensure transformers and torch are installed.")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_model_loading()
    sys.exit(0 if success else 1)