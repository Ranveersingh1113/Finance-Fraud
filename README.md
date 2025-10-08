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

## 📚 Additional Documentation

- **[CODEBASE_ANALYSIS.md](CODEBASE_ANALYSIS.md)** - Comprehensive codebase analysis, architecture, and technical deep-dive
- **[CLEANUP_RECOMMENDATIONS.md](CLEANUP_RECOMMENDATIONS.md)** - Project cleanup and organization guide
- **[IMPLEMENTATION_ROADMAP.md](IMPLEMENTATION_ROADMAP.md)** - Detailed phase-by-phase development roadmap
- **[PROGRESS_TRACKING.md](PROGRESS_TRACKING.md)** - Current progress and milestone tracking
- **[docs/SEBI_FILE_SETUP.md](docs/SEBI_FILE_SETUP.md)** - SEBI data integration guide
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - General setup instructions

## 🚀 Quick Launch

Use the unified launcher script:

**Windows (PowerShell):**
```powershell
.\scripts\start_system.ps1
```

**Or start components individually:**
```bash
# Start Advanced API Server (Port 8001)
python start_advanced_api.py

# Start Streamlit Frontend (Port 8501)
python start_advanced_streamlit.py
```

## 🧹 Project Organization

To organize the project structure (move test files, scripts, etc.):
```powershell
.\scripts\organize_project.ps1
```

See [CLEANUP_RECOMMENDATIONS.md](CLEANUP_RECOMMENDATIONS.md) for details.
