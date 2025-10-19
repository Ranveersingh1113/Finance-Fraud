# AMLSim Transaction Data

**Status:** ✅ Complete & Indexed  
**Last Updated:** October 19, 2025

## Current Data

This directory contains **synthetic transaction data** generated for money laundering detection and pattern analysis.

### Files Present

| File | Records | Description |
|------|---------|-------------|
| `accounts.csv` | 1,000 | Account information (individual & corporate) |
| `tx.csv` | ~12,000 | Account-to-account transactions |
| `alerts.csv` | ~50 | Suspicious activity alerts (fan-out, fan-in, cycle) |
| `cash_tx.csv` | 2,000 | Cash deposit/withdrawal transactions |

### Data Characteristics

**Accounts:**
- 1,000 total accounts
- ~50 marked as suspicious (5%)
- Mix of individual (I) and corporate (C) accounts
- Countries: IN, US, UK, SG

**Transactions:**
- Normal transactions: ~10,000
- Suspicious patterns: ~2,000
- Amount range: $100 - $50,000
- Patterns: fan-out, fan-in, cycles

**Alerts:**
- Fan-out patterns: ~17 (placement/structuring)
- Fan-in patterns: ~17 (integration/collection)
- Cycle patterns: ~16 (layering)

## Knowledge Graph Built

✅ **Transaction Network Graph:**
- **Location:** `data/graphs/amlsim_transaction_graph.gpickle`
- **Nodes:** 1,650 (1,000 accounts + 150 customers + 500 alerts/other)
- **Edges:** ~45,000 (SENT_TO, RECEIVED_FROM, OWNED_BY, TRIGGERED)
- **Patterns Detected:** 12 fraud rings

## ChromaDB Indexed

✅ **Transaction Documents:**
- **Collection:** `amlsim_transactions`
- **Documents:** 10,401 natural language transaction descriptions
- **Indexed:** Yes, ready for RAG queries

## Usage

### Rebuild Graph
```bash
python build_amlsim_graph.py
```

### Reindex Documents
```bash
python index_amlsim_documents.py
```

### Query Transactions
Use the Streamlit UI or API:
```python
query = "Show me accounts with fan-out patterns"
# System queries both SEBI regulations and AMLSim transactions
```

## Data Generation

This data was generated using `generate_amlsim_compatible_data.py` to create AMLSim-compatible CSV files without Java/NetworkX 1.11 dependencies.

### Regenerate Data (if needed)
```bash
python generate_amlsim_compatible_data.py
# Then rebuild graph and reindex
python build_amlsim_graph.py
python index_amlsim_documents.py
```

## Integration with SEBI

The AMLSim transaction network is **integrated with SEBI regulatory knowledge** in the unified GraphRAG system:

- **SEBI Graph:** Provides regulatory context (laws, penalties, precedents)
- **AMLSim Graph:** Provides transaction patterns (fan-out, fan-in, cycles)
- **Unified Query:** Combines both for comprehensive fraud analysis

## Visualization

Interactive network visualization available at:
```
data/graphs/amlsim_network_visualization.html
```

**Features:**
- Red nodes: Fraud/alert accounts
- Green nodes: Normal accounts
- Edge width: Transaction amount
- Hover: Full transaction details

---

**Status:** Production-ready transaction intelligence layer 🚀
