# Retrain Fin-E5 with Improved Configuration

**Why Retrain?**
- Previous training had **critical warmup bug**: 500 steps for 400 total (125%)
- Model likely didn't converge properly
- New improvements: hard negatives, data validation

---

## 🚀 **Step-by-Step Retraining**

### **Step 1: Validate Training Data** (Use Corrected Data!)

```powershell
# Use the CORRECTED training data (already validated/corrected)
python scripts/validate_training_data_quality.py \
    --data data/finetuning/e5_training_data_corrected.json \
    --output data/finetuning/e5_training_data_validated.json
```

**Note**: We start with `e5_training_data_corrected.json` (already corrected) instead of the original.

**What it does**:
- Checks keyword overlap (query-document relevance)
- Validates domain match (financial terminology)
- Filters low-quality pairs
- Removes generic queries

**Expected**: 10-20% of pairs may be filtered out

---

### **Step 2: Mine Hard Negatives (NEW - Major Improvement)**

```powershell
python scripts/mine_hard_negatives.py \
    --training-data data/finetuning/e5_training_data.json \
    --output data/finetuning/e5_training_data_with_hard_negs.json \
    --base-model intfloat/e5-base-v2
```

**What it does**:
- Uses model embeddings (not just keywords)
- Finds semantically similar but irrelevant documents
- Creates challenging negative examples
- **Expected improvement**: +5-10% accuracy

**Time**: ~10-30 minutes (depends on dataset size)

---

### **Step 3: Retrain with Fixed Configuration**

```powershell
python scripts/finetune_e5_model.py \
    --train \
    --data data/finetuning/e5_training_data_with_hard_negs.json \
    --epochs 4 \
    --batch-size 32 \
    --max-seq-length 512
```

**Key Improvements**:
- ✅ **Warmup auto-calculated**: 10% of total steps (not 125%!)
- ✅ **Hard negatives**: Better discrimination
- ✅ **Validated data**: Higher quality training pairs

**Note**: Don't specify `--warmup-steps` - it's auto-calculated now!

---

## 📊 **Expected Improvements**

| Metric | Previous (Buggy) | Improved | Expected Gain |
|--------|-----------------|----------|---------------|
| Accuracy@10 | 77.5% | **82-85%** | +4.5-7.5% |
| Precision@10 | 8.67% | **10-12%** | +1.3-3.3% |
| MRR@10 | 47.8% | **55-60%** | +7-12% |

**Why Better**:
1. **Proper warmup**: Model learns at correct rate
2. **Hard negatives**: Better discrimination
3. **Clean data**: Removes noise

---

## ⚙️ **Configuration Options**

### **Batch Size** (GPU Memory Dependent)

```powershell
# A4000 GPU (16GB) - Recommended
--batch-size 32

# Smaller GPU (8GB)
--batch-size 16

# Very small GPU (4GB)
--batch-size 8
```

### **Epochs**

```powershell
# Recommended: 4 epochs
--epochs 4

# More training (if needed)
--epochs 6
```

### **Sequence Length**

```powershell
# Default: 512 tokens
--max-seq-length 512

# Longer sequences (if needed)
--max-seq-length 768
```

---

## 🔄 **Complete Retraining Workflow**

```powershell
# 1. Validate CORRECTED data (starting point - already has 1000 pairs!)
python scripts/validate_training_data_quality.py \
    --data data/finetuning/e5_training_data_corrected.json \
    --output data/finetuning/e5_training_data_validated.json

# 2. Mine hard negatives
python scripts/mine_hard_negatives.py \
    --training-data data/finetuning/e5_training_data_validated.json \
    --output data/finetuning/e5_training_data_with_hard_negs.json \
    --base-model intfloat/e5-base-v2

# 3. Retrain (WARMUP AUTO-CALCULATED!)
python scripts/finetune_e5_model.py \
    --train \
    --data data/finetuning/e5_training_data_with_hard_negs.json \
    --epochs 4 \
    --batch-size 32 \
    --max-seq-length 512

# 4. Evaluate
python scripts/finetune_e5_model.py \
    --evaluate \
    --model-path models/fin-e5
```

---

## ⚠️ **Important Notes**

1. **Backup Previous Model** (if you want to compare):
   ```powershell
   Copy-Item -Recurse models/fin-e5 models/fin-e5_previous
   ```

2. **Training Time**: 4 epochs ~2-4 hours (depends on GPU)

3. **Monitor Training**: Check `models/fin-e5/eval/` for evaluation metrics

4. **Warmup is Auto**: Don't specify `--warmup-steps` - it's calculated automatically!

---

## ✅ **Verification**

After training, check:

```powershell
# Check evaluation metrics
Get-Content models/fin-e5/eval/Information-Retrieval_evaluation_fin_e5_eval_results.csv

# Test model loading
python test_fin_e5_model.py
```

**Expected**: Metrics should be better than previous training (77.5% → 82-85%)

---

## 🎯 **Quick Start (One Command)**

If you want to skip validation/mining (not recommended):

```powershell
# Just retrain with fixed warmup (uses CORRECTED data)
python scripts/finetune_e5_model.py \
    --train \
    --data data/finetuning/e5_training_data_corrected.json \
    --epochs 4 \
    --batch-size 32
```

**But**: Hard negatives + validation will give better results!

---

**Ready to retrain?** Start with Step 1: Validate training data!

