# Critical Training Configuration Fixes

**Issues Identified from Review**:
1. ❌ Warmup steps too high (500 for 400 steps = 125%!)
2. ❌ Hard negatives not hard enough (keyword-based vs model-based)
3. ⚠️ Training data size may be insufficient
4. ⚠️ Need better validation

**Fixes Applied**:
1. ✅ Auto-calculate warmup steps (5-10% of total)
2. ✅ Model-based hard negative mining
3. ✅ Enhanced data validation
4. ✅ Training data expansion options

