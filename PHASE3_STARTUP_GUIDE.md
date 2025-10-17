# Phase 3: Analyst's Cockpit - Startup Guide

## 🎯 Overview

Phase 3 implementation is complete! This guide will help you start and test the advanced analyst cockpit with all new features.

## ✅ New Features Implemented

### 1. **API Key Authentication** 🔐
- Secure API endpoints with API key validation
- Default development key: `dev-api-key`
- Additional keys: `analyst-key-001`
- All sensitive endpoints require authentication

### 2. **Persistent Case Management** 📁
- SQLite database for case storage (`./data/cases.db`)
- Create, read, update, delete cases
- Case query history tracking
- Evidence storage linked to cases
- Case statistics and analytics

### 3. **SAR Generation** 📝
- AI-powered Suspicious Activity Report generation
- Automated report pre-population using RAG
- SAR report storage and retrieval
- Download SAR reports as text files
- Comprehensive report includes: Executive Summary, Key Findings, Evidence, Recommendations

### 4. **Enhanced UI with Clickable Citations** 🔗
- Quick citation reference links
- Expandable evidence cards
- Source tracing and attribution
- Metadata display with structured fields
- Copy citations functionality
- Link to original documents when available

### 5. **Advanced KPI Dashboard** 📊
- Real-time system performance metrics
- Case management statistics
- Priority distribution visualization
- Query performance analytics
- Interactive Plotly charts
- Case-by-case analytics

## 🚀 Quick Start

### Prerequisites
1. Ensure virtual environment is activated:
   ```bash
   .\financevenv\Scripts\activate
   ```

2. Install any missing dependencies (if needed):
   ```bash
   pip install -r requirements.txt
   ```

### Step 1: Start the Advanced API Server

**Option A: Using startup script (Recommended)**
```bash
python start_advanced_api.py
```

**Option B: Direct execution**
```bash
python -m uvicorn src.api.advanced_main:app --host 127.0.0.1 --port 8001 --reload
```

**Expected Output:**
```
Project root: D:\OneDrive\Desktop\Finance Fraud
Python path: ...
SUCCESS: Advanced API imported successfully
STARTING: Advanced API Server on http://localhost:8001
INFO: Initializing Advanced Financial Intelligence Platform...
INFO: Case manager initialized
INFO: Loading SEBI data...
INFO: Adding ... SEBI chunks to advanced RAG engine...
INFO: Advanced application startup completed successfully
```

**API Server will be available at:** `http://localhost:8001`

### Step 2: Start the Advanced Streamlit UI

**Open a NEW terminal window** (keep API server running), then:

**Option A: Using startup script (Recommended)**
```bash
.\financevenv\Scripts\activate
python start_advanced_streamlit.py
```

**Option B: Direct execution**
```bash
streamlit run src/frontend/advanced_streamlit_app.py --server.port 8501
```

**Expected Output:**
```
SUCCESS: Starting Advanced Streamlit UI...
STREAMLIT: Advanced Analyst Cockpit

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

**Streamlit UI will be available at:** `http://localhost:8501`

## 🧪 Testing the System

### Test 1: System Health Check

1. Open browser to `http://localhost:8501`
2. Check the **🔧 System Status** section at the top
3. Verify all components show as green/active:
   - ✅ Advanced API Connected
   - 🦙 Ollama Llama 3.1 8B (or ⚠️ if not running)
   - 🎯 BGE Reranker
   - 🧠 all-MiniLM-L12-v2

### Test 2: Case Management

1. Navigate to **📁 Case Management** in sidebar
2. Click **🆕 Create New Case**
3. Fill in case details:
   - Case ID: `TEST_CASE_001`
   - Description: "Testing case management system"
   - Priority: "high"
   - Analyst: "Your Name"
   - Tags: "test, phase3"
4. Click **Create Case**
5. Verify case appears in the **📋 Active Cases** list
6. Select the case and verify all details are displayed

### Test 3: Intelligence Search

1. Navigate to **🔍 Intelligence Search**
2. Enter a test query:
   ```
   What are common patterns in insider trading violations?
   ```
3. Click **🧠 Intelligent Search**
4. Wait for processing (10-30 seconds depending on Ollama)
5. Verify you see:
   - **📝 Generated Analysis** - AI-generated answer
   - **📚 Supporting Evidence & Citations** - Clickable evidence cards
   - **Quick Citation Links** - [1], [2], [3], etc.
6. Click on evidence cards to expand and explore:
   - Source attribution
   - Document content
   - Metadata
   - Citation buttons

### Test 4: SAR Generation

1. Ensure you have a case selected (from Test 2)
2. Navigate to **📝 SAR Generation**
3. Verify case summary is displayed
4. Click **🤖 Generate SAR with AI**
5. Wait for SAR generation (30-60 seconds)
6. Verify comprehensive SAR report is generated with:
   - Executive Summary
   - Key Findings
   - Supporting Evidence
   - Recommendations
7. Click **💾 Download SAR Report** to download

### Test 5: Analytics Dashboard

1. Navigate to **📊 Analytics**
2. Verify the following sections are displayed:
   - **🎯 System Performance Metrics** - Document counts, case counts
   - **📁 Case Management Metrics** - Active/closed cases, queries
   - **⚡ Case Priority Distribution** - Pie chart visualization
   - **📈 Query Performance Analytics** - Time trends, confidence charts
   - **📋 Recent Query History** - Query table
   - **📁 Case Analytics** - Case details table

### Test 6: API Direct Access (Optional)

Using a tool like `curl` or Postman:

**Health Check:**
```bash
curl http://localhost:8001/health
```

**Create Case (with API key):**
```bash
curl -X POST http://localhost:8001/cases \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "case_id": "API_TEST_001",
    "description": "Testing API directly",
    "priority": "medium",
    "analyst": "API Tester",
    "tags": ["api", "test"]
  }'
```

**Query RAG Engine:**
```bash
curl -X POST http://localhost:8001/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-api-key" \
  -d '{
    "query": "What are the penalties for market manipulation?",
    "n_results": 5,
    "include_metadata": true
  }'
```

## 📊 API Endpoints Reference

### Public Endpoints (No Authentication)
- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /stats` - System statistics

### Authenticated Endpoints (Require X-API-Key header)
- `POST /query` - RAG query
- `GET /query/simple` - Simple query
- `POST /cases` - Create case
- `GET /cases` - List all cases
- `GET /cases/{case_id}` - Get case details
- `DELETE /cases/{case_id}` - Delete case
- `POST /cases/{case_id}/analyze` - Analyze case
- `POST /cases/{case_id}/sar` - Generate SAR
- `GET /cases/{case_id}/sar` - Get SAR reports

## 🔑 API Keys

Default API keys configured:
- `dev-api-key` - Development/testing key
- `analyst-key-001` - Analyst access key
- Value from `API_KEY` in `.env` file

To add more keys, edit `src/api/advanced_main.py`:
```python
VALID_API_KEYS = {
    settings.api_key,
    "dev-api-key",
    "analyst-key-001",
    "your-new-key-here"  # Add your key
}
```

## 📁 Database Files

### Case Database
- **Location:** `./data/cases.db`
- **Type:** SQLite
- **Tables:**
  - `cases` - Case information
  - `case_queries` - Query history
  - `query_evidence` - Evidence storage
  - `sar_reports` - SAR reports

### Vector Database
- **Location:** `./data/chroma_db/`
- **Type:** ChromaDB (Persistent)
- **Collections:**
  - `transactions_advanced` - Transaction data
  - `sebi_documents_advanced` - SEBI documents

## 🐛 Troubleshooting

### API Server Won't Start

**Issue:** Import errors or module not found
**Solution:**
```bash
# Ensure you're in the project root
cd "D:\OneDrive\Desktop\Finance Fraud"

# Activate virtual environment
.\financevenv\Scripts\activate

# Verify installation
python -c "import fastapi; print('FastAPI OK')"
python -c "import chromadb; print('ChromaDB OK')"
```

### Ollama Not Available

**Issue:** Ollama LLM shows as unavailable
**Solution:**
1. Check if Ollama is installed and running
2. Start Ollama service
3. Pull the model: `ollama pull llama3.1:8b`
4. Restart the API server

**Fallback:** System will work with fallback responses if Ollama is unavailable

### Streamlit Connection Error

**Issue:** Cannot connect to Advanced API Server
**Solution:**
1. Verify API server is running on port 8001
2. Check browser console for errors
3. Verify API key in `advanced_streamlit_app.py` matches server configuration

### Database Locked Error

**Issue:** SQLite database locked
**Solution:**
1. Close all connections to the database
2. Restart the API server
3. If persistent, delete `./data/cases.db` (will lose case data)

### SEBI Data Not Found

**Issue:** Warning about no SEBI data
**Solution:**
```bash
# Run the SEBI processing pipeline
python test_complete_sebi_pipeline.py
```

## 📈 Performance Expectations

- **Query Processing:** 0.2-0.5 seconds (with Ollama)
- **SAR Generation:** 30-60 seconds
- **Case Creation:** < 0.1 seconds
- **Dashboard Load:** 1-2 seconds

## 🎯 Next Steps

Phase 3 is complete! Ready to move to:
- **Phase 4:** GraphRAG & Network Intelligence
- **Phase 5:** Production Deployment
- **Phase 6:** Consumer Security Suite

## 📝 Notes

- The system uses **Ollama with Llama 3.1 8B** as the primary LLM
- **Claude API** is optional (for premium quality)
- **BGE Reranker** improves search relevance
- All case data persists in SQLite
- All query history is tracked and stored
- SAR reports can be regenerated from case data

## 🎉 Success Indicators

You'll know Phase 3 is working when:
1. ✅ API server starts without errors
2. ✅ Streamlit UI loads and connects to API
3. ✅ You can create and manage cases
4. ✅ Queries return AI-generated answers with evidence
5. ✅ SAR reports generate successfully
6. ✅ Analytics dashboard shows real-time statistics
7. ✅ Citations are clickable and traceable
8. ✅ Case data persists across restarts

