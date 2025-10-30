// Frontend: AI Authentication Modal Component (React/TypeScript)
// Sign up/login, API key management, prepaid balance

import React, { useState, useCallback } from 'react';
import './AIAuthModal.css';

interface User {
  id: string;
  email: string;
  username: string;
  balance: {
    total_balance: number;
    available_balance: number;
    spent_balance: number;
  };
}

interface APIKeyInfo {
  id: string;
  provider: string;
  status: string;
  created_at: string;
  usage_count: number;
}

interface AuthToken {
  token: string;
  user_id: string;
  expires_at: string;
}

type TabType = 'login' | 'register' | 'keys' | 'balance';

interface AIAuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (token: string, user: User) => void;
}

const AIAuthModal: React.FC<AIAuthModalProps> = ({
  isOpen,
  onClose,
  onAuthSuccess
}) => {
  // Auth State
  const [activeTab, setActiveTab] = useState<TabType>('login');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // User Data
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // API Keys
  const [apiKeys, setApiKeys] = useState<APIKeyInfo[]>([]);
  const [showAddKeyForm, setShowAddKeyForm] = useState(false);
  const [newKeyProvider, setNewKeyProvider] = useState('openai');
  const [newKeyValue, setNewKeyValue] = useState('');
  const [loadingKeys, setLoadingKeys] = useState(false);

  // Balance
  const [addFundsAmount, setAddFundsAmount] = useState('10');
  const [paymentMethod, setPaymentMethod] = useState('credit_card');

  // ==================== AUTH FUNCTIONS ====================

  const handleLogin = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (!email || !password) {
        throw new Error('Email and password are required');
      }

      const response = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Login failed');
      }

      const data: { data: AuthToken } = await response.json();
      setToken(data.data.token);
      
      // Fetch user data
      await fetchUserData(data.data.token);
      
      setSuccess('Login successful!');
      setTimeout(() => {
        onAuthSuccess(data.data.token, user || {} as User);
      }, 500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  }, [email, password, user, onAuthSuccess]);

  const handleRegister = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      if (!email || !username || !password || !confirmPassword) {
        throw new Error('All fields are required');
      }

      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }

      if (password.length < 8) {
        throw new Error('Password must be at least 8 characters');
      }

      const response = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, password })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Registration failed');
      }

      setSuccess('Registration successful! Now logging in...');
      
      // Auto-login
      setTimeout(() => {
        setActiveTab('login');
        setPassword('');
        setConfirmPassword('');
      }, 1000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  }, [email, username, password, confirmPassword]);

  const fetchUserData = useCallback(async (authToken: string) => {
    try {
      const response = await fetch('/api/v1/auth/verify-token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        // In production, fetch actual user data
        const userData: User = {
          id: 'user-123',
          email: email,
          username: username,
          balance: {
            total_balance: 50,
            available_balance: 45,
            spent_balance: 5
          }
        };
        setUser(userData);
      }
    } catch (err) {
      console.error('Failed to fetch user data:', err);
    }
  }, [email, username]);

  // ==================== API KEY FUNCTIONS ====================

  const loadAPIKeys = useCallback(async () => {
    if (!token) return;

    setLoadingKeys(true);
    try {
      const response = await fetch('/api/v1/balance/api-keys', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setApiKeys(data.data || []);
      }
    } catch (err) {
      setError('Failed to load API keys');
    } finally {
      setLoadingKeys(false);
    }
  }, [token]);

  const addAPIKey = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!newKeyValue) {
      setError('API key is required');
      return;
    }

    try {
      const response = await fetch('/api/v1/balance/api-keys/add', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider: newKeyProvider,
          api_key: newKeyValue
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Failed to add API key');
      }

      setSuccess(`${newKeyProvider} API key added!`);
      setNewKeyValue('');
      setShowAddKeyForm(false);
      await loadAPIKeys();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add API key');
    }
  }, [token, newKeyProvider, newKeyValue, loadAPIKeys]);

  const removeAPIKey = useCallback(async (keyId: string) => {
    if (!token) return;

    try {
      const response = await fetch(`/api/v1/balance/api-keys/${keyId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        setSuccess('API key removed');
        await loadAPIKeys();
      }
    } catch (err) {
      setError('Failed to remove API key');
    }
  }, [token, loadAPIKeys]);

  // ==================== BALANCE FUNCTIONS ====================

  const addFunds = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!addFundsAmount || parseFloat(addFundsAmount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    try {
      const response = await fetch('/api/v1/balance/add-funds', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount: parseFloat(addFundsAmount),
          payment_method: paymentMethod
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Payment failed');
      }

      setSuccess('Funds added successfully!');
      setAddFundsAmount('10');
      
      // Update user balance (in production, fetch updated data)
      if (user) {
        user.balance.total_balance += parseFloat(addFundsAmount);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Payment failed');
    }
  }, [token, addFundsAmount, paymentMethod, user]);

  // ==================== RENDER ====================

  if (!isOpen) return null;

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🤖 AI Marketplace</h2>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>

        {/* Tab Navigation */}
        {!token && (
          <div className="tab-navigation">
            <button
              className={`tab ${activeTab === 'login' ? 'active' : ''}`}
              onClick={() => setActiveTab('login')}
            >
              Login
            </button>
            <button
              className={`tab ${activeTab === 'register' ? 'active' : ''}`}
              onClick={() => setActiveTab('register')}
            >
              Register
            </button>
          </div>
        )}

        {/* Alert Messages */}
        {error && (
          <div className="alert alert-error">
            <span>⚠️ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        {success && (
          <div className="alert alert-success">
            <span>✅ {success}</span>
          </div>
        )}

        {/* Login Tab */}
        {activeTab === 'login' && !token && (
          <form onSubmit={handleLogin} className="auth-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary">
              {isLoading ? 'Logging in...' : 'Login'}
            </button>
          </form>
        )}

        {/* Register Tab */}
        {activeTab === 'register' && !token && (
          <form onSubmit={handleRegister} className="auth-form">
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="username"
                required
              />
            </div>

            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <div className="form-group">
              <label>Confirm Password</label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary">
              {isLoading ? 'Creating account...' : 'Register'}
            </button>
          </form>
        )}

        {/* API Keys Tab */}
        {token && activeTab === 'keys' && (
          <div className="keys-section">
            <h3>API Keys</h3>
            <p>Add your API keys for different providers</p>

            {showAddKeyForm ? (
              <form onSubmit={addAPIKey} className="add-key-form">
                <select
                  value={newKeyProvider}
                  onChange={(e) => setNewKeyProvider(e.target.value)}
                  className="form-control"
                >
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="google_gemini">Google Gemini</option>
                  <option value="huggingface">HuggingFace</option>
                </select>

                <input
                  type="password"
                  value={newKeyValue}
                  onChange={(e) => setNewKeyValue(e.target.value)}
                  placeholder="Paste your API key..."
                  className="form-control"
                />

                <div className="form-actions">
                  <button type="submit" className="btn-primary">Add Key</button>
                  <button
                    type="button"
                    onClick={() => setShowAddKeyForm(false)}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <button
                onClick={() => setShowAddKeyForm(true)}
                className="btn-secondary"
              >
                + Add API Key
              </button>
            )}

            {loadingKeys ? (
              <p>Loading keys...</p>
            ) : (
              <div className="keys-list">
                {apiKeys.map(key => (
                  <div key={key.id} className="key-item">
                    <span className="key-provider">{key.provider}</span>
                    <span className="key-status">{key.status}</span>
                    <button
                      onClick={() => removeAPIKey(key.id)}
                      className="btn-delete"
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Balance Tab */}
        {token && activeTab === 'balance' && (
          <div className="balance-section">
            <h3>Prepaid Balance</h3>

            {user && (
              <div className="balance-info">
                <div className="balance-card">
                  <span className="label">Total Balance</span>
                  <span className="amount">${user.balance.total_balance.toFixed(2)}</span>
                </div>

                <div className="balance-card">
                  <span className="label">Available</span>
                  <span className="amount">${user.balance.available_balance.toFixed(2)}</span>
                </div>

                <div className="balance-card">
                  <span className="label">Spent</span>
                  <span className="amount">${user.balance.spent_balance.toFixed(2)}</span>
                </div>
              </div>
            )}

            <form onSubmit={addFunds} className="add-funds-form">
              <div className="form-group">
                <label>Add Funds</label>
                <input
                  type="number"
                  value={addFundsAmount}
                  onChange={(e) => setAddFundsAmount(e.target.value)}
                  min="1"
                  step="0.01"
                  className="form-control"
                />
              </div>

              <div className="form-group">
                <label>Payment Method</label>
                <select
                  value={paymentMethod}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  className="form-control"
                >
                  <option value="credit_card">Credit Card</option>
                  <option value="debit_card">Debit Card</option>
                  <option value="paypal">PayPal</option>
                </select>
              </div>

              <button type="submit" className="btn-primary">
                Add ${addFundsAmount}
              </button>
            </form>
          </div>
        )}

        {/* Authenticated User Navigation */}
        {token && (
          <div className="user-nav">
            <button
              onClick={() => setActiveTab('keys')}
              className={`nav-btn ${activeTab === 'keys' ? 'active' : ''}`}
            >
              API Keys
            </button>
            <button
              onClick={() => setActiveTab('balance')}
              className={`nav-btn ${activeTab === 'balance' ? 'active' : ''}`}
            >
              Balance
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default AIAuthModal;
