# AMLSim Research & Setup Guide

**Purpose:** Integrate AMLSim (Anti-Money Laundering Simulator) for transaction network graph  
**Phase:** 4 - Week 3-4  
**Status:** Research & Planning

---

## 🔍 What is AMLSim?

**AMLSim** (Anti-Money Laundering Simulator) is an open-source tool developed by **IBM Research** that generates synthetic transaction data for testing AML (Anti-Money Laundering) systems.

### **Key Features:**
- ✅ Generates realistic account-to-account transaction networks
- ✅ Includes labeled money laundering patterns (alerts)
- ✅ Simulates various AML typologies (layering, structuring, fan-out/fan-in)
- ✅ Provides ground truth for testing fraud detection systems
- ✅ CSV output perfect for knowledge graphs

---

## 📊 AMLSim Data Structure

### **Core Data Files:**

#### **1. accounts.csv**
```csv
account_id, init_balance, start, end, country, business_type, is_sar
1000, 50000.00, 0, 100, US, I, false
1001, 100000.00, 0, 100, US, C, true
```

**Fields:**
- `account_id`: Unique account identifier
- `init_balance`: Starting balance
- `start/end`: Simulation time range
- `country`: Account country
- `business_type`: Individual (I), Company (C), etc.
- `is_sar`: Whether account triggered SAR (Suspicious Activity Report)

---

#### **2. transactions.csv**
```csv
transaction_id, timestamp, orig_account, dest_account, amount, transaction_type
T001, 1, 1000, 1001, 5000.00, TRANSFER
T002, 2, 1000, 1002, 5000.00, TRANSFER
```

**Fields:**
- `transaction_id`: Unique transaction ID
- `timestamp`: Transaction time
- `orig_account`: Sender account (FROM)
- `dest_account`: Receiver account (TO)
- `amount`: Transaction amount
- `transaction_type`: TRANSFER, DEPOSIT, WITHDRAWAL, etc.

**🎯 Key Feature:** `orig_account → dest_account` creates **natural graph edges!**

---

#### **3. alert_accounts.csv**
```csv
account_id, alert_type, sar_flag, schedule_id
1001, fan-out, true, S001
1005, layering, true, S002
```

**Fields:**
- `account_id`: Account that triggered alert
- `alert_type`: Type of suspicious pattern
- `sar_flag`: Whether SAR was filed
- `schedule_id`: Reference to pattern schedule

**Alert Types:**
- `fan-out`: Single account → Many accounts (Placement)
- `fan-in`: Many accounts → Single account (Integration)
- `cycle`: Circular transactions (Layering)
- `scatter-gather`: Complex multi-hop pattern
- `bipartite`: Two groups exchanging funds

---

## 🏗️ Graph Schema Design

### **Node Types:**

```python
1. Account Nodes
   Properties:
   - account_id (primary key)
   - balance
   - account_type (Individual/Corporate)
   - country
   - is_sar (boolean)
   - risk_score (calculated)
   - alert_count (number of alerts)

2. Transaction Nodes  
   Properties:
   - transaction_id
   - amount
   - timestamp
   - transaction_type
   - pattern_type (if part of pattern)

3. Alert Nodes
   Properties:
   - alert_id
   - alert_type (fan-out, layering, etc.)
   - sar_flag
   - severity (HIGH/MEDIUM/LOW)
   - accounts_involved

4. Pattern Nodes
   Properties:
   - pattern_id
   - pattern_name
   - typology (PLACEMENT/LAYERING/INTEGRATION)
   - account_count
```

### **Relationship Types:**

```python
1. SENT_TO (Account → Account)
   Properties:
   - amount
   - timestamp
   - transaction_id
   - is_suspicious

2. TRANSACTED (Account → Transaction → Account)
   Properties:
   - role (sender/receiver)

3. TRIGGERED (Account → Alert)
   Properties:
   - confidence_score
   - detection_time

4. PARTICIPATES_IN (Account → Pattern)
   Properties:
   - role (originator/intermediary/destination)
```

---

## 📥 How to Obtain AMLSim Data

### **Option 1: Use IBM AMLSim (Recommended)**

**GitHub:** https://github.com/IBM/AMLSim

**Steps:**
```bash
# 1. Clone repository
git clone https://github.com/IBM/AMLSim.git

# 2. Install dependencies (Java required)
cd AMLSim
# Follow installation instructions

# 3. Generate synthetic data
# Edit conf.json to configure:
# - Number of accounts
# - Transaction patterns
# - Simulation length

# 4. Run simulator
./scripts/run_amlsim.sh

# 5. Output will be in outputs/ directory:
# - accounts.csv
# - transactions.csv
# - alert_accounts.csv
# - patterns.csv

# 6. Copy to your project
cp outputs/*.csv "D:/OneDrive/Desktop/Finance Fraud/data/amlsim/"
```

---

### **Option 2: Use Pre-Generated AMLSim Dataset**

**Search for:**
- "AMLSim dataset download"
- "Anti-money laundering synthetic data"
- "Transaction network dataset"

**Sources:**
- Kaggle (may have AMLSim-based datasets)
- Research papers (often include data links)
- Financial AI competitions

---

### **Option 3: Create Simplified Synthetic Data**

If AMLSim setup is complex, create simplified version:

```python
# create_synthetic_aml_data.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate 1,000 accounts
accounts = []
for i in range(1000):
    accounts.append({
        'account_id': f'ACC_{i:04d}',
        'balance': np.random.uniform(10000, 1000000),
        'account_type': np.random.choice(['Individual', 'Corporate']),
        'country': 'IN',
        'is_sar': np.random.random() < 0.05  # 5% suspicious
    })

# Generate 10,000 transactions with patterns
transactions = []
for i in range(10000):
    # 80% normal, 20% part of patterns
    if np.random.random() < 0.8:
        # Normal transaction
        from_acc = f'ACC_{np.random.randint(0, 1000):04d}'
        to_acc = f'ACC_{np.random.randint(0, 1000):04d}'
        amount = np.random.uniform(100, 50000)
    else:
        # Suspicious pattern (fan-out example)
        from_acc = f'ACC_{np.random.randint(0, 50):04d}'  # Few source accounts
        to_acc = f'ACC_{np.random.randint(100, 1000):04d}'  # Many destinations
        amount = 9900  # Just under threshold
    
    transactions.append({
        'transaction_id': f'TXN_{i:06d}',
        'timestamp': i,
        'orig_account': from_acc,
        'dest_account': to_acc,
        'amount': amount,
        'transaction_type': 'TRANSFER'
    })

# Save
pd.DataFrame(accounts).to_csv('./data/amlsim/accounts.csv', index=False)
pd.DataFrame(transactions).to_csv('./data/amlsim/transactions.csv', index=False)
```

---

## 🎯 AMLSim Integration Plan

### **Phase 1: Data Acquisition (Today - Tomorrow)**
- [ ] Choose data source (IBM AMLSim, public dataset, or synthetic)
- [ ] Download/generate AMLSim data
- [ ] Verify data quality
- [ ] Place in `./data/amlsim/` directory

### **Phase 2: Data Understanding (1-2 days)**
- [ ] Analyze account structure
- [ ] Map transaction flows
- [ ] Identify alert patterns
- [ ] Design graph schema

### **Phase 3: Implementation (3-4 days)**
- [ ] Create `AMLSimLoader`
- [ ] Create `AMLSimGraphManager`
- [ ] Build transaction network
- [ ] Implement pattern detection
- [ ] Test queries

### **Phase 4: Integration (2-3 days)**
- [ ] Index transaction documents in ChromaDB
- [ ] Link to SEBI graph
- [ ] Create unified queries
- [ ] Test combined system

**Total Timeline:** Week 3-4 (10-14 days)

---

## 💡 Quick Start Template

### **Minimal AMLSim Schema:**

```python
# Minimum viable AMLSim data structure

Required Files:
1. accounts.csv
   - account_id (string)
   - is_sar (boolean)

2. transactions.csv  
   - transaction_id (string)
   - orig_account (string) → Links to accounts
   - dest_account (string) → Links to accounts
   - amount (float)
   - timestamp (int/datetime)

Optional:
3. alerts.csv
   - account_id
   - alert_type (fan-out, fan-in, cycle, layering)
```

**This is enough to build:**
- ✅ Account network graph
- ✅ Transaction flow chains
- ✅ Pattern detection (fan-out, fan-in, cycles)
- ✅ Money trail tracing

---

## 🚀 Next Immediate Steps

### **Step 1: Choose Approach** (User Decision Needed)

**A. Full AMLSim (Most Realistic)**
- Download IBM AMLSim from GitHub
- Generate synthetic data with patterns
- **Pros:** Realistic, labeled patterns, comprehensive
- **Cons:** Requires Java, setup time (~1-2 days)

**B. Find Pre-Generated Dataset (Fastest)**
- Search Kaggle, research papers
- Download ready-to-use AMLSim data
- **Pros:** Immediate use, no setup
- **Cons:** May not have exact schema

**C. Create Synthetic Data (Most Control)**
- Write Python script to generate transactions
- Create account network with patterns
- **Pros:** Full control, Python-only, fast
- **Cons:** Less realistic than IBM AMLSim

---

### **Step 2: Create Data Directory**

```bash
# Create AMLSim directory
mkdir data/amlsim

# Expected files after data acquisition:
data/amlsim/
├── accounts.csv
├── transactions.csv
├── alert_accounts.csv (optional)
└── README.md
```

---

## 📋 Success Criteria

**AMLSim integration is successful when:**
- [ ] Data loaded successfully (accounts + transactions)
- [ ] Graph built with Account and Transaction nodes
- [ ] Relationships created (orig_account → dest_account)
- [ ] Can detect fan-out patterns
- [ ] Can detect fan-in patterns
- [ ] Can detect circular transactions
- [ ] Can trace money flow chains
- [ ] Documents indexed in ChromaDB

---

## ✅ Cleanup Summary

### **What We Removed:**
- ✅ IEEE-CIS knowledge graph references from planning docs
- ✅ V-feature clustering from KG plan (kept code for future use)
- ✅ Card/Device/Email graph schema

### **What We Added:**
- ✅ AMLSim integration planning
- ✅ Account/Transaction/Alert graph schema
- ✅ Money laundering pattern detection plan
- ✅ Comprehensive AMLSim research guide

### **What We Kept:**
- ✅ IEEE-CIS data loading code (in `src/data/ingestion.py`)
- ✅ V-feature clustering infrastructure
- ✅ All Phase 1-3 functionality
- ✅ SEBI knowledge graph (20K nodes, 42K edges)

---

## 🎯 Current Status

```
Phase 4 Progress:
├─ Week 0: ✅ Setup Complete
├─ Week 1-2: ✅ SEBI Graph Complete (20K nodes)
├─ IEEE-CIS References: ✅ Removed from KG plans
├─ AMLSim Research: 🚧 In Progress
└─ Week 3-4: ⏳ Awaiting AMLSim data

Next Immediate Action:
→ Choose AMLSim data source (Option A, B, or C)
→ Obtain AMLSim data
→ Begin Week 3 implementation
```

---

**Ready to proceed with AMLSim data acquisition!**

**User Decision Required:** Which approach do you prefer?
- **A.** IBM AMLSim (full setup, most realistic)
- **B.** Find pre-generated dataset (fastest)
- **C.** Create synthetic data (most control)

Let me know and I'll proceed immediately! 🚀

