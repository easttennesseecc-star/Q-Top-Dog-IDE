"""
Database Service for AI Marketplace
Handles persistence layer using PostgreSQL
Can be swapped in place of in-memory dictionaries
"""

from typing import Optional, Dict, List, Tuple
import psycopg2
from psycopg2 import sql
import json
import os
from datetime import datetime


class DatabaseService:
    """Handles all database operations"""
    
    def __init__(self,
                 host: str = os.getenv('DB_HOST', 'localhost'),
                 port: int = int(os.getenv('DB_PORT', 5432)),
                 database: str = os.getenv('DB_NAME', 'q_marketplace'),
                 user: str = os.getenv('DB_USER', 'postgres'),
                 password: str = os.getenv('DB_PASSWORD', 'postgres')):
        """Initialize database connection"""
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.conn = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("✅ Connected to database")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def execute(self, query: str, params: tuple = ()) -> psycopg2.extensions.cursor:
        """Execute a query and return cursor"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor
    
    def commit(self):
        """Commit transaction"""
        self.conn.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.conn.rollback()
    
    def close(self):
        """Close connection"""
        if self.conn:
            self.conn.close()
    
    # ==================== USER OPERATIONS ====================
    
    def create_user(self, user_id: str, email: str, username: str, password_hash: str) -> bool:
        """Create new user"""
        try:
            query = """
                INSERT INTO users (id, email, username, password_hash, is_active)
                VALUES (%s, %s, %s, %s, true)
            """
            cursor = self.execute(query, (user_id, email, username, password_hash))
            self.commit()
            
            # Create balance record
            balance_query = """
                INSERT INTO user_balance (user_id, total_balance, spent_balance)
                VALUES (%s, 0.00, 0.00)
            """
            self.execute(balance_query, (user_id,))
            self.commit()
            
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            self.rollback()
            return False
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            query = """
                SELECT id, email, username, password_hash, is_active, created_at, last_login
                FROM users WHERE email = %s
            """
            cursor = self.execute(query, (email,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'email': row[1],
                    'username': row[2],
                    'password_hash': row[3],
                    'is_active': row[4],
                    'created_at': row[5],
                    'last_login': row[6]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        try:
            query = """
                SELECT id, email, username, password_hash, is_active
                FROM users WHERE username = %s
            """
            cursor = self.execute(query, (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'email': row[1],
                    'username': row[2],
                    'password_hash': row[3],
                    'is_active': row[4]
                }
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def update_last_login(self, user_id: str):
        """Update user last login time"""
        try:
            query = "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s"
            self.execute(query, (user_id,))
            self.commit()
        except Exception as e:
            print(f"Error updating last login: {e}")
    
    # ==================== API KEY OPERATIONS ====================
    
    def add_api_key(self, key_id: str, user_id: str, provider: str, 
                    key_encrypted: str, key_hash: str, daily_limit: Optional[int] = None) -> bool:
        """Add API key for user"""
        try:
            query = """
                INSERT INTO api_keys (id, user_id, provider, key_encrypted, key_hash, status, daily_limit)
                VALUES (%s, %s, %s, %s, %s, 'active', %s)
            """
            self.execute(query, (key_id, user_id, provider, key_encrypted, key_hash, daily_limit))
            self.commit()
            return True
        except Exception as e:
            print(f"Error adding API key: {e}")
            self.rollback()
            return False
    
    def get_api_keys_for_user(self, user_id: str) -> List[Dict]:
        """Get all API keys for user"""
        try:
            query = """
                SELECT id, provider, status, daily_limit, usage_count, created_at, last_used
                FROM api_keys WHERE user_id = %s
            """
            cursor = self.execute(query, (user_id,))
            
            keys = []
            for row in cursor.fetchall():
                keys.append({
                    'id': row[0],
                    'provider': row[1],
                    'status': row[2],
                    'daily_limit': row[3],
                    'usage_count': row[4],
                    'created_at': row[5],
                    'last_used': row[6]
                })
            return keys
        except Exception as e:
            print(f"Error getting API keys: {e}")
            return []
    
    def get_provider_key(self, user_id: str, provider: str) -> Optional[str]:
        """Get encrypted key for provider"""
        try:
            query = """
                SELECT key_encrypted FROM api_keys 
                WHERE user_id = %s AND provider = %s AND status = 'active'
            """
            cursor = self.execute(query, (user_id, provider))
            row = cursor.fetchone()
            
            if row:
                return row[0]
            return None
        except Exception as e:
            print(f"Error getting provider key: {e}")
            return None
    
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        try:
            query = """
                UPDATE api_keys 
                SET status = 'revoked', revoked_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            self.execute(query, (key_id,))
            self.commit()
            return True
        except Exception as e:
            print(f"Error revoking API key: {e}")
            self.rollback()
            return False
    
    # ==================== BALANCE OPERATIONS ====================
    
    def get_user_balance(self, user_id: str) -> Optional[Dict]:
        """Get user balance"""
        try:
            query = """
                SELECT total_balance, spent_balance, currency
                FROM user_balance WHERE user_id = %s
            """
            cursor = self.execute(query, (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'total_balance': float(row[0]),
                    'spent_balance': float(row[1]),
                    'available_balance': float(row[0]) - float(row[1]),
                    'currency': row[2]
                }
            return None
        except Exception as e:
            print(f"Error getting balance: {e}")
            return None
    
    def add_funds(self, user_id: str, amount: float, transaction_id: str) -> bool:
        """Add funds to user balance"""
        try:
            # Update balance
            update_query = """
                UPDATE user_balance 
                SET total_balance = total_balance + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """
            self.execute(update_query, (amount, user_id))
            
            # Log transaction
            trans_query = """
                INSERT INTO transactions (id, user_id, transaction_type, amount, description, status)
                VALUES (%s, %s, 'deposit', %s, %s, 'completed')
            """
            import uuid
            self.execute(trans_query, (str(uuid.uuid4()), user_id, amount, f'Payment: {transaction_id}'))
            
            self.commit()
            return True
        except Exception as e:
            print(f"Error adding funds: {e}")
            self.rollback()
            return False
    
    def deduct_balance(self, user_id: str, amount: float, model_id: str, tokens_used: int) -> bool:
        """Deduct from user balance"""
        try:
            # Check sufficient balance
            balance_query = """
                SELECT total_balance, spent_balance FROM user_balance WHERE user_id = %s
            """
            cursor = self.execute(balance_query, (user_id,))
            row = cursor.fetchone()
            
            if not row or (row[1] + amount) > row[0]:
                return False
            
            # Deduct balance
            deduct_query = """
                UPDATE user_balance 
                SET spent_balance = spent_balance + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s
            """
            self.execute(deduct_query, (amount, user_id))
            
            # Log transaction
            trans_query = """
                INSERT INTO transactions (id, user_id, transaction_type, amount, model_id, tokens_used, description)
                VALUES (%s, %s, 'charge', %s, %s, %s, %s)
            """
            import uuid
            self.execute(trans_query, (
                str(uuid.uuid4()), user_id, amount, model_id, 
                tokens_used, f'Usage: {model_id}'
            ))
            
            # Update model stats
            stats_query = """
                UPDATE model_usage_stats
                SET total_cost = total_cost + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE model_id = %s
            """
            self.execute(stats_query, (amount, model_id))
            
            self.commit()
            return True
        except Exception as e:
            print(f"Error deducting balance: {e}")
            self.rollback()
            return False
    
    def get_balance_transactions(self, user_id: str, limit: int = 50, skip: int = 0) -> List[Dict]:
        """Get user transactions"""
        try:
            query = """
                SELECT id, transaction_type, amount, model_id, tokens_used, description, created_at
                FROM transactions 
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor = self.execute(query, (user_id, limit, skip))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'id': row[0],
                    'type': row[1],
                    'amount': float(row[2]),
                    'model_id': row[3],
                    'tokens_used': row[4],
                    'description': row[5],
                    'created_at': row[6]
                })
            return transactions
        except Exception as e:
            print(f"Error getting transactions: {e}")
            return []
    
    # ==================== CHAT OPERATIONS ====================
    
    def create_chat_session(self, session_id: str, user_id: str, model_id: str, title: str = None) -> bool:
        """Create new chat session"""
        try:
            query = """
                INSERT INTO chat_sessions (id, user_id, model_id, title)
                VALUES (%s, %s, %s, %s)
            """
            self.execute(query, (session_id, user_id, model_id, title))
            self.commit()
            return True
        except Exception as e:
            print(f"Error creating chat session: {e}")
            self.rollback()
            return False
    
    def save_chat_message(self, message_id: str, user_id: str, session_id: str,
                         model_id: str, role: str, content: str, tokens_used: int = 0, cost: float = 0.0) -> bool:
        """Save chat message"""
        try:
            query = """
                INSERT INTO chat_history (id, user_id, session_id, model_id, message_role, message_content, tokens_used, cost)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.execute(query, (message_id, user_id, session_id, model_id, role, content, tokens_used, cost))
            
            # Update session stats
            update_query = """
                UPDATE chat_sessions
                SET total_messages = total_messages + 1,
                    total_tokens = total_tokens + %s,
                    total_cost = total_cost + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            self.execute(update_query, (tokens_used, cost, session_id))
            
            self.commit()
            return True
        except Exception as e:
            print(f"Error saving chat message: {e}")
            self.rollback()
            return False
    
    def get_chat_history(self, session_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for session"""
        try:
            query = """
                SELECT message_role, message_content, tokens_used, cost, created_at
                FROM chat_history
                WHERE session_id = %s
                ORDER BY created_at ASC
                LIMIT %s
            """
            cursor = self.execute(query, (session_id, limit))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'tokens_used': row[2],
                    'cost': float(row[3]) if row[3] else 0.0,
                    'created_at': row[4]
                })
            return messages
        except Exception as e:
            print(f"Error getting chat history: {e}")
            return []


# Usage example:
# db = DatabaseService()
# db.create_user('user-1', 'user@example.com', 'username', 'hash')
# db.add_funds('user-1', 100.00, 'txn-123')
# balance = db.get_user_balance('user-1')
# db.deduct_balance('user-1', 5.50, 'gpt4-turbo', 2500)
# db.close()


# Global database instance
_db_instance = None


def get_db() -> DatabaseService:
    """Get or create the global database instance"""
    global _db_instance
    if _db_instance is None:
        try:
            _db_instance = DatabaseService()
        except Exception as e:
            # If database connection fails, return a dummy instance
            print(f"Warning: Database connection failed: {e}")
            return None
    return _db_instance

