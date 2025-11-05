# 🤖 AI Agent Marketplace - Implementation Checklist

**Status**: Phase 1 Ready (Week 2-3 of 90-Day Plan)  
**Timeline**: 10 working days  
**Team Size**: 2-3 developers  
**Total Lines**: ~3,500  
**Revenue Impact**: $195k MRR (Year 1)  

---

## 📋 COMPLETE TASK BREAKDOWN

### BACKEND TASKS (1,700+ lines)

#### Task 1.1: AI Marketplace Registry Service ⭐
**File**: `backend/services/ai_marketplace_registry.py`  
**Lines**: 320  
**Timeline**: 2 days (Mon-Tue)  
**Assigned to**: Backend Lead  
**Dependencies**: None (standalone)  

**Objective**: Create a registry of 50+ AI models with metadata

**Acceptance Criteria**:
- [ ] Initialize with 50+ models (OpenAI, Anthropic, Google, HuggingFace, Mistral, Ollama)
- [ ] Each model has: name, provider, pricing, capabilities, rating, description, usage_count
- [ ] GET /models returns full list with pagination
- [ ] GET /models/:id returns single model
- [ ] Search by name, provider, capability
- [ ] Filter by: free/paid, capability (code/text/image), rating
- [ ] Models ranked by: popularity, relevance, rating

**Code Structure**:
```python
# Models table schema
class AIModel:
    id: str                    # "gpt4-turbo"
    name: str                  # "GPT-4 Turbo"
    provider: str              # "openai"
    api_endpoint: str          # "https://api.openai.com/v1/chat/completions"
    pricing: {
        "input_token": 0.03,   # per 1K tokens
        "output_token": 0.06
    }
    capabilities: [str]        # ["code", "text", "reasoning"]
    rating: float              # 4.8 (out of 5)
    description: str
    usage_count: int           # How many users use it
    free_tier: bool            # Is there a free option?
    
# Initial seed data
MODELS = [
    {
        "id": "gpt4-turbo",
        "name": "GPT-4 Turbo",
        "provider": "openai",
        "pricing": {"input": 0.03, "output": 0.06},
        "capabilities": ["code", "text", "reasoning"],
        "rating": 4.8,
        "usage_count": 50000
    },
    {
        "id": "claude-3-opus",
        "name": "Claude 3 Opus",
        "provider": "anthropic",
        "pricing": {"input": 0.015, "output": 0.075},
        "capabilities": ["code", "text"],
        "rating": 4.7,
        "usage_count": 35000
    },
    # ... + 48 more models
]
```

**Key Functions**:
- `get_all_models(page=1, per_page=20)` → List with pagination
- `get_model(id)` → Single model details
- `search_models(query, filters)` → Search + filter
- `get_model_rating(id)` → Current rating
- `get_model_usage_count(id)` → Popularity metric
- `get_recommendation_context()` → All models for Q Assistant

**Testing**:
- [ ] Test: Can retrieve all 50+ models
- [ ] Test: Search by name finds correct models
- [ ] Test: Filter by pricing works
- [ ] Test: Rating calculation correct
- [ ] Test: Pagination works (20 per page)

**Definition of Done**:
- ✅ 50+ models in database
- ✅ All queries work (list, get, search, filter)
- ✅ Pagination working
- ✅ 5+ unit tests passing
- ✅ Response time < 100ms

---

#### Task 1.2: AI Authentication Service
**File**: `backend/services/ai_auth_service.py`  
**Lines**: 280  
**Timeline**: 2 days (Tue-Wed)  
**Assigned to**: Backend Lead  
**Dependencies**: Task 1.1 (for reference)  

**Objective**: Handle user authentication and API key management

**Acceptance Criteria**:
- [ ] User registration (email + password)
- [ ] User login (JWT token issued)
- [ ] Manage API keys for multiple providers (OpenAI, Anthropic, etc)
- [ ] Store keys securely (encrypted in database)
- [ ] Create prepaid balance ($5-$500 increments)
- [ ] Track usage per user per model
- [ ] Deduct cost when query made
- [ ] Return balance with every request

**Code Structure**:
```python
# Users table
class User:
    id: str                    # UUID
    email: str                 # unique
    password_hash: str         # bcrypt
    created_at: datetime
    balance: float             # Current prepaid balance
    total_spent: float         # Lifetime spending

# User API Keys
class UserAPIKey:
    user_id: str
    provider: str              # "openai", "anthropic", etc
    encrypted_key: str         # Encrypted with app secret
    created_at: datetime

# Usage tracking
class UsageLog:
    user_id: str
    model_id: str              # "gpt4-turbo"
    provider: str
    tokens_input: int
    tokens_output: int
    cost: float
    timestamp: datetime
```

**Key Functions**:
- `register_user(email, password)` → (user_id, jwt_token)
- `login_user(email, password)` → (user_id, jwt_token)
- `validate_token(jwt)` → user_id or None
- `add_api_key(user_id, provider, key)` → Encrypt & store
- `get_api_key(user_id, provider)` → Decrypt & return
- `add_balance(user_id, amount)` → Update prepaid
- `get_balance(user_id)` → Current balance
- `deduct_cost(user_id, cost)` → Reduce balance
- `log_usage(user_id, model_id, tokens)` → Track usage
- `get_usage_history(user_id)` → All past queries

**Testing**:
- [ ] Test: Registration creates user
- [ ] Test: Login returns JWT
- [ ] Test: JWT validation works
- [ ] Test: Can add API key
- [ ] Test: API key encrypted
- [ ] Test: Balance updates correctly
- [ ] Test: Cost deduction works

**Definition of Done**:
- ✅ User registration/login working
- ✅ JWT token system secure
- ✅ API keys encrypted
- ✅ Balance tracking accurate
- ✅ 7+ unit tests passing
- ✅ No plaintext secrets

---

#### Task 1.3: Q Assistant Recommendation Engine
**File**: `backend/services/ai_recommendation_engine.py`  
**Lines**: 300  
**Timeline**: 2 days (Wed-Thu)  
**Assigned to**: Backend Lead  
**Dependencies**: Task 1.1 (Registry)  

**Objective**: Q Assistant analyzes user query and recommends best models

**Acceptance Criteria**:
- [ ] Accept user query/task description
- [ ] Analyze what type of task (coding, writing, math, etc)
- [ ] Return top 3 recommended models with reasoning
- [ ] Recommendations ranked by: capability match, price, speed, rating
- [ ] Show why each model recommended
- [ ] Return alternative suggestions for budget/speed options
- [ ] Fast execution (< 200ms)

**Code Structure**:
```python
# Recommendation output
class Recommendation:
    rank: int                  # 1, 2, or 3
    model_id: str              # "gpt4-turbo"
    model_name: str
    reasoning: str             # "Best for complex coding tasks"
    price_point: str           # "Premium", "Mid-range", "Budget"
    speed: str                 # "Fast", "Medium", "Slow"
    rating: float
    estimated_cost: float      # For typical query
```

**Key Functions**:
- `analyze_query(query)` → task_type, keywords, requirements
- `get_recommendations(query)` → [Recommendation, Recommendation, Recommendation]
- `score_model(model, task_type)` → relevance_score (0-100)
- `filter_affordable(models, user_budget)` → Filter by price
- `sort_by_preference(models, criteria)` → Order by best fit

**Q Assistant Logic**:
```
User Query: "Debug my Python REST API"
    ↓
Analyze:
  - Task: debugging/troubleshooting
  - Language: Python
  - Complexity: medium
  - Time-sensitive: yes
    ↓
Score Models:
  - Claude 3 Opus: 95 (expert in code, fast, $0.015/1K)
  - GPT-4: 92 (powerful, good for debugging, $0.03/1K)
  - Mistral Large: 85 (cheaper, good enough, $0.007/1K)
    ↓
Return Top 3:
  1. Claude 3 Opus - "Best for API debugging with error analysis"
  2. GPT-4 - "Most powerful, handles complex issues"
  3. Mistral Large - "Budget option, still very capable"
```

**Testing**:
- [ ] Test: Coding query recommends code-focused models
- [ ] Test: Writing query recommends text models
- [ ] Test: Budget constraint filters expensive models
- [ ] Test: Speed/accuracy trade-off reflected in recommendations
- [ ] Test: Reasoning is clear and helpful

**Definition of Done**:
- ✅ Recommendations accurate and relevant
- ✅ Top 3 models returned with reasoning
- ✅ Response time < 200ms
- ✅ 5+ unit tests passing
- ✅ Logic handles edge cases

---

#### Task 1.4: Multi-Provider API Router
**File**: `backend/services/ai_api_router.py`  
**Lines**: 300  
**Timeline**: 2-3 days (Thu-Fri)  
**Assigned to**: Backend Lead  
**Dependencies**: Task 1.2 (Auth), Task 1.3 (Registry)  

**Objective**: Route requests to 5+ AI providers seamlessly

**Acceptance Criteria**:
- [ ] Support OpenAI (GPT-4, GPT-3.5-turbo)
- [ ] Support Anthropic (Claude 3 Opus, Sonnet, Haiku)
- [ ] Support Google (Gemini Pro, Gemini Ultra)
- [ ] Support HuggingFace (Llama 2, Mistral, Falcon)
- [ ] Support Ollama (local self-hosted models)
- [ ] Normalize request/response format across providers
- [ ] Stream responses in real-time
- [ ] Track token usage per provider
- [ ] Handle API errors gracefully

**Code Structure**:
```python
# Unified request format
class ChatRequest:
    model_id: str              # "gpt4-turbo"
    messages: [Message]        # [{"role": "user", "content": "..."}]
    temperature: float         # 0.7
    max_tokens: int           # 2000
    
# Unified response format
class ChatResponse:
    model_id: str
    content: str               # The actual response
    tokens_input: int
    tokens_output: int
    cost: float
    timestamp: datetime

# Provider adapters
class OpenAIAdapter:
    def send_request(request) → ChatResponse
    def stream_response(request) → Stream[ChatResponse]
    
class AnthropicAdapter:
    ...
    
class GeminiAdapter:
    ...
```

**Key Functions**:
- `route_request(user_id, model_id, messages)` → ChatResponse
- `stream_request(user_id, model_id, messages)` → AsyncIterator[ChatResponse]
- `get_provider_adapter(model_id)` → ProviderAdapter instance
- `normalize_request(model_id, generic_request)` → provider_specific_request
- `normalize_response(model_id, provider_response)` → ChatResponse
- `calculate_cost(model_id, tokens_input, tokens_output)` → float
- `handle_provider_error(error)` → user_friendly_message

**Provider Routing Logic**:
```
User selects "Claude 3 Opus"
    ↓
Router identifies provider: Anthropic
    ↓
Get user's Anthropic API key (or use Top Dog default)
    ↓
Transform request to Anthropic format
    ↓
Send to Anthropic API
    ↓
Transform response back to Top Dog format
    ↓
Calculate cost ($0.015/1K input, $0.075/1K output)
    ↓
Deduct from user balance
    ↓
Stream response to user
```

**Testing**:
- [ ] Test: OpenAI requests route correctly
- [ ] Test: Anthropic requests route correctly
- [ ] Test: Gemini requests route correctly
- [ ] Test: HuggingFace requests route correctly
- [ ] Test: Request normalization works for all providers
- [ ] Test: Response normalization works for all providers
- [ ] Test: Token counting accurate per provider
- [ ] Test: Cost calculation correct per provider
- [ ] Test: Error handling graceful

**Definition of Done**:
- ✅ All 5+ providers routed correctly
- ✅ Request/response normalization working
- ✅ Token counting accurate
- ✅ Cost calculation correct
- ✅ 9+ unit tests passing
- ✅ Streaming responses working

---

#### Task 1.5: Marketplace API Endpoints
**File**: `backend/api/v1/ai_marketplace_routes.py`  
**Lines**: 280  
**Timeline**: 2 days (Fri-Mon)  
**Assigned to**: Backend  
**Dependencies**: All previous tasks  

**Objective**: Create REST API endpoints for marketplace frontend

**Endpoints**:
```
GET /api/v1/marketplace/models
  Response: { models: [...], total: 50, page: 1, per_page: 20 }
  
GET /api/v1/marketplace/models/:id
  Response: { id, name, provider, pricing, rating, ... }
  
POST /api/v1/marketplace/search
  Body: { query: "debugging", filters: {...} }
  Response: { results: [...] }
  
POST /api/v1/marketplace/recommendations
  Body: { query: "help me debug" }
  Response: { recommendations: [...] }
  
GET /api/v1/marketplace/user/balance
  Response: { balance: 4.96, total_spent: 5.04, usage_count: 200 }
  
POST /api/v1/marketplace/user/select-model
  Body: { model_id: "gpt4-turbo" }
  Response: { success: true, selected_model: {...} }
```

**Key Endpoints**:
- `GET /models` → List all models with filters
- `GET /models/:id` → Single model details
- `POST /search` → Search models
- `POST /recommendations` → Get Q Assistant recommendations
- `GET /user/balance` → Check account balance
- `POST /user/select-model` → Select model for chat
- `GET /user/usage-history` → Past queries
- `POST /user/add-balance` → Add prepaid credit

**Testing**:
- [ ] Test: All endpoints return correct format
- [ ] Test: Authentication required for user endpoints
- [ ] Test: Search filters work
- [ ] Test: Recommendations generated
- [ ] Test: Balance tracking accurate
- [ ] Test: Error responses meaningful

**Definition of Done**:
- ✅ All 8+ endpoints working
- ✅ Authentication enforced
- ✅ Response format consistent
- ✅ Error handling complete
- ✅ 8+ E2E tests passing

---

#### Task 1.6: Agent Chat API
**File**: `backend/api/v1/ai_agent_routes.py`  
**Lines**: 220  
**Timeline**: 2 days (Mon-Tue)  
**Assigned to**: Backend  
**Dependencies**: Tasks 1.2, 1.4, 1.5  

**Objective**: Create WebSocket + HTTP endpoints for real-time chat

**Endpoints**:
```
POST /api/v1/agents/chat
  Body: { model_id: "gpt4-turbo", message: "..." }
  Response: { response: "...", tokens_used: 150, cost: 0.04 }
  
WS /api/v1/agents/stream/:model_id
  Message: { message: "..." }
  Response (streaming): [chunk1, chunk2, chunk3, ...]
  
GET /api/v1/agents/history
  Response: { messages: [...], total: 500 }
```

**Key Functions**:
- `POST /chat` → Single synchronous response
- `WS /stream/:model_id` → Real-time streaming
- GET `/history` → Conversation history
- POST `/clear-history` → Clear conversation

**Streaming Example**:
```
User: "Write a REST API in Python"
    ↓
WS opens at /stream/gpt4-turbo
    ↓
User message sent
    ↓
Responses stream back:
  "Here's a simple REST API..."
  " using Flask:\n\n"
  "```python\n"
  "from flask import Flask\n"
  "app = Flask(__name__)\n"
  ...
    ↓
When done, send final cost/token data
```

**Testing**:
- [ ] Test: Chat endpoint works
- [ ] Test: WebSocket connects
- [ ] Test: Messages stream correctly
- [ ] Test: History tracked
- [ ] Test: Cost calculated
- [ ] Test: Error handling

**Definition of Done**:
- ✅ HTTP chat endpoint working
- ✅ WebSocket streaming working
- ✅ History tracked
- ✅ Cost calculated
- ✅ 5+ tests passing
- ✅ Error handling complete

---

### FRONTEND TASKS (1,400+ lines)

#### Task 2.1: Marketplace Panel Component
**File**: `frontend/components/AIMarketplacePanel.tsx`  
**Lines**: 550  
**Timeline**: 3 days (Mon-Wed)  
**Assigned to**: Frontend Lead  
**Dependencies**: Backend Tasks 1.1-1.5  

**Objective**: Browse and search 50+ AI models

**Features**:
- [ ] Display 50+ models in cards
- [ ] Search by name/provider
- [ ] Filter by: free/paid, capability, rating
- [ ] Sort by: popularity, rating, price
- [ ] Show model details: pricing, rating, description, usage count
- [ ] [Select Model] button to open chat
- [ ] Ask Q Assistant: "What model do I need?"
- [ ] Show loading states
- [ ] Handle errors gracefully

**UI Components**:
```tsx
<AIMarketplacePanel>
  <header>
    <h1>🤖 AI Agent Marketplace</h1>
    <p>Choose from 50+ AI models</p>
  </header>
  
  <SearchBar placeholder="Search models (GPT-4, Claude, etc)" />
  
  <FilterPanel>
    <FilterToggle label="Free Models" />
    <FilterSelect label="Capability" options={["Code", "Text", "Image"]} />
    <FilterSelect label="Price" options={["Free", "Budget", "Premium"]} />
  </FilterPanel>
  
  <SortSelector defaultSort="popularity" />
  
  <ModelGrid>
    {models.map(model => (
      <ModelCard key={model.id}>
        <h3>{model.name}</h3>
        <p className="provider">{model.provider}</p>
        <div className="pricing">
          ${model.pricing.input}/1K tokens
        </div>
        <Rating>{model.rating}⭐</Rating>
        <p className="description">{model.description}</p>
        <p className="usage">{model.usage_count.toLocaleString()} users</p>
        <Button onClick={() => selectModel(model.id)}>
          Select Model
        </Button>
      </ModelCard>
    ))}
  </ModelGrid>
  
  <AskQAssistant />
</AIMarketplacePanel>
```

**State Management**:
```tsx
const [models, setModels] = useState([])
const [filteredModels, setFilteredModels] = useState([])
const [loading, setLoading] = useState(true)
const [searchQuery, setSearchQuery] = useState("")
const [filters, setFilters] = useState({
  pricingType: "all",      // free, paid, all
  capability: [],          // code, text, image
  minRating: 0,
  sortBy: "popularity"     // popularity, rating, price
})
const [selectedModel, setSelectedModel] = useState(null)
```

**API Calls**:
- `GET /api/v1/marketplace/models` → Load all models
- `POST /api/v1/marketplace/search` → Search models
- `POST /api/v1/marketplace/recommendations` → Ask Q Assistant

**Testing**:
- [ ] Test: Models load and display
- [ ] Test: Search filters results
- [ ] Test: Sorting works
- [ ] Test: Can select model
- [ ] Test: Loading state shown
- [ ] Test: Error state handled

**Definition of Done**:
- ✅ All 50+ models display
- ✅ Search/filter working
- ✅ Sorting working
- ✅ Model selection works
- ✅ UI polished
- ✅ Mobile responsive
- ✅ 5+ component tests passing

---

#### Task 2.2: Authentication Modal
**File**: `frontend/components/AIAuthModal.tsx`  
**Lines**: 400  
**Timeline**: 3 days (Tue-Thu)  
**Assigned to**: Frontend  
**Dependencies**: Backend Tasks 1.2, 1.5  

**Objective**: Sign up, sign in, and manage API keys

**Features**:
- [ ] Sign up form (email + password)
- [ ] Sign in form (email + password)
- [ ] Password validation
- [ ] Add API keys for providers (optional)
- [ ] Prepaid balance display
- [ ] Add credit ($5-$500 options)
- [ ] Profile management
- [ ] Logout

**UI Screens**:

**Screen 1: Sign Up**
```
┌─────────────────────────────┐
│ Welcome to Q Marketplace    │
├─────────────────────────────┤
│ Email:     [_______________]│
│ Password:  [_______________]│
│            [Show password]  │
│ Confirm:   [_______________]│
│                             │
│ [Create Account]            │
│ Already have an account?    │
│ [Sign In]                   │
└─────────────────────────────┘
```

**Screen 2: Sign In**
```
┌─────────────────────────────┐
│ Sign In to Q Marketplace    │
├─────────────────────────────┤
│ Email:     [_______________]│
│ Password:  [_______________]│
│                             │
│ [Sign In]                   │
│ Don't have an account?      │
│ [Create One]                │
└─────────────────────────────┘
```

**Screen 3: API Keys (Post-Auth)**
```
┌─────────────────────────────┐
│ Your API Keys               │
├─────────────────────────────┤
│ OpenAI Key:    [****ed]     │
│ Anthropic Key: [Not set]    │
│ Google Key:    [****ed]     │
│                             │
│ [Add OpenAI Key]            │
│ [Add Anthropic Key]         │
│                             │
│ Balance: $5.00              │
│ [Add $10]  [Add $25]        │
│ [Add $50]  [Add $100]       │
└─────────────────────────────┘
```

**Code Structure**:
```tsx
interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess: (user) => void
}

type AuthMode = "signup" | "signin" | "keys"

const AIAuthModal = ({ isOpen, onClose, onSuccess }: AuthModalProps) => {
  const [mode, setMode] = useState<AuthMode>("signin")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [user, setUser] = useState(null)
  const [apiKeys, setApiKeys] = useState({})
  const [balance, setBalance] = useState(0)
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      {mode === "signin" && <SignInForm ... />}
      {mode === "signup" && <SignUpForm ... />}
      {mode === "keys" && <ManageKeys ... />}
    </Dialog>
  )
}
```

**API Calls**:
- `POST /auth/register` → Create account
- `POST /auth/login` → Sign in
- `POST /auth/add-api-key` → Add provider key
- `GET /marketplace/user/balance` → Get balance
- `POST /marketplace/user/add-balance` → Add credit

**Testing**:
- [ ] Test: Sign up creates account
- [ ] Test: Sign in works
- [ ] Test: Password validation
- [ ] Test: API key management
- [ ] Test: Balance display
- [ ] Test: Add credit works
- [ ] Test: Error messages clear

**Definition of Done**:
- ✅ Sign up/in working
- ✅ API key management secure
- ✅ Balance tracking accurate
- ✅ Add credit working
- ✅ UI polished
- ✅ 6+ component tests passing

---

#### Task 2.3: Chat Component
**File**: `frontend/components/AIAgentChat.tsx`  
**Lines**: 450  
**Timeline**: 3-4 days (Wed-Fri)  
**Assigned to**: Frontend  
**Dependencies**: Backend Tasks 1.4, 1.6, 1.5  

**Objective**: Chat interface with real-time streaming responses

**Features**:
- [ ] Message input field
- [ ] Send button + keyboard shortcut (Enter)
- [ ] Display chat history (messages + responses)
- [ ] Real-time streaming responses (word-by-word)
- [ ] Show model name and current cost
- [ ] Display usage: tokens, cost, balance
- [ ] Syntax highlighting for code blocks
- [ ] Copy response button
- [ ] Clear history button
- [ ] Error handling

**UI Layout**:
```
┌──────────────────────────────────────────┐
│ 🤖 Chat with GPT-4 Turbo                │
├──────────────────────────────────────────┤
│                                          │
│ User: "Write a REST API in Python"      │
│                                          │
│ GPT-4: "Here's a simple REST API..."    │
│ ```python                                │
│ from flask import Flask                  │
│ app = Flask(__name__)                    │
│                                          │
│ @app.route('/api/users', methods=['GET'])
│ def get_users():                         │
│     return {"users": [...]}              │
│ ```                                      │
│ [Copy]                                   │
│                                          │
│ Cost: $0.04 | Balance: $4.96             │
│                                          │
├──────────────────────────────────────────┤
│ [Message input________________] [Send]  │
│                                          │
│ [Clear History]  [Switch Model]         │
└──────────────────────────────────────────┘
```

**Code Structure**:
```tsx
interface Message {
  role: "user" | "assistant"
  content: string
  tokens?: number
  cost?: number
  timestamp: Date
}

const AIAgentChat = ({ modelId }: { modelId: string }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [currentResponse, setCurrentResponse] = useState("")
  const [totalCost, setTotalCost] = useState(0)
  const [balance, setBalance] = useState(0)
  
  const sendMessage = async (text: string) => {
    // Add user message
    setMessages(prev => [...prev, { role: "user", content: text }])
    
    // Stream response
    const response = await fetch(
      `/api/v1/agents/stream/${modelId}`,
      {
        method: "POST",
        body: JSON.stringify({ message: text }),
        headers: { "Content-Type": "application/json" }
      }
    )
    
    const reader = response.body.getReader()
    
    while (true) {
      const { value, done } = await reader.read()
      if (done) break
      
      const text = new TextDecoder().decode(value)
      setCurrentResponse(prev => prev + text)
    }
    
    // Add complete response
    setMessages(prev => [...prev, {
      role: "assistant",
      content: currentResponse
    }])
  }
  
  return (
    <div className="chat-container">
      <ChatHeader model={model} cost={totalCost} balance={balance} />
      <ChatMessages messages={messages} />
      <ChatInput onSend={sendMessage} disabled={loading} />
    </div>
  )
}
```

**WebSocket Streaming**:
```typescript
// Real-time streaming example
const streamChat = async (modelId: string, message: string) => {
  const ws = new WebSocket(
    `wss://api.qide.dev/agents/stream/${modelId}`
  )
  
  ws.onopen = () => {
    ws.send(JSON.stringify({ message }))
  }
  
  ws.onmessage = (event) => {
    const chunk = event.data
    // Display chunk immediately
    setCurrentResponse(prev => prev + chunk)
  }
  
  ws.onclose = () => {
    // Finalize response
    addMessageToHistory(currentResponse)
  }
}
```

**Testing**:
- [ ] Test: Can send message
- [ ] Test: Response streams in real-time
- [ ] Test: Messages display correctly
- [ ] Test: Cost calculated
- [ ] Test: Balance updates
- [ ] Test: Code highlighting works
- [ ] Test: Copy button works
- [ ] Test: Clear history works

**Definition of Done**:
- ✅ Chat working end-to-end
- ✅ Streaming responses real-time
- ✅ Messages persisted
- ✅ Cost tracking accurate
- ✅ UI polished
- ✅ Syntax highlighting for code
- ✅ 7+ component tests passing

---

### TESTING & VALIDATION (400+ lines)

#### Task 3.1: Unit Tests
**File**: `backend/tests/test_ai_marketplace.py`  
**Lines**: 200  
**Timeline**: 1-2 days  
**Assigned to**: Integration Engineer  

**Test Coverage**:
```python
# Registry tests (3)
test_get_all_models()
test_search_models()
test_filter_by_pricing()

# Auth tests (4)
test_register_user()
test_login_user()
test_jwt_validation()
test_add_api_key()

# Recommendations tests (3)
test_analyze_query()
test_get_recommendations()
test_score_accuracy()

# Router tests (4)
test_route_to_openai()
test_route_to_anthropic()
test_normalize_request()
test_cost_calculation()

# API tests (3)
test_marketplace_endpoint()
test_search_endpoint()
test_balance_endpoint()

Total: 17 tests
```

**Testing Framework**: pytest

#### Task 3.2: E2E Tests
**File**: `frontend/tests/e2e/ai-marketplace.spec.ts`  
**Lines**: 200  
**Timeline**: 1-2 days  
**Assigned to**: QA / Integration  

**Test Cases**:
```
1. User Flow: Browse → Select → Sign In → Chat → Pay
2. Search Flow: Search query → Filter results → Select model
3. Q Assistant Flow: Ask recommendation → Get suggestion → Select
4. Chat Flow: Send message → Stream response → Show cost
5. Error Flow: Provider error → Graceful fallback
6. Payment Flow: Add credit → Send query → Deduct cost
7. Multi-Provider: OpenAI → Anthropic → Same cost tracking

Total: 7 critical E2E tests
```

**Testing Framework**: Playwright / Cypress

---

## 📊 SUMMARY BY COMPONENT

| Component | Lines | Days | Owner | Status |
|-----------|-------|------|-------|--------|
| Registry | 320 | 2 | Backend | Ready |
| Auth | 280 | 2 | Backend | Ready |
| Recommendations | 300 | 2 | Backend | Ready |
| Router | 300 | 2-3 | Backend | Ready |
| API Routes | 280 | 2 | Backend | Ready |
| Agent Routes | 220 | 2 | Backend | Ready |
| **Backend Total** | **1,700** | **5-6 days** | - | ✅ |
| Marketplace Panel | 550 | 3 | Frontend | Ready |
| Auth Modal | 400 | 3 | Frontend | Ready |
| Chat Component | 450 | 3-4 | Frontend | Ready |
| **Frontend Total** | **1,400** | **5-6 days** | - | ✅ |
| Unit Tests | 200 | 1-2 | QA | Ready |
| E2E Tests | 200 | 1-2 | QA | Ready |
| **Testing Total** | **400** | **2 days** | - | ✅ |
| **GRAND TOTAL** | **3,500+** | **10 days** | - | ✅ |

---

## 🎯 DAILY BREAKDOWN (Week 2-3)

### WEEK 2 (Nov 3-7)

**Monday (Day 1-2)**:
- Backend: Start Registry (Task 1.1)
- Frontend: Start Marketplace Panel (Task 2.1)
- Kickoff meeting (30 min)

**Tuesday (Day 3)**:
- Backend: Continue Registry → Start Auth (Tasks 1.1 → 1.2)
- Frontend: Continue Marketplace Panel
- Daily standup (3:30 PM)

**Wednesday (Day 4)**:
- Backend: Continue Auth → Start Recommendations (Tasks 1.2 → 1.3)
- Frontend: Continue Marketplace Panel → Start Auth Modal (Task 2.2)
- Daily standup

**Thursday (Day 5)**:
- Backend: Continue Recommendations → Start Router (Tasks 1.3 → 1.4)
- Frontend: Continue Auth Modal → Start Chat (Task 2.3)
- Daily standup
- **WEEKLY GOAL**: Core backend services done, frontend UI components underway

**Friday (Day 6)**:
- Backend: Continue Router → Start API routes (Tasks 1.4 → 1.5/1.6)
- Frontend: Continue Chat component
- Daily standup
- **WEEK 1 GOAL**: MVP v0.1 (marketplace browse + sign in working)

---

### WEEK 3 (Nov 10-14)

**Monday (Day 7)**:
- Backend: Finish API routes, start integration testing
- Frontend: Finish Chat component, start integration
- Integration: Wire frontend ↔ backend
- Daily standup

**Tuesday (Day 8)**:
- Backend: Testing & debugging (Task 3.1)
- Frontend: Integration & polish
- Integration: E2E testing (Task 3.2)
- Daily standup

**Wednesday (Day 9)**:
- Backend: Final testing & edge cases
- Frontend: UI polish, responsive design
- Integration: Production validation
- Daily standup

**Thursday (Day 10)**:
- All: Code review & final fixes
- Documentation: Write API docs, deploy guide
- Daily standup
- **SPRINT GOAL**: All tests passing, ready for private beta

**Friday (Day 11)**:
- Buffer day for fixes
- Performance optimization
- Security audit
- **READY FOR BETA**: Deploy v1.0

---

## ✅ DEFINITION OF DONE

### Backend Complete
- [ ] All 6 services built (Registry, Auth, Recommendations, Router, Marketplace API, Agent API)
- [ ] All services tested (17+ unit tests passing)
- [ ] API endpoints responding correctly
- [ ] Authentication secure
- [ ] Billing tracking accurate
- [ ] All 5 providers routing correctly
- [ ] Performance acceptable (< 200ms per request)

### Frontend Complete
- [ ] All 3 components built (Marketplace Panel, Auth Modal, Chat)
- [ ] UI responsive (desktop + tablet)
- [ ] All features working
- [ ] Real-time streaming working
- [ ] Error states handled
- [ ] Loading states shown
- [ ] Accessible (WCAG 2.1 AA)

### Integration Complete
- [ ] Frontend ↔ Backend communication working
- [ ] End-to-end chat functional
- [ ] Cost calculations accurate
- [ ] Balance updates in real-time
- [ ] All provider integrations working

### Testing Complete
- [ ] 17+ unit tests passing
- [ ] 7+ E2E tests passing
- [ ] Performance benchmarks met
- [ ] Security audit passed
- [ ] No critical bugs

### Launch Ready
- [ ] Documentation complete
- [ ] Deployment guide written
- [ ] Beta users ready (100)
- [ ] Metrics dashboard live
- [ ] Revenue tracking working

---

## 🚀 SUCCESS METRICS (Week 4)

```
By Friday Nov 14 (End of Sprint):

Adoption:
├─ Beta signups: 100 users
├─ Daily active: 30% = 30 users
└─ Daily queries: 60 (2 per user)

Revenue (Week 1 of beta):
├─ Paid queries: 80% of users × 60 queries × 7 days = 33,600 queries
├─ Average cost: $0.02 per query
├─ Gross revenue: $672
└─ Top Dog commission (30%): $202

Growth Trajectory:
├─ Week 1: 30 users
├─ Week 2: 50 users (+67%)
├─ Week 3: 80 users (+60%)
├─ Week 4: 150 users (+88%)

Projected Month 1: $1.8k MRR
Projected Month 6: $120k+ MRR
```

---

## 💡 KEY INSIGHTS

1. **Timing**: Complete in 10 days before Thanksgiving (Nov 22)
2. **Revenue**: 30% commission model is LOW FRICTION (users already paying providers)
3. **Competition**: First IDE with multi-provider AI marketplace
4. **Scalability**: All infrastructure scales to 1M+ users
5. **Retention**: Users will return for cost savings + recommendations

---

## 📚 RELATED DOCUMENTS

- `AI_AGENT_MARKETPLACE_SPEC.md` - Full specification & architecture
- `AI_AGENT_MARKETPLACE_QUICK_START.md` - Visual summary
- `TODAY_ACTION_PLAN.md` - 90-day roadmap (this doc is Phase 1 of Gap #5)

---

**Ready to build?** Start Task 1.1 on Monday! 🚀

Version 1.0 | October 29, 2025
