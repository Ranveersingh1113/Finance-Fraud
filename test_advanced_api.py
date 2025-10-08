"""
Test script for the Advanced API Server with Ollama integration.
"""
import sys
import logging
import asyncio
import requests
import json
from pathlib import Path
import time

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_BASE_URL = "http://localhost:8001"

def test_api_health():
    """Test the health endpoint."""
    logger.info("=== Testing API Health ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info("✅ API Health Check PASSED")
            logger.info(f"Status: {health_data['status']}")
            logger.info(f"Version: {health_data['version']}")
            logger.info(f"Models Available: {health_data['models_available']}")
            return True
        else:
            logger.error(f"❌ API Health Check FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API Health Check FAILED: {e}")
        return False

def test_simple_query():
    """Test simple query endpoint."""
    logger.info("=== Testing Simple Query ===")
    
    try:
        query = "What are the common patterns of insider trading violations?"
        response = requests.get(
            f"{API_BASE_URL}/query/simple",
            params={"query": query, "n_results": 3},
            timeout=120  # Longer timeout for Ollama
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Simple Query PASSED")
            logger.info(f"Query: {result['query']}")
            logger.info(f"Answer: {result['answer'][:200]}...")
            logger.info(f"Confidence: {result['confidence']:.3f}")
            logger.info(f"Evidence Count: {result['evidence_count']}")
            return True
        else:
            logger.error(f"❌ Simple Query FAILED: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Simple Query FAILED: {e}")
        return False

def test_advanced_query():
    """Test advanced query endpoint with full response."""
    logger.info("=== Testing Advanced Query ===")
    
    try:
        query_data = {
            "query": "How does SEBI handle market manipulation cases?",
            "n_results": 5,
            "include_metadata": True
        }
        
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=query_data,
            timeout=120  # Longer timeout for Ollama
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Advanced Query PASSED")
            logger.info(f"Query: {result['query']}")
            logger.info(f"Answer: {result['answer'][:300]}...")
            logger.info(f"Confidence: {result['confidence_score']:.3f}")
            logger.info(f"Query Type: {result['query_type']}")
            logger.info(f"Processing Time: {result['processing_time']:.2f}s")
            logger.info(f"Evidence Count: {len(result['evidence'])}")
            logger.info(f"Model Used: {result['metadata']['model_used']}")
            return True
        else:
            logger.error(f"❌ Advanced Query FAILED: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Advanced Query FAILED: {e}")
        return False

def test_case_management():
    """Test case management endpoints."""
    logger.info("=== Testing Case Management ===")
    
    try:
        # Test case creation
        case_data = {
            "case_id": "TEST_CASE_001",
            "description": "Test case for API validation",
            "priority": "medium",
            "analyst": "test_analyst",
            "tags": ["test", "api", "validation"]
        }
        
        response = requests.post(
            f"{API_BASE_URL}/cases",
            json=case_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("✅ Case Creation PASSED")
            logger.info(f"Case ID: {result['case_id']}")
            logger.info(f"Status: {result['status']}")
            
            # Test case retrieval
            case_id = result['case_id']
            get_response = requests.get(f"{API_BASE_URL}/cases/{case_id}", timeout=30)
            
            if get_response.status_code == 200:
                case_info = get_response.json()
                logger.info("✅ Case Retrieval PASSED")
                logger.info(f"Retrieved Case: {case_info['case_id']}")
                return True
            else:
                logger.error(f"❌ Case Retrieval FAILED: {get_response.status_code}")
                return False
        else:
            logger.error(f"❌ Case Creation FAILED: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Case Management FAILED: {e}")
        return False

def test_system_stats():
    """Test system statistics endpoint."""
    logger.info("=== Testing System Stats ===")
    
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=30)
        
        if response.status_code == 200:
            stats = response.json()
            logger.info("✅ System Stats PASSED")
            logger.info(f"System Status: {stats['system_status']}")
            
            rag_stats = stats.get('rag_engine_stats', {})
            logger.info(f"Database Stats: {rag_stats.get('database_stats', {})}")
            logger.info(f"Models Available: {rag_stats.get('models_available', {})}")
            return True
        else:
            logger.error(f"❌ System Stats FAILED: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ System Stats FAILED: {e}")
        return False

def main():
    """Run all API tests."""
    logger.info("🚀 Starting Advanced API Server Tests")
    
    # Wait for server to be ready
    logger.info("Waiting for API server to be ready...")
    time.sleep(5)
    
    tests = [
        ("Health Check", test_api_health),
        ("Simple Query", test_simple_query),
        ("Advanced Query", test_advanced_query),
        ("Case Management", test_case_management),
        ("System Stats", test_system_stats)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All API tests PASSED!")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests FAILED")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
