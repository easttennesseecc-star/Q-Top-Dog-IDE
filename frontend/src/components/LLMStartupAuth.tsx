/*
 * LLM Startup Authentication Component
 * Q-IDE - Intelligent Development Environment
 * Copyright (c) 2025 Quellum Technologies. All rights reserved.
 * Licensed under the MIT License
 */

import React, { useEffect, useState } from 'react';

interface MissingLLM {
  llm_id: string;
  name: string;
  provider: string;
  auth_type: string;
  assigned_role: string;
  setup_url: string;
  alternatives: string[];
}

interface AuthPrompt {
  status: 'ready' | 'needs_setup';
  message: string;
  needs_action: boolean;
  missing_count?: number;
  missing_llms?: MissingLLM[];
  action_options?: Array<{
    option: string;
    label: string;
    description: string;
  }>;
}

interface LLMStartupAuthProps {
  onClose?: () => void;
  onAction?: (action: string, llmId?: string) => void;
}

export default function LLMStartupAuth({ onClose, onAction }: LLMStartupAuthProps) {
  const [authPrompt, setAuthPrompt] = useState<AuthPrompt | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  useEffect(() => {
    fetchAuthStatus();
  }, []);

  async function fetchAuthStatus() {
    try {
      const res = await fetch('/llm_config/startup_auth_status');
      const data = await res.json();
      
      if (data.startup_prompt) {
        setAuthPrompt(data.startup_prompt);
      }
    } catch (e) {
      console.error('Error fetching auth status:', e);
    } finally {
      setLoading(false);
    }
  }

  async function handleAction(action: string) {
    setSelectedAction(action);
    
    try {
      const res = await fetch('/llm_config/handle_missing_credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
      
      const result = await res.json();
      onAction?.(action, result);
      
      // Auto-close after brief delay
      setTimeout(() => onClose?.(), 1000);
    } catch (e) {
      console.error('Error handling action:', e);
    }
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-[#1e2128] border border-cyan-600/30 rounded p-8 max-w-md">
          <div className="animate-spin w-8 h-8 border-2 border-cyan-600 border-t-transparent rounded-full mx-auto mb-4"></div>
          <p className="text-cyan-300 text-center">Checking LLM authentication...</p>
        </div>
      </div>
    );
  }

  // If everything is ready, don't show prompt
  if (!authPrompt || authPrompt.status === 'ready') {
    return null;
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-[#23272e] border-2 border-cyan-600/50 rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-[#1a1e23] border-b border-cyan-600/30 p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-2xl font-bold text-cyan-300 mb-2">⚠️ LLM Setup Required</h2>
              <p className="text-gray-400">{authPrompt.message}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-cyan-300 text-2xl"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Missing LLMs List */}
        {authPrompt.missing_llms && authPrompt.missing_llms.length > 0 && (
          <div className="p-6 border-b border-cyan-600/20">
            <h3 className="text-lg font-semibold text-cyan-200 mb-4">Missing Credentials</h3>
            <div className="space-y-3">
              {authPrompt.missing_llms.map((llm) => (
                <div
                  key={llm.llm_id}
                  className="p-4 bg-[#0f1114] border border-red-600/30 rounded"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-cyan-200">{llm.name}</h4>
                      <p className="text-sm text-gray-400 mt-1">
                        Assigned to: <span className="text-cyan-300 font-medium">{llm.assigned_role}</span>
                      </p>
                      <p className="text-xs text-gray-500 mt-1">{llm.provider} • {llm.auth_type}</p>
                    </div>
                    <a
                      href={llm.setup_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-3 py-1 text-xs bg-blue-700/40 hover:bg-blue-700/60 text-blue-300 rounded whitespace-nowrap ml-4"
                    >
                      Get Key →
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Options */}
        {authPrompt.action_options && (
          <div className="p-6 space-y-3">
            {authPrompt.action_options.map((option) => (
              <button
                key={option.option}
                onClick={() => handleAction(option.option)}
                disabled={selectedAction !== null}
                className={`w-full p-4 rounded border-2 transition-all text-left ${
                  selectedAction === option.option
                    ? 'border-green-600 bg-green-900/20'
                    : 'border-cyan-600/30 bg-[#0f1114] hover:border-cyan-400 hover:bg-cyan-900/10'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                <div className="font-semibold text-cyan-200">{option.label}</div>
                <div className="text-sm text-gray-400 mt-1">{option.description}</div>
                {selectedAction === option.option && (
                  <div className="mt-2 text-green-400 text-sm">✓ Loading...</div>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Info Box */}
        <div className="bg-blue-900/20 border-t border-blue-600/30 p-6 text-sm text-blue-300">
          <p className="mb-2">
            <strong>💡 What's happening:</strong>
          </p>
          <ul className="list-disc list-inside space-y-1 text-gray-400 text-xs">
            <li>You have LLMs assigned to roles but they need API credentials</li>
            <li>You can add credentials now, use alternatives, or continue with smart fallbacks</li>
            <li>You can always add/change credentials later in LLM Setup → Auth tab</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
