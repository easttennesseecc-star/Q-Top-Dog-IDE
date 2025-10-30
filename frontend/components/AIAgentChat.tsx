// Frontend: AI Agent Chat Component (React/TypeScript)
// Real-time streaming responses, message history, cost tracking

import React, { useState, useRef, useEffect, useCallback } from 'react';
import './AIAgentChat.css';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  tokens_used?: number;
  cost?: number;
  model_id?: string;
}

interface ChatSession {
  id: string;
  model_id: string;
  model_name: string;
  messages: ChatMessage[];
  created_at: string;
  total_tokens: number;
  total_cost: number;
}

interface AIAgentChatProps {
  selectedModelId: string;
  selectedModelName: string;
  userToken: string;
  userBalance: number;
  onBalanceChange: (newBalance: number) => void;
}

const AIAgentChat: React.FC<AIAgentChatProps> = ({
  selectedModelId,
  selectedModelName,
  userToken,
  userBalance,
  onBalanceChange
}) => {
  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Session State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [totalTokens, setTotalTokens] = useState(0);
  const [totalCost, setTotalCost] = useState(0);

  // UI State
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [streamingResponse, setStreamingResponse] = useState('');

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatInputRef = useRef<HTMLTextAreaElement>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingResponse]);

  // ==================== SESSION MANAGEMENT ====================

  const createNewSession = useCallback(() => {
    const newSessionId = `session-${Date.now()}`;
    setSessionId(newSessionId);
    setMessages([]);
    setTotalTokens(0);
    setTotalCost(0);
    setStreamingResponse('');
  }, []);

  // Initialize session on component mount
  useEffect(() => {
    createNewSession();
  }, [createNewSession, selectedModelId]);

  // ==================== MESSAGE SENDING ====================

  const sendMessage = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() || isLoading || isStreaming) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setError(null);
    setStreamingResponse('');

    // Check balance before sending
    if (userBalance < 0.01) {
      setError('Insufficient balance. Please add funds.');
      return;
    }

    setIsLoading(true);

    try {
      // Prepare messages for API
      const conversationMessages = messages.map(m => ({
        role: m.role,
        content: m.content
      }));
      conversationMessages.push({
        role: 'user',
        content: inputValue
      });

      // Send to streaming endpoint
      abortControllerRef.current = new AbortController();

      const response = await fetch('/api/v1/agent/chat/stream', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model_id: selectedModelId,
          messages: conversationMessages,
          stream: true
        }),
        signal: abortControllerRef.current.signal
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to send message');
      }

      // Handle streaming response
      setIsStreaming(true);
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let fullResponse = '';

      while (reader && true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        fullResponse += chunk;
        setStreamingResponse(fullResponse);
      }

      // Create assistant message
      const assistantMessage: ChatMessage = {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: fullResponse,
        timestamp: new Date().toISOString(),
        model_id: selectedModelId,
        tokens_used: Math.ceil(fullResponse.length / 4), // Rough estimate
        cost: (Math.ceil(fullResponse.length / 4) / 1000) * 0.0015 // Estimate based on output
      };

      setMessages(prev => [...prev, assistantMessage]);
      setTotalTokens(prev => prev + (assistantMessage.tokens_used || 0));
      setTotalCost(prev => prev + (assistantMessage.cost || 0));

      // Update balance
      const newBalance = userBalance - (assistantMessage.cost || 0);
      onBalanceChange(newBalance);

      setStreamingResponse('');
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        setError(err.message || 'Failed to send message');
        // Remove incomplete user message
        setMessages(prev => prev.slice(0, -1));
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
      chatInputRef.current?.focus();
    }
  }, [inputValue, isLoading, isStreaming, messages, selectedModelId, userToken, userBalance, onBalanceChange]);

  // ==================== HELPER FUNCTIONS ====================

  const cancelStreaming = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsStreaming(false);
    }
  };

  const clearHistory = () => {
    if (window.confirm('Are you sure? This will clear all messages.')) {
      createNewSession();
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const exportChat = () => {
    const chat = {
      model: selectedModelName,
      session_id: sessionId,
      created_at: new Date().toISOString(),
      total_tokens: totalTokens,
      total_cost: totalCost.toFixed(4),
      messages: messages
    };

    const dataStr = JSON.stringify(chat, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr);

    const exportFileDefaultName = `chat-${sessionId}.json`;

    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // ==================== RENDER ====================

  return (
    <div className="ai-agent-chat">
      <div className="chat-header">
        <div className="header-left">
          <h2>💬 {selectedModelName}</h2>
          <span className="model-badge">{selectedModelId}</span>
        </div>

        <div className="header-right">
          <div className="stats">
            <span className="stat">
              💰 ${userBalance.toFixed(2)}
            </span>
            <span className="stat">
              📊 {totalTokens} tokens
            </span>
            <span className="stat">
              💸 ${totalCost.toFixed(4)}
            </span>
          </div>

          <div className="header-actions">
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="icon-btn"
              title="Settings"
            >
              ⚙️
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="icon-btn"
              title="History"
            >
              📜
            </button>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="settings-panel">
          <h3>Chat Settings</h3>
          <div className="settings-options">
            <label>
              <input type="checkbox" disabled />
              Include Context (Coming Soon)
            </label>
            <label>
              <input type="checkbox" disabled />
              Code Highlighting (Coming Soon)
            </label>
          </div>
          <div className="settings-actions">
            <button onClick={exportChat} className="btn-secondary">
              📥 Export Chat
            </button>
            <button onClick={clearHistory} className="btn-secondary">
              🗑️ Clear History
            </button>
          </div>
        </div>
      )}

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {/* Messages Container */}
      <div className="messages-container">
        {messages.length === 0 && !streamingResponse && (
          <div className="empty-state">
            <div className="empty-icon">🤖</div>
            <h3>Ready to chat!</h3>
            <p>Start a conversation with {selectedModelName}</p>
            <p className="hint">Pro tip: Describe your task clearly for better results</p>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>

            <div className="message-content">
              <div className="message-header">
                <span className="role">{message.role === 'user' ? 'You' : selectedModelName}</span>
                <span className="timestamp">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>

              <div className="message-text">
                {message.content}
              </div>

              {message.role === 'assistant' && (
                <div className="message-meta">
                  <span>🔤 {message.tokens_used} tokens</span>
                  <span>💸 ${message.cost?.toFixed(4)}</span>
                  <button
                    onClick={() => copyToClipboard(message.content)}
                    className="copy-btn"
                    title="Copy"
                  >
                    📋
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {streamingResponse && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>

            <div className="message-content">
              <div className="message-header">
                <span className="role">{selectedModelName}</span>
                <span className="streaming-indicator">Streaming...</span>
              </div>

              <div className="message-text streaming">
                {streamingResponse}
                <span className="cursor">▌</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="input-area">
        <form onSubmit={sendMessage} className="message-form">
          <div className="input-wrapper">
            <textarea
              ref={chatInputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  sendMessage(e as any);
                }
              }}
              placeholder="Type your message... (Ctrl+Enter to send)"
              disabled={isLoading || isStreaming}
              rows={3}
              className="message-input"
            />

            <div className="input-actions">
              <button
                type="submit"
                disabled={isLoading || isStreaming || !inputValue.trim()}
                className="btn-send"
              >
                {isLoading || isStreaming ? '⏳' : '➤'}
              </button>

              {isStreaming && (
                <button
                  type="button"
                  onClick={cancelStreaming}
                  className="btn-cancel"
                >
                  ⏹️ Stop
                </button>
              )}
            </div>
          </div>

          <div className="input-info">
            <span>{inputValue.length} characters</span>
            <span className={userBalance < 0.01 ? 'low-balance' : ''}>
              Balance: ${userBalance.toFixed(2)}
            </span>
          </div>
        </form>
      </div>

      {/* History Sidebar */}
      {showHistory && (
        <div className="history-sidebar">
          <h3>Session</h3>
          <div className="session-info">
            <p><strong>Session ID:</strong> {sessionId}</p>
            <p><strong>Messages:</strong> {messages.length}</p>
            <p><strong>Total Cost:</strong> ${totalCost.toFixed(4)}</p>
          </div>

          <h4>Messages</h4>
          <div className="messages-list">
            {messages.map((msg, idx) => (
              <div key={msg.id} className="history-item">
                <span className="idx">{idx + 1}</span>
                <span className="role">{msg.role === 'user' ? '👤' : '🤖'}</span>
                <span className="preview">
                  {msg.content.substring(0, 40)}...
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAgentChat;
