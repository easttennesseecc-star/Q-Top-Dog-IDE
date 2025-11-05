"""
User Notes & Explanations Service
Persistent storage for user context, preferences, and instructions across sessions.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class NoteType(str, Enum):
    CONTEXT = "context"
    PREFERENCE = "preference"
    INSTRUCTION = "instruction"
    BUILD_RULE = "build_rule"
    CLARIFICATION = "clarification"


@dataclass
class UserNote:
    """Represents a single user note/explanation"""
    id: str
    workspace_id: str
    note_type: NoteType
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class UserNotesService:
    """Service for managing persistent user notes and explanations"""
    
    def __init__(self, storage_dir: str = "./data/user_notes"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "notes_index.json"
        self._ensure_index()
    
    def _ensure_index(self):
        """Ensure index file exists"""
        if not self.index_file.exists():
            self._save_index({})
    
    def _load_index(self) -> Dict:
        """Load notes index"""
        with open(self.index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_index(self, index: Dict):
        """Save notes index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def _get_workspace_file(self, workspace_id: str) -> Path:
        """Get path to workspace notes file"""
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in workspace_id)
        return self.storage_dir / f"{safe_id}.json"
    
    def create_note(
        self,
        workspace_id: str,
        note_type: NoteType,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UserNote:
        """Create a new note"""
        note_id = f"{workspace_id}_{datetime.utcnow().timestamp()}"
        now = datetime.utcnow().isoformat()
        
        note = UserNote(
            id=note_id,
            workspace_id=workspace_id,
            note_type=note_type,
            title=title,
            content=content,
            tags=tags or [],
            created_at=now,
            updated_at=now,
            metadata=metadata or {}
        )
        
        # Load existing workspace notes
        workspace_file = self._get_workspace_file(workspace_id)
        notes = []
        if workspace_file.exists():
            with open(workspace_file, 'r', encoding='utf-8') as f:
                notes = json.load(f)
        
        # Add new note
        notes.append(note.to_dict())
        
        # Save workspace notes
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if workspace_id not in index:
            index[workspace_id] = []
        index[workspace_id].append({
            "id": note_id,
            "title": title,
            "type": note_type,
            "tags": tags or [],
            "created_at": now
        })
        self._save_index(index)
        
        return note
    
    def get_note(self, workspace_id: str, note_id: str) -> Optional[UserNote]:
        """Get a specific note"""
        workspace_file = self._get_workspace_file(workspace_id)
        if not workspace_file.exists():
            return None
        
        with open(workspace_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        for note_dict in notes:
            if note_dict['id'] == note_id:
                return UserNote(**note_dict)
        
        return None
    
    def list_notes(
        self,
        workspace_id: str,
        note_type: Optional[NoteType] = None,
        tags: Optional[List[str]] = None
    ) -> List[UserNote]:
        """List notes for a workspace with optional filters"""
        workspace_file = self._get_workspace_file(workspace_id)
        if not workspace_file.exists():
            return []
        
        with open(workspace_file, 'r', encoding='utf-8') as f:
            notes_data = json.load(f)
        
        notes = [UserNote(**n) for n in notes_data]
        
        # Apply filters
        if note_type:
            notes = [n for n in notes if n.note_type == note_type]
        
        if tags:
            notes = [n for n in notes if any(tag in n.tags for tag in tags)]
        
        return notes
    
    def update_note(
        self,
        workspace_id: str,
        note_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[UserNote]:
        """Update an existing note"""
        workspace_file = self._get_workspace_file(workspace_id)
        if not workspace_file.exists():
            return None
        
        with open(workspace_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        updated = False
        for note_dict in notes:
            if note_dict['id'] == note_id:
                if title is not None:
                    note_dict['title'] = title
                if content is not None:
                    note_dict['content'] = content
                if tags is not None:
                    note_dict['tags'] = tags
                if metadata is not None:
                    note_dict['metadata'].update(metadata)
                note_dict['updated_at'] = datetime.utcnow().isoformat()
                updated = True
                break
        
        if not updated:
            return None
        
        # Save updated notes
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if workspace_id in index:
            for item in index[workspace_id]:
                if item['id'] == note_id and title is not None:
                    item['title'] = title
                    if tags is not None:
                        item['tags'] = tags
        self._save_index(index)
        
        return self.get_note(workspace_id, note_id)
    
    def delete_note(self, workspace_id: str, note_id: str) -> bool:
        """Delete a note"""
        workspace_file = self._get_workspace_file(workspace_id)
        if not workspace_file.exists():
            return False
        
        with open(workspace_file, 'r', encoding='utf-8') as f:
            notes = json.load(f)
        
        original_count = len(notes)
        notes = [n for n in notes if n['id'] != note_id]
        
        if len(notes) == original_count:
            return False
        
        # Save updated notes
        with open(workspace_file, 'w', encoding='utf-8') as f:
            json.dump(notes, f, indent=2, ensure_ascii=False)
        
        # Update index
        index = self._load_index()
        if workspace_id in index:
            index[workspace_id] = [i for i in index[workspace_id] if i['id'] != note_id]
        self._save_index(index)
        
        return True
    
    def search_notes(self, workspace_id: str, query: str) -> List[UserNote]:
        """Search notes by content"""
        notes = self.list_notes(workspace_id)
        query_lower = query.lower()
        
        matches = []
        for note in notes:
            if (query_lower in note.title.lower() or
                query_lower in note.content.lower() or
                any(query_lower in tag.lower() for tag in note.tags)):
                matches.append(note)
        
        return matches
    
    def get_workspace_summary(self, workspace_id: str) -> Dict:
        """Get summary of notes for a workspace"""
        notes = self.list_notes(workspace_id)
        
        summary = {
            "total_notes": len(notes),
            "by_type": {},
            "all_tags": set(),
            "recent_notes": []
        }
        
        for note in notes:
            note_type = note.note_type
            summary["by_type"][note_type] = summary["by_type"].get(note_type, 0) + 1
            summary["all_tags"].update(note.tags)
        
        # Get 5 most recent notes
        sorted_notes = sorted(notes, key=lambda n: n.updated_at, reverse=True)
        summary["recent_notes"] = [
            {"id": n.id, "title": n.title, "type": n.note_type, "updated_at": n.updated_at}
            for n in sorted_notes[:5]
        ]
        
        summary["all_tags"] = list(summary["all_tags"])
        
        return summary


# Singleton instance
_notes_service = None

def get_notes_service() -> UserNotesService:
    """Get singleton notes service instance"""
    global _notes_service
    if _notes_service is None:
        storage_dir = os.getenv("USER_NOTES_DIR", "./data/user_notes")
        _notes_service = UserNotesService(storage_dir)
    return _notes_service
