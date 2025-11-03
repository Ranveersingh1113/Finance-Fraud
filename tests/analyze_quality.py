"""Analyze answer quality and relevance."""
import json
from pathlib import Path


def analyze_quality():
    """Analyze answer quality."""
    with open("tests/rag_test_responses.json", encoding="utf-8") as f:
        data = json.load(f)
    
    responses = data["responses"]
    
    print("=" * 80)
    print("RAG SYSTEM QUALITY ANALYSIS")
    print("=" * 80)
    
    # Sample detailed analysis
    print("\nDETAILED QUERY-ANSWER ANALYSIS (Sample Queries)")
    print("=" * 80)
    
    # Analyze a few key queries in detail
    sample_queries = [
        "What are SEBI penalties for insider trading?",
        "What is money laundering?",
        "Explain the three stages of money laundering",
        "Show entities involved in insider trading"
    ]
    
    for query in sample_queries:
        matching = [r for r in responses if r['query'] == query]
        if not matching:
            continue
        
        r = matching[0]
        print(f"\n{'='*80}")
        print(f"QUERY: {query}")
        print(f"{'='*80}")
        print(f"Category: {r['category']}")
        print(f"Detected Type: {r['query_type_detected']}")
        print(f"Confidence: {r['confidence_score']:.3f}")
        print(f"Processing Time: {r['processing_time']:.1f}s")
        print(f"Evidence Count: {r['evidence_count']}")
        print(f"Answer Length: {r['answer_length']} chars")
        
        # Show answer preview
        print(f"\nAnswer Preview (first 500 chars):")
        print("-" * 80)
        print(r['answer'][:500])
        print("-" * 80)
        
        # Show top evidence
        print(f"\nTop 3 Evidence:")
        for i, ev in enumerate(r['evidence'][:3], 1):
            print(f"\n{i}. Document Preview (first 200 chars):")
            print("  " + ev['document'][:200].replace('\n', ' '))
            print(f"   Similarity: {ev['similarity_score']:.3f}")
            fs = ev['final_score']
            fs_str = f"{fs:.3f}" if fs is not None else "N/A"
            print(f"   Final Score: {fs_str}")
            print(f"   Source: {ev['source']}")
    
    # Evidence quality metrics
    print("\n" + "=" * 80)
    print("EVIDENCE QUALITY METRICS")
    print("=" * 80)
    
    all_similarities = []
    all_final_scores = []
    sources_count = {}
    
    for r in responses:
        for ev in r['evidence']:
            if ev['similarity_score']:
                all_similarities.append(ev['similarity_score'])
            if ev['final_score']:
                all_final_scores.append(ev['final_score'])
            
            src = ev['source']
            sources_count[src] = sources_count.get(src, 0) + 1
    
    if all_similarities:
        print(f"\nSimilarity Scores:")
        print(f"  Average: {sum(all_similarities)/len(all_similarities):.3f}")
        print(f"  Max: {max(all_similarities):.3f}")
        print(f"  Min: {min(all_similarities):.3f}")
    
    if all_final_scores:
        print(f"\nFinal Scores (after re-ranking):")
        print(f"  Average: {sum(all_final_scores)/len(all_final_scores):.3f}")
        print(f"  Max: {max(all_final_scores):.3f}")
        print(f"  Min: {min(all_final_scores):.3f}")
    
    print(f"\nEvidence Sources:")
    for src, count in sorted(sources_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {src}: {count} documents")
    
    print("\n" + "=" * 80)
    print("QUALITY ANALYSIS COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    analyze_quality()

