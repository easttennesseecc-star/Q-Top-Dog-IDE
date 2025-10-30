"""
Python Language Server Integration for Q-IDE
Provides Python-specific completions, type hints, and diagnostics.
"""

import asyncio
import logging
import ast
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticMessage:
    """A diagnostic error/warning message."""
    message: str
    line: int
    column: int
    severity: str  # "error", "warning", "information"


class PythonServer:
    """
    Python Language Server for Q-IDE.
    Provides fast analysis using AST and basic type inference.
    """
    
    def __init__(self):
        self.builtins = self._get_builtins()
        self.stdlib_modules = self._get_stdlib_modules()
        self.initialized = True
        logger.info("PythonServer initialized")
    
    async def get_completions(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int,
        prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """Get Python completions at position."""
        try:
            completions = []
            
            lines = code.split('\n')
            if line >= len(lines):
                return completions
            
            current_line = lines[line]
            if column > len(current_line):
                column = len(current_line)
            
            # Get all available symbols
            symbols = await self._extract_symbols(code, line, column)
            
            # Filter by prefix
            for symbol in symbols:
                name = symbol.get("name", "")
                if name.lower().startswith(prefix.lower()):
                    completions.append({
                        "label": name,
                        "kind": symbol.get("kind", "Variable"),
                        "detail": symbol.get("detail", ""),
                        "documentation": symbol.get("documentation", ""),
                        "insertText": name,
                        "sortText": name,
                        "score": self._score_completion(name, prefix)
                    })
            
            # Sort and limit
            completions.sort(key=lambda x: (-x.get("score", 0), x["label"]))
            completions = completions[:50]
            
            logger.debug(f"Python completions: {len(completions)} items")
            return completions
            
        except Exception as e:
            logger.error(f"Python completion error: {str(e)}")
            return []
    
    async def get_hover(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int
    ) -> Optional[Dict[str, Any]]:
        """Get hover information."""
        try:
            lines = code.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            if column > len(current_line):
                return None
            
            # Extract word at cursor
            word_start = column
            while word_start > 0 and (current_line[word_start-1].isalnum() or current_line[word_start-1] == '_'):
                word_start -= 1
            
            word_end = column
            while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] == '_'):
                word_end += 1
            
            word = current_line[word_start:word_end]
            if not word:
                return None
            
            # Get type information
            type_info = await self._infer_type(code, word, line)
            
            return {
                "content": f"**{word}**: {type_info}",
                "range": [word_start, word_end]
            }
            
        except Exception as e:
            logger.error(f"Python hover error: {str(e)}")
            return None
    
    async def get_definition(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int
    ) -> Optional[Dict[str, Any]]:
        """Get definition location."""
        try:
            lines = code.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            if column > len(current_line):
                return None
            
            # Extract symbol
            word_start = column
            while word_start > 0 and (current_line[word_start-1].isalnum() or current_line[word_start-1] == '_'):
                word_start -= 1
            
            word_end = column
            while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] == '_'):
                word_end += 1
            
            word = current_line[word_start:word_end]
            
            # Find definition
            def_line = await self._find_definition(code, word)
            
            if def_line >= 0:
                return {
                    "uri": f"file://{file_path}",
                    "range": {
                        "start": {"line": def_line, "character": 0},
                        "end": {"line": def_line, "character": 100}
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Python definition error: {str(e)}")
            return None
    
    async def get_diagnostics(
        self,
        file_path: str,
        code: str
    ) -> List[DiagnosticMessage]:
        """Get diagnostic messages."""
        diagnostics = []
        
        try:
            # Parse AST to find errors
            try:
                ast.parse(code)
            except SyntaxError as e:
                diagnostics.append(DiagnosticMessage(
                    message=f"Syntax error: {e.msg}",
                    line=e.lineno - 1 if e.lineno else 0,
                    column=e.offset - 1 if e.offset else 0,
                    severity="error"
                ))
            except Exception as e:
                diagnostics.append(DiagnosticMessage(
                    message=f"Parse error: {str(e)}",
                    line=0,
                    column=0,
                    severity="error"
                ))
            
            # Check for common issues
            lines = code.split('\n')
            for line_no, line in enumerate(lines):
                # Unused imports
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    module = line.split()[1]
                    # Simple check: see if module is used in code
                    if module not in code.split(line):
                        diagnostics.append(DiagnosticMessage(
                            message=f"Unused import: {module}",
                            line=line_no,
                            column=0,
                            severity="warning"
                        ))
                
                # Missing colons
                if any(line.strip().startswith(x) for x in ["if ", "for ", "while ", "def ", "class "]):
                    if not line.rstrip().endswith(":"):
                        diagnostics.append(DiagnosticMessage(
                            message="Missing colon at end of statement",
                            line=line_no,
                            column=len(line),
                            severity="error"
                        ))
            
        except Exception as e:
            logger.error(f"Python diagnostics error: {str(e)}")
        
        return diagnostics
    
    async def _extract_symbols(
        self,
        code: str,
        line: int,
        column: int
    ) -> List[Dict[str, Any]]:
        """Extract available symbols."""
        symbols = []
        lines = code.split('\n')
        
        # Parse AST to get functions and classes
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols.append({
                        "name": node.name,
                        "kind": "Function",
                        "detail": f"def {node.name}(...)",
                        "documentation": ast.get_docstring(node) or ""
                    })
                elif isinstance(node, ast.ClassDef):
                    symbols.append({
                        "name": node.name,
                        "kind": "Class",
                        "detail": f"class {node.name}",
                        "documentation": ast.get_docstring(node) or ""
                    })
        except:
            pass
        
        # Extract variables and imports
        for l in lines:
            l_stripped = l.strip()
            
            # Imports
            if l_stripped.startswith("import "):
                parts = l_stripped.split()
                if len(parts) >= 2:
                    module = parts[1]
                    symbols.append({
                        "name": module,
                        "kind": "Module",
                        "detail": f"import {module}",
                        "documentation": "Module"
                    })
            elif l_stripped.startswith("from "):
                parts = l_stripped.split()
                if len(parts) >= 4 and parts[2] == "import":
                    for name in parts[3:]:
                        name = name.rstrip(',')
                        symbols.append({
                            "name": name,
                            "kind": "Variable",
                            "detail": name,
                            "documentation": "Imported name"
                        })
            
            # Variables
            elif "=" in l_stripped and not l_stripped.startswith("#"):
                parts = l_stripped.split("=")[0]
                name = parts.strip()
                if name.isidentifier() and not any(c in name for c in " ()[]{}"):
                    symbols.append({
                        "name": name,
                        "kind": "Variable",
                        "detail": name,
                        "documentation": "Variable"
                    })
        
        # Add Python builtins
        for builtin in self.builtins:
            symbols.append({
                "name": builtin,
                "kind": "Function",
                "detail": builtin,
                "documentation": f"Python builtin: {builtin}"
            })
        
        # Remove duplicates
        seen = set()
        unique = []
        for symbol in symbols:
            key = symbol["name"]
            if key not in seen:
                seen.add(key)
                unique.append(symbol)
        
        return unique
    
    async def _infer_type(self, code: str, symbol: str, line: int) -> str:
        """Infer type of symbol."""
        lines = code.split('\n')
        
        # Search for assignment
        for l in lines:
            if f"{symbol} =" in l:
                # Simple type inference
                value_part = l.split("=", 1)[1].strip()
                
                if value_part.startswith("["):
                    return "list"
                elif value_part.startswith("{"):
                    return "dict"
                elif value_part.startswith("("):
                    return "tuple"
                elif value_part.startswith("\"") or value_part.startswith("'"):
                    return "str"
                elif value_part.startswith("True") or value_part.startswith("False"):
                    return "bool"
                elif value_part.isdigit() or (value_part.startswith("-") and value_part[1:].isdigit()):
                    return "int"
                elif "." in value_part and all(c.isdigit() or c in "-."):
                    return "float"
                elif value_part.startswith("lambda"):
                    return "Callable"
                else:
                    return "Any"
        
        # Check if it's a builtin
        builtins_types = {
            "len": "Callable",
            "print": "Callable",
            "range": "Callable",
            "str": "type",
            "int": "type",
            "float": "type",
            "list": "type",
            "dict": "type",
            "tuple": "type",
            "set": "type",
        }
        
        return builtins_types.get(symbol, "Any")
    
    async def _find_definition(self, code: str, symbol: str) -> int:
        """Find line where symbol is defined."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            if f"def {symbol}" in line:
                return i
            elif f"class {symbol}" in line:
                return i
            elif f"{symbol} =" in line and "=" in line:
                return i
        
        return -1
    
    def _score_completion(self, name: str, prefix: str) -> float:
        """Score completion for sorting."""
        if not prefix:
            return 0.5
        
        if name == prefix:
            return 1.0
        elif name.startswith(prefix):
            return 0.8
        elif prefix in name:
            return 0.6
        else:
            return 0.3
    
    def _get_builtins(self) -> List[str]:
        """Get Python builtin functions."""
        return [
            "abs", "all", "any", "ascii", "bin", "bool", "breakpoint", "bytearray",
            "bytes", "callable", "chr", "classmethod", "compile", "complex",
            "delattr", "dict", "dir", "divmod", "enumerate", "eval", "exec",
            "filter", "float", "format", "frozenset", "getattr", "globals",
            "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance",
            "issubclass", "iter", "len", "list", "locals", "map", "max",
            "memoryview", "min", "next", "object", "oct", "open", "ord", "pow",
            "print", "property", "range", "repr", "reversed", "round", "set",
            "setattr", "slice", "sorted", "staticmethod", "str", "sum", "super",
            "tuple", "type", "vars", "zip"
        ]
    
    def _get_stdlib_modules(self) -> List[str]:
        """Get common Python standard library modules."""
        return [
            "sys", "os", "json", "time", "datetime", "math", "random", "string",
            "re", "itertools", "functools", "collections", "pathlib", "tempfile",
            "io", "pickle", "csv", "sqlite3", "threading", "asyncio", "concurrent",
            "subprocess", "shutil", "glob", "fnmatch", "urllib", "http", "socket",
            "email", "html", "xml", "urllib", "json", "base64", "hashlib", "hmac",
            "logging", "argparse", "unittest", "doctest", "inspect", "types"
        ]


# Singleton instance
_py_server: Optional[PythonServer] = None


def get_py_server() -> PythonServer:
    """Get or create Python server instance."""
    global _py_server
    if _py_server is None:
        _py_server = PythonServer()
    return _py_server


async def get_py_completions(
    file_path: str,
    code: str,
    line: int,
    column: int,
    prefix: str = ""
) -> List[Dict[str, Any]]:
    """Convenience function for Python completions."""
    server = get_py_server()
    return await server.get_completions(file_path, code, line, column, prefix)


async def get_py_hover(
    file_path: str,
    code: str,
    line: int,
    column: int
) -> Optional[Dict[str, Any]]:
    """Convenience function for Python hover."""
    server = get_py_server()
    return await server.get_hover(file_path, code, line, column)


async def get_py_definition(
    file_path: str,
    code: str,
    line: int,
    column: int
) -> Optional[Dict[str, Any]]:
    """Convenience function for Python definition."""
    server = get_py_server()
    return await server.get_definition(file_path, code, line, column)


async def get_py_diagnostics(
    file_path: str,
    code: str
) -> List[Dict[str, Any]]:
    """Convenience function for Python diagnostics."""
    server = get_py_server()
    diagnostics = await server.get_diagnostics(file_path, code)
    return [
        {
            "message": d.message,
            "line": d.line,
            "column": d.column,
            "severity": d.severity
        }
        for d in diagnostics
    ]
