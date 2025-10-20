# Complete Setup Guide

This guide consolidates all setup instructions for the Financial Fraud Detection GraphRAG Platform.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Knowledge Graph Setup](#knowledge-graph-setup)
4. [Running the Application](#running-the-application)
5. [Adding New Data](#adding-new-data)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS:** Windows 10+, macOS 10.15+, or Linux
- **RAM:** Minimum 8GB (16GB recommended)
- **Storage:** 5GB free space
- **Python:** 3.11 or higher

### Software Dependencies
- **Ollama** (for local LLM) OR **Anthropic API Key**
- **Git** (for version control)
- **PowerShell** (Windows) or **Bash** (macOS/Linux)

### Installing Ollama (Recommended for Local LLM)

**Windows/Mac:**
1. Download from https://ollama.ai
2. Install and run
3. Pull required model:
```bash
ollama pull llama3
```

**Linux:**
```bash
curl https://ollama.ai/install.sh | sh
ollama pull llama3
```

---

## Initial Setup

### 1. Clone/Download Project
```bash
cd "Finance Fraud"
```

### 2. Create Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv financevenv
.\financevenv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv financevenv
source financevenv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs:
- FastAPI, Uvicorn (API server)
- Streamlit (UI framework)
- ChromaDB (vector database)
- NetworkX (graph library)
- spaCy, sentence-transformers (NLP)
- PyPDF2 (PDF processing)
- Pyvis (graph visualization)
- Ollama client (LLM integration)

### 4. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment (Optional)
```bash
cp env.example .env
```

Edit `.env` if using Anthropic API:
```ini
ANTHROPIC_API_KEY=your_api_key_here
USE_OLLAMA=false
```

For Ollama (default - no changes needed):
```ini
USE_OLLAMA=true
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## Knowledge Graph Setup

### SEBI Regulatory Knowledge Graph

The project comes with **229 pre-downloaded SEBI documents**:
- 205 adjudication orders (in `data/sebi/`)
- 24 regulations (in `data/additional_sebi/`)

**Build the SEBI graph:**
```bash
python scripts/setup/build_sebi_knowledge_graph.py
```

**Expected output:**
```
Processing 229 SEBI documents...
Extracting entities and relationships...
Knowledge Graph Statistics:
- Nodes: ~1,200 (Companies, Persons, Violations)
- Edges: ~2,800 (COMMITTED, PENALIZED_BY, SIMILAR_TO)
- Saved to: data/graphs/sebi_knowledge_graph.gpickle
✓ Complete!
```

**Indexing to ChromaDB:**

SEBI documents are automatically indexed when you run `build_sebi_knowledge_graph.py`. If you need to rebuild:
```bash
python rebuild_sebi_chromadb.py
```

### AMLSim Transaction Network Graph

The project includes **pre-generated AMLSim data** in `data/amlsim/`:
- `accounts.csv` - 1,500 accounts
- `tx.csv` - 45,000+ transactions
- `alerts.csv` - 800+ suspicious alerts
- `cash_tx.csv` - Cash transactions

**Build the AMLSim graph:**
```bash
python scripts/setup/build_amlsim_graph.py
```

**Expected output:**
```
Loading AMLSim data...
Building transaction network graph...
Detecting fraud patterns...
Graph Statistics:
- Account Nodes: 1,500
- Customer Nodes: 150
- Transactions: 45,000+
- Fraud Rings Detected: 12
- Saved to: data/graphs/amlsim_transaction_graph.gpickle
✓ Complete!
```

**Indexing to ChromaDB:**
```bash
python scripts/maintenance/index_amlsim_documents.py
```

This generates natural language documents from transactions and indexes them for RAG queries.

---

## Running the Application

### Start the System

You need **TWO terminal windows** (both with virtual environment activated):

**Terminal 1 - API Server:**
```bash
# Activate virtual environment
.\financevenv\Scripts\activate  # Windows
# OR
source financevenv/bin/activate  # macOS/Linux

# Start API
python start_api.py
```

Wait for:
```
INFO: Uvicorn running on http://0.0.0.0:8001
INFO: Application startup complete
```

**Terminal 2 - Streamlit UI:**
```bash
# Activate virtual environment
.\financevenv\Scripts\activate  # Windows
# OR
source financevenv/bin/activate  # macOS/Linux

# Start UI
python start_ui.py
```

Wait for:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Access Points

- **Streamlit UI:** http://localhost:8501
- **API Documentation:** http://localhost:8001/docs
- **API Health Check:** http://localhost:8001/health

### Testing the System

Run integration tests:
```bash
python test_unified_graphrag.py
```

**Expected results:**
```
✓ Test 1: SEBI Graph Query - PASSED
✓ Test 2: AMLSim Fraud Detection - PASSED
✓ Test 3: Cross-Domain Matching - PASSED
✓ Test 4: RAG Retrieval - PASSED
✓ Test 5: Unified Query - PASSED
```

---

## Adding New Data

### Adding New SEBI Documents

1. **Download PDF documents** from SEBI website
   - Regulations: https://www.sebi.gov.in/legal/regulations.html
   - Orders: https://www.sebi.gov.in/enforcement.html

2. **Place PDFs** in `data/additional_sebi/`

3. **Process documents:**
```bash
python scripts/maintenance/process_additional_sebi_docs.py
```

This will:
- Extract text from PDFs
- Classify as regulation or adjudication_order
- Extract entities and relationships
- Update knowledge graph
- Index in ChromaDB

4. **Verify classification:**
Check the output to ensure correct classification:
```
[1/10] Processing: new_regulation.pdf...
  [OK] [REG] Type: regulation, Chunks: 1
  
[2/10] Processing: new_order.pdf...
  [OK] [CASE] Type: adjudication_order, Chunks: 1
```

### Rebuilding ChromaDB

If documents are misclassified or you need to update the database:
```bash
python scripts/maintenance/rebuild_sebi_chromadb.py
```

This rebuilds the entire `sebi_documents_advanced` collection with correct classifications.

### Generating New AMLSim Data

If you want to generate fresh transaction data:
```bash
python scripts/setup/generate_amlsim_compatible_data.py
```

Then rebuild the graph:
```bash
python scripts/setup/build_amlsim_graph.py
python scripts/maintenance/index_amlsim_documents.py
```

---

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors
**Solution:** Ensure virtual environment is activated and dependencies are installed
```bash
.\financevenv\Scripts\activate
pip install -r requirements.txt
```

#### 2. "Ollama connection failed"
**Solution:** 
- Check if Ollama is running: `ollama list`
- Start Ollama service
- Verify model is downloaded: `ollama pull llama3`

#### 3. "ChromaDB collection not found"
**Solution:** Rebuild ChromaDB
```bash
python scripts/maintenance/rebuild_sebi_chromadb.py
python scripts/maintenance/index_amlsim_documents.py
```

#### 4. "Graph file not found"
**Solution:** Build knowledge graphs
```bash
python scripts/setup/build_sebi_knowledge_graph.py
python scripts/setup/build_amlsim_graph.py
```

#### 5. "Port already in use" (8001 or 8501)
**Solution:** Kill existing processes or change ports in scripts

**Windows:**
```powershell
netstat -ano | findstr :8001
taskkill /PID <process_id> /F
```

**macOS/Linux:**
```bash
lsof -ti:8001 | xargs kill -9
```

#### 6. "Memory error during graph building"
**Solution:** Reduce batch size or increase system RAM

Edit `build_sebi_knowledge_graph.py`:
```python
# Line ~80
batch_size = 10  # Reduce from 50 to 10
```

#### 7. "spaCy model not found"
**Solution:** Download the model
```bash
python -m spacy download en_core_web_sm
```

### Performance Issues

#### Slow Query Response
- **Cause:** Large graph traversal or complex RAG query
- **Solution:** Reduce `n_results` parameter or optimize graph structure

#### High Memory Usage
- **Cause:** Large embeddings model loaded in memory
- **Solution:** Use smaller model or increase system RAM

#### Slow Document Processing
- **Cause:** Large PDFs or many documents
- **Solution:** Process in batches, reduce `max_length` in spaCy

### Validation

After setup, verify everything works:

```bash
# 1. Check API health
curl http://localhost:8001/health

# 2. Check ChromaDB collections
python -c "import chromadb; client = chromadb.PersistentClient(path='data/chroma_db'); print(client.list_collections())"

# 3. Check graph files exist
ls data/graphs/
# Should show: sebi_knowledge_graph.gpickle, amlsim_transaction_graph.gpickle

# 4. Run integration test
python test_unified_graphrag.py
```

---

## Advanced Configuration

### Switching LLM Providers

**Use Anthropic Claude:**
```ini
# .env
ANTHROPIC_API_KEY=sk-ant-...
USE_OLLAMA=false
```

**Use OpenAI:**
Edit `src/core/advanced_rag_engine.py` to add OpenAI support

### Customizing Graph Structure

Edit entity extraction patterns in `src/data/entity_extractor.py`:
```python
self.entity_patterns = {
    'COMPANY': [...],
    'PERSON': [...],
    'VIOLATION': [...],
    # Add custom patterns
}
```

### Adjusting RAG Parameters

Edit `src/core/unified_graphrag_engine.py`:
```python
# Line ~430
n_results=10,  # Number of documents to retrieve
rerank_top_k=7,  # Number after reranking

# Line ~310
result['score'] = original_score + 0.5  # Regulation boost amount
```

---

## Next Steps

1. ✅ Complete initial setup
2. ✅ Build knowledge graphs
3. ✅ Launch application
4. ✅ Test with sample queries
5. 📖 Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for common operations
6. 📖 Review [RAG_CLASSIFICATION_FIX_SUMMARY.md](RAG_CLASSIFICATION_FIX_SUMMARY.md) for understanding document classification
7. 🚀 Explore the Analyst's Cockpit UI

---

**Need Help?** Check:
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Common commands
- [PROGRESS_TRACKING.md](PROGRESS_TRACKING.md) - Project status
- [PHASE4_IMPLEMENTATION_PLAN.md](PHASE4_IMPLEMENTATION_PLAN.md) - Technical details

**System Ready!** 🎉

