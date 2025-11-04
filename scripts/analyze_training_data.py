"""
Analyze generated training data for quality and correctness.

Usage:
    python scripts/analyze_training_data.py
"""

import json
from collections import Counter

print("=" * 70)
print("TRAINING DATA QUALITY ANALYSIS")
print("=" * 70)

# Load data
with open('data/finetuning/e5_training_data.json', 'r') as f:
    data = json.load(f)

metadata = data['metadata']
training_pairs = data['training_pairs']

print("\n[1/5] METADATA")
print("-" * 70)
print(f"Created: {metadata['created_at']}")
print(f"Total pairs: {metadata['actual_pairs']}")
print(f"Document-based: {metadata['statistics']['document_based_pairs']}")
print(f"Expert queries: {metadata['statistics']['expert_query_pairs']}")
print(f"Collections: {', '.join(metadata['collections'])}")

print("\n[2/5] QUERY ANALYSIS")
print("-" * 70)

query_lengths = [len(p['query']) for p in training_pairs]
print(f"Query lengths:")
print(f"  Min: {min(query_lengths)} chars")
print(f"  Max: {max(query_lengths)} chars")
print(f"  Avg: {sum(query_lengths)/len(query_lengths):.1f} chars")

# Check for too short queries
short_queries = [p for p in training_pairs if len(p['query']) < 20]
print(f"  Queries < 20 chars: {len(short_queries)} ({len(short_queries)/len(training_pairs)*100:.1f}%)")

# Check for generic queries
generic_patterns = ['what is', 'explain', 'show me', 'tell me']
generic_queries = [p for p in training_pairs if any(pat in p['query'].lower() for pat in generic_patterns)]
print(f"  Generic pattern queries: {len(generic_queries)} ({len(generic_queries)/len(training_pairs)*100:.1f}%)")

print("\n[3/5] DOCUMENT ANALYSIS")
print("-" * 70)

doc_lengths = [len(p['positive']['text']) for p in training_pairs]
print(f"Positive document lengths:")
print(f"  Min: {min(doc_lengths)} chars")
print(f"  Max: {max(doc_lengths)} chars")
print(f"  Avg: {sum(doc_lengths)/len(doc_lengths):.1f} chars")

# Document types
doc_types = Counter([p['doc_type'] for p in training_pairs])
print(f"\nDocument type distribution:")
for dtype, count in doc_types.most_common():
    print(f"  {dtype}: {count} ({count/len(training_pairs)*100:.1f}%)")

# Source collections
sources = Counter([p['source_collection'] for p in training_pairs])
print(f"\nSource collection distribution:")
for source, count in sources.most_common():
    print(f"  {source}: {count} ({count/len(training_pairs)*100:.1f}%)")

print("\n[4/5] NEGATIVE SAMPLING ANALYSIS")
print("-" * 70)

neg_counts = [len(p['negatives']) for p in training_pairs]
print(f"Negatives per query:")
print(f"  Min: {min(neg_counts)}")
print(f"  Max: {max(neg_counts)}")
print(f"  Avg: {sum(neg_counts)/len(neg_counts):.1f}")

print("\n[5/5] SAMPLE PAIRS (Quality Check)")
print("-" * 70)

for i, pair in enumerate(training_pairs[:5]):
    print(f"\n[Sample {i+1}]")
    print(f"Query: {pair['query'][:100]}...")
    print(f"Query length: {len(pair['query'])} chars")
    print(f"Positive doc: {pair['positive']['text'][:120]}...")
    print(f"Doc length: {len(pair['positive']['text'])} chars")
    print(f"Num negatives: {len(pair['negatives'])}")
    print(f"Doc type: {pair['doc_type']}")
    print(f"Source: {pair['source_collection']}")
    
    # Check query-doc overlap
    query_terms = set(pair['query'].lower().split())
    doc_terms = set(pair['positive']['text'][:500].lower().split())
    overlap = len(query_terms & doc_terms) / max(len(query_terms), 1)
    print(f"Query-doc overlap: {overlap:.2%}")

print("\n" + "=" * 70)
print("QUALITY ASSESSMENT")
print("=" * 70)

# Issues found
issues = []
recommendations = []

if len(short_queries) > len(training_pairs) * 0.1:
    issues.append(f"[!] {len(short_queries)} queries are too short (< 20 chars)")
    recommendations.append("Consider increasing minimum query length filter")

if len(generic_queries) > len(training_pairs) * 0.3:
    issues.append(f"[!] {len(generic_queries)} queries use generic patterns")
    recommendations.append("Add more specific query generation logic")

if min(neg_counts) < 3:
    issues.append(f"[!] Some pairs have < 3 negatives")
    recommendations.append("Ensure minimum 3-5 negatives per query")

if len(issues) > 0:
    print("\n[ISSUES FOUND]:")
    for issue in issues:
        print(f"  {issue}")
    print("\n[RECOMMENDATIONS]:")
    for rec in recommendations:
        print(f"  - {rec}")
else:
    print("\n[OK] No critical issues found!")

print("\n[OVERALL ASSESSMENT]:")
avg_query_len = sum(query_lengths)/len(query_lengths)
avg_doc_len = sum(doc_lengths)/len(doc_lengths)
avg_negatives = sum(neg_counts)/len(neg_counts)

score = 0
if avg_query_len > 30: score += 1
if avg_doc_len > 200: score += 1
if avg_negatives >= 3: score += 1
if len(short_queries) < len(training_pairs) * 0.1: score += 1
if len(training_pairs) >= 500: score += 1

if score >= 4:
    print("  [EXCELLENT] Training data is high quality - ready for training!")
elif score >= 3:
    print("  [GOOD] Training data is acceptable - proceed with training")
else:
    print("  [WARNING] Training data may have quality issues - review recommended")

print(f"  Quality score: {score}/5")
print("\n" + "=" * 70)

