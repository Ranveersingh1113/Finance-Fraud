# Financial Intelligence Platform - Quick Reference

## 🚀 Startup Commands

### Start the System (2 Terminals Required)

**Terminal 1 - API Server:**
```bash
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate
python start_advanced_api.py
```

**Terminal 2 - Streamlit UI:**
```bash
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate
python start_advanced_streamlit.py
```

### Access Points
- **UI:** http://localhost:8501
- **API Docs:** http://localhost:8001/docs
- **Health:** http://localhost:8001/health

---

## 🔑 API Keys

Default keys for development:
- `dev-api-key`
- `analyst-key-001`

**Usage in Streamlit:** Configured automatically

**Usage in API calls:**
```bash
curl -H "X-API-Key: dev-api-key" http://localhost:8001/cases
```

---

## 📁 Key Files & Locations

### Databases
- **Cases:** `./data/cases.db` (SQLite)
- **Vectors:** `./data/chroma_db/` (ChromaDB)

### Configuration
- **Environment:** `.env` (create from `env.example`)
- **Settings:** `src/core/config.py`

### Source Data
- **SEBI Docs:** `./data/sebi/*.pdf`
- **Transactions:** `./data/ieee_cis/*.csv`

---

## 🎯 Common Workflows

### Create a Case
1. Navigate to **📁 Case Management**
2. Click **🆕 Create New Case**
3. Fill in details → **Create Case**

### Run Investigation Query
1. Navigate to **🔍 Intelligence Search**
2. Enter query → **🧠 Intelligent Search**
3. Explore evidence with clickable citations

### Generate SAR Report
1. Select a case in **📁 Case Management**
2. Navigate to **📝 SAR Generation**
3. Click **🤖 Generate SAR with AI**
4. Download report

### View Analytics
1. Navigate to **📊 Analytics**
2. View real-time metrics and charts

---

## 🔧 Troubleshooting

### API Won't Start
```bash
# Check if port 8001 is in use
netstat -ano | findstr :8001

# Reinstall dependencies
pip install -r requirements.txt
```

### Streamlit Connection Error
- Verify API is running on port 8001
- Check API health: http://localhost:8001/health

### Ollama Not Available
```bash
# Install Ollama from ollama.ai
# Pull the model
ollama pull llama3.1:8b

# Verify it's running
ollama list
```

### No SEBI Data
```bash
# Process SEBI documents
python test_complete_sebi_pipeline.py
```

---

## 📊 Database Schema

### Cases Table
- `case_id` (PK)
- `description`
- `priority` (low/medium/high/critical)
- `analyst`
- `status` (active/closed)
- `tags` (JSON)
- `created_at`, `updated_at`

### Case Queries Table
- `id` (PK, auto-increment)
- `case_id` (FK)
- `query`, `answer`
- `confidence_score`
- `query_type`
- `timestamp`

### Query Evidence Table
- `id` (PK)
- `query_id` (FK)
- `case_id` (FK)
- `rank`, `score`
- `document`, `source`
- `metadata` (JSON)

### SAR Reports Table
- `id` (PK)
- `case_id` (FK)
- `report_content`
- `generated_at`
- `analyst`
- `status` (draft/final/submitted)

---

## 🌐 API Endpoints Quick Reference

### Public
```
GET  /              - Root
GET  /health        - Health check
GET  /stats         - Statistics
```

### Authenticated (requires X-API-Key)
```
POST   /query                   - RAG query
POST   /cases                   - Create case
GET    /cases                   - List cases
GET    /cases/{id}              - Get case
DELETE /cases/{id}              - Delete case
POST   /cases/{id}/analyze      - Analyze case
POST   /cases/{id}/sar          - Generate SAR
GET    /cases/{id}/sar          - Get SARs
```

---

## 📖 Documentation Index

| Document | Purpose |
|----------|---------|
| **PHASE3_STARTUP_GUIDE.md** | Complete startup & testing guide |
| **PHASE3_COMPLETION_SUMMARY.md** | What was built in Phase 3 |
| **PROGRESS_TRACKING.md** | Overall project progress |
| **IMPLEMENTATION_ROADMAP.md** | All 6 phases roadmap |
| **README.md** | Project overview |
| **QUICK_REFERENCE.md** | This document |

---

## 💡 Tips & Best Practices

### For Analysts
1. **Create cases for investigations** to track all queries
2. **Use descriptive tags** for easy filtering
3. **Review evidence citations** for source verification
4. **Generate SARs early** for draft review
5. **Check analytics** for performance insights

### For Developers
1. **Always activate venv** before running commands
2. **Check API health** before debugging UI issues
3. **Use API docs** at `/docs` for testing
4. **Review logs** in terminal for errors
5. **Backup `cases.db`** before major changes

### Query Writing
- Be specific: "What are the penalties for insider trading in SEBI cases?"
- Use complete questions: "How does SEBI handle market manipulation?"
- Reference specific entities: "What violations were found in XYZ company?"

---

## 🎯 Phase Status

- **Phase 1:** ✅ Complete (Foundation & RAG PoC)
- **Phase 2:** ✅ Complete (Production RAG Engine)
- **Phase 3:** ✅ Complete (Analyst's Cockpit)
- **Phase 4:** 📋 Next (GraphRAG & Network Intelligence)
- **Phase 5:** 📋 Future (Production Deployment)
- **Phase 6:** 📋 Future (Consumer Security Suite)

**Overall Progress: 50% Complete**

---

## 🆘 Getting Help

### Check Logs
- **API:** Terminal 1 (where you started API)
- **Streamlit:** Terminal 2 (where you started UI)

### Common Error Messages

**"Case manager not initialized"**
→ API server didn't start properly, restart it

**"API Error: Connection refused"**
→ API server not running, start it first

**"Invalid or missing API key"**
→ Check API key in headers or Streamlit config

**"No such table: cases"**
→ Database not initialized, restart API to create tables

---

## 🔄 Update & Maintenance

### Update Dependencies
```bash
pip install --upgrade -r requirements.txt
```

### Reset Case Database
```bash
# Backup first!
copy data\cases.db data\cases.db.backup

# Delete database (will be recreated on API start)
del data\cases.db
```

### Clear ChromaDB (Vector Database)
```bash
# Backup first!
# Then delete the directory
rmdir /s data\chroma_db

# Rerun data processing
python test_complete_sebi_pipeline.py
```

---

## 📞 Quick Commands Cheat Sheet

```bash
# Activate environment
.\financevenv\Scripts\activate

# Start API
python start_advanced_api.py

# Start UI (new terminal)
python start_advanced_streamlit.py

# Process SEBI data
python test_complete_sebi_pipeline.py

# Test RAG engine
python test_advanced_rag.py

# Test API
python test_advanced_api.py

# Check Ollama models
ollama list

# Pull Llama model
ollama pull llama3.1:8b
```

---

**Last Updated:** October 16, 2025
**Version:** Phase 3 Complete
**Status:** Production Ready


