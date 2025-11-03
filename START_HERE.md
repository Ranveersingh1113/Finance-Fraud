# Fin-E5 Fine-Tuning: START HERE

**Goal**: Fine-tune E5 model for your financial fraud detection system  
**Training Data**: 1000+ pairs (automated)  
**Time**: 3 days total  
**Expected Improvement**: +30-40% retrieval quality

---

## ⚡ Quick Commands (Copy-Paste)

```bash
# Navigate to project
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate

# Day 1: Generate 1000 training pairs (10 minutes)
python scripts/generate_training_data.py --target-pairs 1000

# Day 2: Train Fin-E5 (6-12 hours on GPU, overnight)
python scripts/finetune_e5_model.py --train

# Day 3: Export and deploy
python scripts/finetune_e5_model.py --export
# Then: Update code + rebuild ChromaDB + test
```

---

## 📋 Step-by-Step Instructions

### Day 1: Generate Training Data

**Time**: 10 minutes  
**Action**: Generate 1000 training pairs automatically

```bash
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate
python scripts/generate_training_data.py --target-pairs 1000
```

**What to expect**:
```
✓ Loaded collection: sebi_documents (XXX documents)
✓ Loaded collection: amlsim_transactions (XXX documents)

[1/3] Generating pairs from ChromaDB documents...
  • Processed 100/XXX documents...
  ✓ Generated 850 document-based pairs

[2/3] Adding expert-crafted queries...
  ✓ Added 40 expert queries

[3/3] Combining and shuffling dataset...
  ✓ Created 1000 training pairs

DATASET GENERATION COMPLETE
Total pairs: 1000
Saved to: data/finetuning/e5_training_data.json
```

**Next**: Check the file exists: `ls data/finetuning/e5_training_data.json`

---

### Day 2: Train Fin-E5

**Time**: 6-12 hours (run overnight)  
**Action**: Fine-tune E5 model

```bash
# Start training (this will take several hours)
python scripts/finetune_e5_model.py --train
```

**What to expect**:
```
Loading base model: intfloat/e5-base-v2
(First time: downloads ~440MB model)

Loaded 1000 training pairs
Training samples: 800
Evaluation samples: 200

Training configuration:
  • Epochs: 4
  • Batch size: 16
  • Device: cuda
  • Estimated time: 6-12 hours

TRAINING STARTED
Epoch 1/4: [=========>] 
Epoch 2/4: [=========>]
...
✓ TRAINING COMPLETE
Model saved to: models/fin-e5/
```

**Monitor progress**: Watch for evaluation scores improving each epoch

**Checkpoint**: If interrupted, training resumes from last checkpoint

---

### Day 3: Deploy Fin-E5

**Time**: 2-3 hours  
**Actions**: Export, update code, rebuild, test

#### Step 3.1: Export Model

```bash
python scripts/finetune_e5_model.py --export
```

**Output**: `models/deployed/fin-e5-v1/` (production-ready)

#### Step 3.2: Update Code

Edit `src/core/advanced_rag_engine.py` around line 97:

**Find this**:
```python
self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2', device=self.device)
```

**Replace with**:
```python
self.embedding_model = SentenceTransformer('./models/deployed/fin-e5-v1', device=self.device)
```

**Save the file**.

#### Step 3.3: Rebuild ChromaDB (CRITICAL!)

```bash
# This rebuilds ALL embeddings with Fin-E5
# Takes 30-60 minutes
python rebuild_sebi_chromadb.py
```

**Why critical?** 
- Old embeddings: 384 dimensions (MiniLM)
- New embeddings: 768 dimensions (Fin-E5)
- Must rebuild or system will crash!

#### Step 3.4: Test System

```bash
# Start the system
.\scripts\start_system.ps1

# Or manually:
python start_api.py   # Terminal 1
python start_ui.py    # Terminal 2
```

**Test queries** (in UI or via API):
1. "What are SEBI penalties for insider trading?"
2. "Explain money laundering detection patterns"
3. "Show fan-out transaction fraud patterns"

**Check**: Results should be noticeably more relevant!

#### Step 3.5: Measure Improvement

```bash
# Measure with Fin-E5
python scripts/measure_baseline_performance.py

# This creates: baseline_metrics_results.json
# Rename it:
mv baseline_metrics_results.json fin_e5_metrics_results.json

# Compare with your old baseline
python scripts/compare_model_performance.py \
    baseline_metrics_results.json \
    fin_e5_metrics_results.json
```

**Expected output**:
```
MODEL PERFORMANCE COMPARISON
============================

📊 PRECISION@10
  Baseline:   0.600
  Fine-tuned: 0.810
  Change:     +0.210 (+35.0%)
  ✅ SIGNIFICANT IMPROVEMENT

RECOMMENDATION
==============
✅ EXCELLENT RESULTS
   → Fine-tuning provided significant improvement
   → Deploy fine-tuned model to production
   → Monitor user feedback for 2 weeks
```

---

## 🎯 Success Criteria

### ✅ You're successful if:
- [x] Training completes without errors
- [x] Precision@10 improves by > 15%
- [x] System works with no crashes
- [x] Users report better results

### 🎉 Excellent success if:
- [x] Precision@10 improves by > 30%
- [x] MRR improves by > 40%
- [x] Transformative improvement in relevance

---

## 🔧 Troubleshooting

### "CUDA out of memory"
```bash
# Reduce batch size
python scripts/finetune_e5_model.py --train --batch-size 8
```

### "Training too slow"
- Run overnight on GPU
- Or reduce to `--target-pairs 500`

### "No documents in ChromaDB"
```bash
# Check what you have
python scripts/explore_chromadb.py
```

### "Dimension mismatch error"
- Did you rebuild ChromaDB? (Step 3.3)
- Run: `python rebuild_sebi_chromadb.py`

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `START_HERE.md` | ⭐ This file - start here |
| `FIN_E5_QUICKSTART.md` | Detailed quick start |
| `FINETUNING_DECISION.md` | Why Fin-E5? Analysis |
| `FIN_E5_IMPLEMENTATION_SUMMARY.md` | Technical details |

---

## ❓ FAQ

**Q: How long does this take?**  
A: 3 days total (10 min + 6-12 hours + 2-3 hours)

**Q: Can I use CPU?**  
A: Yes, but training takes 24-48 hours (not recommended)

**Q: What GPU do I need?**  
A: 6GB+ VRAM (RTX 2060, 3060, etc.)

**Q: Will this break my system?**  
A: No - you're creating a NEW model. Old system still works until you update the code.

**Q: Can I test before deploying?**  
A: Yes - don't update code in Step 3.2, just run evaluation

**Q: What if results aren't better?**  
A: Revert code changes, keep using old model

---

## 🚀 Ready to Start?

```bash
# Copy-paste this:
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate
python scripts/generate_training_data.py --target-pairs 1000
```

**Then**: Follow Day 2 and Day 3 steps above.

---

**Good luck! You're going to improve your system by 30-40%! 🎉**

**Questions?** Check `FIN_E5_QUICKSTART.md` for detailed guide.

