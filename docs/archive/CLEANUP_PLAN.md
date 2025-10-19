# Codebase Cleanup Plan

## Files to Remove

### Temporary Test/Diagnostic Scripts
- `analyze_amlsim_data.py` - One-time analysis, no longer needed
- `check_sebi_collection.py` - Diagnostic script
- `fix_networkx_compatibility.py` - Temporary compatibility fix
- `patch_networkx_direct.py` - Temporary patch
- `test_advanced_api.py` - Superseded by newer tests
- `test_advanced_rag.py` - Superseded by newer tests
- `test_complete_sebi_pipeline.py` - Old pipeline test
- `test_gpu_config.py` - Diagnostic only
- `test_ollama_integration.py` - Diagnostic only
- `test_phase4_setup.py` - Old phase 4 test
- `test_rag_improvements.py` - Diagnostic, served its purpose
- `test_regulatory_coverage.py` - Diagnostic script
- `test_sebi_graph_queries.py` - Superseded

### Session Summaries (Move to Archive)
- `ARCHITECTURAL_CHANGE_IEEE_TO_AMLSIM.md` - Historical
- `CLEANUP_SUMMARY.md` - Old cleanup summary
- `SESSION_SUMMARY_OCT17.md` - Session notes
- `TODAY_SUMMARY_OCT17_18.md` - Session notes
- `PHASE4_WEEK2_SUMMARY.md` - Session notes
- `PHASE4_WEEK34_COMPLETION.md` - Session notes

### Redundant Documentation (Consolidate)
- `AMLSIM_RESEARCH_AND_SETUP.md` - Merge into main docs
- `AMLSIM_SETUP_GUIDE.md` - Merge into main docs
- `setup_amlsim.md` - Duplicate content
- `PHASE4_AMLSIM_INTEGRATION.md` - Merge into implementation plan
- `PHASE4_PLANNING.md` - Old planning doc

## Files to Keep

### Core Application Scripts
- `build_amlsim_graph.py` - Builds transaction network graph
- `build_sebi_knowledge_graph.py` - Builds regulatory graph
- `generate_amlsim_compatible_data.py` - Data generation utility
- `index_amlsim_documents.py` - ChromaDB indexing
- `process_additional_sebi_docs.py` - Add new regulatory docs
- `rebuild_sebi_chromadb.py` - Rebuild ChromaDB utility
- `start_advanced_api.py` - Main API server
- `start_advanced_streamlit.py` - Main UI application
- `test_unified_graphrag.py` - Core system test

### Essential Documentation
- `README.md` - Project overview
- `PROGRESS_TRACKING.md` - Development progress
- `QUICK_REFERENCE.md` - Quick reference guide
- `RAG_CLASSIFICATION_FIX_SUMMARY.md` - Important fix documentation
- `IMPLEMENTATION_ROADMAP.md` - Implementation guide
- `PHASE4_IMPLEMENTATION_PLAN.md` - Current phase plan
- `PRODUCT_REQUIREMENTS_DOCUMENT.json` - Requirements

## Consolidation Tasks

1. Create `docs/archive/` for historical documents
2. Create `SETUP_GUIDE.md` consolidating all setup instructions
3. Update `README.md` with current status
4. Create `tests/integration/` for preserved test scripts

