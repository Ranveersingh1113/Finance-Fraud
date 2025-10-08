# Financial Intelligence Platform - Setup Guide

## Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (optional, for version control)

### 2. Installation

1. **Clone or download the project:**
   ```bash
   # If using git
   git clone <repository-url>
   cd "Finance Fraud"
   
   # Or simply navigate to the project directory
   cd "C:\Users\ricky\OneDrive\Desktop\Finance Fraud"
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

1. **Copy environment template:**
   ```bash
   copy env.example .env
   ```

2. **Edit configuration (optional):**
   - Open `.env` file
   - Modify settings as needed
   - Default settings work for local development

### 4. Run the Demo

**Option 1: Automated Demo (Recommended)**
```bash
python run_demo.py
```

This will start both the backend API and frontend UI automatically.

**Option 2: Manual Setup**

1. **Start the backend API:**
   ```bash
   python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **In a new terminal, start the frontend:**
   ```bash
   streamlit run src/frontend/streamlit_app.py --server.port 8501
   ```

### 5. Access the Application

- **Frontend UI:** http://localhost:8501
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Project Structure

```
Finance Fraud/
├── src/
│   ├── core/           # Core intelligence engine
│   ├── api/            # FastAPI backend
│   ├── frontend/       # Streamlit frontend
│   ├── data/           # Data processing
│   └── models/         # AI model configurations
├── tests/              # Test suite
├── docs/               # Documentation
├── data/               # Data storage
│   ├── ieee_cis/       # IEEE-CIS transaction data
│   ├── sebi/           # SEBI orders data
│   └── chroma_db/      # Vector database
├── requirements.txt    # Python dependencies
├── run_demo.py         # Demo startup script
└── README.md           # Project overview
```

## Features (Phase 1)

### ✅ Implemented
- **Semantic Search**: Natural language queries across financial data
- **Data Ingestion**: IEEE-CIS transactions and SEBI orders
- **Vector Database**: ChromaDB for efficient similarity search
- **REST API**: FastAPI backend with comprehensive endpoints
- **Web Interface**: Streamlit frontend with analytics dashboard
- **Sample Data**: Auto-generated datasets for demonstration

### 🔍 Search Capabilities
- Search transaction data by natural language
- Search SEBI orders and violations
- Filter by collection (transactions, SEBI, or all)
- Configurable result count
- Similarity scoring

### 📊 Analytics
- Database statistics dashboard
- Document distribution charts
- Real-time search results
- Sample query suggestions

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Change ports in `.env` file
   - Kill existing processes using the ports

2. **Dependencies not found:**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **ChromaDB errors:**
   - Delete `data/chroma_db/` folder
   - Restart the application

4. **Memory issues:**
   - Reduce sample data size in `src/data/ingestion.py`
   - Use smaller embedding models

### Getting Help

1. Check the logs in the terminal
2. Visit the API documentation at http://localhost:8000/docs
3. Review the test suite: `pytest tests/`

## Next Steps

This is Phase 1 of the Financial Intelligence Platform. Future phases will include:

- **Phase 2**: Production-grade RAG with fine-tuned models
- **Phase 3**: Advanced UI/UX and case management
- **Phase 4**: GraphRAG and network intelligence
- **Phase 5**: Production deployment
- **Phase 6**: Consumer security suite

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Adding New Data
1. Place CSV files in `data/ieee_cis/` or `data/sebi/`
2. Restart the application
3. Data will be automatically indexed

## Support

For questions or issues, please refer to the project documentation or create an issue in the repository.
