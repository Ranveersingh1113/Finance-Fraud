# Deploy Fin-E5 Model on New Device - Step by Step

**Status**: ✅ Model files present at `models/fin-e5/`  
**Next**: Test, rebuild ChromaDB, and deploy

---

## 🚀 **Step-by-Step Deployment**

### **Step 1: Test Model Loading**

Verify the model loads correctly:

```powershell
python test_fin_e5_model.py
```

**Expected Output**:
- ✅ Model loads from `./models/fin-e5`
- ✅ Dimensions: 768 (E5-base)
- ✅ Encoding works correctly

**If it fails**: Check that `sentence-transformers` and `torch` are installed.

---

### **Step 2: Verify Configuration**

Check that config points to Fin-E5:

```powershell
# Check config file
Get-Content src/core/config.py | Select-String "embedding_model"
```

**Should show**: `default="./models/fin-e5"`

**If not**: The config is already updated (we fixed it earlier).

---

### **Step 3: Backup Existing ChromaDB** ⚠️ **CRITICAL**

**IMPORTANT**: Old ChromaDB has embeddings from `all-MiniLM-L12-v2` (384 dim).  
Fin-E5 uses 768 dim - **they are incompatible!**

```powershell
# Backup existing ChromaDB
Copy-Item -Recurse data/chroma_db data/chroma_db_backup_baseline

# Verify backup
Test-Path data/chroma_db_backup_baseline
```

---

### **Step 4: Rebuild ChromaDB with Fin-E5** 🔥 **REQUIRED**

**Option A: Delete and Rebuild (Recommended)**

```powershell
# Delete old ChromaDB
Remove-Item -Recurse data/chroma_db

# Rebuild SEBI collection with Fin-E5
python rebuild_sebi_chromadb.py

# Re-index transactions (if you have a script)
# python scripts/rebuild_transactions_chromadb.py
```

**Option B: Create New Collections (Keep Old for Comparison)**

Update rebuild scripts to use new collection names:
- `sebi_documents_fin_e5` (instead of `sebi_documents_advanced`)
- `transactions_fin_e5` (instead of `transactions_advanced`)

---

### **Step 5: Verify ChromaDB Rebuild**

```powershell
# Check ChromaDB was rebuilt
python -c "import chromadb; client = chromadb.PersistentClient(path='./data/chroma_db'); col = client.get_collection('sebi_documents_advanced'); print(f'SEBI chunks: {col.count()}')"
```

**Expected**: Should show document count > 0

---

### **Step 6: Test RAG System**

Test the RAG engine with Fin-E5:

```powershell
# Quick test
python -c "
from src.core.advanced_rag_engine import AdvancedRAGEngine
engine = AdvancedRAGEngine()
result = engine.query('What are SEBI penalties for insider trading?', n_results=3)
print(f'Query: {result.query}')
print(f'Results: {len(result.evidence)}')
print(f'Processing time: {result.processing_time:.2f}s')
"
```

**Expected**:
- Model loads successfully
- Query processes without errors
- Results returned

---

### **Step 7: Production Evaluation (Optional)**

Compare performance with baseline:

```powershell
# If you have comparison script
python scripts/compare_model_performance.py
```

**Metrics to check**:
- Precision@10
- Recall@10
- MRR@10
- Query latency

---

## 📋 **Quick Checklist**

- [ ] Step 1: Test model loading (`python test_fin_e5_model.py`)
- [ ] Step 2: Verify config (already done ✅)
- [ ] Step 3: Backup ChromaDB
- [ ] Step 4: **Rebuild ChromaDB with Fin-E5** (CRITICAL!)
- [ ] Step 5: Verify ChromaDB rebuild
- [ ] Step 6: Test RAG system
- [ ] Step 7: Production evaluation (optional)

---

## ⚠️ **Important Notes**

1. **ChromaDB Rebuild is REQUIRED**: Old embeddings won't work with Fin-E5
2. **Backup First**: Always backup before deleting ChromaDB
3. **Storage**: Fin-E5 uses 768 dimensions (2x larger than baseline)
4. **Performance**: Slightly slower but more accurate

---

## 🚨 **Troubleshooting**

### **Model won't load**
```powershell
# Check if model files exist
Test-Path models/fin-e5/model.safetensors

# Check dependencies
pip list | Select-String "sentence-transformers|torch"
```

### **ChromaDB errors**
- Make sure ChromaDB was rebuilt with Fin-E5
- Check collection names match in code

### **Import errors**
```powershell
# Activate venv
.\financevenv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

---

## ✅ **After Deployment**

Once everything works:
1. Test with real queries
2. Monitor performance metrics
3. Compare with baseline (if you kept backup)

**Ready to start?** Begin with Step 1: Test model loading!

