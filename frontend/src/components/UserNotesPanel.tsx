/**
 * User Notes & Explanations Panel
 * Persistent storage for user context, preferences, and instructions
 */

import React, { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Search, Tag, Book, Star, Settings, FileText, HelpCircle } from 'lucide-react';

interface UserNote {
  id: string;
  workspace_id: string;
  note_type: 'context' | 'preference' | 'instruction' | 'build_rule' | 'clarification';
  title: string;
  content: string;
  tags: string[];
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

interface UserNotesPanelProps {
  workspaceId: string;
}

const NOTE_TYPE_ICONS = {
  context: Book,
  preference: Star,
  instruction: FileText,
  build_rule: Settings,
  clarification: HelpCircle
};

const NOTE_TYPE_COLORS = {
  context: 'text-blue-400',
  preference: 'text-purple-400',
  instruction: 'text-green-400',
  build_rule: 'text-orange-400',
  clarification: 'text-pink-400'
};

export default function UserNotesPanel({ workspaceId }: UserNotesPanelProps) {
  const [notes, setNotes] = useState<UserNote[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [editingNote, setEditingNote] = useState<UserNote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    note_type: 'context' as UserNote['note_type'],
    tags: [] as string[],
    tagInput: ''
  });

  useEffect(() => {
    fetchNotes();
  }, [workspaceId]);

  const fetchNotes = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/v1/notes/${workspaceId}`);
      if (!response.ok) throw new Error('Failed to fetch notes');
      const data = await response.json();
      setNotes(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const createNote = async () => {
    try {
      const response = await fetch(`/api/v1/notes/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workspace_id: workspaceId,
          title: formData.title,
          content: formData.content,
          note_type: formData.note_type,
          tags: formData.tags
        })
      });
      if (!response.ok) throw new Error('Failed to create note');
      resetForm();
      setIsCreating(false);
      fetchNotes();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const updateNote = async (noteId: string) => {
    try {
      const response = await fetch(`/api/v1/notes/${workspaceId}/${noteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: formData.title,
          content: formData.content,
          tags: formData.tags
        })
      });
      if (!response.ok) throw new Error('Failed to update note');
      resetForm();
      setEditingNote(null);
      fetchNotes();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const deleteNote = async (noteId: string) => {
    if (!confirm('Delete this note?')) return;
    try {
      const response = await fetch(`/api/v1/notes/${workspaceId}/${noteId}`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error('Failed to delete note');
      fetchNotes();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      note_type: 'context',
      tags: [],
      tagInput: ''
    });
  };

  const startEdit = (note: UserNote) => {
    setEditingNote(note);
    setFormData({
      title: note.title,
      content: note.content,
      note_type: note.note_type,
      tags: note.tags,
      tagInput: ''
    });
    setIsCreating(false);
  };

  const addTag = () => {
    if (formData.tagInput.trim() && !formData.tags.includes(formData.tagInput.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, formData.tagInput.trim()],
        tagInput: ''
      });
    }
  };

  const removeTag = (tag: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(t => t !== tag)
    });
  };

  const filteredNotes = notes.filter(note => {
    if (selectedType && note.note_type !== selectedType) return false;
    if (selectedTags.length > 0 && !selectedTags.some(tag => note.tags.includes(tag))) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return note.title.toLowerCase().includes(query) ||
             note.content.toLowerCase().includes(query) ||
             note.tags.some(tag => tag.toLowerCase().includes(query));
    }
    return true;
  });

  const allTags = Array.from(new Set(notes.flatMap(n => n.tags))).sort();

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white">
      {/* Header */}
      <div className="p-4 border-b border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">User Notes & Context</h2>
          <button
            onClick={() => { setIsCreating(true); setEditingNote(null); resetForm(); }}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
          >
            <Plus size={18} /> New Note
          </button>
        </div>

        {/* Search & Filters */}
        <div className="space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-3 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
            />
          </div>

          {/* Type Filter */}
          <div className="flex gap-2 flex-wrap">
            {Object.keys(NOTE_TYPE_ICONS).map(type => {
              const Icon = NOTE_TYPE_ICONS[type as keyof typeof NOTE_TYPE_ICONS];
              const isSelected = selectedType === type;
              return (
                <button
                  key={type}
                  onClick={() => setSelectedType(isSelected ? null : type)}
                  className={`flex items-center gap-1 px-3 py-1 rounded text-sm ${
                    isSelected ? 'bg-blue-600' : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                >
                  <Icon className={NOTE_TYPE_COLORS[type as keyof typeof NOTE_TYPE_COLORS]} />
                  {type}
                </button>
              );
            })}
          </div>

          {/* Tag Filter */}
          {allTags.length > 0 && (
            <div className="flex gap-2 flex-wrap">
              {allTags.map(tag => {
                const isSelected = selectedTags.includes(tag);
                return (
                  <button
                    key={tag}
                    onClick={() => setSelectedTags(
                      isSelected ? selectedTags.filter(t => t !== tag) : [...selectedTags, tag]
                    )}
                    className={`flex items-center gap-1 px-2 py-1 rounded text-xs ${
                      isSelected ? 'bg-purple-600' : 'bg-gray-700 hover:bg-gray-600'
                    }`}
                  >
                    <Tag size={12} /> {tag}
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Notes List or Form */}
      <div className="flex-1 overflow-y-auto p-4">
        {error && (
          <div className="mb-4 p-3 bg-red-900/50 border border-red-500 rounded text-sm">
            {error}
          </div>
        )}

        {(isCreating || editingNote) ? (
          <div className="bg-gray-800 p-4 rounded border border-gray-700">
            <h3 className="text-lg font-bold mb-4">
              {editingNote ? 'Edit Note' : 'Create Note'}
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Type</label>
                <select
                  value={formData.note_type}
                  onChange={(e) => setFormData({ ...formData, note_type: e.target.value as any })}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                >
                  {Object.keys(NOTE_TYPE_ICONS).map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Title</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="Note title..."
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Content</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="Note content..."
                  rows={8}
                  className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Tags</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={formData.tagInput}
                    onChange={(e) => setFormData({ ...formData, tagInput: e.target.value })}
                    onKeyPress={(e) => e.key === 'Enter' && addTag()}
                    placeholder="Add tag..."
                    className="flex-1 px-3 py-2 bg-gray-900 border border-gray-700 rounded focus:outline-none focus:border-blue-500"
                  />
                  <button
                    onClick={addTag}
                    className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
                  >
                    Add
                  </button>
                </div>
                <div className="flex gap-2 flex-wrap">
                  {formData.tags.map(tag => (
                    <span
                      key={tag}
                      className="flex items-center gap-1 px-2 py-1 bg-gray-700 rounded text-sm"
                    >
                      {tag}
                      <button onClick={() => removeTag(tag)} className="hover:text-red-400">
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => editingNote ? updateNote(editingNote.id) : createNote()}
                  disabled={!formData.title || !formData.content}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {editingNote ? 'Update' : 'Create'}
                </button>
                <button
                  onClick={() => { setIsCreating(false); setEditingNote(null); resetForm(); }}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            {loading && <div className="text-center text-gray-400">Loading notes...</div>}
            {!loading && filteredNotes.length === 0 && (
              <div className="text-center text-gray-400 py-8">
                No notes found. Create your first note to remember context across sessions!
              </div>
            )}
            {filteredNotes.map(note => {
              const Icon = NOTE_TYPE_ICONS[note.note_type];
              return (
                <div
                  key={note.id}
                  className="bg-gray-800 p-4 rounded border border-gray-700 hover:border-gray-600"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className={NOTE_TYPE_COLORS[note.note_type]} />
                      <h3 className="font-semibold">{note.title}</h3>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => startEdit(note)}
                        className="text-blue-400 hover:text-blue-300"
                      >
                        <Edit2 size={16} />
                      </button>
                      <button
                        onClick={() => deleteNote(note.id)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>

                  <p className="text-sm text-gray-300 mb-2 whitespace-pre-wrap">{note.content}</p>

                  {note.tags.length > 0 && (
                    <div className="flex gap-1 flex-wrap mb-2">
                      {note.tags.map(tag => (
                        <span
                          key={tag}
                          className="text-xs px-2 py-1 bg-gray-700 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    Updated: {new Date(note.updated_at).toLocaleString()}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
