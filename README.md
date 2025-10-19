# Financial Fraud Detection - GraphRAG Intelligence Platform

A production-ready financial intelligence platform combining **Knowledge Graphs** and **Retrieval Augmented Generation (RAG)** for advanced fraud detection and regulatory compliance analysis.

## 🎯 Current Status: Phase 4 Complete

✅ **Dual Knowledge Graphs**: SEBI Regulatory + AMLSim Transaction Networks  
✅ **Unified GraphRAG Engine**: Cross-domain pattern analysis  
✅ **Advanced RAG**: Query expansion, document type boosting, reranking  
✅ **Interactive Visualizations**: Pyvis network graphs  
✅ **Production API**: FastAPI with authentication  
✅ **Streamlit UI**: Analyst's Cockpit interface  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend Layer (Streamlit)                 │
│              Interactive UI + Graph Visualization            │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    API Layer (FastAPI)                       │
│         Authentication + Query Processing + SAR Generation   │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│             Unified GraphRAG Engine                          │
│   ┌─────────────────┐           ┌─────────────────┐         │
│   │ SEBI Knowledge  │           │ AMLSim Trans.   │         │
│   │ Graph (Reg.)    │◄─────────►│ Network Graph   │         │
│   └─────────────────┘           └─────────────────┘         │
│                         │                                     │
│   ┌─────────────────────▼─────────────────────┐             │
│   │  ChromaDB Vector Store (RAG)              │             │
│   │  • 24 Regulations + 205 Cases             │             │
│   │  • Transaction Documents                  │             │
│   │  • Alert Patterns                         │             │
│   └───────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- 8GB+ RAM
- Ollama (for local LLM) or Anthropic API key

### Installation

1. **Clone and setup environment:**
```bash
cd "Finance Fraud"
python -m venv financevenv
.\financevenv\Scripts\activate  # Windows
# OR
source financevenv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

2. **Configure environment:**
```bash
cp env.example .env
# Edit .env with your API keys (optional - works with Ollama by default)
```

3. **Build Knowledge Graphs:**
```bash
# Build SEBI regulatory knowledge graph
python build_sebi_knowledge_graph.py

# Build AMLSim transaction network graph
python build_amlsim_graph.py

# Index documents in ChromaDB
python index_amlsim_documents.py
```

4. **Launch the application:**

**Terminal 1 - Start API Server:**
```bash
python start_advanced_api.py
```

**Terminal 2 - Start UI:**
```bash
python start_advanced_streamlit.py
```

Access at:
- **UI:** http://localhost:8501
- **API Docs:** http://localhost:8001/docs

## 📊 Knowledge Graphs

### 1. SEBI Regulatory Graph
- **Nodes:** 1,200+ entities (companies, persons, violations)
- **Edges:** 2,800+ relationships (COMMITTED, PENALIZED_BY, SIMILAR_TO)
- **Documents:** 24 regulations + 205 adjudication orders
- **Source:** SEBI enforcement actions & regulatory documents

### 2. AMLSim Transaction Network
- **Nodes:** 1,500 accounts + 150 customers
- **Edges:** 45,000+ transactions (SENT_TO, RECEIVED_FROM, OWNED_BY)
- **Patterns:** Fan-out, fan-in, cycle detection
- **Source:** AMLSim synthetic financial data

## 🎯 Key Features

### GraphRAG Intelligence
- **Cross-Domain Queries:** Combine regulatory knowledge with transaction patterns
- **Fraud Pattern Detection:** Identify suspicious transaction structures
- **Regulatory Context:** Match patterns to SEBI violations
- **Multi-Hop Traversal:** Trace money flow across multiple accounts

### Advanced RAG
- ✅ **Query Expansion:** Automatic synonym and related term expansion
- ✅ **Document Type Boosting:** Prioritize regulations for regulatory queries (+0.5 score)
- ✅ **Reranking:** BGE reranker for improved relevance
- ✅ **Result Diversity:** Mix of regulations (70%) and cases (30%)
- ✅ **Proper Classification:** 24 regulations correctly identified

### Analyst Tools
- **Case Management:** SQLite database with full CRUD operations
- **SAR Generation:** AI-powered Suspicious Activity Reports
- **Interactive Graphs:** Pyvis network visualization
- **Citation Tracking:** Expandable evidence cards with source attribution
- **KPI Dashboard:** Real-time performance metrics

## 📁 Project Structure

```
Finance Fraud/
├── src/
│   ├── core/
│   │   ├── unified_graphrag_engine.py    # Main GraphRAG engine
│   │   ├── advanced_rag_engine.py        # Enhanced RAG with reranking
│   │   ├── sebi_graph_manager.py         # SEBI knowledge graph
│   │   └── amlsim_graph_manager.py       # Transaction network graph
│   ├── data/
│   │   ├── sebi_processor.py             # SEBI document processing
│   │   ├── sebi_file_processor.py        # Document classification
│   │   ├── amlsim_loader.py              # AMLSim data loading
│   │   └── amlsim_document_generator.py  # Transaction docs
│   ├── api/                              # FastAPI backend
│   └── frontend/                         # Streamlit UI
├── data/
│   ├── sebi/                             # 205 SEBI adjudication orders
│   ├── additional_sebi/                  # 24 regulations (PMLA, PIT, LODR, etc.)
│   ├── amlsim/                           # Transaction data (accounts, tx, alerts)
│   ├── graphs/                           # Saved knowledge graphs
│   └── chroma_db/                        # Vector database
├── build_sebi_knowledge_graph.py         # Build regulatory graph
├── build_amlsim_graph.py                 # Build transaction graph
├── index_amlsim_documents.py             # Index to ChromaDB
├── process_additional_sebi_docs.py       # Add new regulatory docs
├── rebuild_sebi_chromadb.py              # Rebuild vector DB
├── start_advanced_api.py                 # Launch API server
├── start_advanced_streamlit.py           # Launch UI
└── test_unified_graphrag.py              # Integration tests
```

## 🧪 Testing

Run the unified GraphRAG test:
```bash
python test_unified_graphrag.py
```

Expected results:
- ✅ SEBI graph queries return relevant entities
- ✅ AMLSim fraud pattern detection works
- ✅ Cross-domain pattern matching succeeds
- ✅ RAG retrieval prioritizes regulations

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **QUICK_REFERENCE.md** | Command reference and common tasks |
| **PROGRESS_TRACKING.md** | Development milestones and status |
| **RAG_CLASSIFICATION_FIX_SUMMARY.md** | Document classification implementation |
| **PHASE4_IMPLEMENTATION_PLAN.md** | GraphRAG implementation details |
| **IMPLEMENTATION_ROADMAP.md** | Full project roadmap |
| **docs/archive/** | Historical documents and session notes |

## 🔧 Maintenance

### Adding New SEBI Documents
1. Place PDFs in `data/additional_sebi/`
2. Run: `python process_additional_sebi_docs.py`
3. Verify classification in output

### Rebuilding ChromaDB
```bash
python rebuild_sebi_chromadb.py
```

This will:
- Delete existing `sebi_documents_advanced` collection
- Re-process all 229 documents
- Correctly classify 24 regulations + 205 cases
- Re-index with proper metadata

### Updating Knowledge Graphs
```bash
# Rebuild SEBI regulatory graph
python build_sebi_knowledge_graph.py

# Rebuild AMLSim transaction graph
python build_amlsim_graph.py
```

## 🎯 Use Cases

### 1. Regulatory Compliance Analysis
**Query:** "What are SEBI regulations on insider trading?"  
**Result:** PIT Regulations 2015 + related notifications + case precedents

### 2. Transaction Pattern Analysis
**Query:** "Find accounts with suspicious fan-out patterns"  
**Result:** Fraud rings with multi-hop transaction chains + risk scores

### 3. Cross-Domain Investigation
**Query:** "Are there AMLSim accounts matching money laundering violations?"  
**Result:** Transaction patterns mapped to SEBI violations with regulatory context

### 4. SAR Report Generation
**Action:** Generate Suspicious Activity Report  
**Output:** Comprehensive report with evidence, patterns, and recommendations

## 🚧 Known Limitations

1. **Document Size:** SEBI docs are single chunks (no multi-chunk splitting yet)
2. **LLM Dependency:** Requires Ollama or Anthropic API
3. **Graph Persistence:** Graphs saved as pickle files (not live database)
4. **Hybrid Search:** BM25 keyword search not yet implemented (pending TODO)

## 🤝 Contributing

This is an academic/demonstration project. For production use:
1. Implement proper authentication beyond API keys
2. Add audit logging for all queries
3. Deploy with proper security measures
4. Scale ChromaDB to production setup
5. Add multi-user support

## 📄 License

Educational/Research Use

## 🙏 Acknowledgments

- **SEBI** for regulatory documents
- **IBM AMLSim** for synthetic transaction data
- **ChromaDB, NetworkX, Pyvis** for core infrastructure

---

**Status:** ✅ Production-Ready for Demonstration  
**Last Updated:** October 2024  
**Phase:** 4 - GraphRAG Complete
