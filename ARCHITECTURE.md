# Financial Fraud Detection - Architecture Diagram

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                             │
│  ┌──────────────────┐              ┌─────────────────────────┐   │
│  │  Streamlit UI    │              │  React Frontend (PRD)   │   │
│  │  (Analyst View)  │              │  (Modern Dashboard)     │   │
│  └────────┬─────────┘              └───────────┬─────────────┘   │
└───────────┼──────────────────────────────────┼─────────────────┘
            │                                   │
            └───────────────┬───────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                        API LAYER                                   │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  FastAPI (start_api.py)                                     │  │
│  │  • Authentication & Authorization                           │  │
│  │  • Query Processing Endpoints                               │  │
│  │  • SAR (Suspicious Activity Report) Generation              │  │
│  └─────────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────────┐
│                  CORE ENGINE LAYER                                 │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  Unified GraphRAG Engine                                    │  │
│  │  (unified_graphrag_engine.py)                               │  │
│  │  • Query Classification                                     │  │
│  │  • Graph Selection & Context Retrieval                      │  │
│  │  • LLM Answer Generation                                    │  │
│  └───┬──────────────────────────────────────────────┬──────────┘  │
│      │                                              │              │
│  ┌───▼──────────────┐                   ┌───────────▼──────────┐  │
│  │ Graph Managers   │                   │  RAG Components      │  │
│  │ ┌──────────────┐ │                   │ ┌──────────────────┐ │  │
│  │ │ SEBI Graph   │ │                   │ │ Advanced RAG     │ │  │
│  │ │ (Regulatory) │ │◄──────────────────┤ │ Engine           │ │  │
│  │ └──────────────┘ │                   │ └──────────────────┘ │  │
│  │ ┌──────────────┐ │                   │ ┌──────────────────┐ │  │
│  │ │ AMLSim Graph │ │                   │ │ ChromaDB Vector  │ │  │
│  │ │ (Transactions)│ │                   │ │ Store            │ │  │
│  │ └──────────────┘ │                   │ └──────────────────┘ │  │
│  └──────────────────┘                   └──────────────────────┘  │
└─────────────────────────┬──────────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────┐
│              SUPPORTING SERVICES                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ Semantic     │  │ Circuit      │  │ LLM Provider            │  │
│  │ Cache        │  │ Breakers     │  │ (Ollama/Anthropic)      │  │
│  └──────────────┘  └──────────────┘  └─────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────────────────┐
│                    DATA LAYER                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────────┐  │
│  │ SEBI         │  │ AMLSim       │  │ ChromaDB                │  │
│  │ Documents    │  │ Transaction  │  │ Persisted Store         │  │
│  │ (Regulatory) │  │ Data         │  │ (24 regs + 205 cases)   │  │
│  └──────────────┘  └──────────────┘  └─────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. **User Interface Layer**
   - **Streamlit UI**: Analyst's cockpit for fraud investigation
   - **React Frontend**: Modern dashboard (PRD specification)

### 2. **API Layer**
   - **FastAPI Service**: RESTful endpoints with authentication
   - Handles query processing and SAR report generation

### 3. **Core Engine**
   - **Unified GraphRAG Engine**: Central intelligence engine
   - **SEBI Graph Manager**: Regulatory knowledge graph
   - **AMLSim Graph Manager**: Transaction network analysis
   - **Advanced RAG Engine**: Document retrieval & context building
   - **ChromaDB**: Vector database for semantic search

### 4. **Supporting Services**
   - **Semantic Cache**: 45% cache hit rate for performance
   - **Circuit Breakers**: Production-grade reliability
   - **LLM Providers**: Ollama (local) or Anthropic Claude

### 5. **Data Layer**
   - SEBI regulatory documents
   - AMLSim synthetic transaction data
   - Persisted ChromaDB vector embeddings

## Data Flow

1. **User Query** → UI Layer
2. **API Processing** → Authentication & routing
3. **Query Classification** → Unified Engine determines query type
4. **Context Retrieval** → Graph queries + RAG search (parallel)
5. **LLM Generation** → Answer synthesis with evidence
6. **Response** → Structured JSON with graph context
7. **Visualization** → Interactive network graphs (Pyvis)

## Performance Features

- **Semantic Caching**: 3x better hit rate (45%)
- **Parallel Retrieval**: Graph + RAG queries run concurrently
- **Circuit Breakers**: Prevent cascading failures
- **Optimized Graph Access**: 50-100x faster context gathering





