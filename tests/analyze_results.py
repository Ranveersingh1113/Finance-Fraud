"""Analyze RAG test results."""
import json
import statistics
from collections import Counter
from pathlib import Path


def analyze_results():
    """Analyze test results."""
    with open("tests/rag_test_responses.json", encoding="utf-8") as f:
        data = json.load(f)
    
    responses = data["responses"]
    print("=" * 80)
    print("RAG SYSTEM COMPREHENSIVE TEST ANALYSIS")
    print("=" * 80)
    print(f"\nTest Session: {data['test_session']}")
    print(f"Total Tests: {data['total_tests']}")
    
    # Categories
    print("\n" + "=" * 80)
    print("TEST CATEGORIES")
    print("=" * 80)
    categories = Counter(r['category'] for r in responses)
    for cat, count in categories.most_common():
        print(f"  {cat}: {count}")
    
    # Query types
    print("\n" + "=" * 80)
    print("QUERY TYPES")
    print("=" * 80)
    query_types = Counter(r['query_type'] for r in responses)
    for qt, count in query_types.most_common():
        print(f"  {qt}: {count}")
    
    # Performance metrics
    print("\n" + "=" * 80)
    print("PERFORMANCE METRICS")
    print("=" * 80)
    times = [r['processing_time'] for r in responses]
    confidences = [r['confidence_score'] for r in responses]
    lengths = [r['answer_length'] for r in responses]
    evidences = [r['evidence_count'] for r in responses]
    
    print(f"\nProcessing Time:")
    print(f"  Average: {statistics.mean(times):.1f}s")
    print(f"  Median: {statistics.median(times):.1f}s")
    print(f"  Min: {min(times):.1f}s")
    print(f"  Max: {max(times):.1f}s")
    print(f"  Std Dev: {statistics.stdev(times):.1f}s")
    
    print(f"\nConfidence Scores:")
    print(f"  Average: {statistics.mean(confidences):.3f}")
    print(f"  Median: {statistics.median(confidences):.3f}")
    print(f"  Min: {min(confidences):.3f}")
    print(f"  Max: {max(confidences):.3f}")
    
    print(f"\nAnswer Length:")
    print(f"  Average: {statistics.mean(lengths):.0f} chars")
    print(f"  Median: {statistics.median(lengths):.0f} chars")
    print(f"  Min: {min(lengths)} chars")
    print(f"  Max: {max(lengths)} chars")
    
    print(f"\nEvidence Count:")
    print(f"  Average: {statistics.mean(evidences):.1f}")
    print(f"  Median: {statistics.median(evidences):.1f}")
    print(f"  Min: {min(evidences)}")
    print(f"  Max: {max(evidences)}")
    
    # Category performance
    print("\n" + "=" * 80)
    print("PERFORMANCE BY CATEGORY")
    print("=" * 80)
    for category in categories.keys():
        cat_responses = [r for r in responses if r['category'] == category]
        cat_times = [r['processing_time'] for r in cat_responses]
        cat_confs = [r['confidence_score'] for r in cat_responses]
        print(f"\n{category.upper()}:")
        print(f"  Tests: {len(cat_responses)}")
        print(f"  Avg Time: {statistics.mean(cat_times):.1f}s")
        print(f"  Avg Confidence: {statistics.mean(cat_confs):.3f}")
    
    # Success rates
    print("\n" + "=" * 80)
    print("SUCCESS RATES")
    print("=" * 80)
    total = len(responses)
    successful = len([r for r in responses if len(r['answer']) > 0])
    print(f"Total Tests: {total}")
    print(f"Successful: {successful} ({successful/total*100:.1f}%)")
    print(f"Failed: {total - successful} ({(total-successful)/total*100:.1f}%)")
    
    # Top queries by confidence
    print("\n" + "=" * 80)
    print("TOP QUERIES BY CONFIDENCE")
    print("=" * 80)
    sorted_by_conf = sorted(responses, key=lambda x: x['confidence_score'], reverse=True)[:5]
    for i, r in enumerate(sorted_by_conf, 1):
        print(f"\n{i}. Confidence: {r['confidence_score']:.3f}")
        print(f"   Query: {r['query'][:70]}...")
        print(f"   Time: {r['processing_time']:.1f}s")
        print(f"   Answer Length: {r['answer_length']} chars")
    
    # Slowest queries
    print("\n" + "=" * 80)
    print("SLOWEST QUERIES")
    print("=" * 80)
    sorted_by_time = sorted(responses, key=lambda x: x['processing_time'], reverse=True)[:5]
    for i, r in enumerate(sorted_by_time, 1):
        print(f"\n{i}. Time: {r['processing_time']:.1f}s")
        print(f"   Query: {r['query'][:70]}...")
        print(f"   Confidence: {r['confidence_score']:.3f}")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    analyze_results()

