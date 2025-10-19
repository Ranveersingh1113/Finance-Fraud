# IBM AMLSim Setup Guide

**Chosen Approach:** Option A - IBM AMLSim (Official)  
**Purpose:** Generate realistic anti-money laundering transaction network  
**Timeline:** 1-2 days setup + 3-4 days integration

---

## 📋 Prerequisites

### **Required Software:**

1. **Java Development Kit (JDK) 8 or higher**
   ```bash
   # Check if Java is installed
   java -version
   
   # If not installed, download from:
   # https://www.oracle.com/java/technologies/downloads/
   # Or use OpenJDK: https://adoptium.net/
   ```

2. **Python 3.10+** ✅ (Already have)

3. **Git** (For cloning repository)
   ```bash
   git --version
   ```

4. **Maven** (Optional, for building from source)
   ```bash
   # Check if Maven is installed
   mvn -version
   ```

---

## 🚀 Step-by-Step Setup

### **Step 1: Clone IBM AMLSim Repository**

```bash
# Navigate to a working directory (not your project)
cd D:\
mkdir AMLSim_Setup
cd AMLSim_Setup

# Clone the repository
git clone https://github.com/IBM/AMLSim.git
cd AMLSim
```

**Repository Structure:**
```
AMLSim/
├── conf/           # Configuration files
├── scripts/        # Execution scripts
├── paramFiles/     # Parameter files for patterns
├── jars/           # Java JAR files
├── outputs/        # Generated data (after running)
└── README.md       # Documentation
```

---

### **Step 2: Configure AMLSim Parameters**

#### **Edit `conf/conf.json`:**

```json
{
  "general": {
    "simulation_name": "sebi_aml_simulation",
    "random_seed": 0,
    "num_accounts": 5000,
    "num_steps": 1440,
    "transaction_interval": 1
  },
  
  "input": {
    "directory": "paramFiles/",
    "schema": "schema.json",
    "accounts": "accounts.csv",
    "alert_patterns": "alertPatterns.csv"
  },
  
  "output": {
    "directory": "outputs/",
    "transaction_log": "transactions.csv",
    "account_log": "accounts.csv",
    "alert_log": "alert_accounts.csv"
  },
  
  "temporal": {
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }
}
```

**Key Parameters:**
- `num_accounts`: 5,000 accounts (manageable size)
- `num_steps`: 1,440 (one day at 1-minute intervals)
- Generates realistic transaction patterns over time

---

### **Step 3: Customize Money Laundering Patterns**

#### **Edit `paramFiles/alertPatterns.csv`:**

```csv
pattern_id,pattern_type,num_accounts,num_steps,amount_min,amount_max
1,fan_out,10,5,5000,10000
2,fan_in,10,5,5000,10000
3,cycle,5,10,8000,15000
4,scatter_gather,15,8,3000,8000
5,bipartite,20,12,5000,12000
```

**Pattern Explanations:**
- `fan_out`: 1 account sends to many (placement)
- `fan_in`: Many accounts send to 1 (integration)
- `cycle`: Circular transactions (layering)
- `scatter_gather`: Complex multi-hop
- `bipartite`: Two groups exchanging

---

### **Step 4: Run AMLSim Simulation**

```bash
# Windows PowerShell (in AMLSim directory)
cd D:\AMLSim_Setup\AMLSim

# Run the simulator
.\scripts\run_amlsim.bat

# OR if using bash/WSL:
./scripts/run_amlsim.sh
```

**Expected Output:**
```
Generating AML transaction network...
Creating 5,000 accounts...
Simulating 1,440 time steps...
Generating transactions...
Detecting suspicious patterns...
Writing outputs...

Simulation complete!
Generated files:
- outputs/accounts.csv (5,000 accounts)
- outputs/transactions.csv (~50,000 transactions)
- outputs/alert_accounts.csv (suspicious accounts)
- outputs/alert_tx.csv (suspicious transactions)
```

**Processing Time:** 5-15 minutes depending on configuration

---

### **Step 5: Copy Data to Your Project**

```bash
# Create AMLSim directory in your project
mkdir "D:\OneDrive\Desktop\Finance Fraud\data\amlsim"

# Copy generated files
copy D:\AMLSim_Setup\AMLSim\outputs\*.csv "D:\OneDrive\Desktop\Finance Fraud\data\amlsim\"

# Verify files
dir "D:\OneDrive\Desktop\Finance Fraud\data\amlsim\"
```

**Expected Files:**
```
data/amlsim/
├── accounts.csv         # Account information
├── transactions.csv     # Transaction flows
├── alert_accounts.csv   # Suspicious accounts
└── alert_tx.csv         # Suspicious transactions
```

---

## 📊 Understanding AMLSim Output

### **1. accounts.csv**
```csv
account_id,init_balance,start,end,country,business_type,is_sar
0,50000.00,0,1440,US,I,false
1,100000.00,0,1440,US,C,true
2,75000.00,0,1440,US,I,false
```

**Fields:**
- `account_id`: Unique ID
- `init_balance`: Starting balance
- `start/end`: Active time period
- `country`: Account country
- `business_type`: I (Individual), C (Corporate)
- `is_sar`: Flagged for SAR filing

---

### **2. transactions.csv**
```csv
tx_id,timestamp,orig_id,dest_id,tx_amount,tx_type,is_sar
0,1,0,100,5000.00,transfer,false
1,2,0,101,5000.00,transfer,false
2,3,0,102,5000.00,transfer,true
```

**Fields:**
- `tx_id`: Transaction ID
- `timestamp`: When transaction occurred
- `orig_id`: Sender account (**FROM**)
- `dest_id`: Receiver account (**TO**)
- `tx_amount`: Amount transferred
- `tx_type`: Transaction type
- `is_sar`: Part of suspicious pattern

**🎯 Graph Structure:** `orig_id → dest_id` creates natural edges!

---

### **3. alert_accounts.csv**
```csv
account_id,alert_type,sar_flag,schedule_id
0,fan-out,true,1
5,layering,true,3
```

**Fields:**
- `account_id`: Account that triggered alert
- `alert_type`: Pattern type (fan-out, cycle, etc.)
- `sar_flag`: SAR filed
- `schedule_id`: Reference to pattern definition

---

## 🏗️ Integration with Your Project

### **What Happens Next:**

```
Week 3 Day 1-2: AMLSim Setup (Current)
├─ ✅ Install Java
├─ ✅ Clone AMLSim
├─ ✅ Generate transaction data
└─ ✅ Copy to project

Week 3 Day 3-5: Data Loading
├─ Create src/data/amlsim_loader.py
├─ Load accounts, transactions, alerts
├─ Parse and validate data
└─ Test data loading

Week 4 Day 1-3: Graph Construction
├─ Create src/core/amlsim_graph_manager.py
├─ Build account network
├─ Add transaction edges
└─ Link alerts to accounts

Week 4 Day 4-5: Pattern Detection
├─ Implement fan-out detection
├─ Implement fan-in detection
├─ Implement cycle detection
└─ Test graph queries
```

---

## 🎯 Expected Graph After Setup

### **AMLSim Graph Stats (Estimated):**
```
Configuration: 5,000 accounts, 1,440 steps

Expected Output:
├─ Accounts: ~5,000 nodes
├─ Transactions: ~50,000 edges
├─ Alerts: ~250 suspicious patterns
├─ SAR Accounts: ~250 flagged accounts

Graph Queries Will Enable:
- "Show all accounts in fan-out patterns"
- "Trace money flow from Account_0"
- "Find circular transaction chains"
- "Which accounts transact with Account_X?"
```

---

## 🔧 Troubleshooting

### **Issue: Java Not Installed**
```bash
Solution:
1. Download JDK 11 or higher
   - Windows: https://adoptium.net/temurin/releases/
2. Install and set JAVA_HOME
3. Restart terminal
4. Verify: java -version
```

### **Issue: AMLSim Fails to Run**
```bash
Solutions:
1. Check Java version (need 8+)
2. Verify conf.json syntax (valid JSON)
3. Check file paths in conf.json
4. Review AMLSim logs in outputs/
```

### **Issue: No Output Files Generated**
```bash
Solutions:
1. Check AMLSim console for errors
2. Verify paramFiles exist
3. Reduce num_accounts if memory issues
4. Check write permissions on outputs/
```

---

## 📝 Alternative: Quick Start Script

If IBM AMLSim setup is complex, I can create a Python script to generate compatible synthetic data immediately. Just let me know!

---

## 🚀 Next Steps After Data Generation

Once you have AMLSim data in `./data/amlsim/`, I'll create:

1. **`src/data/amlsim_loader.py`**
   - Load accounts, transactions, alerts
   - Parse and validate data
   - Merge related data

2. **`src/core/amlsim_graph_manager.py`**
   - Build account network graph
   - Add transaction relationships
   - Implement pattern detection

3. **`build_amlsim_graph.py`**
   - Process AMLSim data
   - Build complete transaction network
   - Save and persist graph

4. **Test & Validate**
   - Query testing
   - Pattern detection verification
   - Integration with SEBI graph

---

## ✅ Current Progress

```
Phase 4 Timeline:
✅ Week 0: Setup Complete
✅ Week 1-2: SEBI Graph Complete
🚧 Week 3: AMLSim Setup (In Progress)
   ├─ ✅ Chose Option A (IBM AMLSim)
   ├─ ⏳ Clone repository
   ├─ ⏳ Install dependencies
   ├─ ⏳ Generate data
   └─ ⏳ Copy to project
```

---

## 📋 Immediate Actions

**Ready to begin AMLSim setup?**

I'll guide you through:
1. Installing Java (if needed)
2. Cloning AMLSim repository
3. Configuring parameters
4. Running simulation
5. Copying data to your project

**Would you like me to:**
- Check if Java is installed on your system?
- Clone the AMLSim repository?
- Create the data directory structure?

Let me know and I'll proceed with the setup! 🚀
