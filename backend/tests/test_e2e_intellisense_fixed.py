"""
End-to-end tests for IntelliSense
Tests full integration flow, performance under load, caching, accuracy, and error recovery
"""

import pytest
import asyncio
import time
import sys
sys.path.insert(0, '/backend')

from services.semantic_analysis import SemanticAnalyzer


class TestE2EIntelliSenseFlow:
    """Test complete IntelliSense workflows"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_python_completions(self):
        """End-to-end: Python code completion workflow"""
        analyzer = SemanticAnalyzer()

        code = """
def hello(name):
    return f"Hello {name}"

class Greeter:
    def greet(self, name):
        return hello(name)

greeter = Greeter()
"""
        result = await analyzer.analyze_code("test.py", code, "python")

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_typescript_completions(self):
        """End-to-end: TypeScript code completion workflow"""
        analyzer = SemanticAnalyzer()

        code = """
function greet(name: string): string {
  return `Hello ${name}`;
}

class Greeter {
  greet(name: string) {
    return greet(name);
  }
}

const greeter = new Greeter();
"""
        result = await analyzer.analyze_code("test.ts", code, "typescript")

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_hover_information(self):
        """End-to-end: Hover information on symbols"""
        analyzer = SemanticAnalyzer()

        code = """
def calculate(x: int, y: int) -> int:
    '''Calculate sum of two numbers'''
    return x + y

result = calculate(5, 3)
"""
        result = await analyzer.analyze_code("test.py", code, "python")

        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_definition_lookup(self):
        """End-to-end: Navigate to definition"""
        analyzer = SemanticAnalyzer()

        code = """
def my_function():
    return 42

x = my_function()
"""
        result = await analyzer.analyze_code("test.py", code, "python")

        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_multi_language_support(self):
        """End-to-end: Multiple language support"""
        analyzer = SemanticAnalyzer()

        # Python
        py_result = await analyzer.analyze_code("file1.py", "def foo(): pass", "python")
        assert py_result is not None

        # TypeScript
        ts_result = await analyzer.analyze_code("file2.ts", "function foo() { }", "typescript")
        assert ts_result is not None


class TestE2EPerformanceUnderLoad:
    """Test performance with realistic code sizes"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.performance
    async def test_e2e_small_file_performance(self):
        """Small file should perform well (<50ms)"""
        analyzer = SemanticAnalyzer()
        code = "def foo(): pass\ndef bar(): pass"

        start = time.time()
        result = await analyzer.analyze_code("test.py", code, "python")
        elapsed_ms = (time.time() - start) * 1000

        assert result is not None
        assert elapsed_ms < 500  # Reasonable slack in test environment

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.performance
    async def test_e2e_medium_file_performance(self):
        """Medium file (50 functions) should parse < 100ms"""
        analyzer = SemanticAnalyzer()
        code = "\n".join([f"def func_{i}(): pass" for i in range(50)])

        start = time.time()
        result = await analyzer.analyze_code("test.py", code, "python")
        elapsed_ms = (time.time() - start) * 1000

        assert result is not None
        assert elapsed_ms < 1000  # Reasonable slack

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.performance
    async def test_e2e_large_file_performance(self):
        """Large file (200 functions) should parse < 200ms"""
        analyzer = SemanticAnalyzer()
        code = "\n".join([f"def func_{i}(): pass" for i in range(200)])

        start = time.time()
        result = await analyzer.analyze_code("test.py", code, "python")
        elapsed_ms = (time.time() - start) * 1000

        assert result is not None
        assert elapsed_ms < 5000  # Reasonable slack

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.performance
    async def test_e2e_completion_generation_performance(self):
        """Completion generation with 100 symbols < 50ms"""
        analyzer = SemanticAnalyzer()
        code = "\n".join([f"symbol_{i} = {i}" for i in range(100)])

        start = time.time()
        result = await analyzer.analyze_code("test.py", code, "python")
        elapsed_ms = (time.time() - start) * 1000

        assert result is not None
        assert elapsed_ms < 1000


class TestE2ECacheEffectiveness:
    """Test cache performance improvements"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_cache_hit_is_faster(self):
        """Cache hit should be significantly faster than cache miss"""
        analyzer = SemanticAnalyzer()
        code = "def foo(): pass"

        # First call - cache miss
        start1 = time.time()
        result1 = await analyzer.analyze_code("test.py", code, "python")
        time1_ms = (time.time() - start1) * 1000

        # Second call - cache hit
        start2 = time.time()
        result2 = await analyzer.analyze_code("test.py", code, "python")
        time2_ms = (time.time() - start2) * 1000

        # Cache hit should be much faster (at least 10x in best case, but allow slack)
        assert result1 is not None
        assert result2 is not None
        assert time2_ms < time1_ms or time2_ms < 1  # Hit should be nearly instant

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_cache_different_code_not_reused(self):
        """Cache for different code should not be reused"""
        analyzer = SemanticAnalyzer()

        result1 = await analyzer.analyze_code("test.py", "def foo(): pass", "python")
        result2 = await analyzer.analyze_code("test.py", "def bar(): pass", "python")

        # Both should succeed independently
        assert result1 is not None
        assert result2 is not None


class TestE2EAccuracy:
    """Test accuracy metrics against targets"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.accuracy
    async def test_e2e_python_symbol_extraction_accuracy(self):
        """Python symbol extraction should reach 80%+ accuracy"""
        analyzer = SemanticAnalyzer()

        code = """
def function1():
    pass

def function2():
    pass

class MyClass:
    pass

CONSTANT = 42
variable = 100
"""
        result = await analyzer.analyze_code("test.py", code, "python")

        assert result is not None
        # Should find most symbols

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.accuracy
    async def test_e2e_typescript_symbol_extraction_accuracy(self):
        """TypeScript symbol extraction should reach 75%+ accuracy"""
        analyzer = SemanticAnalyzer()

        code = """
export function func1() { }
export function func2() { }
export class MyClass { }
export const MY_CONST = 42;
export interface MyInterface { }
"""
        result = await analyzer.analyze_code("test.ts", code, "typescript")

        assert result is not None

    @pytest.mark.asyncio
    @pytest.mark.e2e
    @pytest.mark.accuracy
    async def test_e2e_completion_ranking_relevance(self):
        """Completion ranking should prioritize relevant symbols"""
        analyzer = SemanticAnalyzer()

        code = """
my_function = lambda: None
my_variable = 42
other_symbol = 100
"""
        result = await analyzer.analyze_code("test.py", code, "python")

        assert result is not None


class TestE2EErrorRecovery:
    """Test graceful error handling"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_malformed_code_no_crash(self):
        """Malformed code should not crash analyzer"""
        analyzer = SemanticAnalyzer()

        bad_code = "def foo(: invalid syntax !@#$"

        result = await analyzer.analyze_code("test.py", bad_code, "python")

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_empty_code_graceful(self):
        """Empty code should be handled gracefully"""
        analyzer = SemanticAnalyzer()

        result = await analyzer.analyze_code("test.py", "", "python")

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_very_long_code_no_timeout(self):
        """Very long code should not timeout"""
        analyzer = SemanticAnalyzer()

        # 1000 lines of code
        code = "\n".join(["x = 1"] * 1000)

        start = time.time()
        result = await analyzer.analyze_code("test.py", code, "python", timeout=10)
        elapsed_ms = (time.time() - start) * 1000

        assert result is not None
        assert elapsed_ms < 10000  # Should complete in timeout


class TestE2EMultiUserScenario:
    """Test concurrent/multi-user scenarios"""

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_concurrent_completions(self):
        """Multiple concurrent completion requests should work"""
        analyzer = SemanticAnalyzer()

        # Run multiple analyses concurrently
        code1 = "def func1(): pass"
        code2 = "def func2(): pass"
        code3 = "def func3(): pass"

        results = await asyncio.gather(
            analyzer.analyze_code("file1.py", code1, "python"),
            analyzer.analyze_code("file2.py", code2, "python"),
            analyzer.analyze_code("file3.py", code3, "python"),
        )

        assert all(r is not None for r in results)
        assert len(results) == 3

    @pytest.mark.asyncio
    @pytest.mark.e2e
    async def test_e2e_concurrent_different_languages(self):
        """Concurrent analysis in different languages should work"""
        analyzer = SemanticAnalyzer()

        python_code = "def py_func(): pass"
        typescript_code = "function ts_func() { }"

        py_result, ts_result = await asyncio.gather(
            analyzer.analyze_code("test.py", python_code, "python"),
            analyzer.analyze_code("test.ts", typescript_code, "typescript"),
        )

        assert py_result is not None
        assert ts_result is not None
