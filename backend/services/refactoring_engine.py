"""
Refactoring Engine - AST-based Code Transformations
Implements core refactoring operations:
- Extract function
- Rename symbol
- Move to file

Reference: AST manipulation + scope analysis
"""

import ast
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RefactoringType(Enum):
    """Types of refactoring operations"""
    EXTRACT_FUNCTION = "extract_function"
    RENAME_SYMBOL = "rename_symbol"
    MOVE_TO_FILE = "move_to_file"


@dataclass
class SourceRange:
    """Represents a range in source code"""
    start_line: int
    start_col: int
    end_line: int
    end_col: int

    def contains(self, line: int, col: int) -> bool:
        """Check if position is in range"""
        if self.start_line == self.end_line:
            return self.start_line == line and self.start_col <= col <= self.end_col
        if line < self.start_line or line > self.end_line:
            return False
        if line == self.start_line:
            return col >= self.start_col
        if line == self.end_line:
            return col <= self.end_col
        return True


@dataclass
class RefactoringResult:
    """Result of a refactoring operation"""
    success: bool
    original_source: str
    refactored_source: str
    changes: List[Dict[str, Any]]
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "original": self.original_source[:100] + "..." if len(self.original_source) > 100 else self.original_source,
            "changes": len(self.changes),
            "error": self.error,
        }


class ScopeAnalyzer(ast.NodeVisitor):
    """Analyzes scopes and symbol references in code"""

    def __init__(self):
        self.scopes: List[Dict[str, List[Tuple[int, int]]]] = [{}]  # Stack of scopes
        self.global_scope = {}
        self.references: Dict[str, List[Tuple[int, int]]] = {}  # symbol -> [(line, col), ...]
        self.definitions: Dict[str, Tuple[int, int]] = {}  # symbol -> (line, col)

    def push_scope(self):
        """Enter new scope"""
        self.scopes.append({})

    def pop_scope(self):
        """Exit scope"""
        self.scopes.pop()

    def add_definition(self, name: str, line: int, col: int):
        """Add symbol definition"""
        self.definitions[name] = (line, col)
        self.scopes[-1][name] = [(line, col)]

    def add_reference(self, name: str, line: int, col: int):
        """Add symbol reference"""
        if name not in self.references:
            self.references[name] = []
        self.references[name].append((line, col))

    def visit_FunctionDef(self, node):
        """Visit function definition"""
        self.add_definition(node.name, node.lineno, node.col_offset)
        self.push_scope()
        for arg in node.args.args:
            self.add_definition(arg.arg, arg.lineno or node.lineno, 0)
        self.generic_visit(node)
        self.pop_scope()

    def visit_ClassDef(self, node):
        """Visit class definition"""
        self.add_definition(node.name, node.lineno, node.col_offset)
        self.push_scope()
        self.generic_visit(node)
        self.pop_scope()

    def visit_Name(self, node):
        """Visit name reference"""
        if isinstance(node.ctx, ast.Store):
            self.add_definition(node.id, node.lineno, node.col_offset)
        else:
            self.add_reference(node.id, node.lineno, node.col_offset)
        self.generic_visit(node)

    def visit_Assign(self, node):
        """Visit assignment"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.add_definition(target.id, target.lineno, target.col_offset)
        self.generic_visit(node)


class ASTRefactoringEngine:
    """Main refactoring engine"""

    def __init__(self):
        self.source: str = ""
        self.tree: Optional[ast.AST] = None
        self.lines: List[str] = []
        self.scope_analyzer: Optional[ScopeAnalyzer] = None

    def parse_source(self, source: str) -> bool:
        """Parse source code into AST"""
        try:
            self.source = source
            self.lines = source.split('\n')
            self.tree = ast.parse(source)
            self.scope_analyzer = ScopeAnalyzer()
            self.scope_analyzer.visit(self.tree)
            return True
        except SyntaxError as e:
            logger.error(f"Parse error: {e}")
            return False

    def extract_function(
        self,
        name: str,
        start_line: int,
        end_line: int,
        parameters: Optional[List[str]] = None
    ) -> RefactoringResult:
        """
        Extract code range into new function
        
        Args:
            name: New function name
            start_line: Start line (1-indexed)
            end_line: End line (1-indexed)
            parameters: Function parameters
        """
        if not self.tree:
            return RefactoringResult(
                success=False,
                original_source=self.source,
                refactored_source="",
                changes=[],
                error="No source code parsed"
            )

        try:
            # Get indentation of first line
            first_line = self.lines[start_line - 1]
            indent = len(first_line) - len(first_line.lstrip())
            indent_str = ' ' * indent

            # Extract code block
            code_block = '\n'.join(self.lines[start_line - 1:end_line])
            
            # Remove leading indent
            block_lines = [line[indent:] if line.startswith(' ' * indent) else line 
                          for line in code_block.split('\n')]
            code_block = '\n'.join(block_lines)

            # Analyze extracted code to find return values
            try:
                ast.parse(code_block)
            except Exception:
                pass

            # Build new function
            params = ', '.join(parameters or [])
            new_function = f"{indent_str}def {name}({params}):\n"
            for line in code_block.split('\n'):
                new_function += f"{indent_str}    {line}\n"

            # Replace original code with function call
            call_line = f"{indent_str}{name}({', '.join(parameters or [])})"
            
            # Build refactored source
            refactored_lines = (
                self.lines[:start_line - 1] +
                [new_function] +
                [call_line] +
                self.lines[end_line:]
            )
            refactored_source = '\n'.join(refactored_lines)

            changes = [
                {
                    "type": "extract_function",
                    "function_name": name,
                    "start_line": start_line,
                    "end_line": end_line,
                    "parameters": parameters or [],
                }
            ]

            return RefactoringResult(
                success=True,
                original_source=self.source,
                refactored_source=refactored_source,
                changes=changes
            )

        except Exception as e:
            logger.error(f"Extract function error: {e}")
            return RefactoringResult(
                success=False,
                original_source=self.source,
                refactored_source="",
                changes=[],
                error=str(e)
            )

    def rename_symbol(self, old_name: str, new_name: str) -> RefactoringResult:
        """
        Rename symbol throughout file
        
        Args:
            old_name: Current symbol name
            new_name: New symbol name
        """
        if not self.tree or not self.scope_analyzer:
            return RefactoringResult(
                success=False,
                original_source=self.source,
                refactored_source="",
                changes=[],
                error="No source code parsed"
            )

        try:
            refactored_source = self.source
            changes = []

            # Replace all references with word boundary
            # This ensures we don't replace parts of other identifiers
            pattern = r'\b' + re.escape(old_name) + r'\b'
            
            def replace_fn(match):
                changes.append({
                    "type": "rename",
                    "old": old_name,
                    "new": new_name,
                    "position": match.start()
                })
                return new_name

            refactored_source = re.sub(pattern, replace_fn, refactored_source)

            return RefactoringResult(
                success=True,
                original_source=self.source,
                refactored_source=refactored_source,
                changes=changes
            )

        except Exception as e:
            logger.error(f"Rename symbol error: {e}")
            return RefactoringResult(
                success=False,
                original_source=self.source,
                refactored_source="",
                changes=[],
                error=str(e)
            )

    def move_to_file(
        self,
        symbol_name: str,
        target_file: str
    ) -> Tuple[RefactoringResult, Optional[str]]:
        """
        Move symbol (function/class) to new file
        
        Args:
            symbol_name: Function or class to move
            target_file: Target file path
            
        Returns:
            (source_file_changes, new_file_content)
        """
        if not self.tree:
            return (RefactoringResult(
                success=False,
                original_source=self.source,
                refactored_source="",
                changes=[],
                error="No source code parsed"
            ), None)

        try:
            # Find symbol in AST

            class SymbolFinder(ast.NodeVisitor):
                def __init__(self):
                    self.found = None
                    self.start = None
                    self.end = None

                def visit_FunctionDef(self, node):
                    if node.name == symbol_name:
                        self.found = node
                        self.start = node.lineno - 1
                        self.end = node.end_lineno
                    self.generic_visit(node)

                def visit_ClassDef(self, node):
                    if node.name == symbol_name:
                        self.found = node
                        self.start = node.lineno - 1
                        self.end = node.end_lineno
                    self.generic_visit(node)

            finder = SymbolFinder()
            finder.visit(self.tree)

            if not finder.found:
                return (RefactoringResult(
                    success=False,
                    original_source=self.source,
                    refactored_source="",
                    changes=[],
                    error=f"Symbol '{symbol_name}' not found"
                ), None)

            # Extract symbol code
            symbol_code = '\n'.join(self.lines[finder.start:finder.end])

            # Remove from original file
            refactored_source = '\n'.join(
                self.lines[:finder.start] +
                self.lines[finder.end:]
            )

            # Add import to original file
            import_line = f"from {target_file.replace('/', '.').replace('.py', '')} import {symbol_name}\n"
            refactored_source = import_line + refactored_source

            # Create new file content
            new_file_content = symbol_code

            changes = [{
                "type": "move_to_file",
                "symbol": symbol_name,
                "target_file": target_file,
                "lines_moved": finder.end - finder.start,
            }]

            return (RefactoringResult(
                success=True,
                original_source=self.source,
                refactored_source=refactored_source,
                changes=changes
            ), new_file_content)

        except Exception as e:
            logger.error(f"Move to file error: {e}")
            return (RefactoringResult(
                success=False,
                original_source=self.source,
                refactored_source="",
                changes=[],
                error=str(e)
            ), None)

    def get_available_refactorings(self, line: int, col: int) -> List[Dict[str, Any]]:
        """Get available refactorings at position"""
        refactorings: List[Dict[str, Any]] = []

        # Check if position is in function definition
        if not self.tree:
            return refactorings
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                end_lineno = getattr(node, "end_lineno", node.lineno)
                end_col = getattr(node, "end_col_offset", node.col_offset) or node.col_offset
                if (node.lineno <= line <= end_lineno and
                    node.col_offset <= col <= end_col + 10):
                    refactorings.append({
                        "type": "extract_function",
                        "name": "Extract Function",
                        "available": True,
                        "symbol": node.name,
                    })
                    refactorings.append({
                        "type": "move_to_file",
                        "name": "Move to File",
                        "available": True,
                        "symbol": node.name,
                    })

        # Rename is always available for identifiers
        refactorings.append({
            "type": "rename_symbol",
            "name": "Rename Symbol",
            "available": True,
        })

        return refactorings


# Global engine instance
_engine: Optional[ASTRefactoringEngine] = None


def get_refactoring_engine() -> ASTRefactoringEngine:
    """Get global refactoring engine instance"""
    global _engine
    if _engine is None:
        _engine = ASTRefactoringEngine()
    return _engine


async def extract_function_refactor(
    source: str,
    name: str,
    start_line: int,
    end_line: int,
    parameters: Optional[List[str]] = None
) -> Dict:
    """Extract function refactoring operation"""
    engine = get_refactoring_engine()
    
    if not engine.parse_source(source):
        return {
            "success": False,
            "error": "Failed to parse source code"
        }

    result = engine.extract_function(name, start_line, end_line, parameters)
    
    return {
        "success": result.success,
        "original": result.original_source[:200],
        "refactored": result.refactored_source[:200],
        "changes": result.changes,
        "error": result.error,
    }


async def rename_symbol_refactor(
    source: str,
    old_name: str,
    new_name: str
) -> Dict:
    """Rename symbol refactoring operation"""
    engine = get_refactoring_engine()
    
    if not engine.parse_source(source):
        return {
            "success": False,
            "error": "Failed to parse source code"
        }

    result = engine.rename_symbol(old_name, new_name)
    
    return {
        "success": result.success,
        "changes": len(result.changes),
        "refactored": result.refactored_source[:200],
        "error": result.error,
    }


async def move_to_file_refactor(
    source: str,
    symbol_name: str,
    target_file: str
) -> Dict:
    """Move to file refactoring operation"""
    engine = get_refactoring_engine()
    
    if not engine.parse_source(source):
        return {
            "success": False,
            "error": "Failed to parse source code"
        }

    source_result, new_file = engine.move_to_file(symbol_name, target_file)
    
    return {
        "success": source_result.success,
        "source_file_changes": source_result.changes,
        "new_file": new_file[:200] if new_file else None,
        "error": source_result.error,
    }
