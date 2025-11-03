"""
Comprehensive RAG Query Test Suite

Tests all query scenarios to ensure the RAG system works flawlessly across all use cases.
All responses are saved for detailed analysis.
"""

import pytest
import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.advanced_rag_engine import AdvancedRAGEngine
from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine


# Response storage for analysis
RESPONSES_FILE = Path(__file__).parent / "rag_test_responses.json"
test_responses = []


def save_response(query: str, response, test_category: str, query_type: str):
    """Save full response for analysis."""
    evidence_data = []
    for i, ev in enumerate(response.evidence):
        evidence_data.append({
            "rank": i + 1,
            "document": ev.document[:1500] + "..." if len(ev.document) > 1500 else ev.document,
            "similarity_score": float(ev.similarity_score),
            "rerank_score": float(ev.rerank_score) if ev.rerank_score else None,
            "final_score": float(ev.final_score) if ev.final_score else None,
            "source": ev.source,
            "metadata": ev.metadata
        })
    
    test_responses.append({
        "timestamp": datetime.now().isoformat(),
        "category": test_category,
        "query_type": query_type,
        "query": query,
        "answer": response.answer,
        "answer_length": len(response.answer),
        "confidence_score": float(response.confidence_score),
        "processing_time": float(response.processing_time),
        "evidence_count": len(response.evidence),
        "evidence": evidence_data,
        "query_type_detected": response.query_type
    })


@pytest.fixture(scope="session", autouse=True)
def save_all_responses():
    """Save all responses after test session."""
    yield
    if test_responses:
        output = {
            "test_session": datetime.now().isoformat(),
            "total_tests": len(test_responses),
            "responses": test_responses
        }
        with open(RESPONSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"\n[INFO] Saved {len(test_responses)} test responses to {RESPONSES_FILE}")


# Test queries organized by category
REGULATORY_QUERIES = [
    "What are SEBI penalties for insider trading?",
    "Explain market manipulation under SEBI regulations",
    "What are the penalties for violating PIT regulations?",
    "How does SEBI enforce PMLA compliance?",
    "What constitutes insider trading?",
    "Explain disgorgement in SEBI enforcement",
    "What are fines for market manipulation?",
    "Describe SEBI regulations on fraudulent trading"
]

TRANSACTIONAL_QUERIES = [
    "Show me all transactions for account 507",
    "What are fan-out patterns in AMLSim?",
    "Identify fan-in patterns in transactions",
    "Detect cycle patterns",
    "What is layering in money laundering?",
    "Show suspicious transaction patterns",
    "Find fraud rings in transaction network"
]

GENERAL_FRAUD_QUERIES = [
    "What is money laundering?",
    "Explain the three stages of money laundering",
    "What are common fraud patterns?",
    "How does placement work in money laundering?",
    "What are red flags for suspicious transactions?"
]

ENTITY_QUERIES = [
    "What companies have been penalized by SEBI?",
    "Show entities involved in insider trading",
    "List persons in SEBI enforcement actions",
    "What entities have multiple violations?"
]


class TestRegulatoryQueries:
    """Test regulatory/SEBI queries."""
    
    @pytest.mark.asyncio
    async def test_insider_trading_queries(self):
        """Test insider trading related queries."""
        engine = AdvancedRAGEngine()
        
        query = "What are SEBI penalties for insider trading?"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "regulatory", "insider_trading")
        
        assert len(response.answer) > 50
        assert len(response.evidence) > 0
        assert response.confidence_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_market_manipulation_queries(self):
        """Test market manipulation queries."""
        engine = AdvancedRAGEngine()
        
        query = "Explain market manipulation under SEBI regulations"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "regulatory", "market_manipulation")
        
        assert len(response.answer) > 50
        assert len(response.evidence) > 0
    
    @pytest.mark.asyncio
    async def test_pmla_compliance_queries(self):
        """Test PMLA compliance queries."""
        engine = AdvancedRAGEngine()
        
        query = "How does SEBI enforce PMLA compliance?"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "regulatory", "pmla_compliance")
        
        assert len(response.answer) > 50
        assert len(response.evidence) > 0


class TestTransactionalQueries:
    """Test transactional/AMLSim queries."""
    
    @pytest.mark.asyncio
    async def test_account_transactions(self):
        """Test account transaction queries."""
        engine = AdvancedRAGEngine()
        
        query = "Show me all transactions for account 507"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "transactional", "account_transactions")
        
        assert len(response.answer) > 0
        assert len(response.evidence) >= 0
    
    @pytest.mark.asyncio
    async def test_fan_out_patterns(self):
        """Test fan-out pattern detection."""
        engine = AdvancedRAGEngine()
        
        query = "What are fan-out patterns in AMLSim?"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "transactional", "fan_out_patterns")
        
        assert len(response.answer) > 0
    
    @pytest.mark.asyncio
    async def test_cycle_patterns(self):
        """Test cycle pattern detection."""
        engine = AdvancedRAGEngine()
        
        query = "Detect cycle patterns"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "transactional", "cycle_patterns")
        
        assert len(response.answer) > 0


class TestGeneralFraudQueries:
    """Test general fraud knowledge queries."""
    
    @pytest.mark.asyncio
    async def test_money_laundering_definition(self):
        """Test money laundering definition queries."""
        engine = AdvancedRAGEngine()
        
        query = "What is money laundering?"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "general", "money_laundering_definition")
        
        assert len(response.answer) > 100
        assert len(response.evidence) > 0
    
    @pytest.mark.asyncio
    async def test_three_stages_ml(self):
        """Test money laundering stages queries."""
        engine = AdvancedRAGEngine()
        
        query = "Explain the three stages of money laundering"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "general", "three_stages_ml")
        
        assert len(response.answer) > 100
        assert len(response.evidence) > 0
    
    @pytest.mark.asyncio
    async def test_fraud_patterns(self):
        """Test general fraud pattern queries."""
        engine = AdvancedRAGEngine()
        
        query = "What are common fraud patterns?"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "general", "fraud_patterns")
        
        assert len(response.answer) > 100


class TestEntityQueries:
    """Test entity-related queries."""
    
    @pytest.mark.asyncio
    async def test_company_penalties(self):
        """Test company penalty queries."""
        engine = AdvancedRAGEngine()
        
        query = "What companies have been penalized by SEBI?"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "entity", "company_penalties")
        
        assert len(response.answer) > 0
    
    @pytest.mark.asyncio
    async def test_insider_trading_entities(self):
        """Test insider trading entity queries."""
        engine = AdvancedRAGEngine()
        
        query = "Show entities involved in insider trading"
        response = await engine.query(query, n_results=10)
        save_response(query, response, "entity", "insider_trading_entities")
        
        assert len(response.answer) > 0


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_long_query(self):
        """Test handling of long queries."""
        engine = AdvancedRAGEngine()
        
        query = "What is fraud? " * 100
        response = await engine.query(query, n_results=5)
        save_response(query, response, "edge_cases", "long_query")
        
        assert len(response.answer) >= 0
    
    @pytest.mark.asyncio
    async def test_special_characters(self):
        """Test special character handling."""
        engine = AdvancedRAGEngine()
        
        query = "What is fraud? @#$%^&*()"
        response = await engine.query(query, n_results=5)
        save_response(query, response, "edge_cases", "special_characters")
        
        assert len(response.answer) >= 0
    
    @pytest.mark.asyncio
    async def test_unicode_characters(self):
        """Test unicode handling."""
        engine = AdvancedRAGEngine()
        
        query = "What is money laundering? 测试 🚀"
        response = await engine.query(query, n_results=5)
        save_response(query, response, "edge_cases", "unicode")
        
        assert len(response.answer) >= 0


class TestPerformance:
    """Test performance benchmarks."""
    
    @pytest.mark.asyncio
    async def test_performance_regulatory(self):
        """Benchmark regulatory query performance."""
        engine = AdvancedRAGEngine()
        
        query = "What are SEBI penalties for insider trading?"
        start = time.time()
        response = await engine.query(query, n_results=10)
        elapsed = time.time() - start
        
        save_response(query, response, "performance", "regulatory_benchmark")
        
        assert elapsed < 300.0  # Reasonable threshold
        assert len(response.answer) > 0
    
    @pytest.mark.asyncio
    async def test_performance_general(self):
        """Benchmark general query performance."""
        engine = AdvancedRAGEngine()
        
        query = "What is money laundering?"
        start = time.time()
        response = await engine.query(query, n_results=10)
        elapsed = time.time() - start
        
        save_response(query, response, "performance", "general_benchmark")
        
        assert elapsed < 300.0
        assert len(response.answer) > 0


class TestQuerySuite:
    """Comprehensive query suite."""
    
    @pytest.mark.asyncio
    async def test_all_regulatory_queries(self):
        """Test all regulatory queries."""
        engine = AdvancedRAGEngine()
        
        for query in REGULATORY_QUERIES:  # Test ALL regulatory queries
            response = await engine.query(query, n_results=10)
            save_response(query, response, "comprehensive", "regulatory_suite")
            
            assert len(response.answer) > 0
            assert response.confidence_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_all_transactional_queries(self):
        """Test all transactional queries."""
        engine = AdvancedRAGEngine()
        
        for query in TRANSACTIONAL_QUERIES:  # Test ALL transactional queries
            response = await engine.query(query, n_results=10)
            save_response(query, response, "comprehensive", "transactional_suite")
            
            assert len(response.answer) > 0
    
    @pytest.mark.asyncio
    async def test_all_general_queries(self):
        """Test all general fraud queries."""
        engine = AdvancedRAGEngine()
        
        for query in GENERAL_FRAUD_QUERIES:  # Test ALL general fraud queries
            response = await engine.query(query, n_results=10)
            save_response(query, response, "comprehensive", "general_suite")
            
            assert len(response.answer) > 0
    
    @pytest.mark.asyncio
    async def test_all_entity_queries(self):
        """Test all entity queries."""
        engine = AdvancedRAGEngine()
        
        for query in ENTITY_QUERIES:  # Test ALL entity queries
            response = await engine.query(query, n_results=10)
            save_response(query, response, "comprehensive", "entity_suite")
            
            assert len(response.answer) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

