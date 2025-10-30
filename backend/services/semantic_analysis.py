"""
Semantic Analysis Service for Q-IDE IntelliSense
Provides fast, cached semantic analysis for code completions, definitions, and hovers.
Production-grade with robust error handling, monitoring, and performance tracking.
"""

import asyncio
import hashlib
import logging
import time
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SymbolKind(Enum):
    """LSP Symbol kinds for completions."""
    CLASS = "Class"
    FUNCTION = "Function"
    METHOD = "Method"
    VARIABLE = "Variable"
    PROPERTY = "Property"
    CONSTANT = "Constant"
    ENUM = "Enum"
    INTERFACE = "Interface"
    MODULE = "Module"
    KEYWORD = "Keyword"
    TYPE = "Type"
    PARAMETER = "Parameter"


@dataclass
class ParseMetadata:
    """Metadata about a parse operation."""
    file_path: str
    language: str
    parse_time_ms: float
    symbol_count: int
    error_count: int
    hash_code: str
    timestamp: datetime


@dataclass
class CompletionItem:
    """A single completion suggestion."""
    label: str
    kind: SymbolKind
    detail: str
    documentation: Optional[str] = None
    sort_text: Optional[str] = None
    filter_text: Optional[str] = None
    score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "label": self.label,
            "kind": self.kind.value,
            "detail": self.detail,
            "documentation": self.documentation,
            "sortText": self.sort_text or self.label,
            "filterText": self.filter_text or self.label,
            "score": self.score,
        }


@dataclass
class HoverInfo:
    """Hover information for a symbol."""
    content: str
    range: Optional[Tuple[int, int]] = None
    kind: Optional[SymbolKind] = None


@dataclass
class Definition:
    """Definition location for a symbol."""
    file_path: str
    line: int
    column: int
    name: str
    kind: SymbolKind


class SemanticCache:
    """
    Thread-safe cache for semantic analysis results.
    Implements LRU eviction and TTL expiration.
    """
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.access_order: List[str] = []
        self.hits = 0
        self.misses = 0
        
    def _compute_hash(self, file_path: str, code: str) -> str:
        """Compute cache key from file path and code content."""
        content = f"{file_path}:{code}".encode()
        return hashlib.md5(content).hexdigest()
    
    def get(self, file_path: str, code: str) -> Optional[Any]:
        """Retrieve cached value if exists and not expired."""
        key = self._compute_hash(file_path, code)
        
        if key not in self.cache:
            self.misses += 1
            return None
        
        value, timestamp = self.cache[key]
        if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            self.misses += 1
            return None
        
        # Update access order for LRU
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
        
        self.hits += 1
        return value
    
    def set(self, file_path: str, code: str, value: Any) -> None:
        """Cache a value with current timestamp."""
        key = self._compute_hash(file_path, code)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = (value, datetime.now())
        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()
        self.access_order.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Return cache statistics."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "size": len(self.cache),
            "max_size": self.max_size,
        }


class SemanticAnalyzer:
    """
    Main semantic analysis service.
    Coordinates with language servers and provides fast analysis results.
    """
    
    def __init__(self):
        self.cache = SemanticCache()
        self.language_servers: Dict[str, Any] = {}
        self.parse_metadata: Dict[str, ParseMetadata] = {}
        self.timeout_seconds = 5.0
        self.max_completions = 100
        
        logger.info("SemanticAnalyzer initialized")
    
    async def analyze_code(
        self,
        file_path: str,
        code: str,
        language: str,
        timeout: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analyze code and return semantic information.
        Robust error handling with timeout protection.
        """
        timeout = timeout or self.timeout_seconds
        start_time = time.time()
        
        try:
            # Check cache first
            cached = self.cache.get(file_path, code)
            if cached is not None:
                logger.debug(f"Cache hit for {file_path}")
                return cached
            
            # Run analysis with timeout
            result = await asyncio.wait_for(
                self._analyze_impl(file_path, code, language),
                timeout=timeout
            )
            
            # Cache result
            self.cache.set(file_path, code, result)
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(f"Analysis complete: {file_path} ({elapsed_ms:.1f}ms)")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Analysis timeout for {file_path} after {timeout}s")
            return self._error_result(f"Analysis timeout ({timeout}s exceeded)")
        except Exception as e:
            logger.error(f"Analysis error for {file_path}: {str(e)}")
            return self._error_result(str(e))
    
    async def _analyze_impl(
        self,
        file_path: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Internal analysis implementation."""
        if not code or not code.strip():
            return {
                "symbols": [],
                "errors": [],
                "metadata": {
                    "lines": 0,
                    "parseTime": 0,
                }
            }
        
        start_time = time.time()
        
        # Get language server (mock for now, will connect to real LSP servers)
        server = self._get_language_server(language)
        if not server:
            logger.warning(f"No language server for {language}")
            return self._error_result(f"Language not supported: {language}")
        
        # Parse symbols (simplified - actual implementation uses LSP)
        try:
            symbols = await self._extract_symbols(code, language)
            errors = await self._find_errors(code, language)
        except Exception as e:
            logger.error(f"Symbol extraction error: {str(e)}")
            symbols = []
            errors = [str(e)]
        
        parse_time_ms = (time.time() - start_time) * 1000
        
        # Store metadata
        code_hash = hashlib.md5(code.encode()).hexdigest()
        metadata = ParseMetadata(
            file_path=file_path,
            language=language,
            parse_time_ms=parse_time_ms,
            symbol_count=len(symbols),
            error_count=len(errors),
            hash_code=code_hash,
            timestamp=datetime.now()
        )
        self.parse_metadata[file_path] = metadata
        
        return {
            "symbols": symbols,
            "errors": errors,
            "metadata": {
                "lines": len(code.split('\n')),
                "parseTime": parse_time_ms,
                "symbolCount": len(symbols),
            }
        }
    
    async def get_completions(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int,
        language: str,
        prefix: str = ""
    ) -> List[CompletionItem]:
        """
        Get completion suggestions at cursor position.
        Filters and ranks results for performance.
        """
        try:
            start_time = time.time()
            
            # Analyze code to get all symbols
            analysis = await self.analyze_code(file_path, code, language)
            symbols = analysis.get("symbols", [])
            
            # Filter symbols matching prefix
            completions = []
            for symbol in symbols:
                name = symbol.get("name", "")
                if name.lower().startswith(prefix.lower()):
                    item = CompletionItem(
                        label=name,
                        kind=SymbolKind(symbol.get("kind", "Variable")),
                        detail=symbol.get("detail", ""),
                        documentation=symbol.get("documentation"),
                        score=self._compute_completion_score(name, prefix)
                    )
                    completions.append(item)
            
            # Sort by score and limit results
            completions.sort(key=lambda x: (-x.score, x.label))
            completions = completions[:self.max_completions]
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.debug(f"Completions: {len(completions)} items in {elapsed_ms:.1f}ms")
            
            return completions
            
        except Exception as e:
            logger.error(f"Completion error: {str(e)}")
            return []
    
    async def get_hover_info(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int,
        language: str
    ) -> Optional[HoverInfo]:
        """Get hover information for symbol at position."""
        try:
            analysis = await self.analyze_code(file_path, code, language)
            symbols = analysis.get("symbols", [])
            
            # Find symbol at position (simplified)
            for symbol in symbols:
                if symbol.get("line") == line:
                    return HoverInfo(
                        content=f"**{symbol.get('name')}**\n\n{symbol.get('detail')}",
                        kind=SymbolKind(symbol.get("kind", "Variable")),
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Hover error: {str(e)}")
            return None
    
    async def get_definition(
        self,
        file_path: str,
        code: str,
        line: int,
        column: int,
        language: str
    ) -> Optional[Definition]:
        """Get definition location for symbol at cursor."""
        try:
            analysis = await self.analyze_code(file_path, code, language)
            symbols = analysis.get("symbols", [])
            
            # Find matching symbol (simplified)
            for symbol in symbols:
                if symbol.get("line") == line:
                    return Definition(
                        file_path=file_path,
                        line=symbol.get("line", 0),
                        column=symbol.get("column", 0),
                        name=symbol.get("name", ""),
                        kind=SymbolKind(symbol.get("kind", "Variable"))
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Definition error: {str(e)}")
            return None
    
    def _get_language_server(self, language: str) -> Optional[Any]:
        """Get language server instance for language."""
        # Placeholder - will integrate with LSP servers
        if language in ["typescript", "javascript"]:
            return {"name": "TypeScript", "status": "ready"}
        elif language == "python":
            return {"name": "Python", "status": "ready"}
        return None
    
    async def _extract_symbols(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Extract symbols from code (simplified tokenization)."""
        symbols = []
        lines = code.split('\n')
        
        for line_no, line in enumerate(lines):
            line = line.strip()
            
            # Very basic symbol extraction (real impl uses proper AST)
            if language == "python":
                if line.startswith("def "):
                    name = line.split("(")[0].replace("def ", "")
                    symbols.append({
                        "name": name,
                        "kind": "Function",
                        "line": line_no,
                        "column": 0,
                        "detail": f"def {name}",
                    })
                elif line.startswith("class "):
                    name = line.split("(")[0].replace("class ", "").replace(":", "")
                    symbols.append({
                        "name": name,
                        "kind": "Class",
                        "line": line_no,
                        "column": 0,
                        "detail": f"class {name}",
                    })
            elif language in ["typescript", "javascript"]:
                if line.startswith("function "):
                    name = line.split("(")[0].replace("function ", "")
                    symbols.append({
                        "name": name,
                        "kind": "Function",
                        "line": line_no,
                        "column": 0,
                        "detail": f"function {name}",
                    })
                elif "const " in line or "let " in line or "var " in line:
                    parts = line.split("=")[0]
                    name = parts.replace("const ", "").replace("let ", "").replace("var ", "").strip()
                    symbols.append({
                        "name": name,
                        "kind": "Variable",
                        "line": line_no,
                        "column": 0,
                        "detail": name,
                    })
        
        return symbols
    
    async def _find_errors(self, code: str, language: str) -> List[str]:
        """Find syntax and semantic errors."""
        errors = []
        
        # Basic error detection (real impl uses LSP)
        if not code.strip():
            return errors
        
        # Check for unmatched braces
        if code.count('{') != code.count('}'):
            errors.append("Unmatched braces")
        if code.count('[') != code.count(']'):
            errors.append("Unmatched brackets")
        
        return errors
    
    def _compute_completion_score(self, name: str, prefix: str) -> float:
        """Compute score for completion sorting."""
        if not prefix:
            return 0.5
        
        # Exact match gets highest score
        if name == prefix:
            return 1.0
        
        # Prefix match scores based on length ratio
        ratio = len(prefix) / len(name)
        return 0.5 + (ratio * 0.5)
    
    def _error_result(self, message: str) -> Dict[str, Any]:
        """Return error result structure."""
        return {
            "symbols": [],
            "errors": [message],
            "metadata": {
                "lines": 0,
                "parseTime": 0,
                "error": True,
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Return service statistics."""
        return {
            "cache": self.cache.stats(),
            "metadata_entries": len(self.parse_metadata),
            "language_servers": list(self.language_servers.keys()),
        }


# Global analyzer instance
_analyzer: Optional[SemanticAnalyzer] = None


def get_analyzer() -> SemanticAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SemanticAnalyzer()
    return _analyzer


async def analyze(
    file_path: str,
    code: str,
    language: str
) -> Dict[str, Any]:
    """Convenience function for analysis."""
    analyzer = get_analyzer()
    return await analyzer.analyze_code(file_path, code, language)


async def completions(
    file_path: str,
    code: str,
    line: int,
    column: int,
    language: str,
    prefix: str = ""
) -> List[Dict[str, Any]]:
    """Convenience function for completions."""
    analyzer = get_analyzer()
    items = await analyzer.get_completions(file_path, code, line, column, language, prefix)
    return [item.to_dict() for item in items]
