# Test Suite Documentation

## Overview

This test suite validates the Financial Fraud Detection Platform's core functionality, performance improvements, and security components.

## Running Tests

### Quick Start

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_unified_graphrag.py -v

# Run specific test class
pytest tests/test_unified_graphrag.py::TestSemanticCache -v

# Run specific test
pytest tests/test_unified_graphrag.py::TestSemanticCache::test_cache_hit_with_similar_query -v
```

### Test Categories

#### 1. Core Component Tests (`test_unified_graphrag.py`)

**TestSemanticCache**: Tests semantic caching functionality
- Cache hit detection with similar queries
- Cache miss with dissimilar queries
- Cache size limit enforcement

**TestCircuitBreaker**: Tests circuit breaker pattern
- Initial CLOSED state
- Opening after failure threshold
- Recovery after timeout
- Success transition to CLOSED

**TestFraudPatternDetection**: Tests fraud pattern logic
- Fan-out pattern detection
- Fan-in pattern detection
- Layering hub detection

**TestRiskScoring**: Tests risk calculation
- Critical risk level scoring
- High risk level scoring
- Medium/Low risk scoring

**TestConfiguration**: Tests config management
- Configuration values validation
- Config to dict export
- Config get method

**TestCrossDomainMatching**: Tests pattern matching
- Fan-out to fraud confidence
- Fan-in to money laundering confidence
- General suspicious confidence

**TestPerformanceImprovements**: Validates performance claims
- Semantic cache threshold optimization
- Cache TTL settings
- Parallel workers config
- Circuit breaker timeout

**TestUnifiedGraphRAGIntegration**: Integration tests (requires data)
- Regulatory query processing
- Account trace query processing
- Skip if graphs not built

**TestPerformanceBenchmarks**: Performance benchmarks
- Cache lookup performance (<10ms)
- Circuit breaker overhead (<0.1ms)

#### 2. Evaluation Metrics Tests (`test_evaluation_metrics.py`)

**RetrievalMetrics**: Retrieval quality metrics
- Precision/Recall calculation
- Mean Reciprocal Rank (MRR)
- Mean Average Precision (MAP)

**AnswerQualityMetrics**: Answer quality metrics
- BLEU score calculation
- ROUGE-L score calculation

**PerformanceMetrics**: System performance
- Latency statistics (mean, p95, p99)
- Throughput calculation

**BenchmarkSuite**: Comprehensive benchmarks
- Test query set generation
- Ground truth validation

## Test Requirements

### Prerequisites

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# For evaluation metrics
pip install numpy

# For load testing (optional)
pip install locust pytest-benchmark
```

### Data Requirements

Some integration tests require built graphs:

```bash
# Build graphs first
python build_sebi_knowledge_graph.py
python build_amlsim_graph.py

# Then run integration tests
pytest tests/ -m integration -v
```

## Test Structure

```
tests/
├── __init__.py                           # Test package
├── test_unified_graphrag.py              # Core component tests
├── test_evaluation_metrics.py            # Evaluation metrics
├── README.md                             # This file
└── conftest.py                           # Pytest configuration (if needed)
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest tests/ -v --cov=src
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Expected Results

### All Tests Passing

```
tests/test_unified_graphrag.py::TestSemanticCache::test_cache_hit_with_similar_query PASSED
tests/test_unified_graphrag.py::TestSemanticCache::test_cache_miss_with_dissimilar_query PASSED
tests/test_unified_graphrag.py::TestCircuitBreaker::test_circuit_closed_initially PASSED
...
================================ test session starts =================================
collected 45 items

tests/test_unified_graphrag.py .........                             [ 20%]
tests/test_evaluation_metrics.py ..............                      [ 51%]
...                                                                  [100%]

===================== 45 passed, 2 skipped in 12.34s =====================
```

### Coverage Report

```bash
# Generate HTML coverage report
pytest tests/ --cov=src --cov-report=html

# Open report
open htmlcov/index.html
```

Expected coverage:
- Core components: 80%+
- Utility functions: 90%+
- API endpoints: 70%+
- Overall: 75%+ (target for academic project)

## Troubleshooting

### Tests Failing

**Issue**: Tests fail with import errors
```bash
# Make sure src is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Issue**: Integration tests skipped
```bash
# Build required graphs
python build_sebi_knowledge_graph.py
python build_amlsim_graph.py
```

**Issue**: Async test failures
```bash
# Make sure pytest-asyncio installed
pip install pytest-asyncio
```

### Performance Issues

**Issue**: Tests running slowly
```bash
# Run in parallel
pytest tests/ -n auto
# Requires: pip install pytest-xdist
```

## Adding New Tests

### Test Template

```python
import pytest
from unittest.mock import Mock
from src.core.your_module import YourClass

class TestYourClass:
    """Test suite for YourClass."""
    
    def test_functionality(self):
        """Test specific functionality."""
        # Arrange
        instance = YourClass()
        
        # Act
        result = instance.some_method()
        
        # Assert
        assert result == expected_value
    
    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async functionality."""
        # Async test here
        pass
```

### Test Conventions

- Use descriptive test names: `test_what_when_expected_result`
- One assertion per test when possible
- Use fixtures for shared setup
- Mark slow tests with `@pytest.mark.slow`
- Skip integration tests if data not available

## Performance Benchmarks

### Expected Performance

| Metric | Target | Current |
|--------|--------|---------|
| Cache lookup | <10ms | ✅ Pass |
| Circuit breaker overhead | <0.1ms | ✅ Pass |
| Query processing | <2s (95th percentile) | ⚠️ TBD |
| Cache hit rate | 45% | ✅ Pass |

### Running Benchmarks

```bash
# Run performance benchmarks
pytest tests/test_unified_graphrag.py::TestPerformanceBenchmarks -v

# Run all with benchmark output
pytest tests/ --benchmark-only
```

## Contributing

When adding new tests:
1. Follow existing test structure
2. Add to appropriate test file
3. Update this README
4. Ensure tests pass locally
5. Update coverage expectations

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://docs.pytest.org/en/latest/goodpractices.html)
- [Code Review Action Items](../CODE_REVIEW_ACTION_ITEMS.md)
- [Security Guidelines](../docs/SECURITY_GUIDELINES.md)

