# AI AGENT MARKETPLACE - IMPLEMENTATION GUIDE

**Phase**: Gap #5 (NEW - After Game Engines)  
**Timeline**: Week 2-3 concurrent with core IDE gaps  
**Team Size**: 2 developers (Backend + Frontend)  
**Scope**: 3,500+ lines of production code  
**Est. Time**: 10 working days  

---

## IMPLEMENTATION ROADMAP

```
Week 1-2 (IntelliSense + Refactoring + Game Engines)
    ├─ Day 1: Marketplace registry + basic backend
    ├─ Day 2-3: Auth service + API key storage
    ├─ Day 3: Recommendation engine
    ├─ Day 4: Multi-LLM router
    ├─ Day 5: REST API endpoints
    └─ Days 1-5 (Parallel): Frontend UI
         ├─ Marketplace browser
         ├─ Auth modal
         └─ Chat interface

Week 2 Focus: Get working version deployed
Week 3: Refinements, add partnerships, scale
```

---

## DETAILED TASK BREAKDOWN

### BACKEND TASKS (6 tasks, ~1,200 lines)

#### TASK 1: AI Marketplace Registry Database
**File**: `backend/services/ai_marketplace_registry.py`  
**Lines**: 320  
**Timeline**: Day 1 (4-5 hours)  
**Owner**: Backend Engineer

**What to build**:
```python
# 1. AIModel dataclass (20 lines)
@dataclass
class AIModel:
    id: str
    name: str
    provider: str  # "openai", "anthropic", "huggingface"
    model_id: str  # "gpt-4", "claude-3-opus"
    pricing_tier: str  # "free", "paid", "premium"
    cost_per_1k: float
    context_window: int
    capabilities: List[str]  # ["code", "text", "image", "vision"]
    rating: float
    use_count: int
    is_available: bool

# 2. MarketplaceRegistry class (300 lines)
class MarketplaceRegistry:
    def __init__(self):
        self.models = INITIAL_MODELS  # 20 models hardcoded
        self.cache = {}
    
    def get_all_models(self) -> List[AIModel]:
        # Return all 20+ models
    
    def search_models(self, query: str) -> List[AIModel]:
        # Full-text search on name + description
        # Use fuzzy matching (fuzzywuzzy library)
    
    def filter_by_tier(self, tier: str) -> List[AIModel]:
        # "free" | "paid" | "premium"
    
    def filter_by_capability(self, capability: str) -> List[AIModel]:
        # "code" | "text" | "image" | "vision"
    
    def get_popular_models(self, limit: int = 5) -> List[AIModel]:
        # Sort by use_count, return top N
    
    def get_model_by_id(self, model_id: str) -> AIModel:
        # Get single model details
```

**Key data to include** (hardcoded in Python dict):
```python
INITIAL_MODELS = [
    # Free Tier
    {
        "id": "llama2-7b",
        "name": "Llama 2 7B",
        "provider": "huggingface",
        "model_id": "meta-llama/Llama-2-7b-hf",
        "tier": "free",
        "cost": 0,
        "context": 4096,
        "capabilities": ["text", "code"],
        "rating": 4.2,
        "use_count": 15000
    },
    {
        "id": "mistral-7b",
        "name": "Mistral 7B",
        "provider": "huggingface",
        "model_id": "mistralai/Mistral-7B-Instruct",
        "tier": "free",
        "cost": 0,
        "context": 8192,
        "capabilities": ["text", "code"],
        "rating": 4.3,
        "use_count": 12000
    },
    
    # Paid Tier
    {
        "id": "gpt4",
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "model_id": "gpt-4-turbo-preview",
        "tier": "paid",
        "cost": 0.03,
        "context": 128000,
        "capabilities": ["text", "code", "image", "vision"],
        "rating": 4.8,
        "use_count": 50000
    },
    {
        "id": "claude3-opus",
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "model_id": "claude-3-opus-20240229",
        "tier": "paid",
        "cost": 0.015,
        "context": 200000,
        "capabilities": ["text", "code"],
        "rating": 4.7,
        "use_count": 35000
    },
    # ... 15+ more models
]
```

**Acceptance Criteria**:
-  All 20+ models loaded and searchable
-  Search returns results in <50ms
-  Filtering works (tier, capability)
-  No database required (hardcoded is fine for v1)

---

#### TASK 2: Authentication Service
**File**: `backend/services/ai_auth_service.py`  
**Lines**: 280  
**Timeline**: Day 2-3 (6-8 hours)  
**Owner**: Backend Engineer

**What to build**:
```python
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet

class User:
    """Represents Top Dog user in marketplace"""
    def __init__(self, user_id: str, email: str):
        self.user_id = user_id
        self.email = email
        self.password_hash = None
        self.api_keys = {}  # Encrypted: {"openai": "sk-...", "anthropic": "sk-..."}
        self.subscription_tier = "free"  # "free" | "pro" | "enterprise"
        self.subscription_expires = None
        self.balance = 0.0  # Prepaid balance in dollars
        self.created_at = datetime.now()

class AIAuthService:
    SECRET_KEY = os.getenv("JWT_SECRET")
    
    def __init__(self):
        self.users = {}  # In-memory (use PostgreSQL in production)
        self.cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
    
    def sign_up(self, email: str, password: str) -> User:
        """Create new user account"""
        if email in [u.email for u in self.users.values()]:
            raise ValueError("Email already registered")
        
        user_id = str(uuid.uuid4())
        user = User(user_id, email)
        user.password_hash = generate_password_hash(password)
        user.balance = 5.0  # Free $5 credit on signup
        self.users[user_id] = user
        return user
    
    def sign_in(self, email: str, password: str) -> str:
        """Authenticate user, return JWT token"""
        user = next((u for u in self.users.values() if u.email == email), None)
        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid credentials")
        
        # Generate JWT token (expires in 7 days)
        payload = {
            "user_id": user.user_id,
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        return jwt.encode(payload, self.SECRET_KEY, algorithm="HS256")
    
    def verify_token(self, token: str) -> User:
        """Verify JWT token, return user"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=["HS256"])
            return self.users[payload["user_id"]]
        except (jwt.DecodeError, jwt.ExpiredSignatureError):
            raise ValueError("Invalid or expired token")
    
    def add_api_key(self, user_id: str, provider: str, api_key: str) -> bool:
        """Add provider API key (encrypted)"""
        user = self.users[user_id]
        encrypted_key = self.cipher.encrypt(api_key.encode())
        user.api_keys[provider] = encrypted_key.decode()
        return True
    
    def get_api_key(self, user_id: str, provider: str) -> str:
        """Get decrypted API key"""
        user = self.users[user_id]
        encrypted = user.api_keys[provider].encode()
        return self.cipher.decrypt(encrypted).decode()
    
    def set_subscription(self, user_id: str, tier: str, months: int):
        """Update subscription tier"""
        user = self.users[user_id]
        user.subscription_tier = tier
        user.subscription_expires = datetime.now() + timedelta(days=30*months)
    
    def add_balance(self, user_id: str, amount: float):
        """Add prepaid balance"""
        user = self.users[user_id]
        user.balance += amount
    
    def deduct_balance(self, user_id: str, amount: float) -> bool:
        """Deduct balance for API usage"""
        user = self.users[user_id]
        if user.balance < amount:
            return False
        user.balance -= amount
        return True
    
    def get_user_balance(self, user_id: str) -> float:
        """Get current balance"""
        return self.users[user_id].balance
```

**Acceptance Criteria**:
-  Sign up creates new user
-  Sign in generates JWT token
-  Token verification works
-  API keys encrypted (never stored in plain text)
-  Balance tracking works
-  Password hashing secure

---

#### TASK 3: Recommendation Engine
**File**: `backend/services/ai_recommendation_engine.py`  
**Lines**: 300  
**Timeline**: Day 3-4 (5-6 hours)  
**Owner**: Backend Engineer

**What to build**:
```python
class RecommendationEngine:
    """Q Assistant powered model recommendations"""
    
    TASK_TO_MODELS = {
        # Map task types to best models
        "code_generation": ["gpt4", "claude3-opus", "gemini-pro"],
        "code_review": ["gpt4", "claude3-opus"],
        "debugging": ["gpt4"],  # Highest accuracy
        "documentation": ["claude3-sonnet", "gemini-pro"],
        "quick_task": ["gpt3.5", "mistral-large"],  # Faster + cheaper
        "budget_conscious": ["mistral-7b", "llama2-7b"],  # Free/cheap
        "brainstorming": ["claude3-opus", "gpt4"],
        "explain_concept": ["claude3-sonnet", "gpt3.5"],
    }
    
    def __init__(self, registry: MarketplaceRegistry, auth: AIAuthService):
        self.registry = registry
        self.auth = auth
    
    def analyze_task(self, task_description: str) -> Dict:
        """
        Analyze user's task to determine type
        Input: "I need to debug a complex Python issue"
        Output: {"type": "debugging", "keywords": ["debug", "python"]}
        """
        keywords = task_description.lower().split()
        
        # Simple keyword matching (can upgrade to ML/LLM later)
        if any(w in keywords for w in ["debug", "bug", "error", "fix"]):
            task_type = "debugging"
        elif any(w in keywords for w in ["generate", "write", "create", "build"]):
            task_type = "code_generation"
        elif any(w in keywords for w in ["review", "check", "audit"]):
            task_type = "code_review"
        elif any(w in keywords for w in ["explain", "understand", "how"]):
            task_type = "explain_concept"
        else:
            task_type = "general"
        
        return {
            "type": task_type,
            "keywords": keywords,
            "confidence": 0.85
        }
    
    def get_recommendations(self, user_id: str, task: str, limit: int = 3) -> List[Dict]:
        """
        Get top N model recommendations for user
        Returns: [
            {
                "model": AIModel,
                "rank": 1,
                "reasoning": "Best for code generation",
                "estimated_cost": 0.05,
                "is_available": true
            },
            ...
        ]
        """
        user = self.auth.users[user_id]
        task_analysis = self.analyze_task(task)
        task_type = task_analysis.get("type", "general")
        
        # Get models for this task type
        model_ids = self.TASK_TO_MODELS.get(task_type, ["gpt4", "claude3-opus"])
        
        recommendations = []
        for rank, model_id in enumerate(model_ids[:limit]):
            model = next((m for m in self.registry.get_all_models() if m.id == model_id), None)
            if not model:
                continue
            
            # Check if user can afford this model
            can_afford = user.balance > model.cost * 2  # Rough estimate
            
            recommendations.append({
                "model": model,
                "rank": rank + 1,
                "reasoning": f"Best for {task_type}",
                "estimated_cost": model.cost * 2.5,  # ~2.5k tokens
                "is_available": model.is_available and can_afford
            })
        
        return recommendations
    
    def score_model_for_task(self, model: AIModel, task_type: str) -> float:
        """Score 1-10: How suited is this model?"""
        base_score = 5.0
        
        # Capability bonus
        if "code" in task_type and "code" in model.capabilities:
            base_score += 2.0
        if "vision" in task_type and "vision" in model.capabilities:
            base_score += 2.0
        
        # Rating bonus
        base_score += (model.rating - 4.0)  # If 4.5 star: +0.5
        
        # Popularity bonus
        if model.use_count > 30000:
            base_score += 1.0
        
        return min(10.0, base_score)
    
    def get_trending_models(self, time_period: str = "week") -> List[AIModel]:
        """Get models trending by usage"""
        all_models = self.registry.get_all_models()
        return sorted(all_models, key=lambda m: m.use_count, reverse=True)[:5]
```

**Acceptance Criteria**:
-  Analyzes task description
-  Returns ranked recommendations
-  Reasoning text provided
-  Handles budget constraints
-  Trending models work

---

#### TASK 4: Multi-LLM API Router
**File**: `backend/services/ai_api_router.py`  
**Lines**: 300  
**Timeline**: Day 4-5 (6-8 hours)  
**Owner**: Backend Engineer

**What to build**:
```python
class APIRouter:
    """Routes requests to correct LLM provider"""
    
    def __init__(self, auth: AIAuthService):
        self.auth = auth
    
    def route_completion(self, user_id: str, model_id: str, prompt: str, 
                        options: dict = None) -> str:
        """
        Universal interface for completions
        Automatically routes to correct provider
        """
        user = self.auth.users[user_id]
        model = self._get_model_by_id(model_id)
        
        # Get API key
        api_key = self.auth.get_api_key(user_id, model.provider)
        
        # Route to provider
        if model.provider == "openai":
            return self._call_openai(api_key, model.model_id, prompt, options)
        elif model.provider == "anthropic":
            return self._call_anthropic(api_key, model.model_id, prompt, options)
        elif model.provider == "huggingface":
            return self._call_huggingface(api_key, model.model_id, prompt, options)
        elif model.provider == "google":
            return self._call_google(api_key, model.model_id, prompt, options)
        elif model.provider == "ollama":
            return self._call_ollama(model.model_id, prompt, options)
        else:
            raise ValueError(f"Unknown provider: {model.provider}")
    
    def _call_openai(self, api_key: str, model: str, prompt: str, options: dict) -> str:
        """OpenAI API call"""
        import openai
        openai.api_key = api_key
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=options.get("max_tokens", 2000),
            temperature=options.get("temperature", 0.7),
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, api_key: str, model: str, prompt: str, options: dict) -> str:
        """Anthropic API call"""
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model=model,
            max_tokens=options.get("max_tokens", 2000),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
    
    def _call_huggingface(self, api_key: str, model: str, prompt: str, options: dict) -> str:
        """HuggingFace API call"""
        import requests
        
        API_URL = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        response = requests.post(
            API_URL,
            headers=headers,
            json={"inputs": prompt}
        )
        return response.json()[0]["generated_text"]
    
    def _call_google(self, api_key: str, model: str, prompt: str, options: dict) -> str:
        """Google Gemini API call"""
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        response = genai.GenerativeModel(model).generate_content(prompt)
        return response.text
    
    def _call_ollama(self, model: str, prompt: str, options: dict) -> str:
        """Local Ollama call (self-hosted)"""
        import requests
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json()["response"]
    
    def handle_streaming(self, user_id: str, model_id: str, prompt: str):
        """Handle streaming responses (for real-time chat)"""
        # Yields chunks of response as they arrive
        pass
```

**Acceptance Criteria**:
-  Routes to OpenAI 
-  Routes to Anthropic 
-  Routes to HuggingFace 
-  Routes to Google 
-  Routes to Ollama (local) 
-  Error handling (fallback to free model)
-  Token counting (for billing)

---

#### TASK 5: REST API - Marketplace Routes
**File**: `backend/api/v1/ai_marketplace_routes.py`  
**Lines**: 280  
**Timeline**: Day 5 (4-5 hours)  
**Owner**: Backend Engineer

**What to build**:
```python
from flask import Blueprint, request, jsonify
from functools import wraps

bp = Blueprint('marketplace', __name__, url_prefix='/api/v1/marketplace')

# Auth endpoints
@bp.route('/auth/signup', methods=['POST'])
def signup():
    """
    POST /auth/signup
    Body: {"email": "user@example.com", "password": "secret"}
    Response: {"success": true, "token": "jwt...", "user_id": "uuid"}
    """
    data = request.json
    try:
        user = auth_service.sign_up(data['email'], data['password'])
        token = auth_service.sign_in(data['email'], data['password'])
        return jsonify({
            "success": True,
            "token": token,
            "user_id": user.user_id,
            "balance": user.balance
        })
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400

@bp.route('/auth/signin', methods=['POST'])
def signin():
    """POST /auth/signin"""
    data = request.json
    try:
        token = auth_service.sign_in(data['email'], data['password'])
        return jsonify({"success": True, "token": token})
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 401

# Models endpoints
@bp.route('/models', methods=['GET'])
def get_all_models():
    """GET /models - List all available models"""
    models = registry.get_all_models()
    return jsonify({
        "success": True,
        "models": [model.to_dict() for model in models],
        "count": len(models)
    })

@bp.route('/models/search', methods=['GET'])
def search_models():
    """GET /models/search?q=code"""
    query = request.args.get('q', '')
    models = registry.search_models(query)
    return jsonify({
        "success": True,
        "models": [m.to_dict() for m in models],
        "query": query
    })

@bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """GET /models/gpt4 - Get single model details"""
    model = registry.get_model_by_id(model_id)
    if not model:
        return jsonify({"success": False, "error": "Model not found"}), 404
    return jsonify({"success": True, "model": model.to_dict()})

# User endpoints (requires auth)
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        try:
            user = auth_service.verify_token(token)
            request.user = user
        except ValueError:
            return jsonify({"success": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

@bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """GET /profile - Get user profile"""
    user = request.user
    return jsonify({
        "success": True,
        "user": {
            "email": user.email,
            "tier": user.subscription_tier,
            "balance": user.balance,
            "api_keys_configured": list(user.api_keys.keys())
        }
    })

@bp.route('/api-keys', methods=['POST'])
@require_auth
def add_api_key():
    """POST /api-keys - Add provider API key"""
    data = request.json
    try:
        auth_service.add_api_key(
            request.user.user_id,
            data['provider'],
            data['api_key']
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# Recommendations endpoint
@bp.route('/recommendations', methods=['POST'])
@require_auth
def get_recommendations():
    """POST /recommendations - Get Q Assistant recommendations"""
    data = request.json
    task = data.get('task', '')
    
    recommendations = recommendation_engine.get_recommendations(
        request.user.user_id,
        task
    )
    
    return jsonify({
        "success": True,
        "recommendations": [
            {
                "model": r["model"].to_dict(),
                "rank": r["rank"],
                "reasoning": r["reasoning"]
            }
            for r in recommendations
        ]
    })

# Billing endpoint
@bp.route('/billing/balance', methods=['GET'])
@require_auth
def get_balance():
    """GET /billing/balance - Check account balance"""
    balance = auth_service.get_user_balance(request.user.user_id)
    return jsonify({
        "success": True,
        "balance": balance,
        "currency": "USD"
    })
```

**Acceptance Criteria**:
-  10 endpoints working
-  Auth required where needed
-  Error handling (400/401/404)
-  All responses in standard format

---

#### TASK 6: REST API - Agent Routes  
**File**: `backend/api/v1/ai_agent_routes.py`  
**Lines**: 220  
**Timeline**: Day 5 (3-4 hours)  
**Owner**: Backend Engineer

**What to build**:
```python
bp = Blueprint('agents', __name__, url_prefix='/api/v1/agents')

@bp.route('/completion', methods=['POST'])
@require_auth
def get_completion():
    """
    POST /completion
    Body: {
        "model": "gpt4",
        "prompt": "Write a Python function...",
        "max_tokens": 2000,
        "temperature": 0.7
    }
    """
    data = request.json
    user = request.user
    model_id = data['model']
    prompt = data['prompt']
    
    # Get model details
    model = registry.get_model_by_id(model_id)
    
    # Check balance
    estimated_cost = model.cost * 2.5  # Rough estimate
    if user.balance < estimated_cost:
        return jsonify({
            "success": False,
            "error": "Insufficient balance",
            "required": estimated_cost,
            "balance": user.balance
        }), 402
    
    try:
        # Get completion from provider
        result = api_router.route_completion(
            user.user_id,
            model_id,
            prompt,
            data.get('options', {})
        )
        
        # Count tokens (estimate)
        input_tokens = len(prompt.split())
        output_tokens = len(result.split())
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        cost = (total_tokens / 1000) * model.cost
        
        # Deduct from balance
        auth_service.deduct_balance(user.user_id, cost)
        
        return jsonify({
            "success": True,
            "result": result,
            "tokens_used": total_tokens,
            "cost": cost,
            "balance_remaining": auth_service.get_user_balance(user.user_id),
            "model": model_id
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@bp.route('/chat', methods=['POST'])
@require_auth
def chat():
    """Multi-turn conversation"""
    # Similar to completion but maintains conversation history
    pass

@bp.route('/agents/<agent_id>/history', methods=['GET'])
@require_auth
def get_history(agent_id):
    """GET /agents/<id>/history - Get conversation history"""
    # Retrieve from database
    pass
```

**Acceptance Criteria**:
-  Completion endpoint works
-  Streaming works (optional)
-  Billing tracked per API call
-  Error handling

---

### FRONTEND TASKS (3 tasks, ~1,400 lines)

#### TASK 7: Marketplace Panel Component
**File**: `frontend/components/AIMarketplacePanel.tsx`  
**Lines**: 550  
**Timeline**: Days 1-5 (parallel with backend)  
**Owner**: Frontend Engineer

**What to build**:
```typescript
import React, { useState, useEffect } from 'react';
import styled from 'styled-components';

interface AIModel {
  id: string;
  name: string;
  provider: string;
  pricing: 'free' | 'paid' | 'premium';
  cost: number;
  rating: number;
  usageCount: number;
  capabilities: string[];
}

export const AIMarketplacePanel: React.FC = () => {
  const [models, setModels] = useState<AIModel[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTier, setSelectedTier] = useState('all');
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [recommendations, setRecommendations] = useState<AIModel[]>([]);

  useEffect(() => {
    // Load all models on mount
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const response = await fetch('/api/v1/marketplace/models');
      const data = await response.json();
      setModels(data.models);
    } catch (error) {
      console.error('Failed to load models:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    const response = await fetch(`/api/v1/marketplace/models/search?q=${query}`);
    const data = await response.json();
    setModels(data.models);
  };

  const handleGetRecommendations = async () => {
    const response = await fetch('/api/v1/marketplace/recommendations', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ task: searchQuery })
    });
    const data = await response.json();
    setRecommendations(data.recommendations.map(r => r.model));
  };

  return (
    <Container>
      <Header>
        <Title>🤖 AI Agent Marketplace</Title>
        {user && <UserBadge>{user.email}</UserBadge>}
      </Header>

      <SearchContainer>
        <SearchInput
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          placeholder="Search models or describe your task..."
        />
        <QAssistantButton onClick={handleGetRecommendations}>
          ✨ Ask Q Assistant
        </QAssistantButton>
      </SearchContainer>

      {recommendations.length > 0 && (
        <RecommendedSection>
          <h3>Recommended for you:</h3>
          <ModelGrid>
            {recommendations.map(model => (
              <ModelCard key={model.id} model={model} />
            ))}
          </ModelGrid>
        </RecommendedSection>
      )}

      <FilterContainer>
        <FilterLabel>Pricing:</FilterLabel>
        {['all', 'free', 'paid', 'premium'].map(tier => (
          <FilterButton
            key={tier}
            selected={selectedTier === tier}
            onClick={() => setSelectedTier(tier)}
          >
            {tier.charAt(0).toUpperCase() + tier.slice(1)}
          </FilterButton>
        ))}
      </FilterContainer>

      {loading ? (
        <Loading>Loading models...</Loading>
      ) : (
        <ModelsGrid>
          {models
            .filter(m => selectedTier === 'all' || m.pricing === selectedTier)
            .map(model => (
              <ModelCard key={model.id} model={model} />
            ))}
        </ModelsGrid>
      )}
    </Container>
  );
};

// Styled components
const Container = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px;
  background: #1e1e1e;
  color: #e0e0e0;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const Title = styled.h2`
  margin: 0;
  font-size: 18px;
`;

const SearchContainer = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 8px 12px;
  background: #2d2d2d;
  border: 1px solid #3d3d3d;
  color: #e0e0e0;
  border-radius: 4px;
  
  &:focus {
    outline: none;
    border-color: #007acc;
  }
`;

const QAssistantButton = styled.button`
  padding: 8px 16px;
  background: #007acc;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  
  &:hover {
    background: #005a9e;
  }
`;

const ModelsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
  overflow-y: auto;
`;

const ModelCard = styled.div`
  background: #2d2d2d;
  border: 1px solid #3d3d3d;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: #007acc;
    background: #353535;
  }
  
  h3 {
    margin: 0 0 8px 0;
    font-size: 14px;
  }
  
  p {
    margin: 4px 0;
    font-size: 12px;
    color: #a0a0a0;
  }
`;
```

**Acceptance Criteria**:
-  Model list displays
-  Search works
-  Filter by tier works
-  Recommendations display
-  Model cards show info
-  Responsive grid layout

---

#### TASK 8: Auth Modal Component
**File**: `frontend/components/AIAuthModal.tsx`  
**Lines**: 400  
**Timeline**: Days 2-4 (parallel)  
**Owner**: Frontend Engineer

**What to build**:
```typescript
export const AIAuthModal: React.FC<{
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (token: string, user: any) => void;
}> = ({ isOpen, onClose, onSuccess }) => {
  const [mode, setMode] = useState<'signin' | 'signup' | 'api-keys'>('signin');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSignUp = async () => {
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('/api/v1/marketplace/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      if (data.success) {
        localStorage.setItem('token', data.token);
        onSuccess(data.token, { email });
        onClose();
      } else {
        setError(data.error);
      }
    } catch (e) {
      setError('Failed to sign up');
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/marketplace/auth/signin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      if (data.success) {
        localStorage.setItem('token', data.token);
        onSuccess(data.token, { email });
        onClose();
      } else {
        setError(data.error);
      }
    } catch (e) {
      setError('Failed to sign in');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal>
      <ModalContent>
        <CloseButton onClick={onClose}>✕</CloseButton>

        <Tabs>
          <Tab active={mode === 'signin'} onClick={() => setMode('signin')}>
            Sign In
          </Tab>
          <Tab active={mode === 'signup'} onClick={() => setMode('signup')}>
            Sign Up
          </Tab>
        </Tabs>

        {error && <ErrorMessage>{error}</ErrorMessage>}

        {mode === 'signin' && (
          <Form>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Button onClick={handleSignIn} disabled={loading}>
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </Form>
        )}

        {mode === 'signup' && (
          <Form>
            <Input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <Input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <Input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
            />
            <Button onClick={handleSignUp} disabled={loading}>
              {loading ? 'Signing up...' : 'Sign Up'}
            </Button>
          </Form>
        )}
      </ModalContent>
    </Modal>
  );
};
```

**Acceptance Criteria**:
-  Sign up form works
-  Sign in form works
-  JWT token stored
-  Error messages display
-  Loading state

---

#### TASK 9: Agent Chat Component
**File**: `frontend/components/AIAgentChat.tsx`  
**Lines**: 450  
**Timeline**: Days 3-5 (parallel)  
**Owner**: Frontend Engineer

**What to build**:
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const AIAgentChat: React.FC<{
  selectedModel: AIModel;
}> = ({ selectedModel }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [balance, setBalance] = useState(0);

  useEffect(() => {
    loadBalance();
  }, []);

  const loadBalance = async () => {
    const token = localStorage.getItem('token');
    const response = await fetch('/api/v1/marketplace/billing/balance', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setBalance(data.balance);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: uuid(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call backend
      const response = await fetch('/api/v1/agents/completion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          model: selectedModel.id,
          prompt: input,
          max_tokens: 2000
        })
      });

      const data = await response.json();
      
      if (data.success) {
        // Add assistant message
        const assistantMessage: Message = {
          id: uuid(),
          role: 'assistant',
          content: data.result,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMessage]);
        setBalance(data.balance_remaining);
      } else {
        // Show error
        const errorMessage: Message = {
          id: uuid(),
          role: 'assistant',
          content: `Error: ${data.error}`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (e) {
      console.error('Failed to send message:', e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ChatContainer>
      <TopBar>
        <ModelName>{selectedModel.name}</ModelName>
        <BalanceInfo>
          💰 ${balance.toFixed(2)}
        </BalanceInfo>
      </TopBar>

      <MessageList>
        {messages.map(msg => (
          <MessageBubble key={msg.id} role={msg.role}>
            {msg.content}
          </MessageBubble>
        ))}
        {loading && <Loading>AI is thinking...</Loading>}
      </MessageList>

      <InputForm onSubmit={handleSendMessage}>
        <TextInput
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <SendButton type="submit" disabled={loading}>
          {loading ? '⏳' : '➤'}
        </SendButton>
      </InputForm>
    </ChatContainer>
  );
};
```

**Acceptance Criteria**:
-  Chat UI displays
-  Messages send/receive
-  Balance shows
-  Streaming works (optional)
-  Loading state

---

### TEST SUITE (1 task, ~400 lines)

#### TASK 10: Testing & Validation
**File**: `backend/tests/test_ai_marketplace.py`  
**Lines**: 400  
**Timeline**: Day 5-6 (2-3 hours)  
**Owner**: Backend or Integration Engineer

**What to test**:
```python
import unittest
from backend.services.ai_marketplace_registry import MarketplaceRegistry
from backend.services.ai_auth_service import AIAuthService
from backend.services.ai_recommendation_engine import RecommendationEngine

class TestMarketplaceRegistry(unittest.TestCase):
    def test_get_all_models(self):
        registry = MarketplaceRegistry()
        models = registry.get_all_models()
        self.assertGreater(len(models), 0)
    
    def test_search_models(self):
        registry = MarketplaceRegistry()
        results = registry.search_models("gpt")
        self.assertGreater(len(results), 0)
    
    def test_filter_by_tier(self):
        registry = MarketplaceRegistry()
        free_models = registry.filter_by_tier("free")
        self.assertGreater(len(free_models), 0)

class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.auth = AIAuthService()
    
    def test_sign_up(self):
        user = self.auth.sign_up("test@example.com", "password123")
        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.balance, 5.0)
    
    def test_sign_in(self):
        self.auth.sign_up("test@example.com", "password123")
        token = self.auth.sign_in("test@example.com", "password123")
        self.assertIsNotNone(token)
    
    def test_api_key_encryption(self):
        user = self.auth.sign_up("test@example.com", "password123")
        self.auth.add_api_key(user.user_id, "openai", "sk-test123")
        key = self.auth.get_api_key(user.user_id, "openai")
        self.assertEqual(key, "sk-test123")

class TestRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.registry = MarketplaceRegistry()
        self.auth = AIAuthService()
        self.engine = RecommendationEngine(self.registry, self.auth)
    
    def test_analyze_task_debugging(self):
        analysis = self.engine.analyze_task("Debug this Python code")
        self.assertEqual(analysis['type'], 'debugging')
    
    def test_get_recommendations(self):
        user = self.auth.sign_up("test@example.com", "password123")
        recs = self.engine.get_recommendations(user.user_id, "generate code")
        self.assertGreater(len(recs), 0)

class TestAPIIntegration(unittest.TestCase):
    def test_openai_routing(self):
        # Test routing to OpenAI
        pass
    
    def test_anthropic_routing(self):
        # Test routing to Anthropic
        pass
    
    def test_balance_deduction(self):
        # Test that balance is deducted on API call
        pass

if __name__ == '__main__':
    unittest.main()
```

**Acceptance Criteria**:
-  15+ unit tests written
-  100% pass rate
-  Coverage > 80%
-  All major features tested

---

## DAILY SCHEDULE

### Day 1
- ☐ Task 1: Marketplace registry (Morning)
- ☐ Task 7 start: Component structure (Afternoon)

### Day 2-3
- ☐ Task 2: Auth service (Morning)
- ☐ Task 8: Auth modal (Afternoon)

### Day 3-4
- ☐ Task 3: Recommendations (Morning)
- ☐ Task 9: Chat component (Afternoon)

### Day 4-5
- ☐ Task 4: API router (Morning)
- ☐ Task 5: Marketplace routes (Afternoon)
- ☐ Task 6: Agent routes (Evening)
- ☐ Tasks 7-9: Polish components

### Day 5-6
- ☐ Task 10: Testing & validation
- ☐ E2E testing
- ☐ Performance tuning

---

## SUCCESS CHECKLIST

### Backend Complete
- [ ] 4 services created (1,200+ lines)
- [ ] 2 API blueprints created (500 lines)
- [ ] All tests passing (15+)
- [ ] All endpoints responding
- [ ] Auth working (JWT, encryption)

### Frontend Complete
- [ ] 3 components created (1,400+ lines)
- [ ] All routes integrated
- [ ] All API calls working
- [ ] Styling complete
- [ ] Responsive design

### Integration
- [ ] Marketplace panel in Editor
- [ ] Auth modal appears on first use
- [ ] Chat works end-to-end
- [ ] Recommendations work
- [ ] Billing tracked

### Testing
- [ ] All unit tests pass
- [ ] All E2E tests pass
- [ ] Performance validated
- [ ] Security audit passed

### Launch Ready
- [ ] Documentation complete
- [ ] Demo prepared
- [ ] Team trained
- [ ] Ready for beta launch

---

**Ready to build?** Start with Task 1 tomorrow (Nov 3).

