# Phase 4: GraphRAG & Network Intelligence - Implementation Plan

**Start Date:** October 17, 2025  
**Target Completion:** December 13, 2025 (8 weeks)  
**Status:** 🚀 IN PROGRESS

---

## 🎯 Vision: Complete Platform with AMLSim Transaction Network

### What We're Building:
```
Dual GraphRAG System:
├─ SEBI Regulatory Intelligence
│  └─ Entity graph: Companies → Violations → Regulators
├─ AMLSim Transaction Network Intelligence
│  ├─ Account → Transaction → Account relationships
│  ├─ Money laundering pattern detection
│  └─ Network graph: Accounts → Transactions → Alert Types
└─ Unified Cross-Domain Analysis
   ├─ Query both knowledge bases (SEBI + AMLSim)
   ├─ Money laundering ring detection
   └─ Interactive visualization
```

---

## 📋 Week-by-Week Implementation

### ✅ Week 0: Setup & Preparation (Current Week)

**Dependencies to Install:**
```bash
# Graph processing
pip install networkx pyvis

# NLP for entity extraction
pip install spacy
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_lg

# Graph visualization
pip install plotly kaleido

# Additional utilities
pip install python-louvain community
```

**Files to Create:**
- [x] `src/core/graph_manager.py` - Base graph management
- [x] `src/core/sebi_graph_manager.py` - SEBI knowledge graph
- [x] `src/core/transaction_graph_manager.py` - Transaction network graph
- [x] `src/data/entity_extractor.py` - NLP entity extraction
- [x] `src/data/transaction_document_generator.py` - Convert transactions to docs
- [x] `src/core/unified_graphrag_engine.py` - Combined system

---

### 🔧 Week 1-2: SEBI Knowledge Graph

**Goal:** Extract entities from 205 SEBI documents and build regulatory graph

#### Tasks:
- [ ] Set up spaCy NLP pipeline
- [ ] Create entity extraction rules for financial domain
- [ ] Extract entities: Companies, People, Violations, Regulators
- [ ] Extract relationships: COMMITTED, PENALIZED_BY, CITED_IN
- [ ] Build SEBI knowledge graph with NetworkX
- [ ] Implement graph query functions
- [ ] Test SEBI graph queries
- [ ] Save graph persistence (pickle/GraphML)

#### Expected Output:
```
SEBI Graph Statistics:
- Nodes: ~500 (entities from 205 documents)
- Edges: ~1,000 (relationships)
- Node Types: Entity, Violation, Regulator, Document
- Query Examples:
  * "What violations did ABC Corp commit?"
  * "Show all entities penalized by SEBI"
  * "Find similar cases to XYZ"
```

---

### 🔧 Week 3-4: AMLSim Transaction Network Intelligence

**Goal:** Integrate AMLSim data and build transaction network graph for money laundering detection

#### Part A: AMLSim Data Understanding (Week 3)
- [ ] Research AMLSim data structure and schema
- [ ] Understand account, transaction, and alert types
- [ ] Map AMLSim relationships to graph schema
- [ ] Identify money laundering patterns in AMLSim
- [ ] Design AMLSim graph schema (Account → Transaction → Account)
- [ ] Plan alert type integration

#### Part B: AMLSim Data Loading & Processing (Week 3)
- [ ] Create `AMLSimDataLoader` class
- [ ] Load AMLSim transaction data (accounts.csv, transactions.csv, alerts.csv)
- [ ] Parse account relationships and transaction flows
- [ ] Extract alert patterns and typologies
- [ ] Create transaction description templates
- [ ] Generate natural language documents from AMLSim data

#### Part C: AMLSim Transaction Network Graph (Week 4)
- [ ] Create `AMLSimGraphManager` class
- [ ] Build Account nodes with properties (account_id, balance, type)
- [ ] Build Transaction nodes with properties (amount, date, pattern)
- [ ] Build Alert nodes for suspicious patterns
- [ ] Create SENT_TO relationships (Account → Account)
- [ ] Create TRIGGERED relationships (Transaction → Alert)
- [ ] Implement money laundering pattern detection
- [ ] Detect layering, structuring, and fan-in/fan-out patterns
- [ ] Test graph queries

#### Expected Output:
```
AMLSim Transaction Intelligence:
- Transaction Graph:
  * Nodes: Account nodes + Transaction nodes + Alert nodes
  * Edges: SENT_TO, RECEIVED_FROM, TRIGGERED
  * Properties: alert_type, transaction_pattern, risk_score
- Money Laundering Patterns Detected:
  * Fan-out (single account → multiple accounts)
  * Fan-in (multiple accounts → single account)
  * Cycle (circular transactions)
  * Layering chains
- Documents: Natural language transaction descriptions indexed in ChromaDB
```

---

### 🔧 Week 5-6: Unified GraphRAG & Visualization

**Goal:** Combine SEBI + AMLSim into unified system with visualization

#### Part A: Unified GraphRAG Engine (Week 5)
- [ ] Create `UnifiedGraphRAGEngine` class
- [ ] Implement dual graph traversal
- [ ] Combine SEBI + transaction contexts
- [ ] Enhanced RAG with graph intelligence
- [ ] Cross-domain query capabilities
- [ ] Test unified queries

#### Part B: API Integration (Week 5)
- [ ] Add GraphRAG endpoints to FastAPI
- [ ] Create graph query endpoints
- [ ] Add fraud ring detection endpoint
- [ ] Add visualization data endpoints
- [ ] Update case management with graph links
- [ ] Test API integration

#### Part C: Interactive Visualization (Week 6)
- [ ] Create Pyvis visualization components
- [ ] SEBI regulatory network view
- [ ] Transaction fraud ring network view
- [ ] Interactive filters and exploration
- [ ] Integrate into Streamlit UI
- [ ] Add graph view to analyst cockpit
- [ ] Color-code by risk level

#### Part D: Complete Integration (Week 6)
- [ ] Link cases to graph entities
- [ ] Enhanced SAR generation with graph insights
- [ ] Update analytics dashboard
- [ ] Complete documentation
- [ ] End-to-end testing

#### Expected Output:
```
Complete GraphRAG Platform:
- Dual knowledge graphs (SEBI + AMLSim)
- Unified query system
- Interactive visualizations
- Money laundering pattern detection
- Cross-domain intelligence (Regulatory + Transactional)
- Production-ready system
```

---

## 🏗️ File Structure

```
src/
├── core/
│   ├── graph_manager.py               ✅ CREATED - Base graph operations
│   ├── sebi_graph_manager.py          ✅ CREATED - SEBI knowledge graph
│   ├── amlsim_graph_manager.py        ⏳ NEW - AMLSim transaction network
│   ├── unified_graphrag_engine.py     ⏳ NEW - Combined system
│   ├── advanced_rag_engine.py         ⏳ ENHANCE - Add graph integration
│   └── case_manager.py                ⏳ ENHANCE - Link to graphs
│
├── data/
│   ├── entity_extractor.py            ✅ CREATED - NLP entity extraction
│   ├── amlsim_loader.py               ⏳ NEW - AMLSim data loading
│   ├── amlsim_document_generator.py   ⏳ NEW - Transaction → docs
│   ├── ingestion.py                   (existing - keep for reference)
│   └── sebi_processor.py              (existing)
│
├── frontend/
│   └── advanced_streamlit_app.py      ⏳ ENHANCE - Add graph view
│
└── api/
    └── advanced_main.py                ⏳ ENHANCE - Add graph endpoints

data/
├── graphs/                             ✅ CREATED
│   ├── sebi_knowledge_graph.gpickle   ✅ Built (20K nodes)
│   ├── amlsim_transaction_graph.gpickle ⏳ To be built
│   └── *.json                          ✅ Export formats
├── amlsim/                             ⏳ NEW - AMLSim data directory
└── (existing directories)
```

---

## 🎯 Success Criteria

### Functional Requirements
- [x] Phase 4 setup complete
- [ ] SEBI graph with 500+ entities
- [ ] Transaction graph with 50K+ nodes
- [ ] V-feature clusters with fraud rates
- [ ] 500K+ transaction documents indexed
- [ ] Fraud ring detection working
- [ ] Unified queries functional
- [ ] Interactive visualization in Streamlit
- [ ] All tests passing

### Performance Requirements
- [ ] Entity extraction: <1s per document
- [ ] Graph building: <15 minutes total
- [ ] Graph query: <0.5s for 2-hop traversal
- [ ] Visualization: <3s to render
- [ ] Unified GraphRAG query: <3s total

### Quality Requirements
- [ ] Entity extraction precision >85%
- [ ] Relationship extraction precision >80%
- [ ] V-clustering meaningful (validate fraud rates)
- [ ] Graph queries return relevant results
- [ ] Visualizations are clear and interactive

---

## 📊 Progress Tracking

| Week | Focus | Status | Progress |
|------|-------|--------|----------|
| 0 | Setup | 🚀 In Progress | 10% |
| 1-2 | SEBI Graph | ⏳ Pending | 0% |
| 3-4 | IEEE-CIS | ⏳ Pending | 0% |
| 5-6 | Unified System | ⏳ Pending | 0% |

**Overall Phase 4 Progress: 10%**

---

## 🚀 Next Immediate Steps

### Today (October 17, 2025):
1. ✅ Create implementation plan (this document)
2. ⏳ Install dependencies
3. ⏳ Create base `graph_manager.py`
4. ⏳ Set up entity extraction framework
5. ⏳ Test basic graph operations

### This Week:
1. Complete setup
2. Begin SEBI entity extraction
3. Create initial graph structure
4. Test on sample SEBI documents

---

## 💡 Key Design Decisions

### Graph Database: NetworkX ✅
- **Why:** Python-native, easy to integrate, good for prototyping
- **Persistence:** Pickle/GraphML for save/load
- **Migration Path:** Can move to Neo4j later if needed

### Entity Extraction: Hybrid Approach ✅
- **spaCy NER:** Baseline entity detection
- **Custom Rules:** Financial domain patterns
- **LLM Validation:** Use Ollama for ambiguous cases

### V-Feature Strategy: Clustering ✅
- **Method:** K-Means on V1-V339 features
- **Output:** 8-10 behavioral clusters with names
- **Integration:** Add to documents and graph properties

---

## 📚 References

- NetworkX Documentation: https://networkx.org/
- spaCy NER Guide: https://spacy.io/usage/linguistic-features
- Pyvis Interactive Graphs: https://pyvis.readthedocs.io/
- Phase 4 Detailed Plan: [PHASE4_IEEE_CIS_INTEGRATION.md](PHASE4_IEEE_CIS_INTEGRATION.md)

---

**Status:** Ready to implement!  
**Next:** Install dependencies and create base graph infrastructure

