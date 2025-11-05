import React, { useState, useEffect } from 'react';

interface Rule {
  id: string;
  name: string;
  description: string;
  rule_text: string;
  rule_type: string;
  scope: string;
  enforcement: string;
  applies_to: string[];
  active: boolean;
  priority: number;
  tags: string[];
  created_by: string;
  created_at: string;
  modified_at: string;
}

const ruleTypeIcons: Record<string, string> = {
  code_style: '📝',
  architecture: '🏗️',
  security: '🔒',
  performance: '⚡',
  testing: '🧪',
  documentation: '📚',
  build: '📦',
  deployment: '☁️',
};

const enforcementColors: Record<string, string> = {
  mandatory: 'bg-red-100 text-red-800',
  strict: 'bg-orange-100 text-orange-800',
  guidance: 'bg-blue-100 text-blue-800',
  suggestion: 'bg-green-100 text-green-800',
};

export default function RulesManagement() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTab, setSelectedTab] = useState(0);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [viewingRule, setViewingRule] = useState<Rule | null>(null);
  
  // Form state
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    rule_text: '',
    rule_type: 'code_style',
    scope: 'global',
    enforcement: 'strict',
    applies_to: [] as string[],
    priority: 100,
    tags: [] as string[],
  });

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const response = await fetch('/rules/');
      if (!response.ok) throw new Error('Failed to fetch rules');
      const data = await response.json();
      setRules(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRule = async () => {
    try {
      const response = await fetch('/rules/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error('Failed to create rule');
      await fetchRules();
      setOpenDialog(false);
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const handleUpdateRule = async () => {
    if (!editingRule) return;
    try {
      const response = await fetch(`/rules/${editingRule.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      if (!response.ok) throw new Error('Failed to update rule');
      await fetchRules();
      setOpenDialog(false);
      setEditingRule(null);
      resetForm();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const handleDeleteRule = async (ruleId: string) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    try {
      const response = await fetch(`/rules/${ruleId}`, { method: 'DELETE' });
      if (!response.ok) throw new Error('Failed to delete rule');
      await fetchRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const handleToggleActive = async (rule: Rule) => {
    try {
      const endpoint = rule.active
        ? `/rules/${rule.id}/deactivate`
        : `/rules/${rule.id}/activate`;
      const response = await fetch(endpoint, { method: 'POST' });
      if (!response.ok) throw new Error('Failed to toggle rule');
      await fetchRules();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const openCreateDialog = () => {
    resetForm();
    setEditingRule(null);
    setOpenDialog(true);
  };

  const openEditDialog = (rule: Rule) => {
    setFormData({
      name: rule.name,
      description: rule.description,
      rule_text: rule.rule_text,
      rule_type: rule.rule_type,
      scope: rule.scope,
      enforcement: rule.enforcement,
      applies_to: rule.applies_to,
      priority: rule.priority,
      tags: rule.tags,
    });
    setEditingRule(rule);
    setOpenDialog(true);
  };

  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      rule_text: '',
      rule_type: 'code_style',
      scope: 'global',
      enforcement: 'strict',
      applies_to: [],
      priority: 100,
      tags: [],
    });
  };

  const filterRules = (rules: Rule[]) => {
    switch (selectedTab) {
      case 1: // Mandatory
        return rules.filter(r => r.enforcement === 'mandatory');
      case 2: // Active
        return rules.filter(r => r.active);
      case 3: // Inactive
        return rules.filter(r => !r.active);
      default: // All
        return rules;
    }
  };

  const filteredRules = filterRules(rules);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Rules Management
        </h1>
        <button
          onClick={openCreateDialog}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
        >
          <span className="text-xl">+</span>
          Create Rule
        </button>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <span className="text-red-600 text-xl">⚠️</span>
          <div className="flex-1">
            <p className="text-red-800">{error}</p>
          </div>
          <button onClick={() => setError(null)} className="text-red-600 hover:text-red-800">
            <span className="text-xl">×</span>
          </button>
        </div>
      )}

      {/* Info Alert */}
      <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
        <span className="text-blue-600 text-xl">ℹ️</span>
        <p className="text-blue-800 font-semibold">
          ALL AI models (Claude, GPT-4, Gemini, Copilot, Cursor, etc.) will automatically
          respect these rules in their responses.
        </p>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex gap-4">
          <button
            onClick={() => setSelectedTab(0)}
            className={`pb-3 px-1 border-b-2 transition ${
              selectedTab === 0
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            All Rules ({rules.length})
          </button>
          <button
            onClick={() => setSelectedTab(1)}
            className={`pb-3 px-1 border-b-2 transition ${
              selectedTab === 1
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Mandatory ({rules.filter(r => r.enforcement === 'mandatory').length})
          </button>
          <button
            onClick={() => setSelectedTab(2)}
            className={`pb-3 px-1 border-b-2 transition ${
              selectedTab === 2
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Active ({rules.filter(r => r.active).length})
          </button>
          <button
            onClick={() => setSelectedTab(3)}
            className={`pb-3 px-1 border-b-2 transition ${
              selectedTab === 3
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            Inactive ({rules.filter(r => !r.active).length})
          </button>
        </div>
      </div>

      {/* Rules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredRules.map((rule) => (
          <div key={rule.id} className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm p-5">
            {/* Rule Header */}
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2 flex-1 min-w-0">
                {ruleTypeIcons[rule.rule_type]}
                <h3 className="font-semibold text-gray-900 dark:text-white truncate">
                  {rule.name}
                </h3>
              </div>
              <div className="flex gap-1 ml-2">
                <button
                  onClick={() => setViewingRule(rule)}
                  className="p-1 text-gray-600 hover:text-blue-600 transition"
                  title="View Details"
                >
                  <span>👁️</span>
                </button>
                <button
                  onClick={() => openEditDialog(rule)}
                  className="p-1 text-gray-600 hover:text-blue-600 transition"
                  title="Edit"
                >
                  <span>✏️</span>
                </button>
                <button
                  onClick={() => handleDeleteRule(rule.id)}
                  className="p-1 text-gray-600 hover:text-red-600 transition"
                  title="Delete"
                >
                  <span>🗑️</span>
                </button>
              </div>
            </div>

            {/* Description */}
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              {rule.description}
            </p>

            {/* Status Badges */}
            <div className="flex flex-wrap gap-2 mb-3">
              <span className={`px-2 py-1 rounded text-xs font-medium ${enforcementColors[rule.enforcement]}`}>
                {rule.enforcement}
              </span>
              <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-300">
                {rule.scope}
              </span>
              <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 border border-gray-300">
                {rule.rule_type}
              </span>
            </div>

            {/* Tags */}
            {rule.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mb-3">
                {rule.tags.map(tag => (
                  <span key={tag} className="px-2 py-0.5 rounded text-xs bg-gray-200 text-gray-700">
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Active Toggle */}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={rule.active}
                onChange={() => handleToggleActive(rule)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {rule.active ? 'Active' : 'Inactive'}
              </span>
            </label>
          </div>
        ))}
      </div>

      {/* Create/Edit Modal */}
      {openDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {editingRule ? 'Edit Rule' : 'Create New Rule'}
              </h2>
              <button onClick={() => setOpenDialog(false)} className="text-gray-500 hover:text-gray-700">
                <span className="text-2xl">×</span>
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Rule Name *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Rule Text *
                </label>
                <textarea
                  value={formData.rule_text}
                  onChange={(e) => setFormData({ ...formData, rule_text: e.target.value })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white font-mono text-sm"
                  required
                />
                <p className="mt-1 text-xs text-gray-500">This is what will be injected into AI model prompts</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Rule Type
                </label>
                <select
                  value={formData.rule_type}
                  onChange={(e) => setFormData({ ...formData, rule_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="code_style">Code Style</option>
                  <option value="architecture">Architecture</option>
                  <option value="security">Security</option>
                  <option value="performance">Performance</option>
                  <option value="testing">Testing</option>
                  <option value="documentation">Documentation</option>
                  <option value="build">Build</option>
                  <option value="deployment">Deployment</option>
                  <option value="custom">Custom</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Scope
                </label>
                <select
                  value={formData.scope}
                  onChange={(e) => setFormData({ ...formData, scope: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="global">Global (All Projects)</option>
                  <option value="project">Project-Specific</option>
                  <option value="file">File/Folder Pattern</option>
                  <option value="build">Build-Specific</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Enforcement Level
                </label>
                <select
                  value={formData.enforcement}
                  onChange={(e) => setFormData({ ...formData, enforcement: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                >
                  <option value="mandatory">🔴 Mandatory - Blocks non-compliant responses</option>
                  <option value="strict">🟠 Strict - Warns on violations</option>
                  <option value="guidance">🟡 Guidance - Best practice (logged)</option>
                  <option value="suggestion">🟢 Suggestion - Nice to have</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Priority
                </label>
                <input
                  type="number"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
                <p className="mt-1 text-xs text-gray-500">Lower numbers = higher priority</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={(e) => setFormData({
                    ...formData,
                    tags: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
                  })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
                />
              </div>
            </div>

            <div className="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-6 flex justify-end gap-3">
              <button
                onClick={() => setOpenDialog(false)}
                className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={editingRule ? handleUpdateRule : handleCreateRule}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                {editingRule ? 'Update' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* View Modal */}
      {viewingRule && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {viewingRule.name}
              </h2>
              <button onClick={() => setViewingRule(null)} className="text-gray-500 hover:text-gray-700">
                <span className="text-2xl">×</span>
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  <strong className="text-gray-900 dark:text-white">Description:</strong> {viewingRule.description}
                </p>
              </div>

              <div>
                <p className="text-sm font-semibold text-gray-900 dark:text-white mb-2">Rule Text:</p>
                <pre className="p-4 bg-gray-100 dark:bg-gray-900 rounded-lg text-sm font-mono whitespace-pre-wrap overflow-x-auto">
                  {viewingRule.rule_text}
                </pre>
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-sm">
                  Type: {viewingRule.rule_type}
                </span>
                <span className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-sm">
                  Scope: {viewingRule.scope}
                </span>
                <span className={`px-3 py-1 rounded text-sm ${enforcementColors[viewingRule.enforcement]}`}>
                  Enforcement: {viewingRule.enforcement}
                </span>
                <span className="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 text-sm">
                  Priority: {viewingRule.priority}
                </span>
              </div>

              <div className="text-xs text-gray-500">
                <p>Created: {new Date(viewingRule.created_at).toLocaleString()}</p>
                <p>Modified: {new Date(viewingRule.modified_at).toLocaleString()}</p>
              </div>
            </div>

            <div className="sticky bottom-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-6 flex justify-end">
              <button
                onClick={() => setViewingRule(null)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
