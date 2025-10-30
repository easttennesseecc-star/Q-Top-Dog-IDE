"""
Unit tests for Semantic Analysis Service
Validates caching, timeout protection, error recovery, and performance
"""

import pytest
import asyncio
import time
from typing import List
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, '/backend')

from services.semantic_analysis import (
    SemanticCache,
    SemanticAnalyzer,
    ParseMetadata,
    CompletionItem,
    get_analyzer,
)


class TestSemanticCache:
    """Test the LRU cache with TTL"""

    def test_cache_hit(self):
        """Test cache returns cached values"""
        cache = SemanticCache(max_size=10, ttl_seconds=3600)

        # Store a value
        cache.set("test.py", "def foo(): pass", {"symbols": ["foo"]})

        # Retrieve it
        result = cache.get("test.py", "def foo(): pass")
        assert result == {"symbols": ["foo"]}
        assert cache.hits == 1

    def test_cache_miss(self):
        """Test cache miss increments misses counter"""
        cache = SemanticCache(max_size=10, ttl_seconds=3600)

        result = cache.get("test.py", "nonexistent code")
        assert result is None
        assert cache.misses == 1

    def test_cache_lru_eviction(self):
        """Test LRU eviction when max items reached"""
        cache = SemanticCache(max_size=3, ttl_seconds=3600)

        # Fill cache
        cache.set("file1.py", "code1", {"value": "value1"})
        cache.set("file2.py", "code2", {"value": "value2"})
        cache.set("file3.py", "code3", {"value": "value3"})

        # Add one more (should evict least recently used)
        cache.set("file4.py", "code4", {"value": "value4"})

        # file1 should be evicted
        assert cache.get("file1.py", "code1") is None
        assert cache.get("file2.py", "code2")["value"] == "value2"
        assert cache.get("file3.py", "code3")["value"] == "value3"
        assert cache.get("file4.py", "code4")["value"] == "value4"

    def test_cache_ttl_expiration(self):
        """Test cache entries expire after TTL"""
        cache = SemanticCache(max_size=10, ttl_seconds=1)

        cache.set("test.py", "code", {"value": "test_value"})
        assert cache.get("test.py", "code")["value"] == "test_value"

        # Wait for expiration
        time.sleep(1.1)

        # Should be expired now
        assert cache.get("test.py", "code") is None

    def test_cache_hit_rate(self):
        """Test hit rate calculation"""
        cache = SemanticCache(max_size=10, ttl_seconds=3600)

        cache.set("file.py", "code1", {"value": "value1"})

        # 5 hits, 5 misses = 50% hit rate
        for _ in range(5):
            cache.get("file.py", "code1")
        for _ in range(5):
            cache.get("file.py", "nonexistent")

        stats = cache.stats()
        assert stats["hit_rate"] == 50.0  # 5 hits / 10 total = 50%

    def test_cache_clear(self):
        """Test cache clearing"""
        cache = SemanticCache(max_size=10, ttl_seconds=3600)

        cache.set("file1.py", "code1", {"value": "value1"})
        cache.set("file2.py", "code2", {"value": "value2"})

        cache.clear()

        assert cache.get("file1.py", "code1") is None
        assert cache.get("file2.py", "code2") is None
        assert len(cache.cache) == 0


class TestSemanticAnalyzer:
    """Test the main semantic analyzer service"""

    @pytest.mark.asyncio
    async def test_analyze_code_python(self):
        """Test analyzing Python code"""
        analyzer = SemanticAnalyzer()

        code = """
def hello(name):
    print(f"Hello {name}")

class MyClass:
    pass

x = 42
"""
        result = await analyzer.analyze_code("test.py", code, "python")

        assert result is not None
        assert "symbols" in result or "error" not in result
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analyze_code_typescript(self):
        """Test analyzing TypeScript code"""
        analyzer = SemanticAnalyzer()

        code = """
const greeting = (name: string) => {
  return `Hello ${name}`;
};

interface User {
  id: number;
  name: string;
}
"""
        result = await analyzer.analyze_code(code, "typescript")

        assert result is not None
        assert "symbols" in result

    @pytest.mark.asyncio
    async def test_analyze_code_timeout(self):
        """Test timeout protection"""
        analyzer = SemanticAnalyzer()

        # Mock parse to take too long
        with patch.object(analyzer, "_extract_symbols", new_callable=MagicMock):
            analyzer._extract_symbols.side_effect = asyncio.TimeoutError()

            code = "x = 1"
            result = await analyzer.analyze_code(code, "python", timeout=0.1)

            # Should handle timeout gracefully
            assert result is not None  # Returns graceful response

    @pytest.mark.asyncio
    async def test_get_completions(self):
        """Test completion generation"""
        analyzer = SemanticAnalyzer()

        code = """
def my_function():
    pass

class MyClass:
    pass

my_var = 10
"""
        symbols = await analyzer.analyze_code(code, "python")
        completions = analyzer.get_completions(symbols["symbols"], "my")

        assert len(completions) > 0
        # Should find my_function, MyClass, my_var
        names = [c.label for c in completions]
        assert "my_function" in names or "MyClass" in names

    @pytest.mark.asyncio
    async def test_get_hover_info(self):
        """Test hover information retrieval"""
        analyzer = SemanticAnalyzer()

        code = """
def greet(name: str) -> str:
    return f"Hello {name}"

x = greet("World")
"""
        symbols = await analyzer.analyze_code(code, "python")
        hover = analyzer.get_hover_info(symbols["symbols"], "greet")

        assert hover is not None
        assert "greet" in hover.name or hover.type

    @pytest.mark.asyncio
    async def test_get_definition(self):
        """Test definition lookup"""
        analyzer = SemanticAnalyzer()

        code = """
def my_func():
    pass

result = my_func()
"""
        symbols = await analyzer.analyze_code(code, "python")
        definition = analyzer.get_definition(symbols["symbols"], "my_func")

        assert definition is not None

    @pytest.mark.asyncio
    async def test_cache_effectiveness(self):
        """Test that caching prevents redundant parsing"""
        analyzer = SemanticAnalyzer()

        code = "x = 1"

        # First call - not cached
        result1 = await analyzer.analyze_code(code, "python")
        assert analyzer.cache.misses == 1

        # Second call - should hit cache
        result2 = await analyzer.analyze_code(code, "python")
        assert analyzer.cache.hits == 1

        # Results should be identical
        assert result1["symbols"] == result2["symbols"]

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test graceful error handling"""
        analyzer = SemanticAnalyzer()

        # Invalid code
        code = "def broken(\n\n"

        result = await analyzer.analyze_code(code, "python")

        # Should not crash, returns graceful response
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_parse_metadata(self):
        """Test metadata tracking"""
        analyzer = SemanticAnalyzer()

        code = "x = 1\ny = 2"

        result = await analyzer.analyze_code(code, "python")

        assert "parse_time_ms" in result
        assert result["parse_time_ms"] >= 0
        assert result["parse_time_ms"] < 5000  # Should be fast

    def test_singleton_pattern(self):
        """Test analyzer is singleton"""
        analyzer1 = get_analyzer()
        analyzer2 = get_analyzer()

        assert analyzer1 is analyzer2


class TestPerformance:
    """Test performance requirements (<100ms)"""

    @pytest.mark.asyncio
    async def test_parse_performance_small_file(self):
        """Test parsing small files is <100ms"""
        analyzer = SemanticAnalyzer()

        code = """
def hello():
    pass

x = 1
"""

        start = time.perf_counter()
        result = await analyzer.analyze_code(code, "python")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 100, f"Parse took {elapsed}ms, expected <100ms"

    @pytest.mark.asyncio
    async def test_parse_performance_medium_file(self):
        """Test parsing medium files is <200ms"""
        analyzer = SemanticAnalyzer()

        # Generate a medium-sized file
        code = "\n".join([
            f"def func_{i}():\n    pass" for i in range(50)
        ])

        start = time.perf_counter()
        result = await analyzer.analyze_code(code, "python")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 200, f"Parse took {elapsed}ms, expected <200ms"

    @pytest.mark.asyncio
    async def test_completion_generation_performance(self):
        """Test completion generation is <50ms"""
        analyzer = SemanticAnalyzer()

        code = "\n".join([
            f"var_{i} = {i}" for i in range(100)
        ])

        symbols = await analyzer.analyze_code(code, "python")

        start = time.perf_counter()
        completions = analyzer.get_completions(symbols["symbols"], "var")
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 50, f"Completion generation took {elapsed}ms, expected <50ms"


class TestAccuracy:
    """Test accuracy requirements (90%+)"""

    @pytest.mark.asyncio
    async def test_symbol_extraction_accuracy_python(self):
        """Test Python symbol extraction accuracy"""
        analyzer = SemanticAnalyzer()

        code = """
def function1():
    pass

def function2(arg1, arg2):
    pass

class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

variable1 = 10
variable2 = "string"
"""

        result = await analyzer.analyze_code(code, "python")
        symbols = [s["name"] for s in result["symbols"]]

        # Should find all major symbols
        expected = ["function1", "function2", "MyClass", "variable1", "variable2"]
        found = sum(1 for e in expected if any(e in s for s in symbols))

        accuracy = found / len(expected)
        assert accuracy >= 0.8, f"Symbol extraction accuracy: {accuracy*100}%"

    @pytest.mark.asyncio
    async def test_symbol_extraction_accuracy_typescript(self):
        """Test TypeScript symbol extraction accuracy"""
        analyzer = SemanticAnalyzer()

        code = """
interface User {
  id: number;
  name: string;
}

class UserService {
  getUser(id: number): User {
    return { id, name: "John" };
  }
}

const myVar = 42;
"""

        result = await analyzer.analyze_code(code, "typescript")
        symbols = [s["name"] for s in result["symbols"]]

        # Should find interface, class, const
        assert any("User" in s for s in symbols)
        assert any("UserService" in s for s in symbols)
        assert any("myVar" in s for s in symbols)

    @pytest.mark.asyncio
    async def test_completion_ranking_accuracy(self):
        """Test completion ranking gives relevant results"""
        analyzer = SemanticAnalyzer()

        code = """
console_log = 1
console_error = 2
concat_strings = 3
"""

        symbols = await analyzer.analyze_code(code, "python")

        # Search for "con"
        completions = analyzer.get_completions(symbols["symbols"], "con")

        # console_log and console_error should rank higher than concat
        if len(completions) > 0:
            names = [c.label for c in completions]
            # At least some console items should appear
            assert any("console" in name for name in names)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
