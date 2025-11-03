# Fin-E5: Fine-Tuning Quick Start Guide

**Model**: E5-base-v2 → Fin-E5 (Domain-adapted for Financial Fraud Detection)  
**Training Data**: 500-1000 pairs (automated generation)  
**Expected Improvement**: +30-40% in retrieval precision

---

## Quick Start (3 Commands)

```bash
# Step 1: Generate 1000 training pairs (5-10 minutes)
python scripts/generate_training_data.py --target-pairs 1000

# Step 2: Train Fin-E5 (6-12 hours on GPU)
python scripts/finetune_e5_model.py --train

# Step 3: Export for deployment
python scripts/finetune_e5_model.py --export
```

Then rebuild ChromaDB and evaluate (see below).

---

## Complete Workflow

### Phase 1: Generate Training Data

```bash
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate

# Generate 1000 training pairs automatically
python scripts/generate_training_data.py \
    --target-pairs 1000 \
    --output data/finetuning/e5_training_data.json
```

**What this does**:
- Extracts all documents from ChromaDB collections
- Generates synthetic queries from document metadata
- Creates positive/negative pairs for contrastive learning
- Adds 40+ expert-crafted queries for key concepts
- Output: `data/finetuning/e5_training_data.json` (~5-10 MB)

**Time**: 5-10 minutes

### Phase 2: Fine-Tune E5 Model

```bash
# Train with default settings (recommended)
python scripts/finetune_e5_model.py --train

# Or customize:
python scripts/finetune_e5_model.py --train \
    --epochs 5 \
    --batch-size 16 \
    --max-seq-length 512
```

**What this does**:
- Downloads E5-base-v2 (first time only)
- Loads 1000 training pairs
- Trains with MultipleNegativesRankingLoss
- Evaluates every 500 steps
- Saves best model to `models/fin-e5/`
- Creates checkpoints for recovery

**Hardware**:
- GPU (6GB+ VRAM): 6-12 hours
- CPU: 24-48 hours (not recommended)

**Time**: 6-12 hours on GPU

### Phase 3: Export for Production

```bash
python scripts/finetune_e5_model.py --export
```

**Output**: `models/deployed/fin-e5-v1/` (production-ready)

### Phase 4: Deploy Fin-E5

**Step 1: Update Code**

Edit `src/core/advanced_rag_engine.py` line ~97:

```python
# OLD:
self.embedding_model = SentenceTransformer('all-MiniLM-L12-v2', device=self.device)

# NEW:
self.embedding_model = SentenceTransformer('./models/deployed/fin-e5-v1', device=self.device)
```

**Step 2: Rebuild ChromaDB (CRITICAL!)**

```bash
# This rebuilds all embeddings with Fin-E5
python rebuild_sebi_chromadb.py
```

**Why critical?** 
- Fin-E5 has 768 dimensions (vs 384 in old model)
- ChromaDB stores embeddings, must rebuild with new model
- Takes 30-60 minutes depending on document count

**Step 3: Test System**

```bash
.\scripts\start_system.ps1

# Or manually:
python start_api.py   # Terminal 1
python start_ui.py    # Terminal 2
```

Test queries:
- "What are SEBI penalties for insider trading?"
- "Explain money laundering detection patterns"
- "Show fan-out transaction fraud patterns"

**Step 4: Measure Improvement**

```bash
# Run evaluation (saves to fin_e5_metrics_results.json)
python scripts/measure_baseline_performance.py

# Compare with baseline
python scripts/compare_model_performance.py \
    baseline_metrics_results.json \
    fin_e5_metrics_results.json
```

---

## Expected Results

### Before (MiniLM-L12-v2)
```
Precision@10: ~0.60
MRR: ~0.50
Dimensions: 384
User Experience: "Results are OK"
```

### After (Fin-E5)
```
Precision@10: ~0.75-0.85 (+25-40%)
MRR: ~0.70-0.80 (+40-60%)
Dimensions: 768
User Experience: "Results are much more relevant"
```

---

## Training Data Details

### Automated Generation Strategy

1. **Document-based pairs** (70-80% of data):
   - From titles: "What is SEBI PIT Regulations 2015?"
   - From keywords: "insider trading penalties"
   - From violations: "SEBI penalties for market manipulation"
   - From content: Extract key phrases

2. **Expert queries** (20-30% of data):
   - "What are SEBI penalties for insider trading violations?"
   - "Explain the three stages of money laundering"
   - "What is fan-out transaction pattern?"
   - 40+ expert-crafted queries

3. **Negative sampling**:
   - Random documents from same collection
   - Hard negatives (similar but not relevant)
   - 3-5 negatives per query

### Example Training Pair

```json
{
  "query": "What are SEBI PIT regulations?",
  "positive": {
    "text": "SEBI (Prohibition of Insider Trading) Regulations 2015...",
    "metadata": {"document_type": "regulation"}
  },
  "negatives": [
    {"text": "SEBI LODR disclosure requirements...", "metadata": {...}},
    {"text": "PMLA money laundering act...", "metadata": {...}},
    ...
  ]
}
```

---

## Files Created

```
Finance Fraud/
├── FINETUNING_DECISION.md           ✅ Decision analysis
├── FIN_E5_QUICKSTART.md             ✅ This guide
│
├── scripts/
│   ├── generate_training_data.py    ✅ Auto-generate 1000+ pairs
│   ├── finetune_e5_model.py         ✅ Train Fin-E5
│   ├── measure_baseline_performance.py  ✅ Evaluation (already exists)
│   └── compare_model_performance.py     ✅ Comparison (already exists)
│
├── data/finetuning/
│   └── e5_training_data.json        (Generated by script)
│
└── models/
    ├── fin-e5/                      (Training output)
    └── deployed/
        └── fin-e5-v1/               (Production model)
```

---

## Troubleshooting

### "CUDA out of memory"
```bash
# Reduce batch size
python scripts/finetune_e5_model.py --train --batch-size 8
```

### "Training too slow"
- Use GPU with 6GB+ VRAM
- Or train overnight on CPU

### "Model not improving"
- Check training data quality: `cat data/finetuning/e5_training_data.json`
- Increase training pairs: `--target-pairs 1500`
- Increase epochs: `--epochs 6`

### "ChromaDB dimension mismatch"
- You MUST rebuild ChromaDB after switching to Fin-E5
- Run: `python rebuild_sebi_chromadb.py`

---

## Next Steps After Deployment

1. **Monitor for 1-2 weeks**
   - User feedback
   - Query logs
   - Error rates

2. **Iterate if needed**
   - Add more training data
   - Retrain with expanded dataset
   - Fine-tune reranker next

3. **Continuous improvement**
   - Collect real user queries
   - Add to training data
   - Periodic retraining (every 3-6 months)

---

## Technical Details

### Model Architecture
- **Base**: E5-base-v2 (110M parameters)
- **Dimensions**: 768 (vs 384 in MiniLM)
- **Max length**: 512 tokens
- **Training**: Contrastive learning with MultipleNegativesRankingLoss

### Training Configuration
```python
{
    'base_model': 'intfloat/e5-base-v2',
    'epochs': 4,
    'batch_size': 16,
    'warmup_steps': 500,
    'max_seq_length': 512,
    'loss': 'MultipleNegativesRankingLoss',
    'evaluation_steps': 500
}
```

### Hardware Requirements
- **GPU**: 6GB+ VRAM (NVIDIA RTX 2060 or better)
- **RAM**: 16GB recommended
- **Disk**: 10GB free space
- **Time**: 6-12 hours training

---

## Success Criteria

### Minimum Success
- ✅ Precision@10: +15% improvement
- ✅ Training completes without errors
- ✅ No system slowdown

### Good Success
- ✅ Precision@10: +20-30% improvement
- ✅ MRR: +20-30% improvement
- ✅ Users notice better results

### Excellent Success
- ✅ Precision@10: +35-40% improvement
- ✅ MRR: +40-50% improvement
- ✅ Transformative user experience

---

## Support

**Documentation**:
- `FINETUNING_DECISION.md` - Why Fin-E5?
- `docs/EVALUATION_METHODOLOGY.md` - How metrics work
- `HOW_TO_MEASURE_METRICS.md` - Quick metrics guide

**Scripts**:
- `scripts/generate_training_data.py --help`
- `scripts/finetune_e5_model.py --help`

**Existing Tools**:
- `scripts/measure_baseline_performance.py` - Evaluation
- `scripts/compare_model_performance.py` - Comparison
- `scripts/explore_chromadb.py` - Data exploration

---

## Summary

**Decision**: Fine-tune E5-base-v2 → Fin-E5  
**Why**: +30-40% improvement potential, SOTA architecture  
**Data**: 1000 auto-generated pairs  
**Time**: 1 day data generation + 1 day training + 1 day deployment  
**ROI**: Significant quality improvement for one-time 3-day effort  

**Ready to start?**

```bash
python scripts/generate_training_data.py --target-pairs 1000
```

---

**Created**: November 3, 2025  
**Status**: Ready to Use  
**Next Action**: Generate training data

