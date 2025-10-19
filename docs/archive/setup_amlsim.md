# AMLSim Setup - Step-by-Step Instructions

**Status:** ✅ Java 23 Installed | ✅ Data directory created  
**Next:** Clone and run IBM AMLSim

---

## 🚀 Quick Start (Copy-Paste Commands)

### **Step 1: Clone AMLSim Repository**

Open a **new PowerShell window** and run:

```powershell
# Navigate to a setup directory
cd D:\
mkdir AMLSim_Setup -ErrorAction SilentlyContinue
cd AMLSim_Setup

# Clone IBM AMLSim
git clone https://github.com/IBM/AMLSim.git
cd AMLSim

# Verify clone
dir
```

**Expected Output:** You should see folders: `conf`, `scripts`, `paramFiles`, `jars`

---

### **Step 2: Run AMLSim Simulation**

```powershell
# Still in D:\AMLSim_Setup\AMLSim

# Run the simulator (Windows)
python scripts\run_amlsim.py
```

**This will:**
- Generate 5,000 accounts
- Simulate money laundering patterns
- Create ~50,000 transactions
- Flag suspicious accounts
- Takes 5-15 minutes

**Expected Console Output:**
```
Generating AML transaction network...
Reading parameter files...
Creating accounts...
Simulating transactions...
Detecting patterns...
Writing outputs...
Done! Check outputs/ directory
```

---

### **Step 3: Copy Data to Your Project**

```powershell
# Copy generated CSV files
copy D:\AMLSim_Setup\AMLSim\outputs\*.csv "D:\OneDrive\Desktop\Finance Fraud\data\amlsim\"

# Verify files copied
dir "D:\OneDrive\Desktop\Finance Fraud\data\amlsim\"
```

**You should see:**
- `accounts.csv`
- `transactions.csv`
- `alert_accounts.csv`
- `alert_tx.csv`

---

### **Step 4: Validate Data**

Return to your project and run:

```powershell
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\python.exe -c "import pandas as pd; df = pd.read_csv('data/amlsim/transactions.csv'); print(f'Loaded {len(df)} transactions'); print(df.head())"
```

**Expected:** Should show transaction data with columns: `tx_id`, `timestamp`, `orig_id`, `dest_id`, `tx_amount`

---

## 📊 What AMLSim Will Generate

### **Data Files:**

**1. accounts.csv** (~5,000 rows)
```
account_id,init_balance,start,end,country,business_type,is_sar
0,50000.00,0,1440,US,I,false
1,100000.00,0,1440,US,C,true
...
```

**2. transactions.csv** (~50,000 rows)
```
tx_id,timestamp,orig_id,dest_id,tx_amount,tx_type,is_sar
0,1,0,100,5000.00,transfer,false
1,2,0,101,5000.00,transfer,false
...
```

**3. alert_accounts.csv** (~250 rows)
```
account_id,alert_type,sar_flag,schedule_id
0,fan-out,true,1
5,cycle,true,3
...
```

---

## 🔧 Troubleshooting

### **If git clone fails:**
```powershell
# Alternative: Download ZIP
# 1. Go to: https://github.com/IBM/AMLSim
# 2. Click "Code" → "Download ZIP"
# 3. Extract to D:\AMLSim_Setup\
```

### **If Python script fails:**
```powershell
# Try the shell script (if you have bash/WSL)
bash scripts/run_amlsim.sh

# OR check Java JAR directly
java -jar jars/amlsim.jar
```

### **If no outputs generated:**
```
Check:
1. Java version (java -version) - need 8+
2. Python packages: pip install networkx numpy pandas
3. Parameter files exist in paramFiles/
4. Check error messages in console
```

---

## ⚡ Alternative: I Can Create Synthetic Data

If IBM AMLSim setup is taking too long, I can create a Python script to generate compatible synthetic data **right now** (5 minutes).

**Just say:** "Create synthetic data instead" and I'll generate it immediately!

---

## 📝 Next Steps After Data is Ready

Once you have AMLSim data in `./data/amlsim/`, return here and I will:

1. ✅ Create `AMLSimLoader` to read the data
2. ✅ Create `AMLSimGraphManager` to build the network
3. ✅ Implement money laundering pattern detection
4. ✅ Build the complete transaction knowledge graph
5. ✅ Test integration with SEBI graph

---

## ✅ Checklist

- [x] Java installed (version 23)
- [x] AMLSim data directory created
- [ ] AMLSim repository cloned
- [ ] Simulation run successfully
- [ ] Data files copied to project
- [ ] Data validated

**Current Step:** Clone AMLSim repository

---

**Ready to clone AMLSim?** 

Just run the commands from Step 1 above, or let me know if you want me to create synthetic data instead! 🚀

