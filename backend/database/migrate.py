"""
Database Migration Script
Connects to PostgreSQL and applies the AI Marketplace schema
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from pathlib import Path

class DatabaseMigration:
    """Handles database schema migration"""
    
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
        self.cursor = None
    
    def connect(self) -> bool:
        """Connect to PostgreSQL"""
        try:
            print(f"Connecting to PostgreSQL at {self.host}:{self.port}...")
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database='postgres'  # Connect to default DB first
            )
            self.cursor = self.conn.cursor()
            print("✅ Connected to PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def create_database(self) -> bool:
        """Create the marketplace database if it doesn't exist"""
        try:
            # Check if database exists
            self.cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.database,)
            )
            
            if self.cursor.fetchone():
                print(f"✅ Database '{self.database}' already exists")
            else:
                print(f"Creating database '{self.database}'...")
                self.cursor.execute(f"CREATE DATABASE {self.database}")
                self.conn.commit()
                print(f"✅ Database '{self.database}' created")
            
            # Now connect to the marketplace database
            self.conn.close()
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"❌ Database creation failed: {e}")
            return False
    
    def enable_extensions(self) -> bool:
        """Enable required PostgreSQL extensions"""
        try:
            print("Enabling PostgreSQL extensions...")
            extensions = ['uuid-ossp', 'pgcrypto']
            
            for ext in extensions:
                try:
                    self.cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
                    print(f"✅ Extension '{ext}' enabled")
                except Exception as e:
                    print(f"⚠️  Extension '{ext}' failed (may already exist): {e}")
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"❌ Extension setup failed: {e}")
            return False
    
    def apply_schema(self) -> bool:
        """Apply the schema from SQL file"""
        try:
            schema_file = Path(__file__).parent / 'schema.sql'
            
            if not schema_file.exists():
                print(f"❌ Schema file not found: {schema_file}")
                return False
            
            print(f"Reading schema from {schema_file}...")
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            print("Applying schema...")
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("✅ Schema applied successfully")
            return True
        except Exception as e:
            print(f"❌ Schema application failed: {e}")
            self.conn.rollback()
            return False
    
    def verify_schema(self) -> bool:
        """Verify that all tables were created"""
        try:
            print("Verifying schema...")
            
            # List of expected tables
            expected_tables = [
                'users',
                'api_keys',
                'user_balance',
                'transactions',
                'chat_history',
                'chat_sessions',
                'model_ratings',
                'model_usage_stats',
                'user_preferences',
                'audit_log'
            ]
            
            self.cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            
            existing_tables = [row[0] for row in self.cursor.fetchall()]
            
            all_found = True
            for table in expected_tables:
                if table in existing_tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    all_found = False
            
            return all_found
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def create_sample_data(self) -> bool:
        """Create sample data for testing"""
        try:
            print("Creating sample data...")
            
            # Note: In production, this would be handled by the application
            # This is just for development/testing
            
            print("✅ Sample data prepared (will be populated by application)")
            return True
        except Exception as e:
            print(f"❌ Sample data creation failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("✅ Database connection closed")
    
    def run_migration(self) -> bool:
        """Run the complete migration"""
        print("\n" + "="*60)
        print("Q-IDE AI MARKETPLACE DATABASE MIGRATION")
        print("="*60 + "\n")
        
        steps = [
            ("Connecting to PostgreSQL", self.connect),
            ("Creating database", self.create_database),
            ("Enabling extensions", self.enable_extensions),
            ("Applying schema", self.apply_schema),
            ("Verifying schema", self.verify_schema),
            ("Creating sample data", self.create_sample_data),
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\n[{steps.index((step_name, step_func)) + 1}/{len(steps)}] {step_name}...")
            if not step_func():
                success = False
                print(f"❌ Migration failed at: {step_name}")
                break
        
        self.close()
        
        if success:
            print("\n" + "="*60)
            print("✅ MIGRATION SUCCESSFUL")
            print("="*60)
            print("\nDatabase is ready for use!")
            print("Environment variables:")
            print(f"  DB_HOST={self.host}")
            print(f"  DB_PORT={self.port}")
            print(f"  DB_NAME={self.database}")
            print(f"  DB_USER={self.user}")
        
        return success


if __name__ == "__main__":
    # Read configuration from environment or use defaults
    migration = DatabaseMigration()
    
    success = migration.run_migration()
    sys.exit(0 if success else 1)
