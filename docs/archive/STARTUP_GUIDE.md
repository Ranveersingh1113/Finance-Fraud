# Quick Startup Guide

## 🚀 Starting the System

You have **3 ways** to start the Financial Fraud Detection Platform:

---

## **Method 1: PowerShell Launcher (Recommended) ⭐**

Start **both** API and UI with one command:

```powershell
cd "D:\OneDrive\Desktop\Finance Fraud"
.\scripts\start_system.ps1
```

**Features:**
- Starts API on port 8001
- Starts UI on port 8501
- Auto-detects virtual environment
- Shows help if Ollama not running
- Press Ctrl+C to stop everything

**Options:**
```powershell
# Start only API
.\scripts\start_system.ps1 -ApiOnly

# Start only UI (requires API to be running)
.\scripts\start_system.ps1 -FrontendOnly

# Show help
.\scripts\start_system.ps1 -Help
```

---

## **Method 2: Two Terminal Windows**

**Terminal 1 - API Server:**
```bash
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate
python start_api.py
```

**Terminal 2 - Streamlit UI:**
```bash
cd "D:\OneDrive\Desktop\Finance Fraud"
.\financevenv\Scripts\activate
python start_ui.py
```

---

## **Method 3: Direct Module Execution**

**Start API:**
```bash
python -m src.api.advanced_main
# OR
uvicorn src.api.advanced_main:app --host 127.0.0.1 --port 8001
```

**Start UI:**
```bash
streamlit run src/frontend/advanced_streamlit_app.py --server.port 8501
```

---

## 🔗 Access Points

Once running:

| Service | URL | Purpose |
|---------|-----|---------|
| **Streamlit UI** | http://localhost:8501 | Main analyst interface |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| **Health Check** | http://localhost:8001/health | System status |
| **API Root** | http://localhost:8001/ | Basic info |

---

## ✅ Prerequisites

1. **Virtual Environment:**
   ```bash
   .\financevenv\Scripts\activate
   ```

2. **Dependencies Installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ollama Running** (for LLM features):
   ```bash
   ollama serve
   # Then pull model:
   ollama pull llama3.1:8b
   ```

4. **Data Prepared:**
   - Knowledge graphs built (`data/graphs/`)
   - ChromaDB indexed (`data/chroma_db/`)

---

## 🔧 If Something Goes Wrong

### "Port already in use"
```bash
# Find and kill process on port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F

# Or change port in start_api.py
```

### "Module not found"
```bash
# Ensure you're in project root
cd "D:\OneDrive\Desktop\Finance Fraud"

# Activate virtual environment
.\financevenv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Ollama connection error"
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve
```

---

## 📝 Quick Reference

**Start Everything:**
```powershell
.\scripts\start_system.ps1
```

**Start API Only:**
```bash
python start_api.py
```

**Start UI Only:**
```bash
python start_ui.py
```

**Stop Everything:**
```
Press Ctrl+C in each terminal
```

---

## 🎯 Next Steps After Startup

1. Open http://localhost:8501 in browser
2. Try a test query: "What are SEBI penalties for insider trading?"
3. Check API docs: http://localhost:8001/docs
4. Test account trace: "Show transactions for account 507"

---

**For more details, see:**
- `README.md` - Full documentation
- `QUICK_REFERENCE.md` - Common commands
- `SETUP_GUIDE.md` - Initial setup
- `CODE_REVIEW_ACTION_ITEMS.md` - Current status

