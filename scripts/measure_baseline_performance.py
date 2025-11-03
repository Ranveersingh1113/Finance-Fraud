"""
Measure baseline performance metrics for the Finance Fraud Detection system.
This script evaluates the current (unfinetuned) model performance.

Usage:
    python scripts/measure_baseline_performance.py
"""

import asyncio
import sys
from pathlib import Path
import json
from typing import List, Dict, Any
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from tests.test_evaluation_metrics import RetrievalMetrics, PerformanceMetrics


class BaselineEvaluator:
    """Evaluate baseline system performance."""
    
    def __init__(self):
        self.engine = None
        self.results = {
            'retrieval_metrics': [],
            'latencies': [],
            'test_cases': []
        }
    
    async def initialize_engine(self):
        """Initialize the GraphRAG engine."""
        print("Initializing UnifiedGraphRAGEngine...")
        self.engine = UnifiedGraphRAGEngine(
            persist_directory="./data/graphs",
            chroma_directory="./data/chroma_db"
        )
        print("Waiting for pattern cache initialization...")
        await asyncio.sleep(5)
        print("Engine ready!\n")
    
    def get_test_queries(self) -> List[Dict[str, Any]]:
        """
        Get test queries with ground truth labels.
        
        NOTE: You need to manually verify these document IDs exist in your ChromaDB.
        Run scripts/explore_chromadb.py first to find actual IDs.
        """
        return [
            {
                'query': "What are SEBI penalties for insider trading violations?",
                'expected_doc_keywords': ['insider trading', 'pit', 'penalty', 'prohibition'],
                'category': 'regulatory',
                'description': 'Regulatory query about insider trading penalties'
            },
            {
                'query': "Explain money laundering detection patterns",
                'expected_doc_keywords': ['money laundering', 'pmla', 'placement', 'layering'],
                'category': 'regulatory',
                'description': 'AML pattern detection query'
            },
            {
                'query': "What is SEBI LODR compliance requirement?",
                'expected_doc_keywords': ['lodr', 'listing obligations', 'disclosure', 'compliance'],
                'category': 'regulatory',
                'description': 'Listing obligations query'
            },
            {
                'query': "Show fan-out transaction patterns",
                'expected_doc_keywords': ['fan-out', 'fan out', 'placement', 'structuring'],
                'category': 'transactional',
                'description': 'Transaction pattern query'
            },
            {
                'query': "Find fraud rings in transaction network",
                'expected_doc_keywords': ['fraud', 'ring', 'network', 'suspicious'],
                'category': 'transactional',
                'description': 'Fraud detection query'
            },
            {
                'query': "What are PFUTP regulations?",
                'expected_doc_keywords': ['pfutp', 'fraudulent', 'unfair trade', 'market manipulation'],
                'category': 'regulatory',
                'description': 'Market manipulation regulations'
            },
        ]
    
    def calculate_keyword_relevance(self, retrieved_doc: Dict, expected_keywords: List[str]) -> bool:
        """
        Approximate relevance by checking if document contains expected keywords.
        This is a heuristic until you have full ground truth labels.
        """
        document_text = retrieved_doc.get('document', '').lower()
        metadata_text = str(retrieved_doc.get('metadata', {})).lower()
        combined_text = document_text + ' ' + metadata_text
        
        # Document is relevant if it contains at least 2 of the expected keywords
        matches = sum(1 for keyword in expected_keywords if keyword in combined_text)
        return matches >= 2
    
    async def evaluate_query(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single query."""
        query = test_case['query']
        expected_keywords = test_case['expected_doc_keywords']
        
        print(f"Testing: {query}")
        print(f"Category: {test_case['category']}")
        
        # Measure retrieval
        start_time = time.time()
        response = await self.engine.unified_query(query, use_graphs=True, n_results=10)
        latency = time.time() - start_time
        
        # Get retrieved documents
        retrieved_docs = []
        retrieved_docs.extend(response.get('sebi_results', [])[:10])
        retrieved_docs.extend(response.get('amlsim_results', [])[:10])
        retrieved_docs = retrieved_docs[:10]  # Top 10 only
        
        # Calculate relevance (keyword-based heuristic)
        relevance_scores = [
            1 if self.calculate_keyword_relevance(doc, expected_keywords) else 0
            for doc in retrieved_docs
        ]
        
        relevant_count = sum(relevance_scores)
        
        # Calculate metrics
        precision = relevant_count / len(retrieved_docs) if retrieved_docs else 0.0
        mrr = RetrievalMetrics.calculate_mrr(relevance_scores)
        
        # Show results
        print(f"  Retrieved: {len(retrieved_docs)} documents")
        print(f"  Relevant (by keywords): {relevant_count}")
        print(f"  Precision@10: {precision:.3f}")
        print(f"  MRR: {mrr:.3f}")
        print(f"  Latency: {latency:.2f}s")
        
        # Show top 3 retrieved documents
        print(f"  Top 3 results:")
        for i, doc in enumerate(retrieved_docs[:3], 1):
            title = doc.get('metadata', {}).get('title', 'Untitled')[:60]
            score = doc.get('score', 0)
            is_relevant = '[+]' if relevance_scores[i-1] == 1 else '[-]'
            print(f"    {i}. [{is_relevant}] {title} (score: {score:.3f})")
        print()
        
        return {
            'query': query,
            'category': test_case['category'],
            'precision': precision,
            'mrr': mrr,
            'latency': latency,
            'relevant_count': relevant_count,
            'total_retrieved': len(retrieved_docs)
        }
    
    async def run_full_evaluation(self):
        """Run full baseline evaluation."""
        print("=" * 70)
        print("BASELINE PERFORMANCE EVALUATION")
        print("=" * 70)
        print()
        
        await self.initialize_engine()
        
        test_queries = self.get_test_queries()
        
        for test_case in test_queries:
            result = await self.evaluate_query(test_case)
            self.results['retrieval_metrics'].append(result)
            self.results['latencies'].append(result['latency'])
        
        # Calculate aggregate metrics
        self.print_summary()
        self.save_results()
    
    def print_summary(self):
        """Print summary statistics."""
        metrics = self.results['retrieval_metrics']
        
        avg_precision = sum(m['precision'] for m in metrics) / len(metrics)
        avg_mrr = sum(m['mrr'] for m in metrics) / len(metrics)
        latency_stats = PerformanceMetrics.calculate_latency_stats(self.results['latencies'])
        
        print("=" * 70)
        print("BASELINE METRICS SUMMARY")
        print("=" * 70)
        print(f"\n[RETRIEVAL QUALITY]:")
        print(f"  * Average Precision@10: {avg_precision:.3f}")
        print(f"  * Average MRR: {avg_mrr:.3f}")
        print(f"  * Total queries tested: {len(metrics)}")
        
        print(f"\n[PERFORMANCE]:")
        print(f"  * Mean latency: {latency_stats['mean']:.2f}s")
        print(f"  * Median latency: {latency_stats['median']:.2f}s")
        print(f"  * P95 latency: {latency_stats['p95']:.2f}s")
        print(f"  * Min/Max: {latency_stats['min']:.2f}s / {latency_stats['max']:.2f}s")
        
        # Category breakdown
        print(f"\n[BY CATEGORY]:")
        categories = {}
        for m in metrics:
            cat = m['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(m['precision'])
        
        for cat, precisions in categories.items():
            avg = sum(precisions) / len(precisions)
            print(f"  • {cat.capitalize()}: {avg:.3f} precision ({len(precisions)} queries)")
        
        # Interpretation
        print(f"\n[INTERPRETATION]:")
        if avg_precision < 0.50:
            print("  [!] LOW - Retrieval quality needs significant improvement")
            print("  --> Recommendation: Finetune embedding model (HIGH PRIORITY)")
        elif avg_precision < 0.70:
            print("  [~] MODERATE - Some relevant documents missed")
            print("  --> Recommendation: Consider finetuning or query expansion")
        else:
            print("  [+] GOOD - Retrieval quality is acceptable")
            print("  --> Recommendation: Focus on answer generation quality")
        
        print("\n" + "=" * 70)
        print(f"Results saved to: baseline_metrics_results.json")
        print("=" * 70)
    
    def save_results(self):
        """Save results to JSON file."""
        output = {
            'summary': {
                'avg_precision_at_10': sum(m['precision'] for m in self.results['retrieval_metrics']) / len(self.results['retrieval_metrics']),
                'avg_mrr': sum(m['mrr'] for m in self.results['retrieval_metrics']) / len(self.results['retrieval_metrics']),
                'latency_stats': PerformanceMetrics.calculate_latency_stats(self.results['latencies']),
                'total_queries': len(self.results['retrieval_metrics'])
            },
            'detailed_results': self.results['retrieval_metrics'],
            'note': 'Relevance calculated using keyword heuristics. For production, use manual ground truth labels.'
        }
        
        with open('baseline_metrics_results.json', 'w') as f:
            json.dump(output, f, indent=2)


async def main():
    """Main entry point."""
    evaluator = BaselineEvaluator()
    await evaluator.run_full_evaluation()


if __name__ == "__main__":
    asyncio.run(main())

