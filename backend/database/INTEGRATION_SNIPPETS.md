# Quick Integration Snippets

## How to Replace In-Memory Data with DatabaseService

### Current Code Pattern (In-Memory)
```python
# OLD - Uses dictionaries
class AuthService:
    def __init__(self):
        self.users = {}  # In-memory dictionary
        self.api_keys = {}
        self.balance_tracker = {}

    def register_user(self, email, username, password):
        user_id = str(uuid.uuid4())
        self.users[user_id] = {
            'email': email,
            'username': username,
            'password_hash': hash_password(password)
        }
        return True, user_id
```

### New Code Pattern (Database)
```python
# NEW - Uses DatabaseService
from database.database_service import DatabaseService

class AuthService:
    def __init__(self):
        self.db = DatabaseService()  # One line replaces all dictionaries

    def register_user(self, email, username, password):
        user_id = str(uuid.uuid4())
        success = self.db.create_user(user_id, email, username, hash_password(password))
        if success:
            return True, user_id
        return False, "Registration failed"
```

## Benefits of Using DatabaseService

| Feature | In-Memory | DatabaseService |
|---------|-----------|-----------------|
| Data Persistence | ❌ Lost on restart | ✅ Permanent |
| Scalability | ❌ Limited | ✅ Scales to millions |
| Multi-process | ❌ Data conflicts | ✅ Atomic transactions |
| Backups | ❌ Manual copy | ✅ Automated with pg_dump |
| Query Analysis | ❌ No insights | ✅ Full audit trail |
| Security | ⚠️ Basic | ✅ Encryption + audit logs |

## Migration Path (Safe Way)

### Option A: Gradual Migration (Recommended for Production)

```python
class AuthService:
    def __init__(self, use_database=True):
        self.use_database = use_database
        if use_database:
            self.db = DatabaseService()
        else:
            self.users = {}  # Keep in-memory as fallback
    
    def get_user(self, email):
        if self.use_database:
            return self.db.get_user_by_email(email)  # New path
        else:
            return self.users.get(email)  # Old path
    
    # Can toggle with environment variable
    # use_db = os.getenv('USE_DATABASE', 'true').lower() == 'true'
```

### Option B: Full Cutover (Recommended for Now)

Since we're just getting started, full cutover is fine:

```python
# Just remove all the in-memory dictionaries
# Replace with:
class AuthService:
    def __init__(self):
        self.db = DatabaseService()  # That's it!
```

## Database Method Mapping

### Users
```python
# Create
self.db.create_user(user_id, email, username, password_hash)

# Read
user = self.db.get_user_by_email(email)
user = self.db.get_user_by_username(username)

# Update
self.db.update_last_login(user_id)
```

### API Keys
```python
# Create
self.db.add_api_key(key_id, user_id, provider, encrypted_key, key_hash)

# Read
keys = self.db.get_api_keys_for_user(user_id)
key = self.db.get_provider_key(user_id, provider)

# Delete
self.db.revoke_api_key(key_id)
```

### Balance
```python
# Read
balance = self.db.get_user_balance(user_id)
# Returns: {'total_balance': 100.0, 'spent_balance': 5.0, 'available_balance': 95.0}

# Update
self.db.add_funds(user_id, 50.0, transaction_id)
self.db.deduct_balance(user_id, 5.0, model_id, tokens_used)

# Read History
transactions = self.db.get_balance_transactions(user_id, limit=50)
```

### Chat
```python
# Create Session
self.db.create_chat_session(session_id, user_id, model_id, title)

# Save Message
self.db.save_chat_message(message_id, user_id, session_id, model_id, 'user', content, tokens, cost)

# Read History
messages = self.db.get_chat_history(session_id)
```

## Implementation Examples

### Example 1: Update Registration Endpoint

```python
@app.route('/register', methods=['POST'])
def register():
    """Before: Used in-memory dict"""
    # OLD CODE:
    # data = request.json
    # user = User(data['email'], data['username'], data['password'])
    # AUTH_SERVICE.users[user.id] = user.__dict__
    
    """After: Uses database"""
    # NEW CODE:
    data = request.json
    success, message = AUTH_SERVICE.register_user(
        data['email'],
        data['username'],
        data['password']
    )
    
    if success:
        return jsonify({'user_id': message, 'message': 'Registered'}), 201
    return jsonify({'error': message}), 400
```

### Example 2: Update Balance Endpoint

```python
@app.route('/balance/<user_id>', methods=['GET'])
def get_balance(user_id):
    """Before: Queried in-memory dict"""
    # OLD CODE:
    # balance = AUTH_SERVICE.balance_tracker.get(user_id, {'total': 0, 'spent': 0})
    # return jsonify(balance)
    
    """After: Queries database"""
    # NEW CODE:
    balance = AUTH_SERVICE.get_balance(user_id)
    if balance:
        return jsonify(balance), 200
    return jsonify({'error': 'User not found'}), 404
```

### Example 3: Update Chat Storage

```python
class AIAgentChat:
    def save_message(self, user_id, session_id, model_id, role, content, tokens, cost):
        """Before: Stored in memory"""
        # OLD CODE:
        # self.chat_history[session_id].append({
        #     'role': role, 'content': content, 'timestamp': time.time()
        # })
        
        """After: Stores in database"""
        # NEW CODE:
        import uuid
        message_id = str(uuid.uuid4())
        self.db.save_chat_message(
            message_id, user_id, session_id, model_id,
            role, content, tokens, cost
        )
    
    def load_history(self, session_id):
        """Before: Returned from memory"""
        # OLD CODE:
        # return self.chat_history.get(session_id, [])
        
        """After: Queries database"""
        # NEW CODE:
        return self.db.get_chat_history(session_id)
```

## Testing the Integration

### Unit Test Example
```python
def test_user_registration_with_database():
    """Test that registration persists to database"""
    auth = AuthService(use_database=True)
    
    # Register user
    success, user_id = auth.register_user('test@example.com', 'testuser', 'password123')
    assert success
    
    # Should be able to retrieve from database
    user = auth.db.get_user_by_email('test@example.com')
    assert user is not None
    assert user['username'] == 'testuser'
    
    # Data should persist after service restart
    auth2 = AuthService(use_database=True)
    user2 = auth2.db.get_user_by_email('test@example.com')
    assert user2['id'] == user['id']
```

### Integration Test Example
```python
def test_balance_transaction_with_database():
    """Test that balance changes persist"""
    auth = AuthService(use_database=True)
    
    # Create user
    success, user_id = auth.register_user('balance@test.com', 'buser', 'password123')
    assert success
    
    # Add funds
    success, msg = auth.add_funds(user_id, 100.0)
    assert success
    
    # Verify balance
    balance = auth.get_balance(user_id)
    assert balance['total_balance'] == 100.0
    assert balance['available_balance'] == 100.0
    
    # Deduct funds
    success = auth.deduct_balance(user_id, 25.0, 'gpt-4', 5000)
    assert success
    
    # Verify new balance
    balance = auth.get_balance(user_id)
    assert balance['total_balance'] == 100.0
    assert balance['spent_balance'] == 25.0
    assert balance['available_balance'] == 75.0
    
    # Check transaction history
    transactions = auth.db.get_balance_transactions(user_id)
    assert len(transactions) >= 2  # Deposit + charge
```

## Rollback Plan

If you need to go back to in-memory:

```python
# Keep a hybrid version
class AuthService:
    def __init__(self):
        self.db = DatabaseService()
        self.in_memory_users = {}  # Fallback
    
    def fallback_register(self, email, username, password):
        """Emergency fallback to in-memory"""
        import uuid
        user_id = str(uuid.uuid4())
        self.in_memory_users[user_id] = {
            'email': email, 'username': username, 'password_hash': hash_password(password)
        }
        return True, user_id

# Then in production, if DB goes down:
try:
    success, user_id = self.db.create_user(...)
except:
    # Fall back to in-memory
    success, user_id = self.fallback_register(...)
```

## Commands Reference

```bash
# Check if service is ready
python -c "from backend.database.database_service import DatabaseService; db = DatabaseService(); print('✅ Connected!')"

# List all methods
python -c "from backend.database.database_service import DatabaseService; print([m for m in dir(DatabaseService) if not m.startswith('_')])"

# Test specific operation
python -c "
from backend.database.database_service import DatabaseService
db = DatabaseService()
success = db.create_user('test-id', 'test@example.com', 'testuser', 'hash123')
print(f'User creation: {'✅ Success' if success else '❌ Failed'}')"
```

---

**You're ready to integrate!** Start with one service (AuthService), test it, then move to the others. Each integration takes ~30 minutes.
