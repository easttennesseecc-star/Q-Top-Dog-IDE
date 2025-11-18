"""
AI Authentication Service
Handles user registration, login, API key management, and balance tracking
"""

from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
import hashlib
import os


class APIKeyStatus(str, Enum):
    """Status of an API key"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    REVOKED = "revoked"
    EXPIRED = "expired"


class ProviderType(str, Enum):
    """Third-party AI provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    GOOGLE_OAUTH = "google_oauth"
    GITHUB = "github"
    GITHUB_COPILOT = "github_copilot"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"


@dataclass
class APIKey:
    """Represents a user's API key for a provider"""
    id: str
    user_id: str
    provider: ProviderType
    key_encrypted: str  # Encrypted API key (we never store plaintext)
    key_hash: str  # Hash of key for quick lookup
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    usage_count: int = 0
    daily_limit: Optional[int] = None  # None = unlimited
    
    def to_dict_safe(self):
        """Convert to dict without exposing encrypted key"""
        return {
            'id': self.id,
            'provider': self.provider.value,
            'status': self.status.value,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'usage_count': self.usage_count,
            'daily_limit': self.daily_limit
        }


@dataclass
class UserBalance:
    """Represents a user's prepaid balance"""
    user_id: str
    total_balance: float = 0.0  # USD
    spent_balance: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    transactions: List[Dict] = field(default_factory=list)
    
    @property
    def available_balance(self) -> float:
        """Calculate available balance"""
        return self.total_balance - self.spent_balance
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'user_id': self.user_id,
            'total_balance': self.total_balance,
            'spent_balance': self.spent_balance,
            'available_balance': self.available_balance,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


@dataclass
class User:
    """Represents a marketplace user"""
    id: str
    email: str
    username: str
    password_hash: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: Optional[str] = None
    api_keys: Dict[str, APIKey] = field(default_factory=dict)
    balance: UserBalance = field(default_factory=lambda: UserBalance(user_id=""))
    is_active: bool = True
    paid: bool = False  # Payment status for user verification
    is_founder: bool = False  # Founder bypass - always has full access
    preferences: Dict = field(default_factory=dict)
    
    def to_dict_safe(self):
        """Convert to dict without exposing sensitive info"""
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'is_active': self.is_active,
            'paid': self.paid,
            'is_founder': self.is_founder,
            'api_keys_count': len(self.api_keys),
            'balance': self.balance.to_dict()
        }


@dataclass
class AuthToken:
    """JWT-like token for authentication"""
    token: str
    user_id: str
    issued_at: datetime
    expires_at: datetime
    
    @property
    def is_valid(self) -> bool:
        """Check if token is still valid"""
        return datetime.now() < self.expires_at
    
    def to_dict(self):
        return {
            'token': self.token,
            'user_id': self.user_id,
            'expires_at': self.expires_at.isoformat()
        }


class PasswordHasher:
    """Handle secure password hashing"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using PBKDF2"""
        salt = secrets.token_hex(32)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${pwd_hash.hex()}"
    
    @staticmethod
    def verify_password(password: str, hash_value: str) -> bool:
        """Verify a password against its hash"""
        salt, pwd_hash = hash_value.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return new_hash.hex() == pwd_hash


class KeyEncryption:
    """Simple encryption for API keys (in production use proper encryption)"""
    
    # In production, use AWS KMS or similar
    SECRET_KEY = "your-secret-key-change-in-production"
    
    @staticmethod
    def encrypt_key(api_key: str) -> str:
        """Encrypt an API key"""
        # Simple XOR encryption (replace with proper encryption in production)
        encrypted = ''.join(chr(ord(c) ^ ord(KeyEncryption.SECRET_KEY[i % len(KeyEncryption.SECRET_KEY)])) 
                           for i, c in enumerate(api_key))
        return encrypted.encode().hex()
    
    @staticmethod
    def decrypt_key(encrypted_key: str) -> str:
        """Decrypt an API key"""
        encrypted = bytes.fromhex(encrypted_key).decode()
        decrypted = ''.join(chr(ord(c) ^ ord(KeyEncryption.SECRET_KEY[i % len(KeyEncryption.SECRET_KEY)])) 
                           for i, c in enumerate(encrypted))
        return decrypted


class AIAuthService:
    """Authentication service for marketplace users"""
    
    # Founder email - always has full access regardless of payment status
    # Can be overridden with env var FOUNDER_EMAIL
    FOUNDER_EMAIL = os.getenv("FOUNDER_EMAIL", "paul@quellum.net")
    
    def __init__(self):
        """Initialize the auth service"""
        self.users: Dict[str, User] = {}
        self.email_index: Dict[str, str] = {}  # email -> user_id
        self.username_index: Dict[str, str] = {}  # username -> user_id
        self.api_key_index: Dict[str, str] = {}  # key_hash -> user_id
        self.tokens: Dict[str, AuthToken] = {}
        self.token_expiry = timedelta(days=7)
    
    # ==================== USER MANAGEMENT ====================
    
    def register_user(
        self,
        email: str,
        username: str,
        password: str
    ) -> Tuple[bool, str, Optional[User]]:
        """Register a new user"""
        
        # Validation
        if email in self.email_index:
            return False, "Email already registered", None
        
        if username in self.username_index:
            return False, "Username already taken", None
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters", None
        
        # Create user
        user_id = secrets.token_hex(8)
        password_hash = PasswordHasher.hash_password(password)
        
        # Check if founder
        is_founder = email.lower() == self.FOUNDER_EMAIL.lower()
        
        user = User(
            id=user_id,
            email=email,
            username=username,
            password_hash=password_hash,
            is_founder=is_founder,
            paid=is_founder  # Founder always has paid access
        )
        user.balance = UserBalance(user_id=user_id)
        
        # Store user
        self.users[user_id] = user
        self.email_index[email] = user_id
        self.username_index[username] = user_id
        
        return True, "User registered successfully", user
    
    def login_user(
        self,
        email: str,
        password: str
    ) -> Tuple[bool, str, Optional[AuthToken]]:
        """Authenticate user and return token"""
        
        # Find user
        if email not in self.email_index:
            return False, "User not found", None
        
        user_id = self.email_index[email]
        user = self.users[user_id]
        
        # Verify password
        if not PasswordHasher.verify_password(password, user.password_hash):
            return False, "Invalid password", None
        
        # Create token
        now = datetime.now()
        token_str = secrets.token_urlsafe(32)
        token = AuthToken(
            token=token_str,
            user_id=user_id,
            issued_at=now,
            expires_at=now + self.token_expiry
        )
        
        self.tokens[token_str] = token
        user.last_login = now.isoformat()
        
        return True, "Login successful", token
    
    def verify_token(self, token_str: str) -> Tuple[bool, Optional[str]]:
        """Verify a token and return user_id"""
        
        if token_str not in self.tokens:
            return False, None
        
        token = self.tokens[token_str]
        if not token.is_valid:
            del self.tokens[token_str]
            return False, None
        
        return True, token.user_id
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        if email in self.email_index:
            return self.users[self.email_index[email]]
        return None
    
    def verify_user_access(self, user_id: str) -> Tuple[bool, str]:
        """
        Verify if user has access based on paid status.
        Founders always have full access regardless of payment.
        
        Returns: (has_access, reason)
        """
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        # Founder bypass - always has full access
        if user.is_founder:
            return True, "Founder access"
        
        # Check paid status
        if user.paid:
            return True, "Paid user"
        
        return False, "Payment required. Please upgrade your account."
    
    def set_paid_status(self, user_id: str, paid: bool) -> Tuple[bool, str]:
        """Set user's paid status (admin function)"""
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        # Cannot modify founder status
        if user.is_founder:
            return True, "Founder always has full access"
        
        user.paid = paid
        return True, f"User paid status set to {paid}"
    
    # ==================== API KEY MANAGEMENT ====================
    
    def add_api_key(
        self,
        user_id: str,
        provider: ProviderType,
        api_key: str,
        daily_limit: Optional[int] = None
    ) -> Tuple[bool, str, Optional[APIKey]]:
        """Add an API key for a provider"""
        
        user = self.get_user(user_id)
        if not user:
            return False, "User not found", None
        
        # Check if already have key for this provider
        for existing_key in user.api_keys.values():
            if existing_key.provider == provider and existing_key.status == APIKeyStatus.ACTIVE:
                return False, f"Already have active key for {provider.value}", None
        
        # Create key entry
        key_id = secrets.token_hex(8)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        encrypted_key = KeyEncryption.encrypt_key(api_key)
        
        api_key_obj = APIKey(
            id=key_id,
            user_id=user_id,
            provider=provider,
            key_encrypted=encrypted_key,
            key_hash=key_hash,
            daily_limit=daily_limit
        )
        
        user.api_keys[key_id] = api_key_obj
        self.api_key_index[key_hash] = user_id
        
        return True, "API key added successfully", api_key_obj
    
    def remove_api_key(self, user_id: str, key_id: str) -> Tuple[bool, str]:
        """Remove/revoke an API key"""
        
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        if key_id not in user.api_keys:
            return False, "API key not found"
        
        # Mark as revoked instead of deleting
        api_key = user.api_keys[key_id]
        api_key.status = APIKeyStatus.REVOKED
        
        return True, "API key revoked"
    
    def get_api_keys(self, user_id: str) -> Tuple[bool, List[Dict]]:
        """Get all API keys for a user"""
        
        user = self.get_user(user_id)
        if not user:
            return False, []
        
        keys = [key.to_dict_safe() for key in user.api_keys.values() 
                if key.status == APIKeyStatus.ACTIVE]
        
        return True, keys
    
    def get_provider_key(self, user_id: str, provider: ProviderType) -> Tuple[bool, Optional[str]]:
        """Get decrypted API key for a provider"""
        
        user = self.get_user(user_id)
        if not user:
            return False, None
        
        for api_key in user.api_keys.values():
            if api_key.provider == provider and api_key.status == APIKeyStatus.ACTIVE:
                decrypted_key = KeyEncryption.decrypt_key(api_key.key_encrypted)
                api_key.last_used = datetime.now().isoformat()
                api_key.usage_count += 1
                return True, decrypted_key
        
        return False, None
    
    # ==================== BALANCE MANAGEMENT ====================
    
    def add_funds(
        self,
        user_id: str,
        amount: float,
        transaction_id: str
    ) -> Tuple[bool, str, Optional[UserBalance]]:
        """Add funds to user's balance"""
        
        user = self.get_user(user_id)
        if not user:
            return False, "User not found", None
        
        if amount <= 0:
            return False, "Amount must be positive", None
        
        user.balance.total_balance += amount
        user.balance.updated_at = datetime.now().isoformat()
        user.balance.transactions.append({
            'type': 'credit',
            'amount': amount,
            'transaction_id': transaction_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return True, "Funds added successfully", user.balance
    
    def deduct_balance(
        self,
        user_id: str,
        amount: float,
        model_id: str,
        tokens_used: int
    ) -> Tuple[bool, str]:
        """Deduct from user's balance"""
        
        user = self.get_user(user_id)
        if not user:
            return False, "User not found"
        
        if user.balance.available_balance < amount:
            return False, "Insufficient balance"
        
        user.balance.spent_balance += amount
        user.balance.updated_at = datetime.now().isoformat()
        user.balance.transactions.append({
            'type': 'debit',
            'amount': amount,
            'model_id': model_id,
            'tokens_used': tokens_used,
            'timestamp': datetime.now().isoformat()
        })
        
        return True, "Balance deducted"
    
    def get_balance(self, user_id: str) -> Tuple[bool, Optional[Dict]]:
        """Get user's balance information"""
        
        user = self.get_user(user_id)
        if not user:
            return False, None
        
        return True, user.balance.to_dict()
    
    def get_balance_transactions(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> Tuple[bool, List[Dict], int]:
        """Get user's transaction history"""
        
        user = self.get_user(user_id)
        if not user:
            return False, [], 0
        
        transactions = user.balance.transactions[::-1]  # Reverse for newest first
        total = len(transactions)
        
        return True, transactions[skip:skip + limit], total
    
    # ==================== STATISTICS ====================
    
    def get_statistics(self) -> Dict:
        """Get authentication service statistics"""
        
        total_users = len(self.users)
        active_tokens = sum(1 for t in self.tokens.values() if t.is_valid)
        total_balance = sum(u.balance.total_balance for u in self.users.values())
        
        return {
            'total_users': total_users,
            'active_tokens': active_tokens,
            'total_api_keys': sum(len(u.api_keys) for u in self.users.values()),
            'total_prepaid_balance': total_balance,
            'average_balance_per_user': total_balance / total_users if total_users > 0 else 0
        }


# Global auth service instance
auth_service = AIAuthService()
