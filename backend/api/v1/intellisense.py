"""
IntelliSense API Endpoints for Q-IDE
Provides HTTP endpoints for code completions, hover info, and definitions.
"""

import time
import logging
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from backend.services.semantic_analysis import get_analyzer
from backend.services.typescript_language_server import get_ts_completions, get_ts_hover, get_ts_definition, get_ts_diagnostics
from backend.services.python_language_server import get_py_completions, get_py_hover, get_py_definition, get_py_diagnostics

logger = logging.getLogger(__name__)

# Import semantic services

# Create router
router = APIRouter(prefix="/api/v1/intellisense", tags=["intellisense"])


# Request/Response Models
class CompletionRequest(BaseModel):
    """Request for code completions."""
    file_path: str = Field(..., description="File path")
    code: str = Field(..., description="Code content")
    language: str = Field(..., description="Programming language (typescript, python, javascript)")
    line: int = Field(..., ge=0, description="Line number (0-indexed)")
    column: int = Field(..., ge=0, description="Column number (0-indexed)")
    prefix: str = Field("", description="Partial word to filter completions")


class CompletionItem(BaseModel):
    """A completion suggestion."""
    label: str
    kind: str
    detail: str
    documentation: Optional[str] = None
    sortText: str
    filterText: str
    score: float = 0.0


class CompletionResponse(BaseModel):
    """Response containing completions."""
    completions: List[CompletionItem]
    latency_ms: float
    count: int


class HoverRequest(BaseModel):
    """Request for hover information."""
    file_path: str
    code: str
    language: str
    line: int = Field(..., ge=0)
    column: int = Field(..., ge=0)


class HoverResponse(BaseModel):
    """Hover information response."""
    content: Optional[str] = None
    range: Optional[Dict[str, int]] = None
    kind: Optional[str] = None
    latency_ms: float


class DefinitionRequest(BaseModel):
    """Request for symbol definition."""
    file_path: str
    code: str
    language: str
    line: int = Field(..., ge=0)
    column: int = Field(..., ge=0)


class DefinitionResponse(BaseModel):
    """Definition location response."""
    uri: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    latency_ms: float


class DiagnosticMessage(BaseModel):
    """A diagnostic message (error/warning)."""
    message: str
    line: int
    column: int
    severity: str  # "error", "warning", "information"


class DiagnosticsRequest(BaseModel):
    """Request for code diagnostics."""
    file_path: str
    code: str
    language: str


class DiagnosticsResponse(BaseModel):
    """Diagnostics response."""
    diagnostics: List[DiagnosticMessage]
    latency_ms: float
    error_count: int
    warning_count: int


# Helper functions
def _validate_language(language: str) -> str:
    """Validate and normalize language."""
    normalized = language.lower().strip()
    valid = ["typescript", "javascript", "python", "js", "ts", "py"]
    if normalized not in valid:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    
    # Normalize
    mapping = {"js": "javascript", "ts": "typescript", "py": "python"}
    return mapping.get(normalized, normalized)


def _validate_position(code: str, line: int, column: int) -> None:
    """Validate line and column are within bounds."""
    lines = code.split('\n')
    if line < 0 or line >= len(lines):
        raise HTTPException(status_code=400, detail=f"Line {line} out of bounds (total: {len(lines)})")
    
    if column < 0 or column > len(lines[line]):
        raise HTTPException(status_code=400, detail=f"Column {column} out of bounds for line {line}")


# Endpoints
@router.post("/completions", response_model=CompletionResponse)
async def completions(request: CompletionRequest) -> CompletionResponse:
    """
    Get code completions at cursor position.
    Target: <100ms response time, 90%+ accuracy
    """
    start_time = time.time()
    
    try:
        # Validate input
        language = _validate_language(request.language)
        _validate_position(request.code, request.line, request.column)
        
        if not request.code or not request.code.strip():
            return CompletionResponse(
                completions=[],
                latency_ms=0.0,
                count=0
            )
        
        # Get completions from appropriate language server
        completions_list = []
        
        if language in ["typescript", "javascript"]:
            completions_list = await get_ts_completions(
                request.file_path,
                request.code,
                request.line,
                request.column,
                request.prefix
            )
        elif language == "python":
            completions_list = await get_py_completions(
                request.file_path,
                request.code,
                request.line,
                request.column,
                request.prefix
            )
        
        # Convert to response model
        items = [CompletionItem(**item) for item in completions_list]
        
        latency_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Completions: {len(items)} items in {latency_ms:.1f}ms "
            f"(language={language}, line={request.line}, col={request.column})"
        )
        
        # Check latency SLA
        if latency_ms > 100:
            logger.warning(f"Completion latency exceeded 100ms: {latency_ms:.1f}ms")
        
        return CompletionResponse(
            completions=items,
            latency_ms=latency_ms,
            count=len(items)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Completion error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hover", response_model=HoverResponse)
async def hover(request: HoverRequest) -> HoverResponse:
    """Get hover information for symbol at cursor."""
    start_time = time.time()
    
    try:
        language = _validate_language(request.language)
        _validate_position(request.code, request.line, request.column)
        
        hover_info = None
        
        if language in ["typescript", "javascript"]:
            hover_info = await get_ts_hover(
                request.file_path,
                request.code,
                request.line,
                request.column
            )
        elif language == "python":
            hover_info = await get_py_hover(
                request.file_path,
                request.code,
                request.line,
                request.column
            )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return HoverResponse(
            content=hover_info.get("content") if hover_info else None,
            range=hover_info.get("range") if hover_info else None,
            kind=hover_info.get("kind") if hover_info else None,
            latency_ms=latency_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hover error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/definition", response_model=DefinitionResponse)
async def definition(request: DefinitionRequest) -> DefinitionResponse:
    """Get definition location for symbol at cursor."""
    start_time = time.time()
    
    try:
        language = _validate_language(request.language)
        _validate_position(request.code, request.line, request.column)
        
        def_info = None
        
        if language in ["typescript", "javascript"]:
            def_info = await get_ts_definition(
                request.file_path,
                request.code,
                request.line,
                request.column
            )
        elif language == "python":
            def_info = await get_py_definition(
                request.file_path,
                request.code,
                request.line,
                request.column
            )
        
        latency_ms = (time.time() - start_time) * 1000
        
        response_data = {"latency_ms": latency_ms}
        
        if def_info:
            response_data.update({
                "uri": def_info.get("uri"),
                "line": def_info.get("range", {}).get("start", {}).get("line"),
                "column": def_info.get("range", {}).get("start", {}).get("character"),
            })
        
        return DefinitionResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Definition error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnostics", response_model=DiagnosticsResponse)
async def diagnostics(request: DiagnosticsRequest) -> DiagnosticsResponse:
    """Get diagnostic messages (errors/warnings) for code."""
    start_time = time.time()
    
    try:
        language = _validate_language(request.language)
        
        if not request.code or not request.code.strip():
            return DiagnosticsResponse(
                diagnostics=[],
                latency_ms=0.0,
                error_count=0,
                warning_count=0
            )
        
        diagnostics_list = []
        
        if language in ["typescript", "javascript"]:
            diagnostics_list = await get_ts_diagnostics(
                request.file_path,
                request.code
            )
        elif language == "python":
            diagnostics_list = await get_py_diagnostics(
                request.file_path,
                request.code
            )
        
        # Count by severity
        errors = sum(1 for d in diagnostics_list if d.get("severity") == "error")
        warnings = sum(1 for d in diagnostics_list if d.get("severity") == "warning")
        
        # Convert to response model
        items = [DiagnosticMessage(**d) for d in diagnostics_list]
        
        latency_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Diagnostics: {len(items)} messages "
            f"({errors} errors, {warnings} warnings) in {latency_ms:.1f}ms"
        )
        
        return DiagnosticsResponse(
            diagnostics=items,
            latency_ms=latency_ms,
            error_count=errors,
            warning_count=warnings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Diagnostics error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health() -> Dict[str, Any]:
    """Health check endpoint."""
    try:
        # Check semantic analyzer
        analyzer = get_analyzer()
        stats = analyzer.get_stats()
        
        return {
            "status": "healthy",
            "services": {
                "semantic_analyzer": "ready",
                "typescript_server": "ready",
                "python_server": "ready",
            },
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@router.get("/stats")
async def stats() -> Dict[str, Any]:
    """Get service statistics."""
    try:
        analyzer = get_analyzer()
        return {
            "cache": analyzer.cache.stats(),
            "metadata_entries": len(analyzer.parse_metadata),
        }
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
