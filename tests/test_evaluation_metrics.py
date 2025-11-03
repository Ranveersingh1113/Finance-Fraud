"""
Evaluation Metrics Framework for Financial Fraud Detection Platform.

Tests and benchmarks for:
- Precision/Recall for retrieval
- BLEU/ROUGE scores for answer quality
- Performance benchmarks
- Comparative analysis with baselines
"""

import pytest
import asyncio
import numpy as np
from typing import List, Dict, Tuple
from unittest.mock import Mock
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.rag_config import RAGConfig


class RetrievalMetrics:
    """Metrics for evaluating RAG retrieval quality."""
    
    @staticmethod
    def calculate_precision_recall(
        retrieved_docs: List[str],
        relevant_docs: List[str],
        total_docs: int
    ) -> Dict[str, float]:
        """
        Calculate precision and recall for retrieval.
        
        Args:
            retrieved_docs: IDs of documents retrieved
            relevant_docs: IDs of truly relevant documents
            total_docs: Total documents in corpus
            
        Returns:
            Dictionary with precision, recall, and F1 score
        """
        # Convert to sets for easier operations
        retrieved_set = set(retrieved_docs)
        relevant_set = set(relevant_docs)
        
        # True positives: documents that are both retrieved AND relevant
        tp = len(retrieved_set & relevant_set)
        
        # False positives: retrieved but not relevant
        fp = len(retrieved_set - relevant_set)
        
        # False negatives: relevant but not retrieved
        fn = len(relevant_set - retrieved_set)
        
        # Precision: of retrieved docs, how many are relevant?
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        
        # Recall: of relevant docs, how many were retrieved?
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        # F1 score: harmonic mean of precision and recall
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            'precision': precision,
            'recall': recall,
            'f1': f1,
            'true_positives': tp,
            'false_positives': fp,
            'false_negatives': fn
        }
    
    @staticmethod
    def calculate_mrr(relevance_scores: List[int]) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR).
        
        Args:
            relevance_scores: List of relevance scores (1=relevant, 0=not)
            
        Returns:
            MRR score
        """
        if not relevance_scores:
            return 0.0
        
        # Find position of first relevant document (rank)
        for i, score in enumerate(relevance_scores, 1):
            if score > 0:
                return 1.0 / i
        
        # No relevant documents found
        return 0.0
    
    @staticmethod
    def calculate_map(relevance_lists: List[List[int]]) -> float:
        """
        Calculate Mean Average Precision (MAP).
        
        Args:
            relevance_lists: List of lists, each containing relevance scores
            
        Returns:
            MAP score
        """
        if not relevance_lists:
            return 0.0
        
        average_precisions = []
        
        for relevance_scores in relevance_lists:
            # Calculate precision at each relevant document
            precisions = []
            relevant_count = 0
            
            for i, score in enumerate(relevance_scores, 1):
                if score > 0:
                    relevant_count += 1
                    precision_at_i = relevant_count / i
                    precisions.append(precision_at_i)
            
            # Average precision for this query
            if precisions:
                ap = sum(precisions) / len(precisions)
                average_precisions.append(ap)
        
        # Mean of all average precisions
        return sum(average_precisions) / len(average_precisions) if average_precisions else 0.0


class AnswerQualityMetrics:
    """Metrics for evaluating generated answer quality."""
    
    @staticmethod
    def calculate_bleu_score(
        predicted: str,
        reference: str,
        n: int = 4
    ) -> float:
        """
        Calculate BLEU score for text generation quality.
        Simplified version - for production, use nltk.translate.bleu_score
        
        Args:
            predicted: Generated answer
            reference: Ground truth answer
            n: Maximum n-gram order
            
        Returns:
            BLEU score (0-1)
        """
        # Tokenize (simplified - split on spaces)
        pred_tokens = predicted.lower().split()
        ref_tokens = reference.lower().split()
        
        if len(pred_tokens) == 0:
            return 0.0
        
        # Calculate precision for each n-gram order
        precisions = []
        
        for i in range(1, n + 1):
            # Generate n-grams
            pred_ngrams = [tuple(pred_tokens[j:j+i]) for j in range(len(pred_tokens) - i + 1)]
            ref_ngrams = [tuple(ref_tokens[j:j+i]) for j in range(len(ref_tokens) - i + 1)]
            
            if not ref_ngrams:
                continue
            
            # Count matches (clipped)
            pred_ngrams_count = {}
            for ngram in pred_ngrams:
                pred_ngrams_count[ngram] = pred_ngrams_count.get(ngram, 0) + 1
            
            ref_ngrams_count = {}
            for ngram in ref_ngrams:
                ref_ngrams_count[ngram] = ref_ngrams_count.get(ngram, 0) + 1
            
            # Clip counts
            matches = 0
            for ngram, count in pred_ngrams_count.items():
                matches += min(count, ref_ngrams_count.get(ngram, 0))
            
            # Precision for this n-gram order
            precision = matches / len(pred_ngrams) if pred_ngrams else 0
            precisions.append(precision)
        
        if not precisions:
            return 0.0
        
        # Geometric mean of precisions
        bleu = np.prod(precisions) ** (1.0 / len(precisions))
        
        # Brevity penalty
        bp = 1.0 if len(pred_tokens) >= len(ref_tokens) else np.exp(1 - len(ref_tokens) / len(pred_tokens))
        
        return bleu * bp
    
    @staticmethod
    def calculate_rouge_l(
        predicted: str,
        reference: str
    ) -> float:
        """
        Calculate ROUGE-L score (Longest Common Subsequence).
        
        Args:
            predicted: Generated answer
            reference: Ground truth answer
            
        Returns:
            ROUGE-L F1 score
        """
        pred_tokens = predicted.lower().split()
        ref_tokens = reference.lower().split()
        
        # Calculate LCS length
        lcs_length = AnswerQualityMetrics._lcs(pred_tokens, ref_tokens)
        
        # ROUGE-L precision and recall
        precision = lcs_length / len(pred_tokens) if pred_tokens else 0.0
        recall = lcs_length / len(ref_tokens) if ref_tokens else 0.0
        
        # F1 score
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return f1
    
    @staticmethod
    def _lcs(seq1: List[str], seq2: List[str]) -> int:
        """Calculate Longest Common Subsequence length."""
        m, n = len(seq1), len(seq2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        return dp[m][n]


class PerformanceMetrics:
    """Metrics for evaluating system performance."""
    
    @staticmethod
    def calculate_latency_stats(latency_samples: List[float]) -> Dict[str, float]:
        """
        Calculate latency statistics.
        
        Args:
            latency_samples: List of latency measurements in seconds
            
        Returns:
            Dictionary with mean, median, p95, p99, min, max
        """
        if not latency_samples:
            return {}
        
        samples = np.array(latency_samples)
        
        return {
            'mean': float(np.mean(samples)),
            'median': float(np.median(samples)),
            'p95': float(np.percentile(samples, 95)),
            'p99': float(np.percentile(samples, 99)),
            'min': float(np.min(samples)),
            'max': float(np.max(samples)),
            'std': float(np.std(samples))
        }
    
    @staticmethod
    def calculate_throughput(
        requests_count: int,
        total_time_seconds: float
    ) -> float:
        """
        Calculate requests per second throughput.
        
        Args:
            requests_count: Number of requests processed
            total_time_seconds: Total time taken
            
        Returns:
            Throughput in requests per second
        """
        return requests_count / total_time_seconds if total_time_seconds > 0 else 0.0


class TestRetrievalMetrics:
    """Test retrieval evaluation metrics."""
    
    def test_precision_perfect_retrieval(self):
        """Test precision when all retrieved docs are relevant."""
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = ['doc1', 'doc2', 'doc3', 'doc4']
        
        metrics = RetrievalMetrics.calculate_precision_recall(
            retrieved, relevant, total_docs=100
        )
        
        assert metrics['precision'] == 1.0
        assert metrics['recall'] == 0.75  # 3 out of 4 relevant docs retrieved
    
    def test_recall_perfect_retrieval(self):
        """Test recall when all relevant docs are retrieved."""
        retrieved = ['doc1', 'doc2', 'doc3', 'doc4']
        relevant = ['doc1', 'doc2']
        
        metrics = RetrievalMetrics.calculate_precision_recall(
            retrieved, relevant, total_docs=100
        )
        
        assert metrics['recall'] == 1.0
        assert metrics['precision'] == 0.5  # 2 out of 4 retrieved are relevant
    
    def test_f1_score_balanced(self):
        """Test F1 score calculation."""
        retrieved = ['doc1', 'doc2', 'doc3']
        relevant = ['doc1', 'doc2', 'doc4']
        
        metrics = RetrievalMetrics.calculate_precision_recall(
            retrieved, relevant, total_docs=100
        )
        
        assert 0.0 < metrics['f1'] < 1.0
        assert metrics['true_positives'] == 2
    
    def test_mrr_calculation(self):
        """Test Mean Reciprocal Rank calculation."""
        # First relevant doc at position 3
        relevance_scores = [0, 0, 1, 1, 0]
        mrr = RetrievalMetrics.calculate_mrr(relevance_scores)
        
        assert mrr == 1.0 / 3  # Reciprocal of rank 3
    
    def test_map_calculation(self):
        """Test Mean Average Precision calculation."""
        # First query: relevant docs at positions 1 and 3
        # Second query: relevant docs at positions 2 and 4
        relevance_lists = [
            [1, 0, 1, 0],  # AP = (1 + 2/3) / 2 = 0.833
            [0, 1, 0, 1],  # AP = (1/2 + 2/4) / 2 = 0.75
        ]
        
        map_score = RetrievalMetrics.calculate_map(relevance_lists)
        
        # Query 1: [1,0,1,0] -> AP = (1.0 + 0.667)/2 = 0.833
        # Query 2: [0,1,0,1] -> AP = (0.5 + 0.5)/2 = 0.5
        # MAP = (0.833 + 0.5) / 2 = 0.667
        assert abs(map_score - 0.667) < 0.01


class TestAnswerQuality:
    """Test answer quality evaluation metrics."""
    
    def test_bleu_perfect_match(self):
        """Test BLEU score for identical texts."""
        predicted = "SEBI imposes penalties for insider trading violations"
        reference = "SEBI imposes penalties for insider trading violations"
        
        bleu = AnswerQualityMetrics.calculate_bleu_score(predicted, reference)
        
        # Should be very close to 1.0
        assert bleu > 0.95
    
    def test_bleu_partial_match(self):
        """Test BLEU score for partial match."""
        # Use similar texts that share many words
        predicted = "SEBI imposes financial penalties for insider trading violations"
        reference = "SEBI imposes penalties for insider trading cases"
        
        bleu = AnswerQualityMetrics.calculate_bleu_score(predicted, reference)
        
        # Should be between 0 and 1 (they share many words)
        assert 0.0 < bleu < 1.0
    
    def test_rouge_l_perfect_match(self):
        """Test ROUGE-L for identical texts."""
        predicted = "Money laundering involves placement layering and integration"
        reference = "Money laundering involves placement layering and integration"
        
        rouge = AnswerQualityMetrics.calculate_rouge_l(predicted, reference)
        
        assert rouge == 1.0
    
    def test_rouge_l_partial_match(self):
        """Test ROUGE-L for texts with common subsequence."""
        predicted = "The system detected suspicious transaction patterns"
        reference = "suspicious patterns were detected by the system"
        
        rouge = AnswerQualityMetrics.calculate_rouge_l(predicted, reference)
        
        # Should find common words: "suspicious", "patterns", "detected", "system"
        assert 0.0 < rouge <= 1.0


class TestPerformanceMetrics:
    """Test performance evaluation metrics."""
    
    def test_latency_stats_calculation(self):
        """Test latency statistics calculation."""
        latencies = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        stats = PerformanceMetrics.calculate_latency_stats(latencies)
        
        assert stats['mean'] == 0.55
        assert stats['median'] == 0.55
        assert abs(stats['p95'] - 0.95) < 0.1
        assert abs(stats['p99'] - 0.99) < 0.1
        assert stats['min'] == 0.1
        assert stats['max'] == 1.0
    
    def test_throughput_calculation(self):
        """Test throughput calculation."""
        throughput = PerformanceMetrics.calculate_throughput(
            requests_count=1000,
            total_time_seconds=10.0
        )
        
        assert throughput == 100.0  # 100 requests per second


class BenchmarkSuite:
    """Benchmark suite for comprehensive evaluation."""
    
    @staticmethod
    def create_test_queries() -> List[Dict[str, any]]:
        """
        Create test query set with ground truth.
        
        Returns:
            List of test queries with expected answers
        """
        return [
            {
                'query': "What are SEBI penalties for insider trading?",
                'expected_docs': ['regulation_pit', 'case_insider_2023'],
                'expected_answer': "SEBI imposes monetary penalties for insider trading violations",
                'category': 'regulatory'
            },
            {
                'query': "What is money laundering?",
                'expected_docs': ['regulation_pmla', 'guide_aml'],
                'expected_answer': "Money laundering involves placement, layering, and integration",
                'category': 'general'
            },
            {
                'query': "Show account 507 transactions",
                'expected_docs': ['account_507_txns'],
                'expected_answer': "Account 507 has 25 outgoing transactions",
                'category': 'transactional'
            },
            {
                'query': "What are fan-out patterns in AML?",
                'expected_docs': ['pattern_guide', 'typology_fanout'],
                'expected_answer': "Fan-out patterns indicate money placement from one account to many",
                'category': 'transactional'
            }
        ]


class TestBenchmarks:
    """Test benchmark suite."""
    
    def test_benchmark_query_set(self):
        """Test that benchmark query set is properly formatted."""
        queries = BenchmarkSuite.create_test_queries()
        
        assert len(queries) > 0
        for query in queries:
            assert 'query' in query
            assert 'expected_docs' in query
            assert 'expected_answer' in query
            assert 'category' in query


if __name__ == "__main__":
    # Run evaluation tests
    pytest.main([__file__, "-v", "--tb=short"])

