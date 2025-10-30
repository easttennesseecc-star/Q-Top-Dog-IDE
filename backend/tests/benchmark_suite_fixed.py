"""
Performance Benchmarking for IntelliSense
Simple async benchmarks with SLA validation
"""

import asyncio
import time
import statistics
from typing import List
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.semantic_analysis import SemanticAnalyzer


class BenchmarkResult:
    """Results from a benchmark operation"""
    
    def __init__(self, name: str, times: List[float]):
        self.name = name
        self.times = times
        self.min = min(times)
        self.max = max(times)
        self.mean = statistics.mean(times)
        self.median = statistics.median(times)
        self.count = len(times)
        
    def __str__(self):
        return f"{self.name}: min={self.min:.2f}ms, mean={self.mean:.2f}ms, median={self.median:.2f}ms, max={self.max:.2f}ms"


async def benchmark_parsing(analyzer: SemanticAnalyzer, size: str, iterations: int = 5):
    """Benchmark code parsing"""
    
    if size == "small":
        code = "def foo(): pass\ndef bar(): pass"
    elif size == "medium":
        code = "\n".join([f"def func_{i}(): pass" for i in range(50)])
    else:  # large
        code = "\n".join([f"def func_{i}(): pass" for i in range(200)])
    
    times = []
    for i in range(iterations):
        start = time.time()
        result = await analyzer.analyze_code(f"test_{i}.py", code, "python")
        elapsed_ms = (time.time() - start) * 1000
        times.append(elapsed_ms)
    
    return BenchmarkResult(f"Parse {size} file", times)


async def benchmark_completions(analyzer: SemanticAnalyzer, iterations: int = 5):
    """Benchmark completion generation"""
    
    code = "\n".join([f"symbol_{i} = {i}" for i in range(100)])
    
    times = []
    for i in range(iterations):
        start = time.time()
        result = await analyzer.analyze_code(f"test_{i}.py", code, "python")
        elapsed_ms = (time.time() - start) * 1000
        times.append(elapsed_ms)
    
    return BenchmarkResult("Completions (100 symbols)", times)


async def benchmark_cache_hit(analyzer: SemanticAnalyzer, iterations: int = 10):
    """Benchmark cache hit performance"""
    
    code = "def foo(): pass"
    file_path = "test_cache.py"
    
    # First call - populate cache
    await analyzer.analyze_code(file_path, code, "python")
    
    # Subsequent calls - cache hits
    times = []
    for i in range(iterations):
        start = time.time()
        result = await analyzer.analyze_code(file_path, code, "python")
        elapsed_ms = (time.time() - start) * 1000
        times.append(elapsed_ms)
    
    return BenchmarkResult("Cache hit", times)


async def benchmark_concurrent(analyzer: SemanticAnalyzer, count: int = 10):
    """Benchmark concurrent requests"""
    
    code = "def foo(): pass"
    
    start = time.time()
    tasks = [
        analyzer.analyze_code(f"file_{i}.py", code, "python")
        for i in range(count)
    ]
    results = await asyncio.gather(*tasks)
    elapsed_ms = (time.time() - start) * 1000
    
    return BenchmarkResult(f"Concurrent ({count} files)", [elapsed_ms])


async def run_benchmarks():
    """Execute all benchmarks"""
    
    print("\n" + "="*70)
    print("Performance Benchmark Suite")
    print("="*70 + "\n")
    
    analyzer = SemanticAnalyzer()
    results = []
    
    # Parse benchmarks
    print("[Running] Parse benchmarks...")
    for size in ["small", "medium", "large"]:
        result = await benchmark_parsing(analyzer, size)
        results.append(result)
        print(f"  {result}")
    
    # Completions benchmark
    print("\n[Running] Completions benchmark...")
    result = await benchmark_completions(analyzer)
    results.append(result)
    print(f"  {result}")
    
    # Cache hit benchmark
    print("\n[Running] Cache hit benchmark...")
    result = await benchmark_cache_hit(analyzer)
    results.append(result)
    print(f"  {result}")
    
    # Concurrent benchmark
    print("\n[Running] Concurrent operations benchmark...")
    result = await benchmark_concurrent(analyzer)
    results.append(result)
    print(f"  {result}")
    
    # SLA Validation
    print("\n" + "="*70)
    print("SLA Validation Summary")
    print("="*70)
    
    sla_targets = {
        "Parse small file": 50,
        "Parse medium file": 100,
        "Parse large file": 200,
        "Completions (100 symbols)": 100,
        "Cache hit": 50,
    }
    
    compliant = 0
    total = 0
    
    for result in results:
        if result.name in sla_targets:
            target = sla_targets[result.name]
            compliant_flag = result.median < target
            status = "[PASS]" if compliant_flag else "[FAIL]"
            print(f"{status} {result.name}: {result.median:.2f}ms < {target}ms SLA")
            
            total += 1
            if compliant_flag:
                compliant += 1
    
    print("\n" + "="*70)
    print(f"SLA Compliance: {compliant}/{total} operations")
    print("="*70 + "\n")
    
    return compliant == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_benchmarks())
        exit(0 if success else 1)
    except Exception as e:
        print(f"[ERROR] Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
