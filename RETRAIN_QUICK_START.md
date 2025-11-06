# Quick Retrain Guide - Using Corrected Data

**Starting Point**: `e5_training_data_corrected.json` (1000 pairs, already corrected)

---

## 🚀 **Recommended Workflow**

### **Step 1: Validate Corrected Data**

```powershell
python scripts/validate_training_data_quality.py \
    --data data/finetuning/e5_training_data_corrected.json \
    --output data/finetuning/e5_training_data_validated.json
```

**Why**: Even though it's "corrected", validation filters out any remaining low-quality pairs.

---

### **Step 2: Mine Hard Negatives**

```powershell
python scripts/mine_hard_negatives.py \
    --training-data data/finetuning/e5_training_data_validated.json \
    --output data/finetuning/e5_training_data_with_hard_negs.json \
    --base-model intfloat/e5-base-v2
```

**Why**: Creates challenging negative examples using model embeddings (better than keywords).

---

### **Step 3: Retrain with Fixed Warmup**

```powershell
python scripts/finetune_e5_model.py \
    --train \
    --data data/finetuning/e5_training_data_with_hard_negs.json \
    --epochs 4 \
    --batch-size 32 \
    --max-seq-length 512
```

**Key**: Don't specify `--warmup-steps` - it's auto-calculated as 10% of total steps!

---

## ⚡ **Quick Retrain (Skip Validation/Mining)**

If you want to retrain immediately with just the warmup fix:

```powershell
python scripts/finetune_e5_model.py \
    --train \
    --data data/finetuning/e5_training_data_corrected.json \
    --epochs 4 \
    --batch-size 32
```

**Note**: This uses the corrected data directly, but you'll get better results with hard negatives.

---

## 📊 **Data Files**

- `e5_training_data.json` - Original (2 pairs - incomplete)
- `e5_training_data_corrected.json` - **CORRECTED (1000 pairs)** ✅ Use this!
- `e5_training_data_validated.json` - After validation (will be created)
- `e5_training_data_with_hard_negs.json` - With hard negatives (will be created)

---

## ✅ **Summary**

**Always start with**: `e5_training_data_corrected.json` (1000 pairs)

**Best path**: Validate → Mine Hard Negatives → Train

**Quick path**: Use corrected data directly → Train (with fixed warmup)

