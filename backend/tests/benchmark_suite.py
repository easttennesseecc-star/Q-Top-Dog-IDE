"""
Performance Benchmarking Suite for IntelliSense
Validates <100ms SLA across all operations
"""

import asyncio
import time
import statistics
from typing import List, Dict, Callable
import sys

sys.path.insert(0, '/backend')

from services.semantic_analysis import get_analyzer
from services.typescript_language_server import get_ts_server
from services.python_language_server import get_py_server


class BenchmarkResult:
    """Results from a benchmark run"""
    def __init__(self, operation: str, times: List[float]):
        self.operation = operation
        self.times = times
        self.min = min(times)
        self.max = max(times)
        self.mean = statistics.mean(times)
        self.median = statistics.median(times)
        self.stdev = statistics.stdev(times) if len(times) > 1 else 0
        self.p95 = sorted(times)[int(len(times) * 0.95)]
        self.p99 = sorted(times)[int(len(times) * 0.99)]

    def __str__(self):
        return f"""
{self.operation}:
  Min:     {self.min:.2f}ms
  Mean:    {self.mean:.2f}ms
  Median:  {self.median:.2f}ms
  P95:     {self.p95:.2f}ms
  P99:     {self.p99:.2f}ms
  Max:     {self.max:.2f}ms
  StDev:   {self.stdev:.2f}ms
"""

    @property
    def sla_compliant(self) -> bool:
        """Check if operation meets SLA targets"""
        # Different SLAs for different operations
        # Parsing: <50ms
        # Completions: <100ms
        # Hover/Def: <100ms
        if "parse" in self.operation.lower():
            return self.p95 < 50 and self.max < 150
        else:
            return self.p95 < 100 and self.max < 200


class BenchmarkSuite:
    """Run comprehensive benchmarks"""

    def __init__(self, iterations: int = 20):
        self.iterations = iterations
        self.results: List[BenchmarkResult] = []

    async def benchmark_python_parsing(self):
        """Benchmark Python code parsing"""
        analyzer = get_analyzer()

        test_cases = [
            ("small", "x = 1\ny = 2\nz = 3"),
            ("medium", "\n".join([f"def func_{i}(): pass" for i in range(50)])),
            ("large", "\n".join([
                f"""def function_{i}(arg1, arg2):
    x = arg1
    y = arg2
    return x + y
""" for i in range(200)
            ])),
        ]

        for size, code in test_cases:
            times = []
            for _ in range(self.iterations):
                start = time.perf_counter()
                await analyzer.analyze_code(code, "python")
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)

            result = BenchmarkResult(f"Python Parsing ({size})", times)
            self.results.append(result)
            print(result)

    async def benchmark_typescript_parsing(self):
        """Benchmark TypeScript code parsing"""
        analyzer = get_analyzer()

        test_cases = [
            ("small", "const x = 1;"),
                ("medium", "\n".join([f"const func_{i} = () => {{}};" for i in range(50)])),
            ("large", "\n".join([
                f"""const function_{i} = (arg1: number, arg2: number) => {{
  const x = arg1;
  const y = arg2;
  return x + y;
}};""" for i in range(200)
            ])),
        ]

        for size, code in test_cases:
            times = []
            for _ in range(self.iterations):
                start = time.perf_counter()
                await analyzer.analyze_code(code, "typescript")
                elapsed = (time.perf_counter() - start) * 1000
                times.append(elapsed)

            result = BenchmarkResult(f"TypeScript Parsing ({size})", times)
            self.results.append(result)
            print(result)

    async def benchmark_completions(self):
        """Benchmark completion generation"""
        analyzer = get_analyzer()

        code = "\n".join([f"variable_{i} = {i}" for i in range(100)])

        # Parse once
        parse_result = await analyzer.analyze_code(code, "python")

        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            analyzer.get_completions(parse_result["symbols"], "var")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        result = BenchmarkResult("Completion Generation (100 symbols)", times)
        self.results.append(result)
        print(result)

    async def benchmark_hover_info(self):
        """Benchmark hover information retrieval"""
        analyzer = get_analyzer()

        code = """
def my_function(param1: str, param2: int) -> str:
    '''This is a function'''
    return f"Result: {param1}"
"""

        parse_result = await analyzer.analyze_code(code, "python")

        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            analyzer.get_hover_info(parse_result["symbols"], "my_function")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        result = BenchmarkResult("Hover Information", times)
        self.results.append(result)
        print(result)

    async def benchmark_definition_lookup(self):
        """Benchmark definition lookup"""
        analyzer = get_analyzer()

        code = """
class Calculator:
    def add(self, a, b):
        return a + b

class Service:
    def __init__(self):
        self.calc = Calculator()
"""

        parse_result = await analyzer.analyze_code(code, "python")

        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            analyzer.get_definition(parse_result["symbols"], "Calculator")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        result = BenchmarkResult("Definition Lookup", times)
        self.results.append(result)
        print(result)

    async def benchmark_cache_hit(self):
        """Benchmark cache hits"""
        analyzer = get_analyzer()

        code = "x = 1\ny = 2"

        # Populate cache
        await analyzer.analyze_code(code, "python")

        # Benchmark cache hits
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter()
            await analyzer.analyze_code(code, "python")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        result = BenchmarkResult("Cache Hit", times)
        self.results.append(result)
        print(result)

    async def benchmark_cache_miss(self):
        """Benchmark cache misses (different code)"""
        analyzer = get_analyzer()

        times = []
        for i in range(self.iterations):
            code = f"x_{i} = {i}"
            start = time.perf_counter()
            await analyzer.analyze_code(code, "python")
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        result = BenchmarkResult("Cache Miss", times)
        self.results.append(result)
        print(result)

    async def benchmark_concurrent_operations(self):
        """Benchmark concurrent parsing"""
        analyzer = get_analyzer()

        codes = [
            f"def func_{i}(): pass\nx_{i} = {i}"
            for i in range(10)
        ]

        times = []
        for _ in range(self.iterations // 10):
            start = time.perf_counter()
            await asyncio.gather(*[
                analyzer.analyze_code(code, "python")
                for code in codes
            ])
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        result = BenchmarkResult("Concurrent Parsing (10 files)", times)
        self.results.append(result)
        print(result)

    async def run_all_benchmarks(self):
        """Run all benchmarks"""
        print("🚀 Starting IntelliSense Performance Benchmarks\n")
        print(f"Iterations: {self.iterations}\n")

        await self.benchmark_python_parsing()
        await self.benchmark_typescript_parsing()
        await self.benchmark_completions()
        await self.benchmark_hover_info()
        await self.benchmark_definition_lookup()
        await self.benchmark_cache_hit()
        await self.benchmark_cache_miss()
        await self.benchmark_concurrent_operations()

        self.print_summary()

    def print_summary(self):
        """Print summary and SLA compliance"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60 + "\n")

        sla_compliant = sum(1 for r in self.results if r.sla_compliant)
        total = len(self.results)

        print(f"SLA Compliance: {sla_compliant}/{total} operations")
        print(f"Success Rate: {sla_compliant/total*100:.1f}%\n")

        if sla_compliant == total:
            print("✅ ALL BENCHMARKS PASSED SLA REQUIREMENTS\n")
        else:
            print("❌ SOME BENCHMARKS FAILED SLA REQUIREMENTS\n")
            print("Failed operations:")
            for result in self.results:
                if not result.sla_compliant:
                    print(f"  - {result.operation}: P95={result.p95:.2f}ms")

        print("\nTop 5 Slowest Operations:")
        sorted_results = sorted(self.results, key=lambda r: r.p95, reverse=True)
        for i, result in enumerate(sorted_results[:5], 1):
            print(f"  {i}. {result.operation}: {result.p95:.2f}ms (P95)")

        print("\nTop 5 Fastest Operations:")
        for i, result in enumerate(sorted_results[-5:], 1):
            print(f"  {i}. {result.operation}: {result.p95:.2f}ms (P95)")


async def main():
    """Run benchmarks"""
    suite = BenchmarkSuite(iterations=20)
    await suite.run_all_benchmarks()


if __name__ == "__main__":
    asyncio.run(main())
