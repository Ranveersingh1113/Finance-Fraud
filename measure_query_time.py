"""
Measure time breakdown for each component of query processing.
Identifies which stage is the bottleneck.
"""
import asyncio
import time
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from src.core.config import settings

async def time_query_components(engine, query, use_graphs=True, n_results=8):
    """Measure time for each component of query processing."""
    
    print(f"\n{'='*80}")
    print(f"COMPONENT-LEVEL TIMING ANALYSIS")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Use Graphs: {use_graphs}")
    print(f"N Results: {n_results}\n")
    
    timings = {}
    
    # 1. Query validation & preprocessing
    start = time.time()
    try:
        validated = await engine._validate_and_preprocess(query)
        timings['validation'] = time.time() - start
        print(f"✓ 1. Validation & Preprocessing: {timings['validation']:.3f}s")
    except Exception as e:
        print(f"✗ 1. Validation Failed: {e}")
        return None
    
    # 2. Query planning
    start = time.time()
    try:
        plan = await engine._create_query_plan(validated, use_graphs=use_graphs, n_results=n_results)
        timings['planning'] = time.time() - start
        print(f"✓ 2. Query Planning: {timings['planning']:.3f}s")
        print(f"   Plan: type={plan['query_type']}, use_graphs={plan['use_graphs']}, account_trace={plan['is_account_trace']}")
    except Exception as e:
        print(f"✗ 2. Planning Failed: {e}")
        return None
    
    # 3. Graph context gathering (if enabled)
    if plan['use_graphs'] and not plan['is_account_trace']:
        start = time.time()
        try:
            graph_context = await engine._gather_graph_context_with_retry(
                plan['query'],
                plan['query_type']
            )
            timings['graph_context'] = time.time() - start
            
            # Count entities
            sebi_count = 0
            amlsim_count = 0
            if 'sebi_context' in graph_context:
                sebi_count = graph_context['sebi_context'].get('total_entities', 0)
            if 'amlsim_context' in graph_context:
                amlsim_count = len(graph_context.get('amlsim_context', {}))
            
            print(f"✓ 3. Graph Context Gathering: {timings['graph_context']:.3f}s")
            print(f"   SEBI entities: {sebi_count}, AMLSim patterns: {amlsim_count}")
        except Exception as e:
            print(f"✗ 3. Graph Context Failed: {e}")
            graph_context = {}
            timings['graph_context'] = 0
    else:
        timings['graph_context'] = 0
        graph_context = {}
        print(f"⊘ 3. Graph Context Gathering: SKIPPED")
    
    # 4. RAG retrieval
    start = time.time()
    try:
        rag_results = await engine._dual_rag_retrieval_parallel(
            plan['query'],
            plan['n_results']
        )
        timings['rag_retrieval'] = time.time() - start
        
        sebi_count = len(rag_results.get('sebi_results', []))
        amlsim_count = len(rag_results.get('amlsim_results', []))
        
        print(f"✓ 4. RAG Retrieval: {timings['rag_retrieval']:.3f}s")
        print(f"   SEBI docs: {sebi_count}, AMLSim docs: {amlsim_count}")
    except Exception as e:
        print(f"✗ 4. RAG Retrieval Failed: {e}")
        rag_results = {'sebi_results': [], 'amlsim_results': []}
        timings['rag_retrieval'] = 0
    
    # 5. Pattern matching
    start = time.time()
    try:
        patterns = engine._match_cross_domain_patterns(graph_context, rag_results)
        timings['pattern_matching'] = time.time() - start
        print(f"✓ 5. Pattern Matching: {timings['pattern_matching']:.3f}s")
        print(f"   Patterns found: {len(patterns) if patterns else 0}")
    except Exception as e:
        print(f"✗ 5. Pattern Matching Failed: {e}")
        patterns = []
        timings['pattern_matching'] = 0
    
    # 6. Answer generation
    start = time.time()
    try:
        answer = await engine._generate_unified_answer(
            plan['query'],
            graph_context,
            rag_results,
            patterns
        )
        timings['answer_generation'] = time.time() - start
        print(f"✓ 6. Answer Generation: {timings['answer_generation']:.3f}s")
        print(f"   Answer length: {len(answer)} chars")
    except Exception as e:
        print(f"✗ 6. Answer Generation Failed: {e}")
        timings['answer_generation'] = 0
    
    # Calculate totals
    total = sum(timings.values())
    
    print(f"\n{'='*80}")
    print(f"TOTAL TIME: {total:.3f}s")
    print(f"{'='*80}")
    print(f"\nBREAKDOWN BY PERCENTAGE:")
    print(f"-"*80)
    
    components = [
        ('Validation & Preprocessing', 'validation'),
        ('Query Planning', 'planning'),
        ('Graph Context Gathering', 'graph_context'),
        ('RAG Retrieval', 'rag_retrieval'),
        ('Pattern Matching', 'pattern_matching'),
        ('Answer Generation', 'answer_generation')
    ]
    
    for name, key in components:
        duration = timings.get(key, 0)
        percentage = (duration / total * 100) if total > 0 else 0
        bar_length = int(percentage / 2)  # Scale to 50 chars max
        bar = '█' * bar_length
        print(f"  {name:.<40} {duration:>6.3f}s  {percentage:>5.1f}%  {bar}")
    
    print(f"{'='*80}\n")
    
    # Identify bottleneck
    if total > 0:
        bottleneck = max(timings.items(), key=lambda x: x[1])
        print(f"🔴 BOTTLENECK: {bottleneck[0]} ({bottleneck[1]:.3f}s, {bottleneck[1]/total*100:.1f}%)")
        
        # Recommendations
        print(f"\n💡 OPTIMIZATION RECOMMENDATIONS:")
        print(f"-"*80)
        
        if bottleneck[0] == 'graph_context' and bottleneck[1] > 10:
            print("  • Graph context gathering is slow (>10s)")
            print("    → Use indexed lookups instead of full node scans")
            print("    → Pre-filter nodes before detailed analysis")
            print("    → Cache frequent graph queries")
        
        if bottleneck[0] == 'rag_retrieval' and bottleneck[1] > 8:
            print("  • RAG retrieval is slow (>8s)")
            print("    → Batch encode query variations")
            print("    → Optimize ChromaDB query parameters")
            print("    → Reduce n_results or use progressive retrieval")
        
        if bottleneck[0] == 'answer_generation' and bottleneck[1] > 15:
            print("  • Answer generation is slow (>15s)")
            print("    → Reduce prompt length (currently ~2000 tokens)")
            print("    → Use shorter document summaries")
            print("    → Enable streaming for faster perceived response")
        
        print(f"{'='*80}\n")
    
    return timings

async def main():
    """Run component timing analysis on test queries."""
    
    print("="*80)
    print("COMPONENT-LEVEL PERFORMANCE ANALYSIS")
    print("="*80)
    print(f"Start Time: {datetime.now().isoformat()}\n")
    
    # Initialize engine
    print("Initializing engine...")
    engine = UnifiedGraphRAGEngine(
        persist_directory=settings.graphs_directory,
        chroma_directory=settings.chroma_persist_directory,
        ollama_model=settings.ollama_model,
        ollama_host=settings.ollama_host
    )
    print("✓ Engine initialized\n")
    
    # Test queries
    test_queries = [
        {
            'query': 'What are the key indicators of insider trading according to SEBI regulations?',
            'name': 'SEBI Regulatory Query',
            'use_graphs': True,
            'n_results': 8
        },
        {
            'query': 'Which transaction patterns in AMLSim align with SEBI\'s definition of circular trading?',
            'name': 'Cross-Domain Query',
            'use_graphs': True,
            'n_results': 10
        }
    ]
    
    all_timings = []
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'#'*80}")
        print(f"TEST {i}/{len(test_queries)}: {test['name']}")
        print(f"{'#'*80}")
        
        timings = await time_query_components(
            engine,
            test['query'],
            test.get('use_graphs', True),
            test.get('n_results', 8)
        )
        
        if timings:
            all_timings.append({
                'name': test['name'],
                'query': test['query'],
                'timings': timings
            })
    
    # Summary across all queries
    if all_timings:
        print(f"\n{'='*80}")
        print("SUMMARY ACROSS ALL QUERIES")
        print(f"{'='*80}\n")
        
        # Average timings
        avg_timings = {}
        for result in all_timings:
            for key, value in result['timings'].items():
                if key not in avg_timings:
                    avg_timings[key] = []
                avg_timings[key].append(value)
        
        print("Average Component Times:")
        print("-"*80)
        for key, values in avg_timings.items():
            avg = sum(values) / len(values)
            print(f"  {key:.<30} {avg:.3f}s")
        
        print(f"\n{'='*80}\n")

if __name__ == "__main__":
    asyncio.run(main())


