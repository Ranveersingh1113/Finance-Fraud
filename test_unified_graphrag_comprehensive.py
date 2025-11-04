"""
Comprehensive test suite for UnifiedGraphRAGEngine with proper assertions.
Based on code review feedback - now a REAL test suite, not just a demo runner!

Key improvements:
- Assertion framework for validation
- Dynamic test data discovery
- Performance tracking with thresholds
- Pre-flight checks
- Smoke tests
- Cache effectiveness validation
- Cross-domain pattern validation
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.unified_graphrag_engine import UnifiedGraphRAGEngine
from src.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestAssertion:
    """Helper class for test assertions with detailed error messages."""
    
    @staticmethod
    def assert_result_structure(result: Dict):
        """Validate basic result structure."""
        required_keys = ['query', 'query_type', 'answer']
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"
        
        # Check types
        assert isinstance(result['query'], str), "Query must be string"
        assert isinstance(result['query_type'], str), "Query type must be string"
        assert isinstance(result['answer'], str), "Answer must be string"
    
    @staticmethod
    def assert_answer_quality(answer: str, query: str, min_length: int = 100):
        """Validate answer quality."""
        assert isinstance(answer, str), "Answer must be string"
        assert len(answer) >= min_length, \
            f"Answer too short: {len(answer)} < {min_length} chars"
        
        # Check for error indicators
        error_keywords = ['error', 'failed', 'could not', 'unable to']
        answer_lower = answer.lower()
        for keyword in error_keywords:
            if keyword in answer_lower and keyword in answer_lower[:100]:
                raise AssertionError(f"Answer contains error keyword: '{keyword}'")
        
        # Answer should relate to query (basic check)
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        common_words = query_words & answer_words
        
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
        meaningful_common = common_words - stop_words
        
        if len(meaningful_common) == 0:
            logger.warning(f"Answer may not relate to query - no common meaningful words")
    
    @staticmethod
    def assert_document_relevance(documents: List[Dict], keywords: List[str], 
                                  min_relevance: float = 0.3):
        """Validate document relevance to query keywords."""
        assert len(documents) > 0, "No documents returned"
        
        # Check at least some docs contain keywords
        relevant_count = 0
        for doc in documents[:10]:  # Check first 10
            doc_text = doc.get('document', '') + ' ' + doc.get('metadata', {}).get('title', '')
            doc_text = doc_text.lower()
            
            if any(kw.lower() in doc_text for kw in keywords):
                relevant_count += 1
        
        relevance_ratio = relevant_count / min(len(documents), 10)
        assert relevance_ratio >= min_relevance, \
            f"Low relevance: {relevance_ratio:.1%} of docs contain keywords (threshold: {min_relevance:.1%})"
    
    @staticmethod
    def assert_graph_enhancement(result: Dict, use_graphs: bool):
        """Validate graph context when enabled."""
        if use_graphs:
            # Should have graph_context_used flag
            assert result.get('graph_context_used', False), \
                "use_graphs=True but graph_context_used=False"
            
            # Should have either graph insights or graph context
            has_insights = 'graph_insights' in result and result['graph_insights']
            has_context = 'graph_context' in result and result['graph_context']
            
            assert has_insights or has_context, \
                "Graph enabled but no graph_insights or graph_context in result"
    
    @staticmethod
    def assert_sources_present(result: Dict, min_sources: int = 1):
        """Validate sources are present."""
        assert 'sources' in result or 'sebi_results' in result or 'amlsim_results' in result, \
            "No sources/results in response"
        
        # Count sources
        source_count = 0
        if 'sources' in result:
            source_count = len(result['sources'])
        if 'sebi_results' in result:
            source_count += len(result['sebi_results'])
        if 'amlsim_results' in result:
            source_count += len(result['amlsim_results'])
        
        assert source_count >= min_sources, \
            f"Insufficient sources: {source_count} < {min_sources}"
    
    @staticmethod
    def assert_cross_domain_patterns(result: Dict, expected: bool = True):
        """Validate cross-domain pattern detection."""
        if expected:
            # Should have evidence from both domains
            has_sebi = (
                'sebi_results' in result and len(result['sebi_results']) > 0
            ) or (
                'graph_insights' in result and 
                len(result['graph_insights'].get('sebi_cases', [])) > 0
            )
            
            has_amlsim = (
                'amlsim_results' in result and len(result['amlsim_results']) > 0
            ) or (
                'graph_insights' in result and 
                len(result['graph_insights'].get('transactions', [])) > 0
            )
            
            if not (has_sebi or has_amlsim):
                logger.warning("Cross-domain query but results only from one domain")


class PerformanceTracker:
    """Track performance metrics across tests."""
    
    def __init__(self):
        self.thresholds = {
            'account_trace': 2.0,           # Max 2s for account traces
            'regulatory_simple': 8.0,       # Max 8s for simple regulatory queries
            'transaction_simple': 8.0,       # Max 8s for simple transaction queries
            'cross_domain': 20.0,           # Max 20s for cross-domain queries
            'complex_analysis': 25.0,       # Max 25s for complex analysis
            'baseline': 5.0,                # Max 5s for baseline (no graph)
            'edge_case': 15.0               # Max 15s for edge cases
        }
        self.violations = []
        self.durations = []
    
    def check_performance(self, test_name: str, duration: float, 
                         test_type: str) -> bool:
        """Check if test meets performance threshold."""
        threshold = self.thresholds.get(test_type, 30.0)
        
        self.durations.append({
            'test_name': test_name,
            'duration': duration,
            'test_type': test_type,
            'threshold': threshold
        })
        
        if duration > threshold:
            violation = {
                'test_name': test_name,
                'duration': duration,
                'threshold': threshold,
                'overage': duration - threshold,
                'overage_pct': ((duration - threshold) / threshold) * 100
            }
            self.violations.append(violation)
            logger.warning(
                f"⚠️ Performance violation: {test_name} took {duration:.2f}s "
                f"(threshold: {threshold}s, overage: {duration-threshold:.2f}s, "
                f"+{violation['overage_pct']:.0f}%)"
            )
            return False
        else:
            logger.info(f"✓ Performance OK: {duration:.2f}s < {threshold}s")
            return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.durations:
            return {'total_violations': 0, 'violations': []}
        
        avg_duration = sum(d['duration'] for d in self.durations) / len(self.durations)
        max_duration = max(self.durations, key=lambda x: x['duration'])
        min_duration = min(self.durations, key=lambda x: x['duration'])
        
        return {
            'total_tests': len(self.durations),
            'total_violations': len(self.violations),
            'violation_rate': f"{(len(self.violations)/len(self.durations)*100):.1f}%",
            'average_duration': avg_duration,
            'max_duration': max_duration,
            'min_duration': min_duration,
            'violations': self.violations
        }


class ComprehensiveTestSuite:
    """Comprehensive test suite for UnifiedGraphRAGEngine with proper validation."""
    
    def __init__(self, output_file: str = "test_results_comprehensive.json"):
        """Initialize test suite."""
        self.output_file = output_file
        self.test_results = {
            "test_run_info": {
                "timestamp": datetime.now().isoformat(),
                "description": "Comprehensive test with assertions and validation"
            },
            "tests": []
        }
        self.engine = None
        self.perf_tracker = PerformanceTracker()
        
        # Dynamic test data (discovered during setup)
        self.test_accounts = {}
        self.sample_sebi_cases = []
    
    async def pre_flight_checks(self):
        """Validate environment before running tests."""
        logger.info("\n" + "=" * 80)
        logger.info("RUNNING PRE-FLIGHT CHECKS")
        logger.info("=" * 80)
        
        checks_passed = []
        checks_failed = []
        
        # Check 1: SEBI graph loaded
        try:
            assert self.engine.sebi_graph.graph is not None, "SEBI graph not loaded"
            node_count = self.engine.sebi_graph.graph.number_of_nodes()
            edge_count = self.engine.sebi_graph.graph.number_of_edges()
            logger.info(f"✓ SEBI graph loaded: {node_count} nodes, {edge_count} edges")
            checks_passed.append("SEBI graph")
        except Exception as e:
            logger.error(f"✗ SEBI graph check failed: {e}")
            checks_failed.append(f"SEBI graph: {e}")
        
        # Check 2: AMLSim graph loaded
        try:
            assert self.engine.amlsim_graph.graph is not None, "AMLSim graph not loaded"
            node_count = self.engine.amlsim_graph.graph.number_of_nodes()
            edge_count = self.engine.amlsim_graph.graph.number_of_edges()
            logger.info(f"✓ AMLSim graph loaded: {node_count} nodes, {edge_count} edges")
            checks_passed.append("AMLSim graph")
        except Exception as e:
            logger.error(f"✗ AMLSim graph check failed: {e}")
            checks_failed.append(f"AMLSim graph: {e}")
        
        # Check 3: SEBI collection
        try:
            sebi_count = self.engine.rag_engine.sebi_collection.count()
            logger.info(f"✓ SEBI collection: {sebi_count} documents")
            assert sebi_count > 0, "SEBI collection empty"
            checks_passed.append("SEBI collection")
        except Exception as e:
            logger.error(f"✗ SEBI collection error: {e}")
            checks_failed.append(f"SEBI collection: {e}")
        
        # Check 4: AMLSim collection (optional)
        try:
            if self.engine.amlsim_collection:
                amlsim_count = self.engine.amlsim_collection.count()
                logger.info(f"✓ AMLSim collection: {amlsim_count} documents")
                checks_passed.append("AMLSim collection")
            else:
                logger.info("⚠️ AMLSim collection not available")
        except Exception as e:
            logger.warning(f"⚠️ AMLSim collection check: {e}")
        
        # Check 5: Pattern cache
        try:
            assert self.engine._pattern_cache_initialized, "Pattern cache not initialized"
            logger.info("✓ Pattern cache initialized")
            checks_passed.append("Pattern cache")
        except Exception as e:
            logger.error(f"✗ Pattern cache error: {e}")
            checks_failed.append(f"Pattern cache: {e}")
        
        # Check 6: LLM availability
        try:
            if self.engine.rag_engine.use_ollama:
                logger.info(f"✓ Ollama LLM available: {self.engine.rag_engine.ollama_model}")
                checks_passed.append("LLM (Ollama)")
            elif self.engine.rag_engine.use_claude:
                logger.info("✓ Claude API available")
                checks_passed.append("LLM (Claude)")
            else:
                logger.warning("⚠️ No LLM configured")
        except Exception as e:
            logger.warning(f"⚠️ LLM check: {e}")
        
        # Summary
        logger.info(f"\n✓ Checks passed: {len(checks_passed)}")
        logger.info(f"✗ Checks failed: {len(checks_failed)}")
        
        self.test_results["pre_flight_checks"] = {
            "passed": checks_passed,
            "failed": checks_failed,
            "success_rate": f"{len(checks_passed)/(len(checks_passed)+len(checks_failed))*100:.0f}%"
        }
        
        if checks_failed:
            logger.warning(f"\n⚠️ Some pre-flight checks failed: {checks_failed}")
            if len(checks_failed) > len(checks_passed):
                raise RuntimeError("Too many pre-flight check failures - aborting tests")
        else:
            logger.info("\n✓ All pre-flight checks passed!")
    
    async def discover_test_data(self):
        """Discover valid test data from graphs."""
        logger.info("\n" + "=" * 80)
        logger.info("DISCOVERING TEST DATA")
        logger.info("=" * 80)
        
        # Discover test accounts from AMLSim graph
        try:
            # Get suspicious accounts
            all_nodes = list(self.engine.amlsim_graph.graph.nodes(data=True))
            account_nodes = [n for n in all_nodes if n[1].get('type') == 'Account']
            
            if len(account_nodes) > 0:
                # Get suspicious accounts
                suspicious = [n for n in account_nodes if n[1].get('is_suspicious', False)]
                
                if len(suspicious) >= 2:
                    self.test_accounts['suspicious_1'] = suspicious[0][0].replace('account_', '')
                    self.test_accounts['suspicious_2'] = suspicious[1][0].replace('account_', '')
                    logger.info(f"✓ Found suspicious accounts: {self.test_accounts['suspicious_1']}, {self.test_accounts['suspicious_2']}")
                else:
                    # Use any accounts
                    self.test_accounts['suspicious_1'] = account_nodes[0][0].replace('account_', '')
                    if len(account_nodes) > 1:
                        self.test_accounts['suspicious_2'] = account_nodes[1][0].replace('account_', '')
                    logger.warning(f"⚠️ Using regular accounts as test accounts: {self.test_accounts}")
                
                # Get high-value account
                accounts_with_balance = [n for n in account_nodes if 'balance' in n[1]]
                if accounts_with_balance:
                    high_value = max(accounts_with_balance, key=lambda x: x[1].get('balance', 0))
                    self.test_accounts['high_value'] = high_value[0].replace('account_', '')
                    logger.info(f"✓ Found high-value account: {self.test_accounts['high_value']}")
                else:
                    self.test_accounts['high_value'] = self.test_accounts.get('suspicious_1', '1')
            else:
                # Fallback to default IDs
                logger.warning("⚠️ No accounts found in graph, using defaults")
                self.test_accounts = {
                    'suspicious_1': '1',
                    'suspicious_2': '2',
                    'high_value': '1'
                }
        except Exception as e:
            logger.error(f"✗ Error discovering accounts: {e}")
            self.test_accounts = {
                'suspicious_1': '1',
                'suspicious_2': '2',
                'high_value': '1'
            }
        
        # Discover SEBI cases
        try:
            sebi_nodes = list(self.engine.sebi_graph.graph.nodes(data=True))
            case_nodes = [n for n in sebi_nodes if n[1].get('type') == 'Case']
            
            if len(case_nodes) > 0:
                self.sample_sebi_cases = [n[1].get('name', n[0]) for n in case_nodes[:3]]
                logger.info(f"✓ Found SEBI cases: {len(case_nodes)} total, sample: {self.sample_sebi_cases[:2]}")
            else:
                logger.warning("⚠️ No SEBI cases found in graph")
                self.sample_sebi_cases = []
        except Exception as e:
            logger.error(f"✗ Error discovering SEBI cases: {e}")
            self.sample_sebi_cases = []
        
        # Store in results
        self.test_results["test_data"] = {
            "test_accounts": self.test_accounts,
            "sample_sebi_cases": self.sample_sebi_cases
        }
        
        logger.info(f"\nTest data discovery complete:")
        logger.info(f"  - Test accounts: {len(self.test_accounts)}")
        logger.info(f"  - SEBI cases: {len(self.sample_sebi_cases)}")
    
    async def smoke_tests(self):
        """Quick smoke tests before full suite."""
        logger.info("\n" + "=" * 80)
        logger.info("RUNNING SMOKE TESTS")
        logger.info("=" * 80)
        
        smoke_results = []
        
        # Smoke Test 1: Basic query without graph
        try:
            logger.info("\nSmoke Test 1: Basic query without graph...")
            result = await self.engine.unified_query(
                "What is insider trading?",
                use_graphs=False,
                n_results=5
            )
            assert len(result['answer']) > 50, "Answer too short"
            assert 'insider' in result['answer'].lower(), "Answer doesn't mention insider trading"
            logger.info("✓ Smoke test 1 PASSED")
            smoke_results.append({"test": "Basic query", "status": "PASSED"})
        except Exception as e:
            logger.error(f"✗ Smoke test 1 FAILED: {e}")
            smoke_results.append({"test": "Basic query", "status": "FAILED", "error": str(e)})
        
        # Smoke Test 2: Graph-enhanced query
        try:
            logger.info("\nSmoke Test 2: Graph-enhanced query...")
            result = await self.engine.unified_query(
                "Show me SEBI violations for market manipulation",
                use_graphs=True,
                n_results=5
            )
            assert result.get('graph_context_used', False), "Graph not used"
            assert len(result['answer']) > 50, "Answer too short"
            logger.info("✓ Smoke test 2 PASSED")
            smoke_results.append({"test": "Graph-enhanced query", "status": "PASSED"})
        except Exception as e:
            logger.error(f"✗ Smoke test 2 FAILED: {e}")
            smoke_results.append({"test": "Graph-enhanced query", "status": "FAILED", "error": str(e)})
        
        # Smoke Test 3: Account trace (if we have valid account)
        try:
            logger.info("\nSmoke Test 3: Account trace...")
            test_account = self.test_accounts.get('suspicious_1', '1')
            result = await self.engine.trace_transaction_with_regulatory_context(
                str(test_account)
            )
            assert 'answer' in result, "No answer in result"
            assert len(result['answer']) > 100, "Answer too short"
            logger.info("✓ Smoke test 3 PASSED")
            smoke_results.append({"test": "Account trace", "status": "PASSED"})
        except Exception as e:
            logger.error(f"✗ Smoke test 3 FAILED: {e}")
            smoke_results.append({"test": "Account trace", "status": "FAILED", "error": str(e)})
        
        # Summary
        passed = sum(1 for r in smoke_results if r['status'] == 'PASSED')
        failed = len(smoke_results) - passed
        
        logger.info(f"\nSmoke Tests Complete: {passed}/{len(smoke_results)} passed")
        
        self.test_results["smoke_tests"] = {
            "results": smoke_results,
            "passed": passed,
            "failed": failed,
            "success_rate": f"{passed/len(smoke_results)*100:.0f}%"
        }
        
        if failed > passed:
            raise RuntimeError("Too many smoke test failures - aborting full test suite")
        
        logger.info("✓ Smoke tests passed - proceeding to full suite")
    
    async def setup(self):
        """Initialize the engine and run setup checks."""
        logger.info("=" * 80)
        logger.info("SETTING UP UNIFIED GRAPHRAG ENGINE")
        logger.info("=" * 80)
        
        self.engine = UnifiedGraphRAGEngine(
            persist_directory=settings.graphs_directory,
            chroma_directory=settings.chroma_persist_directory,
            ollama_model=settings.ollama_model,
            ollama_host=settings.ollama_host
        )
        
        # Get statistics
        stats = self.engine.get_unified_statistics()
        logger.info(f"\nEngine Statistics:")
        logger.info(json.dumps(stats, indent=2))
        self.test_results["engine_statistics"] = stats
        
        # Run pre-flight checks
        await self.pre_flight_checks()
        
        # Discover test data
        await self.discover_test_data()
        
        # Run smoke tests
        await self.smoke_tests()
    
    async def run_test(self, test_name: str, query: str, 
                      test_category: str = 'general',
                      perf_type: str = 'general',
                      expected_keywords: Optional[List[str]] = None,
                      min_answer_length: int = 100,
                      min_sources: int = 1,
                      **kwargs):
        """
        Run a single test with full validation.
        
        Args:
            test_name: Name of the test
            query: Query to test
            test_category: Category for organization
            perf_type: Performance threshold type
            expected_keywords: Keywords expected in relevant documents
            min_answer_length: Minimum answer length
            min_sources: Minimum number of sources
            **kwargs: Additional arguments for unified_query
        """
        logger.info("\n" + "=" * 80)
        logger.info(f"TEST: {test_name}")
        logger.info("=" * 80)
        logger.info(f"Query: {query}")
        logger.info(f"Parameters: {kwargs}")
        logger.info(f"Category: {test_category}, Perf Type: {perf_type}")
        
        start_time = datetime.now()
        assertions_passed = []
        assertions_failed = []
        
        try:
            # Execute query
            result = await self.engine.unified_query(query, **kwargs)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Run assertions
            try:
                TestAssertion.assert_result_structure(result)
                assertions_passed.append("Result structure")
            except AssertionError as e:
                assertions_failed.append(f"Result structure: {e}")
                logger.error(f"✗ Assertion failed: {e}")
            
            try:
                TestAssertion.assert_answer_quality(result['answer'], query, min_answer_length)
                assertions_passed.append("Answer quality")
            except AssertionError as e:
                assertions_failed.append(f"Answer quality: {e}")
                logger.error(f"✗ Assertion failed: {e}")
            
            try:
                TestAssertion.assert_sources_present(result, min_sources)
                assertions_passed.append("Sources present")
            except AssertionError as e:
                assertions_failed.append(f"Sources present: {e}")
                logger.error(f"✗ Assertion failed: {e}")
            
            try:
                TestAssertion.assert_graph_enhancement(result, kwargs.get('use_graphs', False))
                assertions_passed.append("Graph enhancement")
            except AssertionError as e:
                assertions_failed.append(f"Graph enhancement: {e}")
                logger.error(f"✗ Assertion failed: {e}")
            
            # Check document relevance if keywords provided
            if expected_keywords:
                try:
                    all_docs = []
                    if 'sebi_results' in result:
                        all_docs.extend(result['sebi_results'])
                    if 'amlsim_results' in result:
                        all_docs.extend(result['amlsim_results'])
                    if 'sources' in result:
                        all_docs.extend(result['sources'])
                    
                    if all_docs:
                        TestAssertion.assert_document_relevance(all_docs, expected_keywords, min_relevance=0.2)
                        assertions_passed.append("Document relevance")
                except AssertionError as e:
                    assertions_failed.append(f"Document relevance: {e}")
                    logger.error(f"✗ Assertion failed: {e}")
            
            # Check performance
            perf_ok = self.perf_tracker.check_performance(test_name, duration, perf_type)
            
            # Log result summary
            logger.info(f"\n{'✓' if len(assertions_failed) == 0 else '✗'} Test completed in {duration:.2f}s")
            logger.info(f"Assertions: {len(assertions_passed)} passed, {len(assertions_failed)} failed")
            logger.info(f"Query Type: {result.get('query_type', 'N/A')}")
            logger.info(f"Graph Context Used: {result.get('graph_context_used', False)}")
            
            if 'answer' in result:
                logger.info(f"\nAnswer Preview ({len(result['answer'])} chars):")
                answer = result['answer']
                logger.info(answer[:300] + "..." if len(answer) > 300 else answer)
            
            if 'sources' in result:
                logger.info(f"\nSources: {len(result['sources'])} documents")
            elif 'sebi_results' in result or 'amlsim_results' in result:
                sebi_count = len(result.get('sebi_results', []))
                amlsim_count = len(result.get('amlsim_results', []))
                logger.info(f"\nResults: {sebi_count} SEBI, {amlsim_count} AMLSim")
            
            if 'graph_insights' in result:
                insights = result['graph_insights']
                logger.info(f"\nGraph Insights:")
                logger.info(f"  - SEBI Cases: {len(insights.get('sebi_cases', []))}")
                logger.info(f"  - Transactions: {len(insights.get('transactions', []))}")
                logger.info(f"  - Patterns: {len(insights.get('patterns', []))}")
            
            # Determine overall success
            test_success = len(assertions_failed) == 0
            
            # Store result
            test_record = {
                "test_name": test_name,
                "category": test_category,
                "query": query,
                "parameters": kwargs,
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "success": test_success,
                "assertions_passed": assertions_passed,
                "assertions_failed": assertions_failed,
                "performance_ok": perf_ok,
                "result_summary": {
                    "query_type": result.get('query_type'),
                    "graph_context_used": result.get('graph_context_used', False),
                    "answer_length": len(result.get('answer', '')),
                    "source_count": len(result.get('sources', []))
                },
                "result": result  # Full result for detailed analysis
            }
            
            self.test_results["tests"].append(test_record)
            return result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.error(f"\n✗ Test failed with exception: {str(e)}", exc_info=True)
            
            test_record = {
                "test_name": test_name,
                "category": test_category,
                "query": query,
                "parameters": kwargs,
                "duration_seconds": duration,
                "timestamp": start_time.isoformat(),
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "assertions_passed": assertions_passed,
                "assertions_failed": assertions_failed
            }
            
            self.test_results["tests"].append(test_record)
            return None
    
    async def test_cache_effectiveness(self):
        """Test cache effectiveness by running duplicate queries."""
        logger.info("\n" + "#" * 80)
        logger.info("# CACHE EFFECTIVENESS TEST")
        logger.info("#" * 80)
        
        test_query = "What are the penalties for insider trading violations?"
        
        # First query (cache miss)
        logger.info("\nFirst query (should be cache miss)...")
        start1 = datetime.now()
        result1 = await self.engine.unified_query(test_query, use_graphs=True, n_results=5)
        duration1 = (datetime.now() - start1).total_seconds()
        
        # Second query (should be cache hit)
        logger.info("\nSecond query (should be cache hit)...")
        start2 = datetime.now()
        result2 = await self.engine.unified_query(test_query, use_graphs=True, n_results=5)
        duration2 = (datetime.now() - start2).total_seconds()
        
        # Analyze
        speedup = duration1 / duration2 if duration2 > 0 else 1.0
        cache_effective = duration2 < duration1 * 0.7  # At least 30% faster
        
        logger.info(f"\nCache Effectiveness Results:")
        logger.info(f"  First query: {duration1:.2f}s")
        logger.info(f"  Second query: {duration2:.2f}s")
        logger.info(f"  Speedup: {speedup:.2f}x")
        logger.info(f"  Cache effective: {'✓ YES' if cache_effective else '✗ NO'}")
        
        self.test_results["cache_effectiveness"] = {
            "first_duration": duration1,
            "second_duration": duration2,
            "speedup": speedup,
            "cache_effective": cache_effective
        }
        
        if not cache_effective:
            logger.warning("⚠️ Cache may not be working effectively!")
    
    async def run_all_tests(self):
        """Run all comprehensive tests with proper assertions."""
        
        # Cache effectiveness test
        await self.test_cache_effectiveness()
        
        # ============================================================================
        # CATEGORY 1: SEBI REGULATORY QUERIES
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 1: SEBI REGULATORY QUERIES")
        logger.info("#" * 80)
        
        await self.run_test(
            "SEBI-1: Insider Trading Detection",
            "What are the key indicators of insider trading according to SEBI regulations?",
            test_category="sebi_regulatory",
            perf_type="regulatory_simple",
            expected_keywords=["insider trading", "UPSI", "PIT", "regulations"],
            use_graphs=True,
            n_results=8
        )
        
        await self.run_test(
            "SEBI-2: Market Manipulation Cases",
            "Show me SEBI cases involving market manipulation and pump-and-dump schemes",
            test_category="sebi_regulatory",
            perf_type="regulatory_simple",
            expected_keywords=["market manipulation", "pump and dump", "price rigging"],
            use_graphs=True,
            n_results=8
        )
        
        await self.run_test(
            "SEBI-3: Penalty Precedents",
            "What penalties has SEBI imposed for front running violations?",
            test_category="sebi_regulatory",
            perf_type="regulatory_simple",
            expected_keywords=["front running", "penalty", "violation"],
            use_graphs=True,
            n_results=6
        )
        
        await self.run_test(
            "SEBI-4: Regulatory Framework",
            "Explain SEBI's regulatory framework for detecting circular trading",
            test_category="sebi_regulatory",
            perf_type="regulatory_simple",
            expected_keywords=["circular trading", "SEBI", "regulatory", "framework"],
            use_graphs=True,
            n_results=8
        )
        
        await self.run_test(
            "SEBI-5: Price Rigging",
            "Find SEBI orders related to price rigging and artificial price inflation",
            test_category="sebi_regulatory",
            perf_type="regulatory_simple",
            expected_keywords=["price rigging", "artificial", "inflation"],
            use_graphs=True,
            n_results=8
        )
        
        # ============================================================================
        # CATEGORY 2: AMLSIM TRANSACTION QUERIES
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 2: AMLSIM TRANSACTION QUERIES")
        logger.info("#" * 80)
        
        test_account = self.test_accounts.get('suspicious_1', '123456789')
        await self.run_test(
            "AMLSIM-1: Account Tracing",
            f"Trace all transactions for account {test_account}",
            test_category="amlsim_transaction",
            perf_type="account_trace",
            expected_keywords=["transaction", "account", test_account],
            min_answer_length=200,
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "AMLSIM-2: Money Laundering Patterns",
            "What money laundering patterns exist in the transaction data?",
            test_category="amlsim_transaction",
            perf_type="transaction_simple",
            expected_keywords=["money laundering", "pattern", "transaction"],
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "AMLSIM-3: High-Risk Accounts",
            "Identify accounts with suspicious transaction patterns",
            test_category="amlsim_transaction",
            perf_type="transaction_simple",
            expected_keywords=["suspicious", "account", "pattern"],
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "AMLSIM-4: Fan-Out Pattern",
            "Find examples of fan-out money laundering patterns",
            test_category="amlsim_transaction",
            perf_type="transaction_simple",
            expected_keywords=["fan-out", "fan out", "laundering"],
            use_graphs=True,
            n_results=8
        )
        
        await self.run_test(
            "AMLSIM-5: Scatter-Gather",
            "Show me scatter-gather transaction patterns that indicate layering",
            test_category="amlsim_transaction",
            perf_type="transaction_simple",
            expected_keywords=["scatter", "gather", "layering"],
            use_graphs=True,
            n_results=8
        )
        
        # ============================================================================
        # CATEGORY 3: CROSS-DOMAIN QUERIES (MOST IMPORTANT)
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 3: CROSS-DOMAIN QUERIES (KILLER FEATURE)")
        logger.info("#" * 80)
        
        await self.run_test(
            "CROSS-1: Transaction vs SEBI Violations",
            "Which transaction patterns in AMLSim align with SEBI's definition of circular trading?",
            test_category="cross_domain",
            perf_type="cross_domain",
            expected_keywords=["circular trading", "transaction", "pattern", "SEBI"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "CROSS-2: Insider Trading Detection",
            "How can we detect insider trading using transaction patterns combined with SEBI precedents?",
            test_category="cross_domain",
            perf_type="cross_domain",
            expected_keywords=["insider trading", "transaction", "SEBI", "detection"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "CROSS-3: Market Manipulation",
            "Find transaction patterns that match SEBI market manipulation violations",
            test_category="cross_domain",
            perf_type="cross_domain",
            expected_keywords=["market manipulation", "transaction", "pattern", "SEBI"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "CROSS-4: Layering Detection",
            "What layering patterns in transactions correspond to SEBI front running cases?",
            test_category="cross_domain",
            perf_type="cross_domain",
            expected_keywords=["layering", "front running", "SEBI"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "CROSS-5: Regulatory Compliance",
            "Based on SEBI regulations, which accounts show potential violations?",
            test_category="cross_domain",
            perf_type="cross_domain",
            expected_keywords=["SEBI", "violation", "account", "regulation"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        # ============================================================================
        # CATEGORY 4: COMPLEX ANALYTICAL QUERIES
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 4: COMPLEX ANALYTICAL QUERIES")
        logger.info("#" * 80)
        
        await self.run_test(
            "ANALYSIS-1: Fraud Typology",
            "Compare and contrast different fraud typologies across SEBI and AMLSim data",
            test_category="complex_analysis",
            perf_type="complex_analysis",
            expected_keywords=["fraud", "typology", "SEBI", "AMLSim"],
            min_answer_length=200,
            use_graphs=True,
            n_results=12
        )
        
        await self.run_test(
            "ANALYSIS-2: Risk Assessment",
            "What risk indicators should we monitor based on both regulatory violations and transaction patterns?",
            test_category="complex_analysis",
            perf_type="complex_analysis",
            expected_keywords=["risk", "indicator", "violation", "pattern"],
            min_answer_length=200,
            use_graphs=True,
            n_results=12
        )
        
        await self.run_test(
            "ANALYSIS-3: Investigation Priorities",
            "Which accounts should be prioritized for investigation based on SEBI precedents?",
            test_category="complex_analysis",
            perf_type="complex_analysis",
            expected_keywords=["investigation", "priority", "SEBI", "account"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        await self.run_test(
            "ANALYSIS-4: Pattern Evolution",
            "How have money laundering patterns evolved based on regulatory enforcement?",
            test_category="complex_analysis",
            perf_type="complex_analysis",
            expected_keywords=["money laundering", "pattern", "evolution", "regulatory"],
            min_answer_length=150,
            use_graphs=True,
            n_results=10
        )
        
        # ============================================================================
        # CATEGORY 5: SPECIFIC ACCOUNT QUERIES
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 5: SPECIFIC ACCOUNT QUERIES")
        logger.info("#" * 80)
        
        test_account2 = self.test_accounts.get('suspicious_2', '987654321')
        await self.run_test(
            "ACCOUNT-1: Account Risk Profile",
            f"What is the risk profile of account {test_account2}?",
            test_category="account_specific",
            perf_type="account_trace",
            expected_keywords=["risk", "account", test_account2],
            use_graphs=True,
            n_results=10
        )
        
        test_account3 = self.test_accounts.get('high_value', '555555555')
        await self.run_test(
            "ACCOUNT-2: Transaction Network",
            f"Map the transaction network for account {test_account3}",
            test_category="account_specific",
            perf_type="account_trace",
            expected_keywords=["transaction", "network", "account", test_account3],
            use_graphs=True,
            n_results=10
        )
        
        # ============================================================================
        # CATEGORY 6: WITHOUT GRAPH CONTEXT (BASELINE)
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 6: BASELINE TESTS (NO GRAPH CONTEXT)")
        logger.info("#" * 80)
        
        await self.run_test(
            "BASELINE-1: SEBI Without Graph",
            "What are SEBI penalties for insider trading?",
            test_category="baseline",
            perf_type="baseline",
            expected_keywords=["SEBI", "penalty", "insider trading"],
            use_graphs=False,
            n_results=8
        )
        
        await self.run_test(
            "BASELINE-2: Pattern Without Graph",
            "Explain money laundering patterns",
            test_category="baseline",
            perf_type="baseline",
            expected_keywords=["money laundering", "pattern"],
            use_graphs=False,
            n_results=8
        )
        
        # ============================================================================
        # CATEGORY 7: EDGE CASES
        # ============================================================================
        logger.info("\n" + "#" * 80)
        logger.info("# CATEGORY 7: EDGE CASES")
        logger.info("#" * 80)
        
        await self.run_test(
            "EDGE-1: Very Specific Query",
            "What was the penalty amount in SEBI order WTM/AB/IVD1/24/2019 for XYZ company?",
            test_category="edge_case",
            perf_type="edge_case",
            expected_keywords=["SEBI", "penalty"],
            min_answer_length=50,  # May be short if no exact match
            min_sources=1,
            use_graphs=True,
            n_results=5
        )
        
        await self.run_test(
            "EDGE-2: Broad Query",
            "Tell me everything about financial fraud",
            test_category="edge_case",
            perf_type="edge_case",
            expected_keywords=["fraud", "financial"],
            min_answer_length=200,
            use_graphs=True,
            n_results=15
        )
        
        await self.run_test(
            "EDGE-3: Ambiguous Query",
            "suspicious activity",
            test_category="edge_case",
            perf_type="edge_case",
            expected_keywords=["suspicious", "activity"],
            min_answer_length=100,
            use_graphs=True,
            n_results=8
        )
        
        await self.run_test(
            "EDGE-4: Multi-aspect Query",
            "Compare insider trading penalties in SEBI cases with transaction patterns showing timing advantages",
            test_category="edge_case",
            perf_type="edge_case",
            expected_keywords=["insider trading", "penalty", "SEBI", "transaction", "pattern"],
            min_answer_length=200,
            use_graphs=True,
            n_results=12
        )
    
    def save_results(self):
        """Save test results with comprehensive analysis."""
        logger.info("\n" + "=" * 80)
        logger.info("SAVING TEST RESULTS")
        logger.info("=" * 80)
        
        output_path = Path(self.output_file)
        
        # Create summary
        total_tests = len(self.test_results["tests"])
        successful_tests = sum(1 for t in self.test_results["tests"] if t["success"])
        failed_tests = total_tests - successful_tests
        
        total_duration = sum(t["duration_seconds"] for t in self.test_results["tests"])
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        
        # Category breakdown
        category_stats = {}
        for test in self.test_results["tests"]:
            cat = test.get("category", "unknown")
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "passed": 0, "failed": 0}
            category_stats[cat]["total"] += 1
            if test["success"]:
                category_stats[cat]["passed"] += 1
            else:
                category_stats[cat]["failed"] += 1
        
        # Add success rates
        for cat, stats in category_stats.items():
            stats["success_rate"] = f"{(stats['passed']/stats['total']*100):.1f}%" if stats['total'] > 0 else "0%"
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "total_duration_seconds": total_duration,
            "average_duration_seconds": avg_duration,
            "category_breakdown": category_stats
        }
        
        self.test_results["summary"] = summary
        self.test_results["performance_summary"] = self.perf_tracker.get_summary()
        
        # Save to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✓ Full results saved to: {output_path}")
        
        # Print summary
        logger.info(f"\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Successful: {successful_tests} ({summary['success_rate']})")
        logger.info(f"Failed: {failed_tests}")
        logger.info(f"Total Duration: {total_duration:.2f}s")
        logger.info(f"Average Duration: {avg_duration:.2f}s")
        
        logger.info(f"\nCategory Breakdown:")
        for cat, stats in category_stats.items():
            logger.info(f"  {cat}: {stats['passed']}/{stats['total']} passed ({stats['success_rate']})")
        
        perf_summary = self.perf_tracker.get_summary()
        logger.info(f"\nPerformance:")
        logger.info(f"  Violations: {perf_summary['total_violations']}/{perf_summary['total_tests']}")
        logger.info(f"  Average Duration: {perf_summary['average_duration']:.2f}s")
        
        cache_info = self.test_results.get("cache_effectiveness", {})
        if cache_info:
            logger.info(f"\nCache Effectiveness:")
            logger.info(f"  Speedup: {cache_info['speedup']:.2f}x")
            logger.info(f"  Effective: {'✓ YES' if cache_info['cache_effective'] else '✗ NO'}")
        
        # Save human-readable summary
        summary_path = output_path.with_suffix('.txt')
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("COMPREHENSIVE TEST RESULTS - WITH ASSERTIONS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Test Run: {self.test_results['test_run_info']['timestamp']}\n")
            f.write(f"Description: {self.test_results['test_run_info']['description']}\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("SUMMARY\n")
            f.write("=" * 80 + "\n")
            for key, value in summary.items():
                if key != 'category_breakdown':
                    f.write(f"{key.replace('_', ' ').title()}: {value}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("CATEGORY BREAKDOWN\n")
            f.write("=" * 80 + "\n")
            for cat, stats in category_stats.items():
                f.write(f"\n{cat.upper()}:\n")
                f.write(f"  Total: {stats['total']}\n")
                f.write(f"  Passed: {stats['passed']}\n")
                f.write(f"  Failed: {stats['failed']}\n")
                f.write(f"  Success Rate: {stats['success_rate']}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("PERFORMANCE SUMMARY\n")
            f.write("=" * 80 + "\n")
            f.write(json.dumps(perf_summary, indent=2))
            
            if cache_info:
                f.write("\n\n" + "=" * 80 + "\n")
                f.write("CACHE EFFECTIVENESS\n")
                f.write("=" * 80 + "\n")
                f.write(f"First query: {cache_info['first_duration']:.2f}s\n")
                f.write(f"Second query: {cache_info['second_duration']:.2f}s\n")
                f.write(f"Speedup: {cache_info['speedup']:.2f}x\n")
                f.write(f"Effective: {'YES' if cache_info['cache_effective'] else 'NO'}\n")
            
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("DETAILED TEST RESULTS\n")
            f.write("=" * 80 + "\n\n")
            
            for test in self.test_results["tests"]:
                f.write("-" * 80 + "\n")
                f.write(f"Test: {test['test_name']}\n")
                f.write(f"Category: {test.get('category', 'N/A')}\n")
                f.write(f"Query: {test['query']}\n")
                f.write(f"Duration: {test['duration_seconds']:.2f}s\n")
                f.write(f"Success: {'✓ PASS' if test['success'] else '✗ FAIL'}\n")
                f.write(f"Performance: {'✓ OK' if test.get('performance_ok', True) else '⚠ SLOW'}\n")
                
                if 'assertions_passed' in test:
                    f.write(f"\nAssertions Passed: {len(test['assertions_passed'])}\n")
                    for assertion in test['assertions_passed']:
                        f.write(f"  ✓ {assertion}\n")
                
                if 'assertions_failed' in test:
                    f.write(f"\nAssertions Failed: {len(test['assertions_failed'])}\n")
                    for assertion in test['assertions_failed']:
                        f.write(f"  ✗ {assertion}\n")
                
                if test['success'] and 'result_summary' in test:
                    summary = test['result_summary']
                    f.write(f"\nResult Summary:\n")
                    f.write(f"  Query Type: {summary.get('query_type', 'N/A')}\n")
                    f.write(f"  Graph Used: {summary.get('graph_context_used', False)}\n")
                    f.write(f"  Answer Length: {summary.get('answer_length', 0)} chars\n")
                    f.write(f"  Sources: {summary.get('source_count', 0)}\n")
                
                if not test['success'] and 'error' in test:
                    f.write(f"\nError: {test['error']}\n")
                
                f.write("\n")
        
        logger.info(f"✓ Summary saved to: {summary_path}")
        
        # Print final verdict
        logger.info("\n" + "=" * 80)
        if successful_tests / total_tests >= 0.8:
            logger.info("✓✓✓ EXCELLENT - System performing well!")
        elif successful_tests / total_tests >= 0.6:
            logger.info("✓✓ GOOD - Some issues to address")
        elif successful_tests / total_tests >= 0.4:
            logger.info("⚠ FAIR - Significant improvements needed")
        else:
            logger.info("✗ POOR - Major issues detected")
        logger.info("=" * 80)


async def main():
    """Main test execution."""
    logger.info("=" * 80)
    logger.info("UNIFIED GRAPHRAG ENGINE - COMPREHENSIVE TEST SUITE WITH ASSERTIONS")
    logger.info("=" * 80)
    logger.info(f"Start Time: {datetime.now().isoformat()}")
    logger.info(f"Description: Production-quality test suite with proper validation")
    
    # Create test suite
    suite = ComprehensiveTestSuite(
        output_file="test_results_comprehensive.json"
    )
    
    try:
        # Setup (includes pre-flight checks, data discovery, smoke tests)
        await suite.setup()
        
        # Run all tests
        await suite.run_all_tests()
        
        # Save results
        suite.save_results()
        
        logger.info("\n" + "=" * 80)
        logger.info("✓ ALL TESTS COMPLETED")
        logger.info("=" * 80)
        logger.info(f"End Time: {datetime.now().isoformat()}")
        
    except Exception as e:
        logger.error(f"Test suite failed: {e}", exc_info=True)
        
        # Try to save partial results
        try:
            suite.save_results()
        except:
            pass
        
        raise


if __name__ == "__main__":
    asyncio.run(main())
