"""
TypeScript Language Server Integration for Q-IDE
Connects to TypeScript/JavaScript language services via LSP.
Provides type information, definitions, and hover data.
"""

import asyncio
import logging
import json
import subprocess
import os
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import tempfile

logger = logging.getLogger(__name__)


@dataclass
class DiagnosticMessage:
    """A diagnostic error/warning message."""
    message: str
    line: int
    column: int
    severity: str  # "error", "warning", "information"
    code: Optional[str] = None


class TypeScriptServer:
    """
    TypeScript Language Server Protocol (LSP) adapter.
    Communicates with tsserver or similar TS language service.
    """
    
    def __init__(self, project_root: str = "."):
        self.project_root = project_root
        self.process: Optional[subprocess.Popen] = None
        self.message_id = 0
        self.diagnostics: Dict[str, List[DiagnosticMessage]] = {}
        self.initialized = False
        self.request_timeout = 5.0
        
        logger.info(f"TypeScriptServer initialized for {project_root}")
    
    async def initialize(self) -> bool:
        """Initialize the language server."""
        try:
            # In production, this would spawn tsserver process
            # For now, we implement basic local type inference
            self.initialized = True
            logger.info("TypeScript server initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize TS server: {str(e)}")
            return False
    
    async def get_completions(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int,
        prefix: str = ""
    ) -> List[Dict[str, Any]]:
        """Get TypeScript completions at position."""
        try:
            if not self.initialized:
                await self.initialize()
            
            completions: List[Dict[str, Any]] = []
            
            # Extract context around cursor
            lines = code.split('\n')
            if line >= len(lines):
                return completions
            
            current_line = lines[line] if line < len(lines) else ""
            
            # Get all symbols in scope (simplified implementation)
            symbols: List[Dict[str, Any]] = await self._extract_symbols(code, line, column)
            
            # Filter and rank
            for symbol in symbols:
                if symbol.get("name", "").lower().startswith(prefix.lower()):
                    completions.append({
                        "label": symbol["name"],
                        "kind": symbol.get("kind", "Variable"),
                        "detail": symbol.get("detail", ""),
                        "documentation": symbol.get("documentation", ""),
                        "insertText": symbol["name"],
                        "sortText": symbol["name"],
                        "score": self._score_completion(symbol, prefix)
                    })
            
            # Sort by score and filter top results
            completions.sort(key=lambda x: (-x.get("score", 0), x["label"]))
            completions = completions[:50]
            
            logger.debug(f"TS completions: {len(completions)} items")
            return completions
            
        except Exception as e:
            logger.error(f"TS completion error: {str(e)}")
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
            if not self.initialized:
                await self.initialize()
            
            # Find symbol at position
            lines = code.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            if column > len(current_line):
                return None
            
            # Extract word at cursor
            word_start = column
            while word_start > 0 and (current_line[word_start-1].isalnum() or current_line[word_start-1] in "_$"):
                word_start -= 1
            
            word_end = column
            while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] in "_$"):
                word_end += 1
            
            word = current_line[word_start:word_end]
            if not word:
                return None
            
            # Get type information (simplified)
            type_info = await self._infer_type(code, word, line, column)
            
            return {
                "content": f"**{word}**: {type_info}",
                "range": [word_start, word_end]
            }
            
        except Exception as e:
            logger.error(f"TS hover error: {str(e)}")
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
            if not self.initialized:
                await self.initialize()
            
            lines = code.split('\n')
            if line >= len(lines):
                return None
            
            current_line = lines[line]
            if column > len(current_line):
                return None
            
            # Find symbol name
            word_start = column
            while word_start > 0 and (current_line[word_start-1].isalnum() or current_line[word_start-1] in "_$"):
                word_start -= 1
            
            word_end = column
            while word_end < len(current_line) and (current_line[word_end].isalnum() or current_line[word_end] in "_$"):
                word_end += 1
            
            word = current_line[word_start:word_end]
            
            # Find definition (simplified - searches code for declaration)
            def_line = await self._find_symbol_definition(code, word)
            
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
            logger.error(f"TS definition error: {str(e)}")
            return None
    
    async def get_diagnostics(
        self,
        file_path: str,
        code: str
    ) -> List[DiagnosticMessage]:
        """Get diagnostic messages (errors/warnings)."""
        try:
            if not self.initialized:
                await self.initialize()
            
            diagnostics: List[DiagnosticMessage] = []
            
            # Basic error detection
            lines = code.split('\n')
            for line_no, line in enumerate(lines):
                line_stripped = line.strip()
                
                # Check for common errors
                if "const " in line and "=" not in line and not line_stripped.endswith(","):
                    diagnostics.append(DiagnosticMessage(
                        message="Missing initializer in const declaration",
                        line=line_no,
                        column=0,
                        severity="error"
                    ))
                
                # Unmatched braces
                if line.count('{') != line.count('}'):
                    diagnostics.append(DiagnosticMessage(
                        message="Unmatched braces",
                        line=line_no,
                        column=len(line),
                        severity="error"
                    ))
            
            self.diagnostics[file_path] = diagnostics
            return diagnostics
            
        except Exception as e:
            logger.error(f"TS diagnostics error: {str(e)}")
            return []
    
    async def _extract_symbols(
        self,
        code: str,
        line: int,
        column: int
    ) -> List[Dict[str, Any]]:
        """Extract available symbols at location."""
        symbols = []
        lines = code.split('\n')
        
        # Get all imports and global symbols
        for i, l in enumerate(lines):
            l = l.strip()
            
            # Imports
            if l.startswith("import "):
                parts = l.split(" ")
                if len(parts) >= 4:
                    name = parts[1]
                    symbols.append({
                        "name": name,
                        "kind": "Module",
                        "detail": f"import {name}",
                        "documentation": "Imported module"
                    })
            
            # Functions
            elif l.startswith("function "):
                name = l.split("(")[0].replace("function ", "")
                symbols.append({
                    "name": name,
                    "kind": "Function",
                    "detail": f"function {name}(...)",
                    "documentation": "Function declaration"
                })
            
            # Classes
            elif l.startswith("class "):
                name = l.split("{")[0].replace("class ", "").split(" ")[0]
                symbols.append({
                    "name": name,
                    "kind": "Class",
                    "detail": f"class {name}",
                    "documentation": "Class declaration"
                })
            
            # Variables
            elif "const " in l or "let " in l or "var " in l:
                lhs = l.split("=")[0]
                for keyword in ["const ", "let ", "var "]:
                    if keyword in lhs:
                        name = lhs.replace(keyword, "").strip()
                        symbols.append({
                            "name": name,
                            "kind": "Variable",
                            "detail": name,
                            "documentation": "Variable declaration"
                        })
                        break
        
        # Add common global objects and methods
        globals_ts = [
            {"name": "console", "kind": "Module", "detail": "console"},
            {"name": "Math", "kind": "Module", "detail": "Math"},
            {"name": "Array", "kind": "Class", "detail": "Array"},
            {"name": "Object", "kind": "Class", "detail": "Object"},
            {"name": "String", "kind": "Class", "detail": "String"},
            {"name": "Promise", "kind": "Class", "detail": "Promise"},
            {"name": "setTimeout", "kind": "Function", "detail": "setTimeout(...)"},
            {"name": "setInterval", "kind": "Function", "detail": "setInterval(...)"},
        ]
        symbols.extend(globals_ts)
        
        return symbols
    
    async def _infer_type(self, code: str, symbol: str, line: int, column: int) -> str:
        """Infer type of symbol (simplified)."""
        lines = code.split('\n')
        
        # Search for symbol declaration
        for l in lines:
            if f"const {symbol}" in l:
                if "[]" in l:
                    return "Array"
                elif "{" in l:
                    return "Object"
                elif "true" in l or "false" in l:
                    return "boolean"
                elif '"' in l or "'" in l:
                    return "string"
                elif "function" in l or "=>" in l:
                    return "Function"
                else:
                    return "any"
        
        # Check if it's a built-in
        builtins = {
            "console": "Console",
            "Math": "Math",
            "Array": "ArrayConstructor",
            "Object": "ObjectConstructor",
            "String": "StringConstructor",
            "Promise": "PromiseConstructor",
        }
        
        return builtins.get(symbol, "any")
    
    async def _find_symbol_definition(self, code: str, symbol: str) -> int:
        """Find line number where symbol is defined."""
        lines = code.split('\n')
        
        for i, line in enumerate(lines):
            if f"const {symbol}" in line:
                return i
            elif f"function {symbol}" in line:
                return i
            elif f"class {symbol}" in line:
                return i
            elif f"let {symbol}" in line:
                return i
        
        return -1
    
    def _score_completion(self, symbol: Dict[str, Any], prefix: str) -> float:
        """Score completion item for sorting."""
        name = symbol.get("name", "")
        
        if not prefix:
            return 0.5
        
        # Exact match
        if name == prefix:
            return 1.0
        
        # Prefix match
        if name.startswith(prefix):
            return 0.8
        
        # Contains match
        if prefix in name:
            return 0.6
        
        return 0.3
    
    def shutdown(self) -> None:
        """Shutdown the language server."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception as e:
                logger.error(f"Error shutting down TS server: {str(e)}")
        
        self.initialized = False
        logger.info("TypeScript server shut down")


# Singleton instance
_ts_server: Optional[TypeScriptServer] = None


def get_ts_server() -> TypeScriptServer:
    """Get or create TypeScript server instance."""
    global _ts_server
    if _ts_server is None:
        _ts_server = TypeScriptServer()
    return _ts_server


async def get_ts_completions(
    file_path: str,
    code: str,
    line: int,
    column: int,
    prefix: str = ""
) -> List[Dict[str, Any]]:
    """Convenience function for TypeScript completions."""
    server = get_ts_server()
    if not server.initialized:
        await server.initialize()
    return await server.get_completions(file_path, code, line, column, prefix)


async def get_ts_hover(
    file_path: str,
    code: str,
    line: int,
    column: int
) -> Optional[Dict[str, Any]]:
    """Convenience function for TypeScript hover."""
    server = get_ts_server()
    if not server.initialized:
        await server.initialize()
    return await server.get_hover(file_path, code, line, column)


async def get_ts_definition(
    file_path: str,
    code: str,
    line: int,
    column: int
) -> Optional[Dict[str, Any]]:
    """Convenience function for TypeScript definition."""
    server = get_ts_server()
    if not server.initialized:
        await server.initialize()
    return await server.get_definition(file_path, code, line, column)


async def get_ts_diagnostics(
    file_path: str,
    code: str
) -> List[Dict[str, Any]]:
    """Convenience function for TypeScript diagnostics."""
    server = get_ts_server()
    if not server.initialized:
        await server.initialize()
    diagnostics = await server.get_diagnostics(file_path, code)
    return [
        {
            "message": d.message,
            "line": d.line,
            "column": d.column,
            "severity": d.severity,
            "code": d.code
        }
        for d in diagnostics
    ]
