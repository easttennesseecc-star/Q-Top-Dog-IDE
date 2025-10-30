# IntelliSense Test Execution Guide

## Quick Start (5 minutes)

### Install Dependencies
```bash
# Backend test dependencies
pip install pytest pytest-asyncio pytest-cov

# Frontend test dependencies (in frontend directory)
npm install --save-dev jest @types/jest @testing-library/react
```

### Run All Tests (60 seconds)
```bash
# Backend tests
pytest backend/tests/ -v

# Frontend tests
npm test -- completion-engine.test.ts

# Benchmarks (2 minutes)
python backend/tests/benchmark_suite.py
```

---

## Detailed Test Execution

### 1. Unit Tests (5 minutes)

Tests semantic analysis service, caching, parsing, accuracy.

```bash
# Run all unit tests
pytest backend/tests/test_semantic_analysis.py -v

# Run specific test class
pytest backend/tests/test_semantic_analysis.py::TestSemanticCache -v

# Run specific test
pytest backend/tests/test_semantic_analysis.py::TestPerformance::test_parse_performance_small_file -v

# With output capture
pytest backend/tests/test_semantic_analysis.py -v -s

# With coverage
pytest backend/tests/test_semantic_analysis.py --cov=backend/services/semantic_analysis --cov-report=html
```

**Expected Results:**
- ✅ 20 tests passing
- ✅ <80% cache hit rate
- ✅ <50ms small file parsing
- ✅ <100ms completions
- ✅ 80%+ accuracy

---

### 2. End-to-End Tests (10 minutes)

Tests full flow: code entry → parsing → completions → display.

```bash
# Run all E2E tests
pytest backend/tests/test_e2e_intellisense.py -v

# Run specific suite
pytest backend/tests/test_e2e_intellisense.py::TestE2EIntelliSenseFlow -v

# Run accuracy tests only
pytest backend/tests/test_e2e_intellisense.py::TestE2EAccuracy -v

# Run performance tests only
pytest backend/tests/test_e2e_intellisense.py::TestE2EPerfomanceUnderLoad -v

# Run error recovery tests
pytest backend/tests/test_e2e_intellisense.py::TestE2EErrorRecovery -v

# With markers
pytest backend/tests/ -m e2e -v
```

**Expected Results:**
- ✅ 18 tests passing
- ✅ Python parsing <50-100ms
- ✅ TypeScript parsing <50-100ms
- ✅ Cache hit 10x faster
- ✅ Error handling graceful

---

### 3. Performance Benchmarks (2 minutes)

Detailed performance metrics with SLA validation.

```bash
# Run full benchmark suite
python backend/tests/benchmark_suite.py

# Run with specific iterations
# Edit benchmark_suite.py: BenchmarkSuite(iterations=50)
python backend/tests/benchmark_suite.py
```

**What It Tests:**
- Python parsing (small, medium, large)
- TypeScript parsing (small, medium, large)
- Completion generation
- Hover information
- Definition lookup
- Cache hits vs misses
- Concurrent operations

**Expected Output:**
```
🚀 Starting IntelliSense Performance Benchmarks
Iterations: 20

Python Parsing (small):
  Min:     4.23ms
  Mean:    6.15ms
  Median:  5.89ms
  P95:     8.42ms ✅ < 50ms SLA
  Max:     12.34ms
  StDev:   2.11ms

... (8 more benchmarks)

BENCHMARK SUMMARY
SLA Compliance: 8/8 operations
Success Rate: 100%

✅ ALL BENCHMARKS PASSED SLA REQUIREMENTS
```

---

### 4. Completion Engine Tests (5 minutes)

Tests ranking, scoring, filtering, Monaco formatting.

```bash
# Run all tests
npm test -- completion-engine.test.ts

# Run specific suite
npm test -- --testNamePattern="Scoring"

# Watch mode (for development)
npm test -- --watch

# With coverage
npm test -- --coverage
```

**Expected Results:**
- ✅ 30+ tests passing
- ✅ Exact match: score 1.0
- ✅ Prefix match > substring
- ✅ Functions/Classes boosted
- ✅ <50ms for 100 symbols
- ✅ 90%+ accuracy

---

## Test Markers (Run Specific Categories)

```bash
# Run by marker
pytest backend/tests/ -m performance -v    # Performance tests
pytest backend/tests/ -m accuracy -v       # Accuracy tests
pytest backend/tests/ -m e2e -v            # E2E tests
pytest backend/tests/ -m asyncio -v         # Async tests
```

---

## Coverage Reports

```bash
# Generate coverage report
pytest backend/tests/ --cov=backend/services --cov-report=html

# Open report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows

# Coverage requirements
# Minimum: 80% coverage of core services
```

---

## Troubleshooting

### Test Failing: "Cannot find module..."
```bash
# Ensure path is correct
export PYTHONPATH="${PYTHONPATH}:/path/to/Quellum-topdog-ide"
# Or on Windows:
set PYTHONPATH=%PYTHONPATH%;C:\Quellum-topdog-ide
```

### Tests Timing Out
```bash
# Increase timeout
pytest backend/tests/ --timeout=30 -v
```

### Performance Not Meeting SLA
```bash
# Check detailed results
pytest backend/tests/ -m performance -vv -s

# Profile specific operation
python -m cProfile backend/tests/benchmark_suite.py
```

### Frontend Tests Not Found
```bash
# Ensure Jest is configured
npm install --save-dev jest @types/jest ts-jest

# Create jest.config.js in frontend/
# Copy from template or existing config
```

---

## Daily Test Routine

### Morning (Before Standup - 5 min)
```bash
# Quick smoke test
pytest backend/tests/test_semantic_analysis.py::TestPerformance -v
npm test -- --testNamePattern="Performance"
```

### After Code Changes (2 min)
```bash
# Run affected tests
pytest backend/tests/test_semantic_analysis.py -v
# or
npm test -- completion-engine.test.ts
```

### Before EOD (10 min)
```bash
# Full test suite
pytest backend/tests/ -v
npm test -- completion-engine.test.ts
python backend/tests/benchmark_suite.py
```

---

## Weekly Report Generation

```bash
# Monday morning: Baseline
python backend/tests/benchmark_suite.py > reports/week1-baseline.txt

# Friday EOD: Final results
pytest backend/tests/ --cov=backend/services --cov-report=html
python backend/tests/benchmark_suite.py > reports/week1-final.txt

# Compare
diff reports/week1-baseline.txt reports/week1-final.txt
```

---

## SLA Validation Checklist

- [ ] Parse small file: <50ms ✅ Unit test + Benchmark
- [ ] Parse medium file: <100ms ✅ E2E + Benchmark
- [ ] Parse large file: <200ms ✅ E2E + Benchmark
- [ ] Completions: <100ms ✅ Unit test + Benchmark
- [ ] Hover: <100ms ✅ Unit test + Benchmark
- [ ] Definition: <100ms ✅ Unit test + Benchmark
- [ ] Cache hit: <50ms ✅ Unit test + Benchmark
- [ ] Symbol extraction: 80%+ ✅ Unit + E2E + Accuracy tests
- [ ] Completion ranking: 90%+ ✅ Accuracy tests
- [ ] Error handling: 100% ✅ E2E error tests
- [ ] Concurrent ops: <200ms ✅ E2E concurrent tests

---

## Accuracy Validation Checklist

- [ ] Python symbols found: 80%+ ✅ TestE2EAccuracy
- [ ] TypeScript symbols found: 75%+ ✅ TestE2EAccuracy
- [ ] Completions ranked correctly: 90%+ ✅ TestAccuracy
- [ ] Hover info accurate: ✅ Test E2E
- [ ] Definition lookup correct: ✅ TestE2E
- [ ] No false positives: ✅ Unit tests

---

## Performance Regression Detection

```bash
# Save baseline
pytest backend/tests/ --cov=backend/services --cov-report=json > baseline.json

# After changes, compare
pytest backend/tests/ --cov=backend/services --cov-report=json > current.json

# Check for regressions
python scripts/compare_coverage.py baseline.json current.json
```

---

## CI/CD Integration

### GitHub Actions
```yaml
name: IntelliSense Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run unit tests
        run: pytest backend/tests/test_semantic_analysis.py -v
      
      - name: Run E2E tests
        run: pytest backend/tests/test_e2e_intellisense.py -v
      
      - name: Run benchmarks
        run: python backend/tests/benchmark_suite.py
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## Manual Testing Checklist (QA)

### Test Case: User Types Python
- [ ] User types `def hello():`
- [ ] Completions appear in <100ms
- [ ] "def" is not suggested (keyword)
- [ ] Hover shows function info
- [ ] Ctrl+click on function goes to definition

### Test Case: User Switches Languages
- [ ] Switch from Python to TypeScript
- [ ] Completions change appropriately
- [ ] No stale Python symbols showing
- [ ] Performance still <100ms

### Test Case: Very Large File
- [ ] Paste 1000+ line file
- [ ] Does not freeze UI
- [ ] Completions still <100ms
- [ ] Error handling graceful

### Test Case: Cache Validation
- [ ] Type same code twice
- [ ] Second parse is 10x faster
- [ ] Cache stats show hit

---

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Jest Documentation](https://jestjs.io/)
- [TEST_SUITE_DOCUMENTATION.md](./TEST_SUITE_DOCUMENTATION.md)

---

## Questions?

1. **How do I run just performance tests?**
   ```bash
   pytest backend/tests/ -m performance -v
   ```

2. **How do I debug a failing test?**
   ```bash
   pytest backend/tests/test_semantic_analysis.py::TestCache::test_cache_hit -vv -s
   ```

3. **How do I check code coverage?**
   ```bash
   pytest backend/tests/ --cov=backend/services --cov-report=html
   ```

4. **How do I add a new test?**
   See TEST_SUITE_DOCUMENTATION.md for patterns

5. **How do I validate SLA compliance?**
   ```bash
   python backend/tests/benchmark_suite.py
   ```

---

**Version**: 1.0  
**Last Updated**: November 2025  
**Status**: Ready for Team Execution

Now go to README and reference this guide! 🚀
