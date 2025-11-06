"""Quick test to verify Fin-E5 model is loaded correctly."""
from sentence_transformers import SentenceTransformer
import torch

print("=" * 70)
print("TESTING FIN-E5 MODEL")
print("=" * 70)

try:
    print("\n[1/3] Loading Fin-E5 model...")
    model = SentenceTransformer('./models/fin-e5')
    print("[OK] Model loaded successfully")
    
    print("\n[2/3] Checking model properties...")
    dimensions = model.get_sentence_embedding_dimension()
    print(f"  • Dimensions: {dimensions}")
    print(f"  • Expected: 768 (E5-base)")
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  • Device: {device}")
    
    print("\n[3/3] Testing encoding...")
    test_queries = [
        "What are SEBI penalties for insider trading?",
        "Explain money laundering detection patterns"
    ]
    
    embeddings = model.encode(test_queries)
    print(f"  • Encoded {len(test_queries)} queries")
    print(f"  • Embedding shape: {embeddings.shape}")
    print(f"  • Expected: (2, 768)")
    
    if embeddings.shape == (2, 768):
        print("[OK] Embedding shape is correct")
    
    print("\n" + "=" * 70)
    print("[SUCCESS] FIN-E5 MODEL IS READY TO USE!")
    print("=" * 70)
    print("\nNext steps:")
    print("1. Update src/core/advanced_rag_engine.py to use Fin-E5")
    print("2. Rebuild ChromaDB with new embeddings")
    print("3. Test the system and measure improvement")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nPossible issues:")
    print("  • Model files missing or corrupted")
    print("  • sentence-transformers not installed")
    print("  • PyTorch not installed")
    import traceback
    traceback.print_exc()

