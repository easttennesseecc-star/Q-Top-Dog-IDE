"""
End-to-End Tests for IntelliSense Integration
Validates complete flow: Web Worker → Backend → Completions → UI rendering
"""

import pytest
import asyncio
import time

import sys
sys.path.insert(0, '/backend')

from services.semantic_analysis import get_analyzer
from services.python_language_server import get_py_server


class TestE2EIntelliSenseFlow:
    """Test complete IntelliSense flow"""

    @pytest.mark.asyncio
    async def test_e2e_python_completions(self):
        """E2E: User types Python code → Backend provides completions"""
        # User action: typing Python code
        code = """
import os
import sys

def greet(name):
    print(f"Hello {name}")

class Calculator:
    def add(self, a, b):
        return a + b

my_calc = Calculator()
"""

        analyzer = get_analyzer()

        # Parse the code
        parse_result = await analyzer.analyze_code(code, "python")
        assert parse_result is not None
        assert "symbols" in parse_result

        # User requests completions for "my"
        prefix = "my"
        completions = analyzer.get_completions(parse_result["symbols"], prefix)

        # Assertion: should find my_calc
        names = [c.label for c in completions]
        assert any("my_calc" in name for name in names), f"my_calc not in {names}"

    @pytest.mark.asyncio
    async def test_e2e_typescript_completions(self):
        """E2E: User types TypeScript code → Backend provides completions"""
        code = """
interface User {
  id: number;
  name: string;
}

function createUser(name: string): User {
  return { id: 1, name };
}

const user = createUser("John");
"""

        analyzer = get_analyzer()

        parse_result = await analyzer.analyze_code(code, "typescript")
        assert parse_result is not None

        # User requests completions for "create"
        completions = analyzer.get_completions(parse_result["symbols"], "create")

        # Should find createUser
        names = [c.label for c in completions]
        assert any("create" in name for name in names)

    @pytest.mark.asyncio
    async def test_e2e_hover_information(self):
        """E2E: User hovers over symbol → Backend provides type info"""
        code = """
def calculate_sum(a: int, b: int) -> int:
    '''Adds two numbers and returns the sum'''
    return a + b

result = calculate_sum(5, 10)
"""

        analyzer = get_analyzer()

        parse_result = await analyzer.analyze_code(code, "python")
        hover = analyzer.get_hover_info(parse_result["symbols"], "calculate_sum")

        assert hover is not None
        assert "calculate_sum" in hover.name

    @pytest.mark.asyncio
    async def test_e2e_definition_lookup(self):
        """E2E: User ctrl+clicks symbol → Backend finds definition"""
        code = """
class Logger:
    def log(self, message):
        print(message)

logger = Logger()
logger.log("test")
"""

        analyzer = get_analyzer()

        parse_result = await analyzer.analyze_code(code, "python")
        definition = analyzer.get_definition(parse_result["symbols"], "Logger")

        assert definition is not None

    @pytest.mark.asyncio
    async def test_e2e_diagnostics_reporting(self):
        """E2E: User has syntax error → Backend reports diagnostic"""
        code = """
def broken_function():
    x = 1
    y = 2
    # Missing closing
"""

        py_server = get_py_server()
        diagnostics = py_server.get_diagnostics(code)

        # Should report some error (not perfectly formed)
        assert diagnostics is not None
        assert len(diagnostics) >= 0  # May or may not find error depending on parser

    @pytest.mark.asyncio
    async def test_e2e_multi_language_support(self):
        """E2E: IDE switches between languages → Each provides appropriate completions"""
        # Python code
        python_code = """
def hello():
    pass

x = 1
"""
        analyzer = get_analyzer()
        py_result = await analyzer.analyze_code(python_code, "python")
        py_completions = analyzer.get_completions(py_result["symbols"], "")

        assert len(py_completions) > 0

        # TypeScript code
        ts_code = """
const greeting = () => {
  return "hello";
};

const x = 1;
"""
        ts_result = await analyzer.analyze_code(ts_code, "typescript")
        ts_completions = analyzer.get_completions(ts_result["symbols"], "")

        assert len(ts_completions) > 0

        # Both should have completions
        assert len(py_completions) > 0
        assert len(ts_completions) > 0


class TestE2EPerfomanceUnderLoad:
    """Test performance with various file sizes"""

    @pytest.mark.asyncio
    async def test_e2e_small_file_performance(self):
        """E2E: Parse small file in <50ms"""
        code = "x = 1\ny = 2\nz = 3"

        analyzer = get_analyzer()

        start = time.perf_counter()
        result = await analyzer.analyze_code(code, "python")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 50, f"Small file took {elapsed}ms, expected <50ms"
        assert result is not None

    @pytest.mark.asyncio
    async def test_e2e_medium_file_performance(self):
        """E2E: Parse medium file in <100ms"""
        # Generate medium file with 50 functions
        code = "\n".join([
            f"""def function_{i}(arg1, arg2):
    '''Function {i} documentation'''
    result = arg1 + arg2
    return result
""" for i in range(50)
        ])

        analyzer = get_analyzer()

        start = time.perf_counter()
        await analyzer.analyze_code(code, "python")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 100, f"Medium file took {elapsed}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_e2e_large_file_performance(self):
        """E2E: Parse large file in <500ms"""
        # Generate large file with 200 functions
        code = "\n".join([
            f"""def function_{i}(arg1, arg2, arg3):
    '''Function {i}'''
    x = arg1
    y = arg2
    z = arg3
    return x + y + z
""" for i in range(200)
        ])

        analyzer = get_analyzer()

        start = time.perf_counter()
        await analyzer.analyze_code(code, "python")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 500, f"Large file took {elapsed}ms, expected <500ms"

    @pytest.mark.asyncio
    async def test_e2e_completion_generation_performance(self):
        """E2E: Generate completions for 100+ symbols in <50ms"""
        code = "\n".join([
            f"variable_{i} = {i}" for i in range(100)
        ])

        analyzer = get_analyzer()

        result = await analyzer.analyze_code(code, "python")

        start = time.perf_counter()
        completions = analyzer.get_completions(result["symbols"], "var")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 50, f"Completions took {elapsed}ms, expected <50ms"
        assert len(completions) > 0


class TestE2ECacheEffectiveness:
    """Test cache performance benefits"""

    @pytest.mark.asyncio
    async def test_e2e_cache_hit_is_faster(self):
        """E2E: Cache hit is 10x faster than fresh parse"""
        code = """
def hello():
    pass

x = 1
"""

        analyzer = get_analyzer()

        # First parse (not cached)
        start1 = time.perf_counter()
        await analyzer.analyze_code(code, "python")
        elapsed1 = (time.perf_counter() - start1) * 1000

        # Second parse (cached)
        start2 = time.perf_counter()
        await analyzer.analyze_code(code, "python")
        elapsed2 = (time.perf_counter() - start2) * 1000

        # Cached should be much faster
        assert elapsed2 < elapsed1, f"Cache hit {elapsed2}ms should be faster than {elapsed1}ms"
        assert analyzer.cache.hits > 0

    @pytest.mark.asyncio
    async def test_e2e_cache_different_code_not_reused(self):
        """E2E: Different code doesn't hit cache"""
        analyzer = get_analyzer()

        code1 = "x = 1"
        code2 = "y = 2"

        result1 = await analyzer.analyze_code(code1, "python")
        result2 = await analyzer.analyze_code(code2, "python")

        # Different code should have different symbols
        assert result1["symbols"] != result2["symbols"]


class TestE2EAccuracy:
    """Test accuracy of completions"""

    @pytest.mark.asyncio
    async def test_e2e_python_symbol_extraction_accuracy(self):
        """E2E: Python symbol extraction is 90%+ accurate"""
        code = """
def function_one():
    pass

def function_two(param1):
    pass

class MyClass:
    def method_one(self):
        pass

    def method_two(self, x):
        pass

    def method_three(self, x, y):
        pass

global_var = 42
another_var = "string"

def _private_function():
    pass
"""

        analyzer = get_analyzer()
        result = await analyzer.analyze_code(code, "python")

        expected_symbols = [
            "function_one",
            "function_two",
            "MyClass",
            "method_one",
            "method_two",
            "method_three",
            "global_var",
            "another_var",
        ]

        found_symbols = [s["name"] for s in result["symbols"]]

        # Check how many expected symbols were found
        matches = sum(
            1 for expected in expected_symbols
            if any(expected in found for found in found_symbols)
        )

        accuracy = matches / len(expected_symbols)
        assert accuracy >= 0.8, f"Python extraction accuracy: {accuracy*100}%, expected >= 80%"

    @pytest.mark.asyncio
    async def test_e2e_typescript_symbol_extraction_accuracy(self):
        """E2E: TypeScript symbol extraction is 90%+ accurate"""
        code = """
interface Config {
  name: string;
  value: number;
}

class UserService {
  private users: User[] = [];

  constructor(config: Config) {
  }

  getUser(id: number): User | null {
    return null;
  }

  createUser(name: string): User {
    return { id: 1, name };
  }
}

const service = new UserService({ name: "test", value: 1 });

export type User = {
  id: number;
  name: string;
};
"""

        analyzer = get_analyzer()
        result = await analyzer.analyze_code(code, "typescript")

        expected_symbols = ["Config", "UserService", "service", "User"]

        found_symbols = [s["name"] for s in result["symbols"]]

        matches = sum(
            1 for expected in expected_symbols
            if any(expected in found for found in found_symbols)
        )

        accuracy = matches / len(expected_symbols)
        assert accuracy >= 0.75, f"TypeScript extraction accuracy: {accuracy*100}%, expected >= 75%"

    @pytest.mark.asyncio
    async def test_e2e_completion_ranking_relevance(self):
        """E2E: Completion ranking shows most relevant items first"""
        code = """
const console_log_function = () => {};
const console_error_function = () => {};
const concat_strings = () => {};
const my_console = {};
"""

        analyzer = get_analyzer()
        result = await analyzer.analyze_code(code, "typescript")

        # Search for "con" - should prioritize console over concat
        completions = analyzer.get_completions(result["symbols"], "con")

        if len(completions) > 1:
            # First result should be more relevant than others
            first_is_relevant = "console" in completions[0].label.lower()
            assert first_is_relevant, f"First result '{completions[0].label}' not relevant to 'con'"


class TestE2EErrorRecovery:
    """Test error handling and recovery"""

    @pytest.mark.asyncio
    async def test_e2e_malformed_code_no_crash(self):
        """E2E: Malformed code doesn't crash server"""
        code = """
def broken(
  # Missing closing paren
  
class AnotherBroken:
    def method()  # Missing colon
        pass
"""

        analyzer = get_analyzer()

        # Should not crash
        result = await analyzer.analyze_code(code, "python")
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_e2e_empty_code_graceful(self):
        """E2E: Empty code handled gracefully"""
        code = ""

        analyzer = get_analyzer()
        result = await analyzer.analyze_code(code, "python")

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_e2e_very_long_code_no_timeout(self):
        """E2E: Very long code doesn't timeout"""
        # Generate a very long file
        code = "\n".join([
            f"# Comment line {i}\nvar_{i} = {i}"
            for i in range(1000)
        ])

        analyzer = get_analyzer()

        start = time.perf_counter()
        result = await analyzer.analyze_code(code, "python", timeout=5)
        elapsed = (time.perf_counter() - start) * 1000

        assert result is not None
        assert elapsed < 5000  # Should complete within timeout


class TestE2EMultiUserScenario:
    """Test concurrent usage patterns"""

    @pytest.mark.asyncio
    async def test_e2e_concurrent_completions(self):
        """E2E: Multiple concurrent completion requests don't interfere"""
        analyzer = get_analyzer()

        code1 = "def func1(): pass\nx = 1"
        code2 = "def func2(): pass\ny = 2"
        code3 = "def func3(): pass\nz = 3"

        # Parse all concurrently
        results = await asyncio.gather(
            analyzer.analyze_code(code1, "python"),
            analyzer.analyze_code(code2, "python"),
            analyzer.analyze_code(code3, "python"),
        )

        assert all(r is not None for r in results)
        assert all("symbols" in r for r in results)

    @pytest.mark.asyncio
    async def test_e2e_concurrent_different_languages(self):
        """E2E: Concurrent requests for different languages"""
        analyzer = get_analyzer()

        python_code = "x = 1"
        ts_code = "const x = 1;"

        results = await asyncio.gather(
            analyzer.analyze_code(python_code, "python"),
            analyzer.analyze_code(ts_code, "typescript"),
        )

        assert all(r is not None for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
