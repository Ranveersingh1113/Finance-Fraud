# Architectural Change: IEEE-CIS → AMLSim

**Date:** October 17, 2025  
**Phase:** 4 (Week 2)  
**Type:** Strategic Data Source Change  
**Status:** ✅ Cleanup Complete

---

## 🔄 What Changed

### **Original Plan:**
```
Phase 4 Transaction Intelligence:
├─ IEEE-CIS Dataset
├─ V-Feature Clustering (V1-V339)
├─ Card → Device → Email graph
└─ Generic fraud detection
```

### **New Plan:**
```
Phase 4 Transaction Intelligence:
├─ AMLSim Dataset
├─ Account → Transaction → Account graph
├─ Money laundering pattern detection
└─ AML-specific fraud detection
```

---

## 🎯 Why the Change?

### **IEEE-CIS Limitations for Knowledge Graphs:**
1. ❌ No explicit account relationships
2. ❌ Transactions are independent (not connected)
3. ❌ V-features are anonymized (hard to interpret)
4. ❌ Had to infer Card→Device relationships
5. ❌ Generic fraud, not AML-specific

### **AMLSim Advantages:**
1. ✅ Built-in account-to-account relationships
2. ✅ Explicit transaction chains (A→B→C)
3. ✅ Labeled money laundering patterns
4. ✅ Natural graph structure
5. ✅ Aligns with SEBI AML enforcement

---

## 📊 Impact Assessment

### **Code Changes Required:**

| Component | Status | Action |
|-----------|--------|--------|
| **Documentation** | ✅ Updated | Removed IEEE-CIS references |
| **Phase 4 Plan** | ✅ Updated | Changed to AMLSim |
| **Progress Tracking** | ✅ Updated | AMLSim integration planned |
| **Data Ingestion** | ℹ️ Keep | IEEE-CIS loader kept for reference |
| **V-Clustering Code** | ℹ️ Keep | May be useful for other features |
| **Graph Schemas** | ✅ Updated | Designed for AMLSim |

### **No Code Deleted:**
- ✅ IEEE-CIS loading infrastructure preserved
- ✅ V-feature clustering code kept (may use later)
- ✅ Only planning documents updated

---

## 🏗️ New Architecture

### **Dual Knowledge Graph System:**

```
┌────────────────────────────────────────────────────────┐
│ SEBI Regulatory Knowledge Graph                        │
├────────────────────────────────────────────────────────┤
│ Status: ✅ Built (20K nodes, 42K edges)                │
│ Purpose: Regulatory precedents, violations, penalties  │
│                                                        │
│ Entities: Companies, Persons, Violations, Regulators  │
│ Queries: "What penalties for money laundering?"       │
└────────────────────────────────────────────────────────┘
                         +
┌────────────────────────────────────────────────────────┐
│ AMLSim Transaction Network Graph                      │
├────────────────────────────────────────────────────────┤
│ Status: ⏳ To Be Built (Week 3-4)                      │
│ Purpose: Transaction flows, AML patterns, money trails│
│                                                        │
│ Entities: Accounts, Transactions, Alerts, Patterns    │
│ Queries: "Trace money flow from Account X"            │
└────────────────────────────────────────────────────────┘
                         =
┌────────────────────────────────────────────────────────┐
│ Unified GraphRAG System                               │
├────────────────────────────────────────────────────────┤
│ Cross-Domain Queries:                                 │
│ "Is this account's pattern similar to SEBI cases?"    │
│ "Show transaction chains matching regulatory violations" │
│                                                        │
│ Result: Regulatory context + Transaction evidence     │
└────────────────────────────────────────────────────────┘
```

---

## 📋 Updated Timeline

### **Phase 4 Revised:**

```
✅ Week 0: Setup (COMPLETE)
   - NetworkX, spaCy, Pyvis installed
   - Base graph infrastructure built

✅ Week 1-2: SEBI Knowledge Graph (COMPLETE)
   - 20,202 nodes, 41,843 edges
   - 8,831 entities, 25 violations
   - 3,803 semantic relationships

⏳ Week 3-4: AMLSim Integration (NEXT)
   - Research AMLSim
   - Load AMLSim data
   - Build transaction network graph
   - Implement pattern detection

⏳ Week 5-6: Unified System (FUTURE)
   - Combine SEBI + AMLSim
   - GraphRAG integration
   - Interactive visualization
```

---

## 🎯 AMLSim Integration Checklist

### **Week 3 Tasks:**
- [ ] Research AMLSim structure and schema
- [ ] Obtain AMLSim dataset (download or generate)
- [ ] Create `AMLSimLoader` class
- [ ] Create `AMLSimDocumentGenerator` class
- [ ] Test data loading

### **Week 4 Tasks:**
- [ ] Create `AMLSimGraphManager` class
- [ ] Build account network graph
- [ ] Implement pattern detection (fan-out, fan-in, cycles)
- [ ] Generate transaction documents
- [ ] Index in ChromaDB
- [ ] Test AMLSim queries

---

## 💡 Key Benefits of This Change

### **For Graph Construction:**
```
IEEE-CIS Approach:
- Inferred relationships ⚠️
- Card-Device links (guessed)
- No explicit money flow
- V-features hard to interpret

AMLSim Approach:
- Explicit relationships ✅
- Account-Account links (direct)
- Clear money flow chains
- Labeled patterns
```

### **For Client Value:**
```
IEEE-CIS:
"We detected fraud patterns using behavioral clustering"

AMLSim:
"We traced $1.2M through 15 accounts in layering pattern,
matching SEBI Case #2020-042 (money laundering, ₹50L penalty)"

= More actionable intelligence! ✅
```

### **For Regulatory Compliance:**
```
IEEE-CIS: Generic fraud detection
AMLSim: Specific AML/CFT compliance

Better alignment with:
- SEBI AML regulations
- PMLA (Prevention of Money Laundering Act)
- Financial institution requirements
```

---

## 📊 Risk Assessment

### **Risks of This Change:**

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Data Availability** | Medium | Multiple AMLSim sources available |
| **Learning Curve** | Low | AMLSim simpler than IEEE-CIS |
| **Time Impact** | Low | Same timeline (Week 3-4) |
| **Code Rewrite** | Low | Only new code, no deletions |

### **Overall Risk: LOW** ✅

---

## ✅ Cleanup Summary

### **Files Updated:**
1. `PHASE4_IMPLEMENTATION_PLAN.md` - Updated to AMLSim
2. `PROGRESS_TRACKING.md` - Changed references
3. `QUICK_REFERENCE.md` - Updated data sources
4. `PHASE4_AMLSIM_INTEGRATION.md` - Created new integration guide

### **Files Deleted:**
1. `PHASE4_IEEE_CIS_INTEGRATION.md` - Removed (obsolete)

### **Files Preserved:**
1. `src/data/ingestion.py` - IEEE-CIS loader kept (may use for other purposes)
2. V-feature clustering code - Preserved (may be useful later)

---

## 🚀 Next Steps

### **Immediate (Today):**
1. ✅ Remove IEEE-CIS from KG plans
2. ✅ Update documentation
3. ⏳ Research AMLSim

### **Week 3 (Next):**
1. Obtain AMLSim dataset
2. Design AMLSim graph schema
3. Create AMLSim loader
4. Begin graph construction

---

## 📝 Status Update

```
Phase 4 Progress:
├─ Week 0: ✅ Setup (100%)
├─ Week 1-2: ✅ SEBI Graph (100%)
├─ Week 3-4: ⏳ AMLSim Integration (0%)
└─ Week 5-6: ⏳ Unified System (0%)

Overall Phase 4: 35% Complete
Overall Project: 52% Complete
```

**Status:** ✅ Ready to proceed with AMLSim integration

---

**Strategic Decision:** IEEE-CIS → AMLSim = Better GraphRAG foundation  
**Impact:** Positive - Cleaner architecture, better client value  
**Timeline:** Unchanged - Still targeting December 2025

---

**Next:** Research AMLSim and obtain data! 🚀

