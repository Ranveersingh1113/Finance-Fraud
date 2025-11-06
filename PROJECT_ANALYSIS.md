# Financial Fraud Detection Platform - Deep Analysis

## 📋 Executive Summary

This is a **production-ready Financial Intelligence Platform** that combines:
- **GraphRAG (Graph + RAG)**: Knowledge graphs + Retrieval Augmented Generation
- **Dual Knowledge Graphs**: SEBI regulatory data + AMLSim transaction networks
- **Advanced RAG Engine**: Fine-tuned embeddings, reranking, semantic caching
- **Full-Stack Application**: React frontend + FastAPI backend

**Status**: Phase 4 Complete - Production Ready (8.5/10)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React/Vite)                    │
│  • React 18 + TypeScript                                    │
│  • shadcn/ui components                                     │
│  • React Router, React Query                                │
│  • Port: 8080 (dev) / Static build (prod)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST API
┌───────────────────────▼─────────────────────────────────────┐
│                  Backend (FastAPI)                           │
│  • FastAPI + Uvicorn                                        │
│  • Port: 8001                                               │
│  • API Key Authentication                                   │
│  • CORS enabled                                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ Unified      │ │ Advanced    │ │ Case       │
│ GraphRAG     │ │ RAG Engine  │ │ Manager    │
│ Engine       │ │             │ │ (SQLite)   │
└───────┬──────┘ └──────┬──────┘ └────────────┘
        │               │
        │       ┌───────┴───────┐
        │       │               │
┌───────▼───────▼───────▼───────▼───────┐
│         Data Layer                     │
│  • ChromaDB (Vector Store)             │
│  • NetworkX Graphs (SEBI + AMLSim)     │
│  • SQLite (Cases)                      │
│  • Neo4j (Optional - not required)     │
└────────────────────────────────────────┘
        │
┌───────▼────────────────────────────────┐
│         Models Layer                    │
│  • Fine-tuned E5 Embeddings (768-dim)   │
│  • Ollama LLM (llama3.1:8b)            │
│  • BGE Reranker                         │
└─────────────────────────────────────────┘
```

---

## 🔧 Tech Stack

### Frontend (`prd-pathfinder-69/`)
- **Framework**: React 18.3.1 + TypeScript
- **Build Tool**: Vite 5.4.19
- **UI Library**: shadcn/ui (Radix UI components)
- **Styling**: Tailwind CSS
- **State Management**: React Query (TanStack Query)
- **Routing**: React Router DOM 6.30.1
- **Charts**: Recharts 2.15.4
- **Graph Visualization**: ReactFlow 11.11.4
- **PWA Support**: Vite PWA Plugin

### Backend (`src/`)
- **Framework**: FastAPI 0.104.1
- **ASGI Server**: Uvicorn 0.24.0
- **Language**: Python 3.11+
- **Validation**: Pydantic 2.5.0
- **Async Support**: asyncio, httpx

### Data & Storage
- **Vector DB**: ChromaDB 0.4.18 (persistent, local file-based)
- **Graph DB**: NetworkX 3.2.1 (in-memory, persisted as pickle)
- **Relational DB**: SQLite (for cases)
- **Optional**: Neo4j 5.14.1 (configured but not required)

### ML/AI Models
- **Embeddings**: Fine-tuned E5-base-v2 (768 dimensions)
  - Location: `./models/fin-e5/`
  - Base: `intfloat/e5-base-v2`
  - Trained on: 990 domain pairs (SEBI + AMLSim)
  - Performance: Recall@10 = 66.92%, NDCG@10 = 0.450
- **LLM**: Ollama (llama3.1:8b) - local inference
  - Alternative: Anthropic Claude (optional)
- **Reranker**: BGE Reranker (ms-marco-MiniLM-L-12-v2)

### Core Libraries
- **NLP**: spaCy 3.7.0, sentence-transformers 2.2.2
- **ML**: PyTorch 2.1.1, transformers 4.36.0, scikit-learn 1.4.0
- **Vector Search**: FAISS-CPU 1.7.4
- **PDF Processing**: PyPDF2, pdfplumber, pymupdf
- **Graph Processing**: python-louvain, community detection

---

## 🎯 Core Services & Components

### 1. Unified GraphRAG Engine (`src/core/unified_graphrag_engine.py`)
**Purpose**: Combines SEBI regulatory graph + AMLSim transaction graph for cross-domain intelligence

**Key Features**:
- Cross-domain pattern matching (85% confidence)
- Pre-computed fraud pattern cache (instant queries)
- Semantic caching (45% cache hit rate)
- Circuit breakers (failure recovery)
- Parallel retrieval (SEBI + AMLSim concurrently)
- Graph statistics cache (O(1) access, 50-100x faster)

**Performance Optimizations**:
- Semantic cache: 15% → 45% hit rate
- Async pattern cache: 60s → 15s startup
- Graph stats cache: 5-10s → <100ms context gathering

**Dependencies**:
- SEBIGraphManager
- AMLSimGraphManager
- AdvancedRAGEngine
- SemanticCache
- GraphStatsCache
- CircuitBreaker

### 2. Advanced RAG Engine (`src/core/advanced_rag_engine.py`)
**Purpose**: Production-grade RAG with multi-stage retrieval

**Features**:
- Query expansion (synonym + related terms)
- Document type boosting (regulations prioritized)
- Reranking with BGE reranker
- Result diversity (70% regulations, 30% cases)
- Multiple collections (SEBI, FIU, Income Tax, AMLSim)

**Collections**:
- `sebi_documents_advanced`: 24 regulations + 205 cases
- `fiu_documents`: FIU reports
- `incometax_documents`: Income tax data
- `amlsim_transactions`: Transaction documents

### 3. SEBI Graph Manager (`src/core/sebi_graph_manager.py`)
**Purpose**: Manages SEBI regulatory knowledge graph

**Graph Structure**:
- **Nodes**: 1,200+ entities (companies, persons, violations)
- **Edges**: 2,800+ relationships (COMMITTED, PENALIZED_BY, SIMILAR_TO)
- **Storage**: NetworkX graph, persisted as pickle

**Operations**:
- Entity extraction from documents
- Relationship inference
- Graph querying (find violations, entities, patterns)
- Subgraph extraction

### 4. AMLSim Graph Manager (`src/core/amlsim_graph_manager.py`)
**Purpose**: Manages transaction network graph

**Graph Structure**:
- **Nodes**: 1,500 accounts + 150 customers
- **Edges**: 45,000+ transactions (SENT_TO, RECEIVED_FROM, OWNED_BY)
- **Patterns**: Fan-out, fan-in, cycle detection

**Operations**:
- Ego network extraction (N-hop subgraphs)
- Pattern detection (fan-out, fan-in, cycles)
- Account analysis
- Transaction flow tracing

### 5. Case Manager (`src/core/case_manager.py`)
**Purpose**: Case management system

**Storage**: SQLite database (`./data/cases.db`)

**Features**:
- CRUD operations for cases
- Query tracking per case
- SAR (Suspicious Activity Report) generation
- Case statistics

### 6. API Server (`src/api/advanced_main.py`)
**Purpose**: FastAPI REST API

**Endpoints**:
- `POST /query` - Basic RAG queries
- `POST /query/unified` - Unified GraphRAG queries
- `GET /query/simple` - Simple query (no auth)
- `POST /cases` - Create case
- `GET /cases` - List cases
- `GET /cases/{id}` - Get case details
- `POST /cases/{id}/analyze` - Analyze case
- `POST /cases/{id}/sar` - Generate SAR report
- `GET /graph/account/{id}` - Get account graph
- `GET /graph/status` - Graph diagnostics
- `GET /health` - Health check
- `GET /stats` - System statistics

**Security**:
- API key authentication (X-API-Key header)
- Input validation and sanitization
- Rate limiting (slowapi)
- Audit logging

### 7. Frontend Application (`prd-pathfinder-69/src/`)
**Purpose**: React-based web interface

**Pages**:
- Dashboard (`Dashboard.tsx`)
- Cases (`Cases.tsx`, `CaseDetail.tsx`)
- Search (`SearchPage.tsx`)
- Graph View (`GraphView.tsx`)
- Alerts (`Alerts.tsx`)
- Profile (`Profile.tsx`)

**Key Hooks**:
- `useCases.ts` - Case management
- `useSearch.ts` - Search functionality
- `useStats.ts` - Statistics
- `useUser.ts` - User profile

**API Client**: `lib/api-client.ts` - HTTP client for backend

---

## 📊 Data Flow

### Query Flow (Unified GraphRAG)
```
1. User Query → Frontend
2. Frontend → POST /query/unified (with API key)
3. FastAPI → UnifiedGraphRAGEngine.unified_query()
4. Engine:
   a. Check semantic cache (45% hit rate)
   b. If miss:
      - Parallel retrieval:
        * SEBI graph query (entities, violations)
        * AMLSim graph query (patterns, accounts)
        * ChromaDB vector search (documents)
      - Cross-domain pattern matching
      - Context assembly
   c. LLM generation (Ollama)
   d. Cache result
5. Response → Frontend
6. Frontend displays: answer + evidence + graph visualization
```

### Data Ingestion Flow
```
1. Raw Documents (PDFs, CSVs) → Data Processors
2. Processing:
   - Text extraction (PyPDF2, pdfplumber)
   - Chunking (200-1000 chars)
   - Entity extraction (spaCy)
   - Embedding generation (Fine-tuned E5)
3. Storage:
   - ChromaDB: Document chunks + embeddings
   - NetworkX: Entities + relationships (graphs)
   - SQLite: Case metadata
4. Indexing complete → Ready for queries
```

---

## 🤖 Models & AI Components

### 1. Fine-tuned E5 Embeddings
- **Model**: `models/fin-e5/` (local)
- **Base**: `intfloat/e5-base-v2`
- **Dimensions**: 768
- **Training**: 990 domain pairs, 4 epochs
- **Performance**: +13% Recall@10, +26% NDCG@10 vs baseline
- **Usage**: Document embeddings, query embeddings

### 2. Ollama LLM
- **Model**: `llama3.1:8b`
- **Host**: `http://localhost:11434` (default)
- **Usage**: Answer generation from retrieved context
- **Alternative**: Anthropic Claude (if API key provided)

### 3. BGE Reranker
- **Model**: `ms-marco-MiniLM-L-12-v2`
- **Usage**: Re-rank retrieved documents for better relevance

### 4. spaCy NLP
- **Model**: `en_core_web_sm`
- **Usage**: Entity extraction, document classification

---

## 📦 Dependencies & Requirements

### System Requirements
- **Python**: 3.11+
- **Node.js**: 18+ (for frontend)
- **RAM**: 8GB+ (16GB recommended)
- **Storage**: 10-20GB (for models + data)
- **GPU**: Optional (CUDA for faster inference)

### Python Dependencies (Backend)
- FastAPI, Uvicorn
- ChromaDB, sentence-transformers
- PyTorch, transformers
- NetworkX, pandas, numpy
- spaCy, PyPDF2
- See `requirements.txt` for complete list

### Node.js Dependencies (Frontend)
- React, TypeScript
- Vite, Tailwind CSS
- React Router, React Query
- shadcn/ui components
- See `prd-pathfinder-69/package.json`

### External Services
- **Ollama**: Required (local LLM inference)
  - Default: `http://localhost:11434`
  - Can be deployed separately
- **Anthropic API**: Optional (alternative to Ollama)
- **Neo4j**: Optional (not required, can use NetworkX only)

---

## 🔄 Project Flow

### Development Flow
1. **Data Preparation**:
   - Process SEBI PDFs → chunks → embeddings
   - Process AMLSim CSVs → transaction graph
   - Build knowledge graphs

2. **Model Training** (if needed):
   - Fine-tune E5 embeddings on domain data
   - Evaluate performance

3. **Indexing**:
   - Load documents into ChromaDB
   - Build graphs (SEBI + AMLSim)
   - Pre-compute patterns

4. **API Development**:
   - FastAPI endpoints
   - Authentication
   - Error handling

5. **Frontend Development**:
   - React components
   - API integration
   - Graph visualization

### Production Flow
1. **Startup**:
   - Load models (E5 embeddings, Ollama)
   - Initialize ChromaDB collections
   - Load graphs from disk
   - Pre-compute pattern cache
   - Start FastAPI server

2. **Query Processing**:
   - Receive query
   - Check cache
   - Retrieve from graphs + vector DB
   - Generate answer
   - Return response

3. **Monitoring**:
   - Cache hit rates
   - Query performance
   - Error rates
   - Circuit breaker states

---

## 🗂️ Data Structure

### ChromaDB Collections
- **sebi_documents_advanced**: SEBI regulations + cases
- **fiu_documents**: FIU reports
- **incometax_documents**: Income tax data
- **amlsim_transactions**: Transaction documents

### Graph Files
- **SEBI Graph**: `data/graphs/sebi_graph.pkl`
- **AMLSim Graph**: `data/graphs/amlsim_graph.pkl`

### SQLite Database
- **Cases DB**: `data/cases.db`
  - Tables: cases, queries, sar_reports

### Model Files
- **E5 Embeddings**: `models/fin-e5/`
- **Clustering Models**: `data/clustering_models.pkl`

---

## 🔐 Security Features

1. **API Key Authentication**: Required for most endpoints
2. **Input Validation**: Query sanitization, length limits
3. **CORS Configuration**: Configurable origins
4. **Audit Logging**: All queries logged
5. **Rate Limiting**: SlowAPI integration
6. **Prompt Injection Protection**: Blocked patterns

---

## 📈 Performance Metrics

### Current Performance (Optimized Oct 2025)
- **Cache Hit Rate**: 45% (up from 15%)
- **Startup Time**: 15s (down from 60s)
- **Context Gathering**: <100ms (down from 5-10s)
- **Query Processing**: 2-5x faster with caching
- **Graph Queries**: O(1) with stats cache

### Resource Usage
- **GPU Memory**: 2-3GB (with FP16)
- **System RAM**: 4-6GB
- **Storage**: 5-10GB (models + data)

---

## 🚀 Deployment Considerations

### Challenges
1. **Model Size**: Fine-tuned E5 model (~400MB)
2. **Ollama Dependency**: Requires Ollama service running
3. **Data Persistence**: ChromaDB, graphs, SQLite need persistent storage
4. **Memory Requirements**: 8GB+ RAM recommended
5. **Startup Time**: 15s (acceptable but not instant)

### Opportunities
1. **Stateless API**: Can scale horizontally
2. **Caching**: Reduces load on models
3. **Optional GPU**: Works on CPU (slower but functional)
4. **Docker Support**: Can containerize easily

---

## 📝 Next Steps for Deployment

1. **Containerization**: Dockerize backend + frontend
2. **Environment Configuration**: Production .env setup
3. **Ollama Deployment**: Deploy Ollama separately or use API
4. **Database Migration**: Consider PostgreSQL for cases (optional)
5. **Monitoring**: Add logging, metrics, health checks
6. **CI/CD**: Automated deployment pipeline

---

**Last Updated**: January 2025
**Status**: Production Ready (8.5/10)
**Phase**: 4 - GraphRAG Complete

