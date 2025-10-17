# Financial Intelligence Platform

A state-of-the-art, dual-audience financial intelligence platform featuring:
- **Analyst's Cockpit**: Next-generation fraud detection using GraphRAG
- **Consumer Security Suite**: AI-powered personal financial fraud prevention

## Architecture

The platform uses a modular, three-tier microservices architecture:

- **Tier 1**: Data Ingestion & Processing (real-time pipeline)
- **Tier 2**: Core Intelligence Engine (RAG and GraphRAG logic)
- **Tier 3**: Application & Presentation Layer (Analyst's Cockpit + Consumer Suite)

## Technology Stack

- **Orchestration**: Langchain / LlamaIndex
- **Vector Database**: ChromaDB (local)
- **Graph Database**: Neo4j Desktop / NetworkX
- **LLM**: Ollama with local models (Llama 3, Mistral)
- **Backend**: FastAPI (Python)
- **Frontend**: Streamlit
- **Deployment**: Streamlit Community Cloud / Hugging Face Spaces

## Project Phases

### Phase 1: Foundation & RAG Proof-of-Concept (Weeks 1-4)
- Environment setup and CI/CD
- Data ingestion prototype
- Baseline RAG pipeline with all-MiniLM-L12-v2
- Demo interface

### Phase 2: Production-Grade RAG Engine (Weeks 5-10)
- Data processing pipeline
- Core engine with full model suite
- Performance benchmarking

### Phase 3: Analyst's Cockpit (Weeks 11-15)
- Secure API gateway
- UI/UX development
- Case management features

### Phase 4: GraphRAG & Network Intelligence (Weeks 16-21)
- Graph database integration
- GraphRAG core engine
- Interactive graph visualization

### Phase 5: Production Deployment (Weeks 22-25)
- Cloud deployment
- Final testing and documentation

### Phase 6: Consumer Security Suite (Weeks 26-31)
- Public-facing application
- Document analysis tools
- Real-time scam detection

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the application:
```bash
streamlit run src/frontend/streamlit_app.py
```

## SEBI Data Integration

The platform includes integration with SEBI (Securities and Exchange Board of India) documents for Indian financial fraud detection:

- **Adjudication Orders**: Legal documents detailing enforcement actions against fraud
- **Investigation Reports**: Detailed analyses of market manipulation and insider trading
- **Press Releases**: Updates on regulatory actions and policy changes

### Getting SEBI Documents

SEBI documents must be manually downloaded and placed in the `./data/sebi/` directory:

1. **Setup directory structure**:
   ```bash
   python setup_sebi_directory.py
   ```

2. **Download documents** from SEBI website:
   - [Adjudication Orders](https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=2&ssid=9&smid=6)
   - [Investigation Reports](https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=4&ssid=38&smid=35)
   - [Press Releases](https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=6&ssid=23&smid=0)

3. **Process documents**:
   ```bash
   python test_sebi_file_processing.py
   ```

See [SEBI File Setup Guide](docs/SEBI_FILE_SETUP.md) for detailed instructions.

## Development

This project follows a modular structure:
- `src/core/` - Core intelligence engine
- `src/api/` - FastAPI backend
- `src/frontend/` - Streamlit frontend
- `src/data/` - Data processing and ingestion
- `src/models/` - AI model configurations
- `tests/` - Test suite
- `docs/` - Documentation
- `scripts/` - Utility and launcher scripts

## ✨ Phase 3 Features (NEW!)

### 🔐 API Key Authentication
- Secure API endpoints with multiple authentication keys
- Development, analyst, and custom key support
- Header-based authentication (`X-API-Key`)

### 📁 Persistent Case Management
- SQLite database with full CRUD operations
- Case creation, tracking, and deletion
- Query history per case
- Evidence storage and retrieval
- Case statistics and analytics

### 📝 AI-Powered SAR Generation
- Automated Suspicious Activity Report creation
- Comprehensive reports with:
  - Executive Summary
  - Key Findings & Evidence
  - Pattern Analysis
  - Recommendations
- Download SAR reports as text files
- Database storage with versioning

### 🔗 Enhanced Clickable Citations
- Quick citation reference links
- Expandable evidence cards with metadata
- Source attribution and tracing
- Copy citation functionality
- Link to original documents

### 📊 Advanced KPI Dashboard
- Real-time system performance metrics
- Case management statistics
- Priority distribution visualization
- Query performance analytics
- Interactive Plotly charts

## 📚 Additional Documentation

- **[PHASE3_STARTUP_GUIDE.md](PHASE3_STARTUP_GUIDE.md)** - ⭐ Complete Phase 3 startup and testing guide
- **[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Detailed phase-by-phase development roadmap
- **[PROGRESS_TRACKING.md](PROGRESS_TRACKING.md)** - Current progress and milestone tracking
- **[docs/SEBI_FILE_SETUP.md](docs/SEBI_FILE_SETUP.md)** - SEBI data integration guide
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - General setup instructions

## 🚀 Quick Launch

### Phase 3: Production-Ready Analyst Cockpit

**Step 1: Start the Advanced API Server**
```bash
# Activate virtual environment
.\financevenv\Scripts\activate

# Start API server
python start_advanced_api.py
```

**Step 2: Start the Streamlit UI (New Terminal)**
```bash
# Activate virtual environment
.\financevenv\Scripts\activate

# Start Streamlit
python start_advanced_streamlit.py
```

**Access the system:**
- **Streamlit UI:** http://localhost:8501
- **API Documentation:** http://localhost:8001/docs
- **API Health Check:** http://localhost:8001/health

**📖 For detailed startup and testing instructions, see:** [PHASE3_STARTUP_GUIDE.md](PHASE3_STARTUP_GUIDE.md)

## 🧹 Project Organization

To organize the project structure (move test files, scripts, etc.):
```powershell
.\scripts\organize_project.ps1
```

See [CLEANUP_RECOMMENDATIONS.md](CLEANUP_RECOMMENDATIONS.md) for details.
