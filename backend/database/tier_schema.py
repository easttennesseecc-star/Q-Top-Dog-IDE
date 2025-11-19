"""
Database schema for membership tiers (SQLite Version)
Uses SQLite for local development, easy to switch to PostgreSQL in production
"""

import sqlite3
import os


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
        agent_roles_limit INTEGER DEFAULT 0,
        models_unrestricted BOOLEAN DEFAULT 1,
        code_execution BOOLEAN DEFAULT 0,
        data_persistence BOOLEAN DEFAULT 1,
        webhooks BOOLEAN DEFAULT 0,
        api_keys_limit INTEGER DEFAULT 1,
        byok_slots_per_seat INTEGER DEFAULT 0,
        org_byok_base INTEGER DEFAULT 0,
        org_byok_per_seat INTEGER DEFAULT 0,
        org_pooled_api_calls_per_seat INTEGER DEFAULT 0,
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

    # Lightweight organization model (for pooled quotas & BYOK pools)
    CREATE_ORGANIZATIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        tier_id TEXT NOT NULL REFERENCES membership_tiers(tier_id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    CREATE_ORG_MEMBERS_TABLE = """
    CREATE TABLE IF NOT EXISTS organization_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(org_id, user_id)
    );
    """

    CREATE_ORG_DAILY_USAGE_TABLE = """
    CREATE TABLE IF NOT EXISTS org_daily_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id TEXT NOT NULL,
        usage_date DATE NOT NULL,
        api_calls_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(org_id, usage_date)
    );
    """

    CREATE_ORG_BYOK_TABLE = """
    CREATE TABLE IF NOT EXISTS organization_byok_credentials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id TEXT NOT NULL,
        provider TEXT NOT NULL,
        key_ref TEXT NOT NULL,
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    CREATE_INDEXES = """
    CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);
    CREATE INDEX IF NOT EXISTS idx_daily_usage_user_id ON daily_usage_tracking(user_id);
    CREATE INDEX IF NOT EXISTS idx_daily_usage_date ON daily_usage_tracking(usage_date);
    CREATE INDEX IF NOT EXISTS idx_tier_audit_user_id ON tier_audit_log(user_id);
    CREATE INDEX IF NOT EXISTS idx_org_members_user ON organization_members(user_id);
    CREATE INDEX IF NOT EXISTS idx_org_members_org ON organization_members(org_id);
    CREATE INDEX IF NOT EXISTS idx_org_usage_org ON org_daily_usage(org_id);
    CREATE INDEX IF NOT EXISTS idx_org_usage_date ON org_daily_usage(usage_date);
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

            # Lightweight org model tables
            cursor.execute(MembershipTierSchema.CREATE_ORGANIZATIONS_TABLE)
            print("✅ Created organizations table")

            cursor.execute(MembershipTierSchema.CREATE_ORG_MEMBERS_TABLE)
            print("✅ Created organization_members table")

            cursor.execute(MembershipTierSchema.CREATE_ORG_DAILY_USAGE_TABLE)
            print("✅ Created org_daily_usage table")

            cursor.execute(MembershipTierSchema.CREATE_ORG_BYOK_TABLE)
            print("✅ Created organization_byok_credentials table")
            
            # Create indexes
            for index_sql in MembershipTierSchema.CREATE_INDEXES.split(';'):
                if index_sql.strip():
                    cursor.execute(index_sql)
            print("✅ Created indexes")
            
            conn.commit()

            # Ensure new columns exist on membership_tiers (idempotent migrations)
            cursor.execute("PRAGMA table_info(membership_tiers)")
            existing_cols = {row[1] for row in cursor.fetchall()}
            migrations = {
                'agent_roles_limit': "ALTER TABLE membership_tiers ADD COLUMN agent_roles_limit INTEGER DEFAULT 0",
                'models_unrestricted': "ALTER TABLE membership_tiers ADD COLUMN models_unrestricted BOOLEAN DEFAULT 1",
                'byok_slots_per_seat': "ALTER TABLE membership_tiers ADD COLUMN byok_slots_per_seat INTEGER DEFAULT 0",
                'org_byok_base': "ALTER TABLE membership_tiers ADD COLUMN org_byok_base INTEGER DEFAULT 0",
                'org_byok_per_seat': "ALTER TABLE membership_tiers ADD COLUMN org_byok_per_seat INTEGER DEFAULT 0",
                'org_pooled_api_calls_per_seat': "ALTER TABLE membership_tiers ADD COLUMN org_pooled_api_calls_per_seat INTEGER DEFAULT 0",
            }
            for col, stmt in migrations.items():
                if col not in existing_cols:
                    try:
                        cursor.execute(stmt)
                    except Exception:
                        pass
            conn.commit()
            conn.close()
            
            print("\n✅ All membership tier tables created successfully")
            print(f"   Database: {db_path}\n")
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            raise


# Tier configurations — Dev lineup aligned with proposal
TIER_CONFIGS = [
    {
        'tier_id': 'free',
        'name': 'DEV_FREE',
        'price': 0,
        'daily_call_limit': 75,
        'daily_llm_requests': 40,
        'concurrent_sessions': 1,
        'storage_gb': 0.5,
        'agent_roles_limit': 2,
        'models_unrestricted': True,
        'code_execution': False,
        'data_persistence': True,
        'webhooks': False,
        'api_keys_limit': 1,
        'byok_slots_per_seat': 2,
        'org_byok_base': 0,
        'org_byok_per_seat': 0,
        'org_pooled_api_calls_per_seat': 0,
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
        'name': 'DEV_PRO',
        'price': 29,
        'daily_call_limit': 800,
        'daily_llm_requests': 300,
        'concurrent_sessions': 2,
        'storage_gb': 5,
        'agent_roles_limit': 3,
        'models_unrestricted': True,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 3,
        'byok_slots_per_seat': 3,
        'org_byok_base': 0,
        'org_byok_per_seat': 0,
        'org_pooled_api_calls_per_seat': 0,
        'debug_logs_retention_days': 30,
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
        'support_tier': 'Email',
        'support_response_hours': 48
    },
    {
        'tier_id': 'pro_plus',
        'name': 'DEV_PRO_PLUS',
        'price': 49,
        'daily_call_limit': 1200,
        'daily_llm_requests': 450,
        'concurrent_sessions': 3,
        'storage_gb': 15,
        'agent_roles_limit': 5,
        'models_unrestricted': True,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 5,
        'byok_slots_per_seat': 5,
        'org_byok_base': 0,
        'org_byok_per_seat': 0,
        'org_pooled_api_calls_per_seat': 0,
        'debug_logs_retention_days': 60,
        'custom_llms': True,
        'team_members': 1,
        'role_based_access': False,
        'shared_workspaces': False,
        'audit_logs': False,
        'resource_quotas': False,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': False,
        'data_residency': False,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': False,
        'support_tier': 'Priority-lite',
        'support_response_hours': 36
    },
    {
        'tier_id': 'teams',
        'name': 'DEV_TEAMS',
        'price': 39,
        'daily_call_limit': 1600,
        'daily_llm_requests': 600,
        'concurrent_sessions': 3,
        'storage_gb': 10,
        'agent_roles_limit': 5,
        'models_unrestricted': True,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 0,
        'byok_slots_per_seat': 0,
        'org_byok_base': 12,
        'org_byok_per_seat': 2,
        'org_pooled_api_calls_per_seat': 400,
        'debug_logs_retention_days': 90,
        'custom_llms': True,
        'team_members': 3,
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
        'support_tier': 'Priority',
        'support_response_hours': 24
    },
    {
        'tier_id': 'enterprise',
        'name': 'DEV_ENTERPRISE',
        'price': 79,
        'daily_call_limit': 3500,
        'daily_llm_requests': 1400,
        'concurrent_sessions': 6,
        'storage_gb': 50,
        'agent_roles_limit': 5,
        'models_unrestricted': True,
        'code_execution': True,
        'data_persistence': True,
        'webhooks': True,
        'api_keys_limit': 0,
        'byok_slots_per_seat': 0,
        'org_byok_base': 24,
        'org_byok_per_seat': 3,
        'org_pooled_api_calls_per_seat': 1750,
        'debug_logs_retention_days': 365,
        'custom_llms': True,
        'team_members': 10,
        'role_based_access': True,
        'shared_workspaces': True,
        'audit_logs': True,
        'resource_quotas': True,
        'hipaa_ready': False,
        'soc2_certified': False,
        'sso_saml': True,
        'data_residency': True,
        'custom_integrations': True,
        'on_premise_deploy': False,
        'account_manager': True,
        'support_tier': 'Priority+',
        'support_response_hours': 8
    }
]
