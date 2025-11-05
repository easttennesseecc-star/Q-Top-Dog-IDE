"""
User Notes API Routes
REST endpoints for managing persistent user notes and explanations.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.services.user_notes_service import (
    get_notes_service,
    UserNote,
    NoteType
)

router = APIRouter(prefix="/api/v1/notes", tags=["user-notes"])


class CreateNoteRequest(BaseModel):
    workspace_id: str = Field(..., description="Workspace identifier")
    note_type: NoteType = Field(..., description="Type of note")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = Field(default=[], description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class UpdateNoteRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class NoteResponse(BaseModel):
    id: str
    workspace_id: str
    note_type: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]


@router.post("/", response_model=NoteResponse, status_code=201)
async def create_note(request: CreateNoteRequest):
    """Create a new user note"""
    service = get_notes_service()
    note = service.create_note(
        workspace_id=request.workspace_id,
        note_type=request.note_type,
        title=request.title,
        content=request.content,
        tags=request.tags,
        metadata=request.metadata
    )
    return note.to_dict()


@router.get("/{workspace_id}", response_model=List[NoteResponse])
async def list_notes(
    workspace_id: str,
    note_type: Optional[NoteType] = Query(None, description="Filter by note type"),
    tags: Optional[str] = Query(None, description="Comma-separated tags to filter")
):
    """List notes for a workspace with optional filters"""
    service = get_notes_service()
    tag_list = tags.split(",") if tags else None
    notes = service.list_notes(workspace_id, note_type=note_type, tags=tag_list)
    return [n.to_dict() for n in notes]


@router.get("/{workspace_id}/summary")
async def get_workspace_summary(workspace_id: str):
    """Get summary of notes for a workspace"""
    service = get_notes_service()
    return service.get_workspace_summary(workspace_id)


@router.get("/{workspace_id}/search")
async def search_notes(
    workspace_id: str,
    q: str = Query(..., min_length=1, description="Search query")
):
    """Search notes by content, title, or tags"""
    service = get_notes_service()
    notes = service.search_notes(workspace_id, q)
    return [n.to_dict() for n in notes]


@router.get("/{workspace_id}/{note_id}", response_model=NoteResponse)
async def get_note(workspace_id: str, note_id: str):
    """Get a specific note"""
    service = get_notes_service()
    note = service.get_note(workspace_id, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note.to_dict()


@router.put("/{workspace_id}/{note_id}", response_model=NoteResponse)
async def update_note(
    workspace_id: str,
    note_id: str,
    request: UpdateNoteRequest
):
    """Update an existing note"""
    service = get_notes_service()
    note = service.update_note(
        workspace_id=workspace_id,
        note_id=note_id,
        title=request.title,
        content=request.content,
        tags=request.tags,
        metadata=request.metadata
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note.to_dict()


@router.delete("/{workspace_id}/{note_id}", status_code=204)
async def delete_note(workspace_id: str, note_id: str):
    """Delete a note"""
    service = get_notes_service()
    success = service.delete_note(workspace_id, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None
