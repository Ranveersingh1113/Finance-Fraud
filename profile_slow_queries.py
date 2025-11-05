"""
Performance profiling script for slow queries.
Identifies bottlenecks in query processing pipeline.
"""
import asyncio
import cProfile
import pstats
import io
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from src.core.config import settings

async def profile_query(engine, query, query_name, use_graphs=True, n_results=8):
    """Profile a single query and return stats."""
    print(f"\n{'='*80}")
    print(f"PROFILING: {query_name}")
    print(f"{'='*80}")
    print(f"Query: {query}")
    print(f"Use Graphs: {use_graphs}")
    print(f"N Results: {n_results}\n")
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    start = datetime.now()
    try:
        result = await engine.unified_query(query, use_graphs=use_graphs, n_results=n_results)
        duration = (datetime.now() - start).total_seconds()
        
        profiler.disable()
        
        # Print timing
        print(f"✓ Duration: {duration:.2f}s")
        print(f"  Query Type: {result.get('query_type')}")
        print(f"  Graph Used: {result.get('graph_context_used', False)}")
        print(f"  Answer Length: {len(result.get('answer', ''))} chars")
        
        # Get stats
        s = io.StringIO()
        stats = pstats.Stats(profiler, stream=s)
        stats.sort_stats('cumulative')
        stats.print_stats(30)  # Top 30 functions
        
        return {
            'query_name': query_name,
            'query': query,
            'duration': duration,
            'success': True,
            'profile_stats': s.getvalue(),
            'result_summary': {
                'query_type': result.get('query_type'),
                'graph_used': result.get('graph_context_used', False),
                'answer_length': len(result.get('answer', ''))
            }
        }
    except Exception as e:
        profiler.disable()
        duration = (datetime.now() - start).total_seconds()
        print(f"✗ ERROR after {duration:.2f}s: {e}")
        
        return {
            'query_name': query_name,
            'query': query,
            'duration': duration,
            'success': False,
            'error': str(e)
        }

async def main():
    """Profile slow queries to identify bottlenecks."""
    
    print("="*80)
    print("PERFORMANCE PROFILING - SLOW QUERIES")
    print("="*80)
    print(f"Start Time: {datetime.now().isoformat()}")
    print(f"Ollama Model: {settings.ollama_model}")
    print(f"Ollama Host: {settings.ollama_host}\n")
    
    # Initialize engine
    print("Initializing UnifiedGraphRAGEngine...")
    start_init = datetime.now()
    engine = UnifiedGraphRAGEngine(
        persist_directory=settings.graphs_directory,
        chroma_directory=settings.chroma_persist_directory,
        ollama_model=settings.ollama_model,
        ollama_host=settings.ollama_host
    )
    init_duration = (datetime.now() - start_init).total_seconds()
    print(f"✓ Engine initialized in {init_duration:.2f}s\n")
    
    # Test queries (from slowest categories in test results)
    test_queries = [
        {
            'name': 'SEBI-1: Insider Trading (Slow: 42s)',
            'query': 'What are the key indicators of insider trading according to SEBI regulations?',
            'use_graphs': True,
            'n_results': 8
        },
        {
            'name': 'SEBI-4: Regulatory Framework (Very Slow: 73s)',
            'query': 'Explain SEBI\'s regulatory framework for detecting circular trading',
            'use_graphs': True,
            'n_results': 8
        },
        {
            'name': 'CROSS-3: Market Manipulation (Slowest: 88s)',
            'query': 'Find transaction patterns that match SEBI market manipulation violations',
            'use_graphs': True,
            'n_results': 10
        },
        {
            'name': 'ANALYSIS-1: Fraud Typology (Slow: 62s)',
            'query': 'Compare and contrast different fraud typologies across SEBI and AMLSim data',
            'use_graphs': True,
            'n_results': 12
        }
    ]
    
    results = []
    for i, test in enumerate(test_queries, 1):
        print(f"\n[{i}/{len(test_queries)}] Starting profile...")
        result = await profile_query(
            engine,
            test['query'],
            test['name'],
            test.get('use_graphs', True),
            test.get('n_results', 8)
        )
        results.append(result)
    
    # Calculate summary
    successful_results = [r for r in results if r['success']]
    avg_duration = sum(r['duration'] for r in successful_results) / len(successful_results) if successful_results else 0
    
    # Save results
    output_file = 'profiling_results.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("PERFORMANCE PROFILING RESULTS\n")
        f.write("="*80 + "\n")
        f.write(f"Date: {datetime.now().isoformat()}\n")
        f.write(f"Total Queries: {len(results)}\n")
        f.write(f"Successful: {len(successful_results)}\n")
        f.write(f"Average Duration: {avg_duration:.2f}s\n")
        f.write("="*80 + "\n\n")
        
        for result in results:
            f.write(f"\n{'='*80}\n")
            f.write(f"Query: {result['query_name']}\n")
            f.write(f"{'='*80}\n")
            f.write(f"Full Query: {result['query']}\n")
            f.write(f"Duration: {result['duration']:.2f}s\n")
            f.write(f"Success: {result['success']}\n")
            
            if result['success']:
                f.write(f"\nResult Summary:\n")
                for key, value in result['result_summary'].items():
                    f.write(f"  {key}: {value}\n")
                
                f.write(f"\nTop Functions by Cumulative Time:\n")
                f.write("-"*80 + "\n")
                f.write(result['profile_stats'])
            else:
                f.write(f"\nError: {result.get('error', 'Unknown error')}\n")
            
            f.write("\n" + "="*80 + "\n")
    
    print(f"\n{'='*80}")
    print("PROFILING COMPLETE")
    print(f"{'='*80}")
    print(f"✓ Results saved to: {output_file}")
    print(f"✓ Total Queries: {len(results)}")
    print(f"✓ Successful: {len(successful_results)}")
    print(f"✓ Average Duration: {avg_duration:.2f}s")
    print(f"{'='*80}\n")
    
    # Print quick analysis
    if successful_results:
        print("QUICK ANALYSIS:")
        print("-"*80)
        for result in successful_results:
            duration = result['duration']
            graph_used = result['result_summary']['graph_used']
            print(f"  {result['query_name'][:50]}")
            print(f"    → {duration:.2f}s (graph: {graph_used})")
        print("-"*80)

if __name__ == "__main__":
    asyncio.run(main())



