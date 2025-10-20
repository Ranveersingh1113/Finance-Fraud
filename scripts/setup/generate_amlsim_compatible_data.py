"""
Generate AMLSim-Compatible Transaction Data
Creates same CSV format as IBM AMLSim without dependency issues
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

print("="*70)
print("AMLSim-Compatible Data Generator")
print("="*70)

# Configuration
NUM_ACCOUNTS = 1000
NUM_NORMAL_TRANSACTIONS = 10000
NUM_SUSPICIOUS_PATTERNS = 50
OUTPUT_DIR = Path("data/amlsim")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"\nConfiguration:")
print(f"  Accounts: {NUM_ACCOUNTS}")
print(f"  Normal Transactions: {NUM_NORMAL_TRANSACTIONS}")
print(f"  Suspicious Patterns: {NUM_SUSPICIOUS_PATTERNS}")

# Step 1: Generate Accounts
print("\n[Step 1] Generating accounts...")
accounts = []
suspicious_account_ids = set()

for i in range(NUM_ACCOUNTS):
    # 5% of accounts will be suspicious
    is_suspicious = random.random() < 0.05
    if is_suspicious:
        suspicious_account_ids.add(i)
    
    accounts.append({
        'ACCOUNT_ID': i,
        'PRIMARY_CUSTOMER_ID': f'C_{i}',
        'init_balance': round(random.uniform(5000, 500000), 2),
        'start': 0,
        'end': 720,  # 720 time steps (~1 month)
        'country': random.choice(['IN', 'US', 'UK', 'SG']),
        'business': random.choice(['I', 'C']),  # Individual or Corporate
        'suspicious': is_suspicious,
        'isFraud': is_suspicious,
        'modelID': 0
    })

df_accounts = pd.DataFrame(accounts)
print(f"  [OK] Generated {len(df_accounts)} accounts")
print(f"  Suspicious accounts: {len(suspicious_account_ids)}")

# Step 2: Generate Normal Transactions
print("\n[Step 2] Generating normal transactions...")
transactions = []
txn_id = 0

for _ in range(NUM_NORMAL_TRANSACTIONS):
    orig = random.randint(0, NUM_ACCOUNTS-1)
    dest = random.randint(0, NUM_ACCOUNTS-1)
    
    # Avoid self-transactions
    while dest == orig:
        dest = random.randint(0, NUM_ACCOUNTS-1)
    
    transactions.append({
        'TXN_ID': txn_id,
        'ACCOUNT_ID': orig,
        'COUNTER_PARTY_ACCOUNT_NUM': dest,
        'TXN_SOURCE_TYPE_CODE': 'TRANSFER',
        'tx_count': 1,
        'TXN_AMOUNT_ORIG': round(random.uniform(100, 50000), 2),
        'start': random.randint(1, 700),
        'end': random.randint(1, 700)
    })
    txn_id += 1

print(f"  [OK] Generated {len(transactions)} normal transactions")

# Step 3: Generate Suspicious Patterns
print("\n[Step 3] Generating suspicious patterns...")
alerts = []
alert_id = 0

# Pattern 1: Fan-Out (1 account → many accounts)
print("  Generating fan-out patterns...")
for pattern_num in range(NUM_SUSPICIOUS_PATTERNS // 3):
    source_account = random.choice(list(suspicious_account_ids))
    num_destinations = random.randint(5, 15)
    
    for _ in range(num_destinations):
        dest = random.randint(0, NUM_ACCOUNTS-1)
        if dest == source_account:
            continue
        
        transactions.append({
            'TXN_ID': txn_id,
            'ACCOUNT_ID': source_account,
            'COUNTER_PARTY_ACCOUNT_NUM': dest,
            'TXN_SOURCE_TYPE_CODE': 'TRANSFER',
            'tx_count': 1,
            'TXN_AMOUNT_ORIG': round(random.uniform(9000, 9900), 2),  # Just under threshold
            'start': random.randint(1, 100),
            'end': random.randint(1, 100)
        })
        txn_id += 1
    
    alerts.append({
        'ALERT_KEY': alert_id,
        'ALERT_TEXT': 'fan-out',
        'ACCOUNT_ID': source_account,
        'CUSTOMER_ID': f'C_{source_account}',
        'EVENT_DATE': '2024-01-01',
        'CHECK_NAME': 'FAN_OUT_DETECTION',
        'Organization_Type': 'INDIVIDUAL' if accounts[source_account]['business'] == 'I' else 'CORPORATE',
        'Escalated_To_Case_Investigation': 'YES'
    })
    alert_id += 1

# Pattern 2: Fan-In (many accounts → 1 account)
print("  Generating fan-in patterns...")
for pattern_num in range(NUM_SUSPICIOUS_PATTERNS // 3):
    dest_account = random.choice(list(suspicious_account_ids))
    num_sources = random.randint(5, 15)
    
    for _ in range(num_sources):
        source = random.randint(0, NUM_ACCOUNTS-1)
        if source == dest_account:
            continue
        
        transactions.append({
            'TXN_ID': txn_id,
            'ACCOUNT_ID': source,
            'COUNTER_PARTY_ACCOUNT_NUM': dest_account,
            'TXN_SOURCE_TYPE_CODE': 'TRANSFER',
            'tx_count': 1,
            'TXN_AMOUNT_ORIG': round(random.uniform(9000, 9900), 2),
            'start': random.randint(200, 300),
            'end': random.randint(200, 300)
        })
        txn_id += 1
    
    alerts.append({
        'ALERT_KEY': alert_id,
        'ALERT_TEXT': 'fan-in',
        'ACCOUNT_ID': dest_account,
        'CUSTOMER_ID': f'C_{dest_account}',
        'EVENT_DATE': '2024-02-01',
        'CHECK_NAME': 'FAN_IN_DETECTION',
        'Organization_Type': 'INDIVIDUAL' if accounts[dest_account]['business'] == 'I' else 'CORPORATE',
        'Escalated_To_Case_Investigation': 'YES'
    })
    alert_id += 1

# Pattern 3: Cycle (A → B → C → A)
print("  Generating cycle patterns...")
for pattern_num in range(NUM_SUSPICIOUS_PATTERNS // 3):
    cycle_length = random.randint(3, 6)
    cycle_accounts = random.sample(list(suspicious_account_ids), min(cycle_length, len(suspicious_account_ids)))
    
    for i in range(len(cycle_accounts)):
        source = cycle_accounts[i]
        dest = cycle_accounts[(i + 1) % len(cycle_accounts)]
        
        transactions.append({
            'TXN_ID': txn_id,
            'ACCOUNT_ID': source,
            'COUNTER_PARTY_ACCOUNT_NUM': dest,
            'TXN_SOURCE_TYPE_CODE': 'TRANSFER',
            'tx_count': 1,
            'TXN_AMOUNT_ORIG': round(random.uniform(5000, 15000), 2),
            'start': random.randint(400, 500),
            'end': random.randint(400, 500)
        })
        txn_id += 1
    
    # Add alert for the first account in cycle
    alerts.append({
        'ALERT_KEY': alert_id,
        'ALERT_TEXT': 'cycle',
        'ACCOUNT_ID': cycle_accounts[0],
        'CUSTOMER_ID': f'C_{cycle_accounts[0]}',
        'EVENT_DATE': '2024-03-01',
        'CHECK_NAME': 'CYCLE_DETECTION',
        'Organization_Type': 'INDIVIDUAL',
        'Escalated_To_Case_Investigation': 'YES'
    })
    alert_id += 1

df_transactions = pd.DataFrame(transactions)
df_alerts = pd.DataFrame(alerts)

print(f"  [OK] Generated {len(df_transactions)} total transactions")
print(f"  [OK] Generated {len(df_alerts)} alerts")

# Step 4: Generate Cash Transactions
print("\n[Step 4] Generating cash transactions...")
cash_transactions = []
cash_txn_id = 0

for _ in range(2000):
    account_id = random.randint(0, NUM_ACCOUNTS-1)
    cash_transactions.append({
        'TXN_ID': cash_txn_id,
        'ACCOUNT_ID': account_id,
        'BRANCH_ID': random.randint(1, 50),
        'TXN_SOURCE_TYPE_CODE': random.choice(['DEPOSIT', 'WITHDRAWAL']),
        'tx_count': 1,
        'TXN_AMOUNT_ORIG': round(random.uniform(100, 5000), 2),
        'RUN_DATE': random.randint(1, 720),
        'end': random.randint(1, 720)
    })
    cash_txn_id += 1

df_cash = pd.DataFrame(cash_transactions)
print(f"  [OK] Generated {len(df_cash)} cash transactions")

# Step 5: Save all data
print("\n[Step 5] Saving data files...")

df_accounts.to_csv(OUTPUT_DIR / 'accounts.csv', index=False)
print(f"  [OK] Saved: {OUTPUT_DIR / 'accounts.csv'}")

df_transactions.to_csv(OUTPUT_DIR / 'tx.csv', index=False)
print(f"  [OK] Saved: {OUTPUT_DIR / 'tx.csv'}")

df_alerts.to_csv(OUTPUT_DIR / 'alerts.csv', index=False)
print(f"  [OK] Saved: {OUTPUT_DIR / 'alerts.csv'}")

df_cash.to_csv(OUTPUT_DIR / 'cash_tx.csv', index=False)
print(f"  [OK] Saved: {OUTPUT_DIR / 'cash_tx.csv'}")

# Summary
print("\n" + "="*70)
print("AMLSim Data Generation Complete!")
print("="*70)

print(f"\nGenerated Data:")
print(f"  Accounts: {len(df_accounts):,}")
print(f"  Account-to-Account Transactions: {len(df_transactions):,}")
print(f"  Cash Transactions: {len(df_cash):,}")
print(f"  Suspicious Alerts: {len(df_alerts):,}")

print(f"\nSuspicious Patterns:")
print(f"  Fan-Out patterns: ~{NUM_SUSPICIOUS_PATTERNS // 3}")
print(f"  Fan-In patterns: ~{NUM_SUSPICIOUS_PATTERNS // 3}")
print(f"  Cycle patterns: ~{NUM_SUSPICIOUS_PATTERNS // 3}")

print(f"\nGraph Potential:")
print(f"  Nodes (Accounts): {len(df_accounts):,}")
print(f"  Edges (Transactions): {len(df_transactions):,}")
print(f"  Suspicious Accounts: {len(suspicious_account_ids)}")

print(f"\nFiles saved to: {OUTPUT_DIR}")
print("\nNext: Run 'python build_amlsim_graph.py' to build knowledge graph")
print("="*70)

