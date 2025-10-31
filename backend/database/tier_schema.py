"""
Database schema for membership tiers (SQLite Version)
Uses SQLite for local development, easy to switch to PostgreSQL in production
"""

import sqlite3
import os
from datetime import datetime


class MembershipTierSchema:
    """SQL schema definitions for membership tiers"""
    
    # Create tables SQL (SQLite syntax)
    CREATE_MEMBERSHIP_TIERS_TABLE = """
    CREATE TABLE IF NOT EXISTS membership_tiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tier_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        daily_call_limit INTEGER NOT NULL,
        daily_llm_requests INTEGER NOT NULL,
        concurrent_sessions INTEGER,
        storage_gb INTEGER,
        code_execution BOOLEAN DEFAULT 0,
        data_persistence BOOLEAN DEFAULT 1,
        webhooks BOOLEAN DEFAULT 0,
        api_keys_limit INTEGER DEFAULT 1,
        debug_logs_retention_days INTEGER DEFAULT 0,
        custom_llms BOOLEAN DEFAULT 0,
        team_members INTEGER DEFAULT 1,
        role_based_access BOOLEAN DEFAULT 0,
        shared_workspaces BOOLEAN DEFAULT 0,
        audit_logs BOOLEAN DEFAULT 0,
        resource_quotas BOOLEAN DEFAULT 0,
        hipaa_ready BOOLEAN DEFAULT 0,
        soc2_certified BOOLEAN DEFAULT 0,
        sso_saml BOOLEAN DEFAULT 0,
        data_residency BOOLEAN DEFAULT 0,
        custom_integrations BOOLEAN DEFAULT 0,
        on_premise_deploy BOOLEAN DEFAULT 0,
        account_manager BOOLEAN DEFAULT 0,
        support_tier TEXT,
        support_response_hours INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_USER_SUBSCRIPTIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS user_subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT UNIQUE NOT NULL,
        tier_id TEXT NOT NULL REFERENCES membership_tiers(tier_id),
        subscription_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        trial_expiry TIMESTAMP,
        is_active BOOLEAN DEFAULT 1,
        last_payment_date TIMESTAMP,
        next_billing_date TIMESTAMP
    );
    """
    
    CREATE_DAILY_USAGE_TABLE = """
    CREATE TABLE IF NOT EXISTS daily_usage_tracking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        usage_date DATE NOT NULL,
        api_calls_used INTEGER DEFAULT 0,
        llm_requests_used INTEGER DEFAULT 0,
        code_executions_used INTEGER DEFAULT 0,
        storage_used_gb REAL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, usage_date)
    );
    """
    
    CREATE_TIER_AUDIT_LOG = """
    CREATE TABLE IF NOT EXISTS tier_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        old_tier TEXT,
        new_tier TEXT NOT NULL,
        change_reason TEXT,
        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = """
    CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
    CREATE INDEX IF NOT EXISTS idx_daily_usage_user_id ON daily_usage_tracking(user_id);
    CREATE INDEX IF NOT EXISTS idx_daily_usage_date ON daily_usage_tracking(usage_date);
    CREATE INDEX IF NOT EXISTS idx_tier_audit_user_id ON tier_audit_log(user_id);
    """
    
    @staticmethod
    def get_db_path():
        """Get SQLite database path"""
        db_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(db_dir, 'q_ide.db')
        return db_path
    
    @staticmethod
    def setup_all_tables():
        """Create all membership tier tables"""
        db_path = MembershipTierSchema.get_db_path()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create tables
            cursor.execute(MembershipTierSchema.CREATE_MEMBERSHIP_TIERS_TABLE)
            print("✅ Created membership_tiers table")
            
            cursor.execute(MembershipTierSchema.CREATE_USER_SUBSCRIPTIONS_TABLE)
            print("✅ Created user_subscriptions table")
            
            cursor.execute(MembershipTierSchema.CREATE_DAILY_USAGE_TABLE)
            print("✅ Created daily_usage_tracking table")
            
            cursor.execute(MembershipTierSchema.CREATE_TIER_AUDIT_LOG)
            print("✅ Created tier_audit_log table")
            
            # Create indexes
            for index_sql in MembershipTierSchema.CREATE_INDEXES.split(';'):
                if index_sql.strip():
                    cursor.execute(index_sql)
            print("✅ Created indexes")
            
            conn.commit()
            conn.close()
            
            print(f"\n✅ All membership tier tables created successfully")
            print(f"   Database: {db_path}\n")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise


# Tier configurations - Progressive Value Ladder
TIER_CONFIGS = [
    {
        'tier_id': 'free',
        'name': 'FREE',
        'price': 0,
        'daily_call_limit': 20,
        'daily_llm_requests': 2,
        'concurrent_sessions': 1,
        'storage_gb': 0.5,
        'code_execution': False,  # ❌ UNLOCK IN PRO
        'data_persistence': True,
        'webhooks': False,
        'api_keys_limit': 1,
        'debug_logs_retention_days': 7,
        'custom_llms': False,
        'team_members': 1,
        'role_based_access': False,
        'shared_workspaces': False,
        'audit_logs': False,
        'resource_quotas': False,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': False,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Community',
        'support_response_hours': 72
    },
    {
        'tier_id': 'pro',
        'name': 'PRO',
        'price': 20,
        'daily_call_limit': 10000,
        'daily_llm_requests': 1000,
        'concurrent_sessions': 5,
        'storage_gb': 100,
        'code_execution': True,  # ✅ FIRST MAJOR UNLOCK
        'data_persistence': True,
        'webhooks': True,  # ✅ PRO UNLOCK: Webhooks
        'api_keys_limit': 5,  # ✅ PRO UNLOCK: Multiple keys
        'debug_logs_retention_days': 30,
        'custom_llms': False,  # ❌ UNLOCK IN PRO-PLUS
        'team_members': 1,
        'role_based_access': False,
        'shared_workspaces': False,
        'audit_logs': False,
        'resource_quotas': False,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': False,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Email',
        'support_response_hours': 24
    },
    {
        'tier_id': 'pro_plus',
        'name': 'PRO-PLUS',
        'price': 45,
        'daily_call_limit': 50000,
        'daily_llm_requests': 5000,
        'concurrent_sessions': 8,
        'storage_gb': 250,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 10,
        'debug_logs_retention_days': 60,
        'custom_llms': True,  # ✅ PRO-PLUS UNLOCK: Custom LLMs
        'team_members': 1,
        'role_based_access': False,
        'shared_workspaces': False,
        'audit_logs': False,
        'resource_quotas': False,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': True,  # ✅ PRO-PLUS UNLOCK: Custom integrations
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Priority Email',
        'support_response_hours': 12
    },
    {
        'tier_id': 'pro_team',
        'name': 'PRO-TEAM',
        'price': 75,
        'daily_call_limit': 50000,
        'daily_llm_requests': 5000,
        'concurrent_sessions': 8,
        'storage_gb': 250,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 10,
        'debug_logs_retention_days': 30,
        'custom_llms': True,  # ✅ PRO-TEAM HAS: Custom LLMs (like PRO-PLUS)
        'team_members': 3,  # ✅ PRO-TEAM UNLOCK: Small team support (3 people)
        'role_based_access': True,  # ✅ PRO-TEAM UNLOCK: Basic RBAC (Admin/Viewer)
        'shared_workspaces': True,  # ✅ PRO-TEAM UNLOCK: Shared workspaces
        'audit_logs': True,  # ✅ PRO-TEAM UNLOCK: Audit logs (7-day retention)
        'resource_quotas': False,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,  # ❌ Enterprise only
        'data_residency': False,  # ❌ Enterprise only
        'custom_integrations': True,
        'on_premise_deploy': False,  # ❌ Enterprise only
        'account_manager': False,  # ❌ Enterprise only
        'support_tier': 'Email + Community',
        'support_response_hours': 24
    },
    {
        'tier_id': 'teams_small',
        'name': 'TEAMS-SMALL',
        'price': 100,
        'daily_call_limit': 100000,
        'daily_llm_requests': 10000,
        'concurrent_sessions': 10,
        'storage_gb': 1000,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 20,
        'debug_logs_retention_days': 90,
        'custom_llms': True,
        'team_members': 5,  # ✅ TEAMS UNLOCK: Collaboration (5 members)
        'role_based_access': True,  # ✅ TEAMS UNLOCK: RBAC
        'shared_workspaces': True,  # ✅ TEAMS UNLOCK: Shared spaces
        'audit_logs': True,  # ✅ TEAMS UNLOCK: Audit trail
        'resource_quotas': True,  # ✅ TEAMS UNLOCK: Resource limits
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Email SLA',
        'support_response_hours': 24
    },
    {
        'tier_id': 'teams_medium',
        'name': 'TEAMS-MEDIUM',
        'price': 300,
        'daily_call_limit': 500000,
        'daily_llm_requests': 50000,
        'concurrent_sessions': 20,
        'storage_gb': 2000,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': -1,  # Unlimited
        'debug_logs_retention_days': 180,
        'custom_llms': True,
        'team_members': 30,  # ✅ Scaled team size
        'role_based_access': True,
        'shared_workspaces': True,
        'audit_logs': True,
        'resource_quotas': True,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Priority Email',
        'support_response_hours': 12
    },
    {
        'tier_id': 'teams_large',
        'name': 'TEAMS-LARGE',
        'price': 800,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 50,
        'storage_gb': 5000,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': -1,
        'debug_logs_retention_days': 365,
        'custom_llms': True,
        'team_members': 100,  # ✅ Large teams
        'role_based_access': True,
        'shared_workspaces': True,
        'audit_logs': True,
        'resource_quotas': True,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Priority Phone',
        'support_response_hours': 4
    },
    {
        'tier_id': 'enterprise_standard',
        'name': 'ENTERPRISE-STANDARD',
        'price': 5000,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 100,
        'storage_gb': 10000,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': -1,
        'debug_logs_retention_days': -1,  # Forever
        'custom_llms': True,
        'team_members': 500,
        'role_based_access': True,
        'shared_workspaces': True,
        'audit_logs': True,
        'resource_quotas': True,
        'hipaa_ready': True,  # ✅ ENTERPRISE UNLOCK: Compliance
        'soc2_certified': True,  # ✅ ENTERPRISE UNLOCK: Security
        'sso_saml': False,  # ❌ Premium only
        'data_residency': False,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Dedicated 24/7',
        'support_response_hours': 1
    },
    {
        'tier_id': 'enterprise_premium',
        'name': 'ENTERPRISE-PREMIUM',
        'price': 15000,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 100,
        'storage_gb': 50000,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': -1,
        'debug_logs_retention_days': -1,
        'custom_llms': True,
        'team_members': 2000,
        'role_based_access': True,
        'shared_workspaces': True,
        'audit_logs': True,
        'resource_quotas': True,
        'hipaa_ready': True,
        'soc2_certified': True,
        'sso_saml': True,  # ✅ PREMIUM UNLOCK: SSO/SAML
        'data_residency': False,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': True,  # ✅ PREMIUM UNLOCK: Account Manager
        'support_tier': 'Dedicated 24/7 + Account Manager',
        'support_response_hours': 1
    },
    {
        'tier_id': 'enterprise_ultimate',
        'name': 'ENTERPRISE-ULTIMATE',
        'price': 50000,
        'daily_call_limit': 9999999,
        'daily_llm_requests': 9999999,
        'concurrent_sessions': 999,
        'storage_gb': 999999,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': -1,
        'debug_logs_retention_days': -1,
        'custom_llms': True,
        'team_members': 99999,
        'role_based_access': True,
        'shared_workspaces': True,
        'audit_logs': True,
        'resource_quotas': True,
        'hipaa_ready': True,
        'soc2_certified': True,
        'sso_saml': True,
        'data_residency': True,  # ✅ ULTIMATE UNLOCK: Data residency
        'custom_integrations': True,
        'on_premise_deploy': True,  # ✅ ULTIMATE UNLOCK: On-premise
        'account_manager': True,
        'support_tier': 'Dedicated 24/7 + Executive Access',
        'support_response_hours': 0.5  # 30 minutes
    }
]
