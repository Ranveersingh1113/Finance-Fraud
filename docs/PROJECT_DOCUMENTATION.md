# Finance Fraud Detection Platform - Documentation Index

## Quick Links

- [Setup Guide](SETUP_GUIDE.md) - Initial system setup
- [GPU Setup Guide](../GPU_SETUP_GUIDE.md) - GPU acceleration configuration
- [SEBI File Setup](SEBI_FILE_SETUP.md) - SEBI data processing
- [Quick Reference](../QUICK_REFERENCE.md) - Common commands and operations

## Project Structure

```
Finance Fraud/
├── src/                          # Source code
│   ├── api/                      # FastAPI endpoints
│   ├── core/                     # Core functionality
│   │   ├── device_config.py      # GPU/CPU management
│   │   ├── rag_engine.py         # Baseline RAG
│   │   ├── advanced_rag_engine.py # Advanced RAG
│   │   ├── graph_manager.py      # Graph operations
│   │   └── sebi_graph_manager.py # SEBI graph
│   ├── data/                     # Data processing
│   ├── frontend/                 # Streamlit UI
│   └── models/                   # Model registry
├── data/                         # Data storage
│   ├── chroma_db/               # Vector database
│   ├── graphs/                  # Knowledge graphs
│   ├── ieee_cis/                # Transaction data
│   └── sebi/                    # SEBI documents
├── docs/                         # Documentation
├── scripts/                      # Utility scripts
└── tests/                        # Test files
```

## Current Status

### ✅ Completed (Phase 1-3)
- RAG engine with ChromaDB
- Advanced RAG with Claude/Ollama
- SEBI data processing
- Knowledge graph foundation
- GPU acceleration

### 🚀 In Progress (Phase 4)
- SEBI Knowledge Graph construction
- IEEE-CIS transaction intelligence
- Unified GraphRAG system

## Key Features

### 1. RAG Engine
- **Baseline**: ChromaDB + MiniLM embeddings
- **Advanced**: Multi-stage retrieval + reranking
- **GPU Accelerated**: 3-4x faster processing

### 2. Knowledge Graphs
- **SEBI Graph**: Regulatory violations & entities
- **Transaction Graph**: IEEE-CIS fraud patterns
- **Unified Graph**: Cross-dataset insights

### 3. Models
- **Embeddings**: all-MiniLM-L12-v2 (GPU)
- **Reranker**: BGE-reranker-large (GPU)
- **LLM**: Claude 3.5 Haiku / Ollama Llama 3.1

## Usage Examples

### Build Knowledge Graph
```bash
python build_sebi_knowledge_graph.py
```

### Test RAG System
```bash
python test_advanced_rag.py
```

### Start API Server
```bash
python start_api.py
```

### Start Web Interface
```bash
python start_ui.py
```

## Development

### Running Tests
```bash
# All tests
pytest

# Specific test
python test_gpu_config.py
python test_sebi_graph_queries.py
```

### Code Quality
```bash
# Format code
black src/

# Lint code
flake8 src/
```

## Performance

### With GPU (RTX 3050 Ti 4GB)
- Embedding generation: ~3-4x faster
- Reranking: ~4-5x faster
- Query processing: ~3x faster
- Knowledge graph building: ~2x faster

### Resource Usage
- GPU Memory: ~2-3GB (with FP16)
- System RAM: ~4-6GB
- Storage: ~5-10GB (depends on data)

## API Endpoints

### Query
```
POST /query
{
  "query": "What are insider trading penalties?",
  "n_results": 5
}
```

### Graph Query
```
POST /graph/entity/{entity_name}/violations
GET /graph/stats
```

### System
```
GET /health
GET /stats
```

## Configuration

See `.env` file for configuration options:
- `DEVICE`: cuda/cpu/auto
- `USE_FP16`: true/false
- `EMBEDDING_MODEL`: model name
- `LLM_MODEL`: ollama model
- Data paths and API settings

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review test files for examples
3. Check GPU_SETUP_GUIDE.md for GPU issues
4. Review logs for error details

## Roadmap

### Phase 4 (Current)
- [x] SEBI Knowledge Graph (Week 1-2)
- [ ] IEEE-CIS Transaction Intelligence (Week 3-4)
- [ ] Unified GraphRAG System (Week 5-6)

### Future
- Fine-tuned embeddings (Fin-E5)
- Real-time fraud detection
- Advanced analytics dashboard
- Multi-modal document processing

