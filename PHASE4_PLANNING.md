# Phase 4: GraphRAG & Network Intelligence - Planning Document

## 📍 Current Position Verification

### ✅ Completed Phases

| Phase | Status | Completion Date | Key Deliverables |
|-------|--------|----------------|------------------|
| **Phase 1** | ✅ Complete | Sep 2025 | Foundation, RAG PoC, ChromaDB, Basic UI |
| **Phase 2** | ✅ Complete | Sep 2025 | Production RAG, Ollama, BGE Reranker, Multi-stage retrieval |
| **Phase 3** | ✅ Complete | Oct 16, 2025 | Case Management, SAR Generation, API Auth, Enhanced UI |

**Total Progress:** 3/6 Phases = **50% Complete** ✅

---

## 🎯 Phase 4 Overview (From Implementation Roadmap)

**Goal:** To implement the platform's key differentiator: relationship-aware intelligence using a knowledge graph.

**Timeline:** Weeks 16-21 (estimated 4-6 weeks for implementation)

**Deliverable:** A locally runnable GraphRAG system capable of answering complex, multi-hop queries and visualizing financial networks.

---

## 📋 Phase 4 Epics Breakdown

### Epic 1: Graph Database Integration

**From Roadmap:**
- [ ] Set up and configure Neo4j Desktop OR use NetworkX library
- [ ] Design graph schema (nodes: Customer, Account, Device; edges: Owns, Used, Transferred_To)

**Financial Fraud Context Schema:**
```
Nodes:
- Entity (Companies, Individuals)
- Case (Investigation cases from our system)
- Document (SEBI orders, reports)
- Transaction (Financial transactions)
- Violation (Types of fraud/violations)
- Regulator (SEBI, RBI, etc.)

Edges/Relationships:
- COMMITTED (Entity → Violation)
- INVOLVED_IN (Entity → Case)
- CITED_IN (Entity → Document)
- TRANSACTED_WITH (Entity → Entity)
- PENALIZED_BY (Entity → Regulator)
- SIMILAR_TO (Violation → Violation)
- REFERENCES (Document → Document)
```

**Decision Point:**
- **Neo4j Desktop:** Full-featured graph database, better for production
- **NetworkX:** Python library, easier for prototyping, in-memory

**Recommendation:** Start with NetworkX for rapid prototyping, migrate to Neo4j if needed.

---

### Epic 2: Graph ETL Pipeline

**From Roadmap:**
- [ ] Enhance data processing to include Entity and Relationship Extraction (NLP)
- [ ] Write logic to populate graph database in real-time

**Tasks:**
1. **Entity Extraction from SEBI Documents**
   - Extract company names, person names, regulators
   - Extract violation types, penalty amounts
   - Extract dates, locations, case numbers

2. **Relationship Extraction**
   - Parse "X committed insider trading" → (X)-[COMMITTED]->(insider_trading)
   - Parse "SEBI penalized Y" → (Y)-[PENALIZED_BY]->(SEBI)
   - Parse "Similar to case Z" → (current_case)-[SIMILAR_TO]->(Z)

3. **Graph Population**
   - Create nodes for each entity
   - Create edges for each relationship
   - Update graph as new documents are processed

**NLP Tools Needed:**
- spaCy for Named Entity Recognition (NER)
- Custom rules for financial domain entities
- Relationship extraction patterns

---

### Epic 3: GraphRAG Core Engine Upgrade

**From Roadmap:**
- [ ] Update RAG retrieval logic to perform multi-hop graph traversals before querying vector DB

**Current RAG Flow:**
```
User Query → Vector Search → Top-K Documents → Rerank → Generate Answer
```

**Enhanced GraphRAG Flow:**
```
User Query 
    ↓
Extract Entities (NER)
    ↓
Graph Traversal (find related entities, cases, violations)
    ↓
Expanded Context (entities + relationships)
    ↓
Vector Search (enhanced query with graph context)
    ↓
Top-K Documents + Graph Context
    ↓
Rerank
    ↓
Generate Answer (with graph insights)
```

**Example:**
- Query: "What violations has ABC Corp been involved in?"
- Graph finds: ABC Corp → [COMMITTED] → Insider Trading
- Graph finds: ABC Corp → [SIMILAR_TO] → XYZ Corp
- Graph finds: XYZ Corp → [PENALIZED_BY] → SEBI (₹50L)
- RAG then searches with enriched context
- Answer includes: "ABC Corp committed insider trading, similar pattern to XYZ Corp which was penalized ₹50L by SEBI"

---

### Epic 4: Interactive Graph Visualization

**From Roadmap:**
- [ ] Develop UI component for visualizing entity connections
- [ ] Use Pyvis for NetworkX or built-in Neo4j visualization

**Visualization Features:**
1. **Entity Network View**
   - Nodes colored by type (Entity, Violation, Document)
   - Edges labeled with relationship type
   - Interactive: click to explore

2. **Case Network View**
   - Show all entities involved in a specific case
   - Show relationships between entities
   - Highlight fraud patterns

3. **Violation Pattern View**
   - Show common patterns across cases
   - Cluster similar violations
   - Identify repeat offenders

**Tools:**
- Pyvis for NetworkX (generates HTML visualizations)
- Streamlit component integration
- Interactive filters (node type, relationship type, time range)

---

## 🛠️ Technical Implementation Plan

### Phase 4.1: Graph Database Setup (Week 1)

**Tasks:**
1. Install NetworkX and visualization libraries
2. Design graph schema for financial fraud domain
3. Create graph database manager class
4. Test basic graph operations (add nodes, edges, query)

**Files to Create:**
- `src/core/graph_manager.py` - Graph database management
- `src/data/entity_extractor.py` - NLP entity extraction
- `requirements.txt` - Add NetworkX, spaCy, Pyvis

---

### Phase 4.2: Entity Extraction Pipeline (Week 2)

**Tasks:**
1. Set up spaCy NLP pipeline
2. Create custom entity extraction rules for financial domain
3. Extract entities from existing SEBI documents
4. Store entities in graph database

**Entity Types to Extract:**
- Organizations (companies, firms)
- People (executives, directors)
- Violations (insider trading, market manipulation)
- Amounts (penalties, fines)
- Dates (violation dates, order dates)

**Files to Create:**
- `src/data/relationship_extractor.py` - Relationship extraction
- `tests/test_entity_extraction.py` - Testing

---

### Phase 4.3: GraphRAG Integration (Week 3-4)

**Tasks:**
1. Enhance RAG engine with graph traversal
2. Implement multi-hop query expansion
3. Combine graph context with vector search
4. Test enhanced queries

**Files to Modify:**
- `src/core/advanced_rag_engine.py` - Add graph integration
- `src/api/advanced_main.py` - Add graph query endpoints

---

### Phase 4.4: Visualization & UI (Week 5-6)

**Tasks:**
1. Create graph visualization component
2. Integrate Pyvis into Streamlit
3. Add graph view to Streamlit UI
4. Enable interactive graph exploration

**Files to Modify:**
- `src/frontend/advanced_streamlit_app.py` - Add graph visualization tab

---

## 📊 Dependencies & Prerequisites

### Software Requirements
```bash
# New packages needed
pip install networkx pyvis spacy
python -m spacy download en_core_web_sm

# Optional (for Neo4j route)
pip install neo4j py2neo
```

### Data Requirements
- ✅ SEBI documents (already processed - 205 documents)
- ✅ Transaction data (already loaded)
- ⚠️ Need to extract entities from existing data

### System Requirements
- ✅ Python 3.10+ (already have)
- ✅ Virtual environment (already have)
- ✅ ChromaDB running (already have)
- ⚠️ NetworkX graph database (to be created)

---

## 🎯 Success Criteria for Phase 4

### Functional Requirements
- [ ] Graph database stores 500+ entities from SEBI documents
- [ ] Graph database stores 1000+ relationships
- [ ] Entity extraction achieves >80% accuracy
- [ ] Multi-hop graph queries work (2-3 hops)
- [ ] Graph visualization displays in Streamlit UI
- [ ] GraphRAG queries return enhanced context
- [ ] Users can explore entity networks interactively

### Performance Requirements
- [ ] Entity extraction: <1s per document
- [ ] Graph query: <0.5s for 2-hop traversal
- [ ] Graph visualization: <2s to render
- [ ] Combined GraphRAG query: <3s total

### Quality Requirements
- [ ] Entity extraction precision >85%
- [ ] Relationship extraction precision >80%
- [ ] Graph queries return relevant connections
- [ ] Visualization is clear and interactive

---

## 🔍 Example Use Cases for GraphRAG

### Use Case 1: Multi-Hop Entity Investigation
**Query:** "Show me all violations related to ABC Corp and similar companies"

**GraphRAG Process:**
1. Extract entity: "ABC Corp"
2. Graph query: Find ABC Corp → violations
3. Graph query: Find ABC Corp → similar entities
4. Graph query: Find similar entities → violations
5. Vector search: Get documents for all violations
6. Generate comprehensive answer with network context

**Expected Answer:**
"ABC Corp was involved in insider trading (Case #2023-042). The company has connections to XYZ Industries, which was also penalized for market manipulation (Case #2022-018). Both cases share similar patterns of executive trading before announcements. SEBI imposed penalties of ₹35L and ₹50L respectively."

---

### Use Case 2: Pattern Recognition
**Query:** "What are common patterns in insider trading cases?"

**GraphRAG Process:**
1. Graph query: Find all insider_trading nodes
2. Graph query: Find entities connected to insider_trading
3. Analyze relationship patterns (executive roles, timing, amounts)
4. Vector search: Get detailed case descriptions
5. Generate pattern analysis

---

### Use Case 3: Network Visualization
**Analyst Action:** Click "View Entity Network" for Case #2023-042

**Result:** Interactive graph showing:
- Central node: ABC Corp
- Connected nodes: 3 executives, 2 related companies
- Violation nodes: Insider trading, market manipulation
- Regulator node: SEBI
- Document nodes: 5 related SEBI orders

---

## 📅 Proposed Implementation Schedule

### Week 1: Foundation (Nov 4-8, 2025)
- Day 1-2: Set up NetworkX, design schema
- Day 3-4: Create graph_manager.py
- Day 5: Test basic operations

### Week 2: Entity Extraction (Nov 11-15, 2025)
- Day 1-2: Set up spaCy, create extraction rules
- Day 3-4: Extract entities from SEBI docs
- Day 5: Test and validate extraction

### Week 3-4: GraphRAG Integration (Nov 18-29, 2025)
- Week 3: Implement graph traversal in RAG engine
- Week 4: Test and optimize GraphRAG queries

### Week 5-6: Visualization (Dec 2-13, 2025)
- Week 5: Create Pyvis visualizations
- Week 6: Integrate into Streamlit UI, polish

**Target Completion:** December 13, 2025

---

## 🚨 Risks & Mitigation

### Risk 1: Entity Extraction Accuracy
- **Risk:** NER may not work well for financial domain
- **Mitigation:** Use custom rules + fine-tuned models
- **Fallback:** Manual entity curation for critical cases

### Risk 2: Graph Complexity
- **Risk:** Graph queries may become too slow with large graphs
- **Mitigation:** Index key properties, limit traversal depth
- **Fallback:** Cache common queries

### Risk 3: Visualization Performance
- **Risk:** Large graphs may be hard to visualize
- **Mitigation:** Limit displayed nodes, add filtering
- **Fallback:** Paginated or clustered views

---

## 🎯 Immediate Next Steps

### Step 1: Validate Phase 3 Completion
- [ ] Test API server startup
- [ ] Test Streamlit UI
- [ ] Verify case management works
- [ ] Verify SAR generation works
- [ ] Check all Phase 3 features

### Step 2: Begin Phase 4 Setup
- [ ] Install NetworkX and dependencies
- [ ] Create initial graph schema
- [ ] Set up graph database structure
- [ ] Plan entity extraction strategy

### Step 3: Create Development Branch
- [ ] Create `phase4-graphrag` branch
- [ ] Set up testing framework
- [ ] Create placeholder files

---

## ❓ Decision Points for User

### Question 1: Graph Database Choice
**Options:**
A. **NetworkX** (Python library, in-memory)
   - ✅ Easy to set up
   - ✅ Good for prototyping
   - ❌ In-memory only (unless persisted manually)
   
B. **Neo4j Desktop** (Full graph database)
   - ✅ Production-grade
   - ✅ Built-in persistence
   - ✅ Cypher query language
   - ❌ More setup required

**Recommendation:** Start with NetworkX, migrate later if needed

### Question 2: Entity Extraction Approach
**Options:**
A. **spaCy NER** (Pre-trained models)
   - ✅ Fast, good baseline
   - ❌ May need fine-tuning
   
B. **Custom Rules** (Pattern matching)
   - ✅ Domain-specific
   - ❌ Manual effort
   
C. **LLM-based** (Use Ollama for extraction)
   - ✅ High quality
   - ❌ Slower, more expensive

**Recommendation:** Hybrid approach - spaCy + custom rules + LLM validation

### Question 3: Scope
**Options:**
A. **Full Phase 4** (All 4 epics)
B. **MVP Phase 4** (Graph + basic GraphRAG, no visualization)
C. **Experimental** (Test concept first, then expand)

**Recommendation:** Full Phase 4 as planned

---

## 📚 References & Resources

### Graph Database Concepts
- NetworkX Documentation: https://networkx.org/
- Neo4j Graph Academy: https://neo4j.com/graphacademy/
- Graph Data Science: https://www.manning.com/books/graph-powered-machine-learning

### Entity Extraction
- spaCy NER: https://spacy.io/usage/linguistic-features#named-entities
- Financial NER: Custom domain adaptation
- LLM-based extraction patterns

### Visualization
- Pyvis Documentation: https://pyvis.readthedocs.io/
- Streamlit Components: Custom graph viewers
- Interactive network layouts

---

## ✅ Phase 4 Checklist

### Epic 1: Graph Database Integration
- [ ] Install NetworkX and dependencies
- [ ] Design financial fraud graph schema
- [ ] Create GraphManager class
- [ ] Implement basic CRUD for nodes/edges
- [ ] Add persistence layer (pickle/JSON)
- [ ] Test graph operations

### Epic 2: Graph ETL Pipeline
- [ ] Set up spaCy pipeline
- [ ] Create entity extraction rules
- [ ] Implement relationship extraction
- [ ] Process existing SEBI documents
- [ ] Populate graph with entities
- [ ] Validate extraction accuracy

### Epic 3: GraphRAG Core Engine
- [ ] Add graph traversal to RAG engine
- [ ] Implement multi-hop query expansion
- [ ] Combine graph + vector search
- [ ] Add graph context to prompts
- [ ] Test enhanced queries
- [ ] Benchmark performance

### Epic 4: Interactive Visualization
- [ ] Create Pyvis visualization component
- [ ] Integrate into Streamlit
- [ ] Add interactive filters
- [ ] Create case network view
- [ ] Create entity network view
- [ ] Add visualization to UI

---

**Status:** Ready to begin Phase 4
**Prerequisites:** All Phase 3 components tested and working
**Estimated Duration:** 4-6 weeks
**Expected Completion:** December 2025

