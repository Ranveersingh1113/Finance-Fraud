# Performance Optimization Plan

**Based on:** Test Results Analysis - 88.9% performance violation rate  
**Target:** Reduce to 20-30% violations  
**Timeline:** 1-2 weeks

---

## 🎯 PHASE 1: VERIFICATION (In Progress)

### Status: Running Tests
- Running comprehensive test suite with fixes
- Expected improvement: 7.4% → 60-70% success rate
- Will verify graph_context_used flag is working
- Will confirm query key is present in all responses

---

## 🔍 PHASE 2: PROFILING & BOTTLENECK IDENTIFICATION

### 2.1 Performance Profiling Script

Create `profile_slow_queries.py`:

```python
import asyncio
import cProfile
import pstats
import io
from datetime import datetime
from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from src.core.config import settings

async def profile_query(engine, query, query_name, use_graphs=True):
    """Profile a single query and return stats."""
    print(f"\n{'='*80}")
    print(f"PROFILING: {query_name}")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Use Graphs: {use_graphs}\n")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    start = datetime.now()
    result = await engine.unified_query(query, use_graphs=use_graphs, n_results=8)
    duration = (datetime.now() - start).total_seconds()
    
    profiler.disable()
    
    # Print timing
    print(f"Duration: {duration:.2f}s")
    print(f"Query Type: {result.get('query_type')}")
    print(f"Graph Used: {result.get('graph_context_used', False)}")
    print(f"Answer Length: {len(result.get('answer', ''))}")
    
    # Get stats
    s = io.StringIO()
    stats = pstats.Stats(profiler, stream=s)
    stats.sort_stats('cumulative')
    stats.print_stats(30)  # Top 30 functions
    
    return {
        'query_name': query_name,
        'duration': duration,
        'profile_stats': s.getvalue()
    }

async def main():
    """Profile slow queries to identify bottlenecks."""
    
    # Initialize engine
    engine = UnifiedGraphRAGEngine(
        persist_directory=settings.graphs_directory,
        chroma_directory=settings.chroma_persist_directory,
        ollama_model=settings.ollama_model,
        ollama_host=settings.ollama_host
    )
    
    # Test queries (from slowest categories)
    test_queries = [
        {
            'name': 'SEBI Regulatory (Slow)',
            'query': 'What are the key indicators of insider trading according to SEBI regulations?',
            'use_graphs': True
        },
        {
            'name': 'Cross-Domain (Very Slow)',
            'query': 'Which transaction patterns in AMLSim align with SEBI\'s definition of circular trading?',
            'use_graphs': True
        },
        {
            'name': 'Complex Analysis (Slow)',
            'query': 'Compare and contrast different fraud typologies across SEBI and AMLSim data',
            'use_graphs': True
        }
    ]
    
    results = []
    for test in test_queries:
        result = await profile_query(
            engine,
            test['query'],
            test['name'],
            test['use_graphs']
        )
        results.append(result)
    
    # Save results
    with open('profiling_results.txt', 'w') as f:
        f.write("PERFORMANCE PROFILING RESULTS\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"\nQuery: {result['query_name']}\n")
            f.write(f"Duration: {result['duration']:.2f}s\n")
            f.write(f"\nTop Functions by Cumulative Time:\n")
            f.write(result['profile_stats'])
            f.write("\n" + "="*80 + "\n")
    
    print(f"\n✓ Profiling results saved to profiling_results.txt")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.2 Quick Performance Measurement

Create `measure_query_time.py`:

```python
import asyncio
import time
from datetime import datetime
from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from src.core.config import settings

async def time_query_components(engine, query):
    """Measure time for each component of query processing."""
    
    print(f"\nQuery: {query}\n")
    
    # 1. Query validation & preprocessing
    start = time.time()
    validated = await engine._validate_and_preprocess(query)
    t_validate = time.time() - start
    print(f"1. Validation & Preprocessing: {t_validate:.3f}s")
    
    # 2. Query planning
    start = time.time()
    plan = await engine._create_query_plan(validated, use_graphs=True, n_results=8)
    t_plan = time.time() - start
    print(f"2. Query Planning: {t_plan:.3f}s")
    
    # 3. Graph context gathering (if enabled)
    if plan['use_graphs']:
        start = time.time()
        graph_context = await engine._gather_graph_context_with_retry(
            plan['query'],
            plan['query_type']
        )
        t_graph = time.time() - start
        print(f"3. Graph Context Gathering: {t_graph:.3f}s")
    else:
        t_graph = 0
        print(f"3. Graph Context Gathering: SKIPPED")
    
    # 4. RAG retrieval
    start = time.time()
    rag_results = await engine._dual_rag_retrieval_parallel(
        plan['query'],
        plan['n_results']
    )
    t_rag = time.time() - start
    print(f"4. RAG Retrieval: {t_rag:.3f}s")
    
    # 5. Pattern matching
    start = time.time()
    patterns = engine._match_cross_domain_patterns(graph_context if plan['use_graphs'] else {}, rag_results)
    t_patterns = time.time() - start
    print(f"5. Pattern Matching: {t_patterns:.3f}s")
    
    # 6. Answer generation
    start = time.time()
    answer = await engine._generate_unified_answer(
        plan['query'],
        graph_context if plan['use_graphs'] else {},
        rag_results,
        patterns
    )
    t_answer = time.time() - start
    print(f"6. Answer Generation: {t_answer:.3f}s")
    
    total = t_validate + t_plan + t_graph + t_rag + t_patterns + t_answer
    
    print(f"\nTOTAL: {total:.3f}s")
    print(f"\nBREAKDOWN:")
    print(f"  Validation: {t_validate/total*100:.1f}%")
    print(f"  Planning: {t_plan/total*100:.1f}%")
    print(f"  Graph Context: {t_graph/total*100:.1f}%")
    print(f"  RAG Retrieval: {t_rag/total*100:.1f}%")
    print(f"  Pattern Matching: {t_patterns/total*100:.1f}%")
    print(f"  Answer Generation: {t_answer/total*100:.1f}%")

async def main():
    engine = UnifiedGraphRAGEngine(
        persist_directory=settings.graphs_directory,
        chroma_directory=settings.chroma_persist_directory,
        ollama_model=settings.ollama_model,
        ollama_host=settings.ollama_host
    )
    
    # Test with slow query
    await time_query_components(
        engine,
        "What are the key indicators of insider trading according to SEBI regulations?"
    )

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🚀 PHASE 3: OPTIMIZATION IMPLEMENTATIONS

### 3.1 Graph Context Optimization (Priority 1)

**Target:** Reduce graph context gathering from 20-30s to 5-10s

#### Issue: Full Node Scans
```python
# CURRENT (SLOW) - src/core/unified_graphrag_engine.py
async def _gather_graph_context(self, query, query_type):
    # Scans ALL nodes every time
    all_cases = [n for n in self.sebi_graph.graph.nodes(data=True) 
                 if n[1].get('type') == 'Case']
```

#### Solution: Use Graph Stats Cache
```python
# OPTIMIZED - Use pre-computed indexes
async def _gather_graph_context(self, query, query_type):
    # Get relevant cases from cache
    case_stats = self.graph_stats_cache.get_stat('sebi_case_index')
    
    # Filter by keyword using index
    keywords = self._extract_keywords(query)
    relevant_cases = []
    for keyword in keywords:
        if keyword in case_stats.get('keyword_index', {}):
            relevant_cases.extend(case_stats['keyword_index'][keyword])
    
    # Limit to top N most relevant
    relevant_cases = relevant_cases[:50]  # Much smaller than full scan
```

#### Implementation Task
```python
# Add to src/core/graph_stats_cache.py

class GraphStatsCache:
    def build_keyword_index(self, graph):
        """Build inverted index: keyword -> [case_ids]"""
        keyword_index = {}
        
        for node_id, data in graph.nodes(data=True):
            if data.get('type') == 'Case':
                # Extract keywords from case
                case_name = data.get('name', '').lower()
                violation = data.get('violation_type', '').lower()
                
                # Index by words
                words = set(case_name.split() + violation.split())
                for word in words:
                    if len(word) > 3:  # Skip short words
                        if word not in keyword_index:
                            keyword_index[word] = []
                        keyword_index[word].append(node_id)
        
        return keyword_index
```

### 3.2 RAG Retrieval Optimization (Priority 2)

**Target:** Reduce RAG retrieval from 10-15s to 3-5s

#### Issue: Sequential Queries
```python
# CURRENT - Some queries still sequential
sebi_results = await self._query_sebi_collection(query, n_results)
amlsim_results = await self._query_amlsim_collection(query, n_results)
```

#### Solution: Batch Encoding
```python
# OPTIMIZED - Batch embeddings
async def _dual_rag_retrieval_parallel(self, query, n_results):
    # Expand query once
    expanded_queries = self._expand_query(query)
    
    # Encode all variations in batch
    all_queries = [query] + expanded_queries
    embeddings = await self.rag_engine.encode_batch(all_queries)
    
    # Query both collections in parallel with batch embeddings
    sebi_task = self._query_sebi_batch(embeddings, n_results)
    amlsim_task = self._query_amlsim_batch(embeddings, n_results)
    
    results = await asyncio.gather(sebi_task, amlsim_task)
    return self._merge_and_dedupe(results)
```

### 3.3 LLM Generation Optimization (Priority 3)

**Target:** Reduce answer generation from 15-20s to 5-10s

#### Issue: Long Prompts
Current prompts are 2000-3000 tokens with lots of context.

#### Solution: Streamlined Prompts
```python
# CURRENT (VERBOSE)
prompt = f"""
Based on the following comprehensive regulatory documents and transaction patterns,
please provide a detailed analysis of the query: {query}

REGULATORY CONTEXT:
{sebi_doc_1_full_text}  # 500+ tokens
{sebi_doc_2_full_text}  # 500+ tokens
...

TRANSACTION CONTEXT:
{transaction_details}  # 300+ tokens
...

Please analyze thoroughly considering all aspects...
"""

# OPTIMIZED (CONCISE)
prompt = f"""
Query: {query}

Evidence:
- SEBI: {sebi_summary_1} | {sebi_summary_2}  # 100 tokens total
- Transactions: {txn_summary}  # 50 tokens

Answer concisely with: 1) Key findings, 2) Evidence, 3) Recommendation.
"""
```

### 3.4 Query Result Caching (Priority 4)

**Target:** 50%+ cache hit rate for repeated queries

#### Add Query Result Cache
```python
# src/core/query_result_cache.py
class QueryResultCache:
    """Cache full query results (beyond semantic cache)."""
    
    def __init__(self, max_size=1000, ttl=3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
    
    def get(self, query, use_graphs, n_results):
        """Get cached result if available."""
        key = self._make_key(query, use_graphs, n_results)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return result
            else:
                del self.cache[key]
        
        return None
    
    def set(self, query, use_graphs, n_results, result):
        """Cache query result."""
        key = self._make_key(query, use_graphs, n_results)
        
        # Evict oldest if full
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
        
        self.cache[key] = (result, time.time())
```

---

## 📊 PHASE 4: VALIDATION

### 4.1 Re-run Test Suite
```bash
python test_unified_graphrag_comprehensive.py
```

### 4.2 Expected Results After Each Optimization

| Phase | Success Rate | Avg Duration | Violation Rate |
|-------|-------------|--------------|----------------|
| Current (with fixes) | 60-70% | 51s | 88.9% |
| After Graph Opt | 70-75% | 35s | 60% |
| After RAG Opt | 75-80% | 25s | 40% |
| After LLM Opt | 80-85% | 18s | 25% |
| After Caching | 85-90% | 15s | 20% |

### 4.3 Performance Benchmarks

Create `benchmark.py` to track improvements:

```python
import asyncio
from datetime import datetime
from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from src.core.config import settings

async def benchmark():
    engine = UnifiedGraphRAGEngine(
        persist_directory=settings.graphs_directory,
        chroma_directory=settings.chroma_persist_directory
    )
    
    queries = [
        "What are SEBI penalties for insider trading?",
        "Trace transactions for account 507",
        "Which patterns align with circular trading?"
    ]
    
    results = []
    for query in queries:
        start = datetime.now()
        result = await engine.unified_query(query, use_graphs=True)
        duration = (datetime.now() - start).total_seconds()
        
        results.append({
            'query': query,
            'duration': duration,
            'graph_used': result.get('graph_context_used', False)
        })
    
    avg_duration = sum(r['duration'] for r in results) / len(results)
    print(f"\nAverage Duration: {avg_duration:.2f}s")
    
    for r in results:
        print(f"{r['query'][:50]}: {r['duration']:.2f}s (graph: {r['graph_used']})")

if __name__ == "__main__":
    asyncio.run(benchmark())
```

---

## 🎯 SUCCESS METRICS

### Phase 2 Complete (Profiling)
- [ ] Identified top 3 bottlenecks
- [ ] Created optimization plan for each
- [ ] Estimated time savings

### Phase 3 Complete (Optimization)
- [ ] Graph context gathering < 10s
- [ ] RAG retrieval < 5s
- [ ] Answer generation < 10s
- [ ] Cache hit rate > 50%

### Phase 4 Complete (Validation)
- [ ] Test success rate > 85%
- [ ] Average duration < 20s
- [ ] Performance violation rate < 25%

---

## 📅 TIMELINE

| Phase | Duration | Completion Date |
|-------|----------|-----------------|
| 1. Verification | 20 min | Today |
| 2. Profiling | 2-3 hours | Today |
| 3.1 Graph Opt | 4-6 hours | Tomorrow |
| 3.2 RAG Opt | 2-3 hours | Day 3 |
| 3.3 LLM Opt | 2-3 hours | Day 3 |
| 3.4 Caching | 2-3 hours | Day 4 |
| 4. Validation | 1-2 hours | Day 4 |

**Total Estimated Time:** 14-20 hours over 4-5 days
**Expected Completion:** End of next week

---

## 🔧 IMPLEMENTATION NOTES

### Tools Needed
- cProfile for Python profiling
- memory_profiler for memory usage
- line_profiler for line-by-line profiling
- pytest-benchmark for regression testing

### Testing Strategy
- Profile before each optimization
- Measure improvement
- Run full test suite
- Document results

### Rollback Plan
- Git commit before each optimization
- Keep original code commented for reference
- Test incrementally

---

## 📞 NEXT ACTIONS

1. **NOW:** Wait for test results to verify fixes work
2. **Today:** Run profiling scripts to identify bottlenecks
3. **Tomorrow:** Start implementing graph context optimization
4. **This Week:** Complete all optimizations and validation

