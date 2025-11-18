"""
Test Suite for Refactoring Engine
Tests all refactoring operations: extract, rename, move
"""

import pytest
from backend.services.refactoring_engine import (
    ASTRefactoringEngine,
    ScopeAnalyzer,
    extract_function_refactor,
    rename_symbol_refactor,
    move_to_file_refactor,
)


class TestScopeAnalyzer:
    """Test scope analysis"""

    def test_function_definition(self):
        """Test function definition detection"""
        import ast
        code = """
def foo():
    x = 1
    return x
"""
        tree = ast.parse(code)
        analyzer = ScopeAnalyzer()
        analyzer.visit(tree)
        
        assert 'foo' in analyzer.definitions
        assert 'x' in analyzer.definitions

    def test_variable_references(self):
        """Test variable reference tracking"""
        import ast
        code = """
x = 1
y = x + 2
z = x * 3
"""
        tree = ast.parse(code)
        analyzer = ScopeAnalyzer()
        analyzer.visit(tree)
        
        assert 'x' in analyzer.definitions
        assert len(analyzer.references.get('x', [])) >= 2


class TestExtractFunction:
    """Test extract function refactoring"""

    def test_extract_simple_block(self):
        """Test extracting simple code block"""
        engine = ASTRefactoringEngine()
        source = """def main():
    x = 1
    y = 2
    z = x + y
    return z
"""
        engine.parse_source(source)
        result = engine.extract_function(
            name="calculate",
            start_line=2,
            end_line=3,
            parameters=[]
        )
        
        assert result.success
        assert "calculate" in result.refactored_source

    def test_extract_with_parameters(self):
        """Test extracting with function parameters"""
        engine = ASTRefactoringEngine()
        source = """def main():
    x = 1
    y = 2
    return x + y
"""
        engine.parse_source(source)
        result = engine.extract_function(
            name="add",
            start_line=4,
            end_line=4,
            parameters=["x", "y"]
        )
        
        assert result.success
        assert "add" in result.refactored_source

    def test_extract_invalid_range(self):
        """Test extracting invalid range"""
        engine = ASTRefactoringEngine()
        source = """x = 1
y = 2
"""
        engine.parse_source(source)
        result = engine.extract_function(
            name="test",
            start_line=10,
            end_line=20,
            parameters=[]
        )
        
        # Should handle gracefully
        assert result is not None

    def test_extract_marks_changes(self):
        """Test that extract marks changes"""
        engine = ASTRefactoringEngine()
        source = """def test():
    a = 1
    b = 2
"""
        engine.parse_source(source)
        result = engine.extract_function(
            name="init",
            start_line=2,
            end_line=3,
            parameters=[]
        )
        
        assert len(result.changes) > 0
        assert result.changes[0]["type"] == "extract_function"


class TestRenameSymbol:
    """Test rename symbol refactoring"""

    def test_rename_simple_variable(self):
        """Test renaming simple variable"""
        engine = ASTRefactoringEngine()
        source = """x = 1
y = x + 2
z = x * 3
"""
        engine.parse_source(source)
        result = engine.rename_symbol("x", "value")
        
        assert result.success
        assert "value" in result.refactored_source
        assert "x = 1" not in result.refactored_source or "value = 1" in result.refactored_source

    def test_rename_function(self):
        """Test renaming function"""
        engine = ASTRefactoringEngine()
        source = """def foo():
    return 42

result = foo()
"""
        engine.parse_source(source)
        result = engine.rename_symbol("foo", "get_answer")
        
        assert result.success
        assert "get_answer" in result.refactored_source

    def test_rename_tracks_changes(self):
        """Test that rename tracks all changes"""
        engine = ASTRefactoringEngine()
        source = """x = 1
y = x
z = x + 1
"""
        engine.parse_source(source)
        result = engine.rename_symbol("x", "value")
        
        assert result.success
        assert len(result.changes) >= 3  # 3 references

    def test_rename_preserves_other_identifiers(self):
        """Test that rename doesn't affect other identifiers"""
        engine = ASTRefactoringEngine()
        source = """x = 1
x_value = 2
result = x + x_value
"""
        engine.parse_source(source)
        result = engine.rename_symbol("x", "num")
        
        assert result.success
        assert "x_value" in result.refactored_source  # Should remain unchanged


class TestMoveToFile:
    """Test move to file refactoring"""

    def test_move_function(self):
        """Test moving function to new file"""
        engine = ASTRefactoringEngine()
        source = """def helper():
    return 42

def main():
    return helper()
"""
        engine.parse_source(source)
        source_result, new_file = engine.move_to_file("helper", "utils.py")
        
        assert source_result.success
        assert new_file is not None
        assert "helper" in new_file
        assert "from utils import helper" in source_result.refactored_source

    def test_move_class(self):
        """Test moving class to new file"""
        engine = ASTRefactoringEngine()
        source = """class Helper:
    def method(self):
        return 42

obj = Helper()
"""
        engine.parse_source(source)
        source_result, new_file = engine.move_to_file("Helper", "models.py")
        
        assert source_result.success
        assert new_file is not None
        assert "class Helper" in new_file

    def test_move_nonexistent_symbol(self):
        """Test moving nonexistent symbol"""
        engine = ASTRefactoringEngine()
        source = """x = 1
y = 2
"""
        engine.parse_source(source)
        source_result, new_file = engine.move_to_file("nonexistent", "utils.py")
        
        assert not source_result.success
        assert new_file is None

    def test_move_adds_import(self):
        """Test that move adds import statement"""
        engine = ASTRefactoringEngine()
        source = """def my_func():
    pass
"""
        engine.parse_source(source)
        source_result, new_file = engine.move_to_file("my_func", "helpers.py")
        
        assert source_result.success
        assert "import my_func" in source_result.refactored_source


class TestParseSource:
    """Test source parsing"""

    def test_parse_valid_python(self):
        """Test parsing valid Python code"""
        engine = ASTRefactoringEngine()
        source = "x = 1\ny = 2\n"
        assert engine.parse_source(source)
        assert engine.tree is not None

    def test_parse_invalid_python(self):
        """Test parsing invalid Python code"""
        engine = ASTRefactoringEngine()
        source = "x = = 1"  # Invalid syntax
        assert not engine.parse_source(source)

    def test_parse_empty_source(self):
        """Test parsing empty source"""
        engine = ASTRefactoringEngine()
        source = ""
        assert engine.parse_source(source)


class TestGetAvailableRefactorings:
    """Test available refactorings detection"""

    def test_refactorings_in_function(self):
        """Test detecting refactorings inside function"""
        engine = ASTRefactoringEngine()
        source = """def my_func():
    pass
"""
        engine.parse_source(source)
        refactorings = engine.get_available_refactorings(1, 4)
        
        assert len(refactorings) > 0

    def test_rename_always_available(self):
        """Test that rename is always available"""
        engine = ASTRefactoringEngine()
        source = "x = 1"
        engine.parse_source(source)
        refactorings = engine.get_available_refactorings(1, 0)
        
        rename_types = [r["type"] for r in refactorings]
        assert "rename_symbol" in rename_types


class TestAPIEndpoints:
    """Test refactoring API operations"""

    @pytest.mark.asyncio
    async def test_extract_function_api(self):
        """Test extract function via API"""
        source = """def test():
    x = 1
    y = 2
"""
        result = await extract_function_refactor(
            source=source,
            name="init",
            start_line=2,
            end_line=3,
            parameters=[]
        )
        
        assert result["success"]
        assert len(result["changes"]) > 0

    @pytest.mark.asyncio
    async def test_rename_symbol_api(self):
        """Test rename symbol via API"""
        source = """x = 1
y = x + 2
"""
        result = await rename_symbol_refactor(
            source=source,
            old_name="x",
            new_name="value"
        )
        
        assert result["success"]
        assert result["changes"] > 0

    @pytest.mark.asyncio
    async def test_move_to_file_api(self):
        """Test move to file via API"""
        source = """def helper():
    return 42
"""
        result = await move_to_file_refactor(
            source=source,
            symbol_name="helper",
            target_file="utils.py"
        )
        
        assert result["success"]


class TestRefactoringPerformance:
    """Test performance of refactoring operations"""

    @pytest.mark.performance
    def test_extract_performance(self):
        """Test extract function performance"""
        engine = ASTRefactoringEngine()
        source = "\n".join([f"x{i} = {i}" for i in range(100)])
        engine.parse_source(source)
        
        import time
        start = time.time()
        engine.extract_function("test", 10, 20, [])
        duration = time.time() - start
        
        assert duration < 0.1  # Should complete in <100ms

    @pytest.mark.performance
    def test_rename_performance(self):
        """Test rename symbol performance"""
        engine = ASTRefactoringEngine()
        source = "\n".join(
            [f"x = {i}" for i in range(50)] +
            [f"y = x + {i}" for i in range(50)]
        )
        engine.parse_source(source)
        
        import time
        start = time.time()
        engine.rename_symbol("x", "value")
        duration = time.time() - start
        
        assert duration < 0.1  # Should complete in <100ms


class TestRefactoringIntegration:
    """End-to-end refactoring tests"""

    def test_complete_refactoring_workflow(self):
        """Test complete refactoring workflow"""
        engine = ASTRefactoringEngine()
        
        # Start with original code
        source = """def process():
    x = 1
    y = 2
    result = x + y
    return result
"""
        assert engine.parse_source(source)
        
        # Extract calculation
        extract_result = engine.extract_function(
            name="calculate",
            start_line=3,
            end_line=4,
            parameters=[]
        )
        assert extract_result.success
        
        # Rename variable in result
        rename_result = engine.rename_symbol("result", "output")
        assert rename_result.success

    def test_refactoring_preserves_functionality(self):
        """Test that refactorings preserve code functionality"""
        engine = ASTRefactoringEngine()
        source = """def add(a, b):
    return a + b

result = add(1, 2)
"""
        assert engine.parse_source(source)
        
        # Rename function
        rename_result = engine.rename_symbol("add", "sum_values")
        assert rename_result.success
        
        # Verify renamed function is called correctly
        assert "sum_values(1, 2)" in rename_result.refactored_source
