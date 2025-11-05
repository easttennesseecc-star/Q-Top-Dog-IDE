-- ============================================
-- Q-IDE AI MARKETPLACE DATABASE SCHEMA
-- PostgreSQL 13+
-- ============================================

-- ============================================
-- 1. USERS TABLE
-- ============================================
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    profile_picture_url VARCHAR(500),
    preferences JSONB DEFAULT '{}',
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- 2. API KEYS TABLE (Encrypted)
-- ============================================
CREATE TABLE api_keys (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    key_encrypted VARCHAR(500) NOT NULL,
    key_hash VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    daily_limit INT,
    usage_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    revoked_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_provider (provider),
    INDEX idx_status (status),
    UNIQUE (user_id, provider)
);

-- ============================================
-- 3. USER BALANCE TABLE
-- ============================================
CREATE TABLE user_balance (
    user_id VARCHAR(36) PRIMARY KEY,
    total_balance DECIMAL(10, 2) DEFAULT 0.00,
    spent_balance DECIMAL(10, 2) DEFAULT 0.00,
    currency VARCHAR(3) DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 4. TRANSACTIONS TABLE
-- ============================================
CREATE TABLE transactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    model_id VARCHAR(100),
    tokens_used INT,
    description VARCHAR(255),
    status VARCHAR(20) DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user_balance(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_type (transaction_type)
);

-- ============================================
-- 5. CHAT HISTORY TABLE
-- ============================================
CREATE TABLE chat_history (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    session_id VARCHAR(36) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    message_role VARCHAR(20) NOT NULL,
    message_content TEXT NOT NULL,
    tokens_used INT,
    cost DECIMAL(10, 6),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_model_id (model_id),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- 6. CHAT SESSIONS TABLE
-- ============================================
CREATE TABLE chat_sessions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    title VARCHAR(255),
    model_id VARCHAR(100) NOT NULL,
    total_messages INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    total_cost DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN DEFAULT false,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at),
    INDEX idx_archived (archived)
);

-- ============================================
-- 7. MODEL RATINGS TABLE (For Q Assistant learning)
-- ============================================
CREATE TABLE model_ratings (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    rating DECIMAL(2, 1),
    feedback TEXT,
    use_case VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_model_id (model_id),
    UNIQUE (user_id, model_id)
);

-- ============================================
-- 8. MODEL USAGE STATS TABLE
-- ============================================
CREATE TABLE model_usage_stats (
    id VARCHAR(36) PRIMARY KEY,
    model_id VARCHAR(100) NOT NULL,
    total_uses INT DEFAULT 0,
    total_tokens INT DEFAULT 0,
    total_cost DECIMAL(12, 6) DEFAULT 0,
    avg_rating DECIMAL(2, 1),
    monthly_active_users INT DEFAULT 0,
    last_used TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (model_id),
    INDEX idx_model_id (model_id)
);

-- ============================================
-- 9. USER PREFERENCES TABLE
-- ============================================
CREATE TABLE user_preferences (
    user_id VARCHAR(36) PRIMARY KEY,
    preferred_model VARCHAR(100),
    preferred_providers VARCHAR(500),
    budget_limit DECIMAL(10, 2),
    notifications_enabled BOOLEAN DEFAULT true,
    auto_select_model BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ============================================
-- 10. AUDIT LOG TABLE
-- ============================================
CREATE TABLE audit_log (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(36),
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- 11. USER NOTES TABLE (Persistent user context & explanations)
-- ============================================
CREATE TABLE user_notes (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    workspace_id VARCHAR(255) NOT NULL,
    note_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    tags JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_workspace (user_id, workspace_id),
    INDEX idx_note_type (note_type),
    INDEX idx_created_at (created_at),
    INDEX idx_tags ((tags->>'$'))
);

-- ============================================
-- 12. BUILD MANIFESTS TABLE (QR code concept for project rules)
-- ============================================
CREATE TABLE build_manifests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    workspace_id VARCHAR(255) NOT NULL,
    project_name VARCHAR(255) NOT NULL,
    version VARCHAR(50) NOT NULL,
    qr_hash VARCHAR(64) NOT NULL,
    languages JSONB DEFAULT '[]',
    frameworks JSONB DEFAULT '[]',
    dependencies JSONB DEFAULT '{}',
    rules JSONB DEFAULT '[]',
    directory_structure JSONB DEFAULT '{}',
    required_files JSONB DEFAULT '[]',
    ignored_patterns JSONB DEFAULT '[]',
    build_commands JSONB DEFAULT '[]',
    test_commands JSONB DEFAULT '[]',
    deploy_commands JSONB DEFAULT '[]',
    naming_conventions JSONB DEFAULT '{}',
    code_style_config JSONB DEFAULT '{}',
    custom_metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_workspace (user_id, workspace_id),
    INDEX idx_qr_hash (qr_hash),
    INDEX idx_project_name (project_name),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Chat queries
CREATE INDEX idx_chat_user_session ON chat_history(user_id, session_id, created_at DESC);
CREATE INDEX idx_chat_model_user ON chat_history(model_id, user_id);

-- Transaction queries
CREATE INDEX idx_transaction_user_type ON transactions(user_id, transaction_type, created_at DESC);

-- Session queries  
CREATE INDEX idx_session_user_model ON chat_sessions(user_id, model_id, updated_at DESC);

-- API key queries
CREATE INDEX idx_api_key_user_status ON api_keys(user_id, status);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- User with balance info
CREATE VIEW user_with_balance AS
SELECT 
    u.id,
    u.email,
    u.username,
    u.is_active,
    u.created_at,
    COALESCE(ub.total_balance, 0) as total_balance,
    COALESCE(ub.spent_balance, 0) as spent_balance,
    COALESCE(ub.total_balance - ub.spent_balance, 0) as available_balance
FROM users u
LEFT JOIN user_balance ub ON u.id = ub.user_id;

-- Model popularity (for Q Assistant recommendations)
CREATE VIEW model_popularity AS
SELECT 
    model_id,
    total_uses,
    monthly_active_users,
    avg_rating,
    RANK() OVER (ORDER BY total_uses DESC) as popularity_rank
FROM model_usage_stats
ORDER BY total_uses DESC;

-- Recent user activity
CREATE VIEW recent_activity AS
SELECT 
    u.id,
    u.username,
    MAX(CASE WHEN cs.updated_at > u.last_login THEN cs.updated_at ELSE NULL END) as last_activity,
    COUNT(DISTINCT cs.id) as session_count
FROM users u
LEFT JOIN chat_sessions cs ON u.id = cs.user_id AND cs.created_at > NOW() - INTERVAL '30 days'
GROUP BY u.id, u.username;

-- ============================================
-- STORED PROCEDURES
-- ============================================

-- Deduct balance for model usage
CREATE FUNCTION deduct_user_balance(
    p_user_id VARCHAR(36),
    p_amount DECIMAL(10, 6),
    p_model_id VARCHAR(100),
    p_tokens INT,
    p_description VARCHAR(255)
)
RETURNS BOOLEAN
LANGUAGE PLPGSQL
AS $$
BEGIN
    -- Check balance exists and is sufficient
    IF NOT EXISTS (SELECT 1 FROM user_balance WHERE user_id = p_user_id AND spent_balance + p_amount <= total_balance) THEN
        RETURN FALSE;
    END IF;
    
    -- Deduct from balance
    UPDATE user_balance 
    SET spent_balance = spent_balance + p_amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id;
    
    -- Log transaction
    INSERT INTO transactions (
        id, user_id, transaction_type, amount, model_id, 
        tokens_used, description, status
    ) VALUES (
        gen_random_uuid()::text, p_user_id, 'charge', p_amount, p_model_id,
        p_tokens, p_description, 'completed'
    );
    
    -- Update model stats
    UPDATE model_usage_stats
    SET total_cost = total_cost + p_amount,
        updated_at = CURRENT_TIMESTAMP
    WHERE model_id = p_model_id;
    
    RETURN TRUE;
END;
$$;

-- Add funds to user balance
CREATE FUNCTION add_user_funds(
    p_user_id VARCHAR(36),
    p_amount DECIMAL(10, 2),
    p_transaction_id VARCHAR(100)
)
RETURNS BOOLEAN
LANGUAGE PLPGSQL
AS $$
BEGIN
    -- Create or update balance
    INSERT INTO user_balance (user_id, total_balance, spent_balance)
    VALUES (p_user_id, p_amount, 0)
    ON CONFLICT (user_id) DO UPDATE
    SET total_balance = total_balance + p_amount,
        updated_at = CURRENT_TIMESTAMP;
    
    -- Log transaction
    INSERT INTO transactions (
        id, user_id, transaction_type, amount, description, status
    ) VALUES (
        gen_random_uuid()::text, p_user_id, 'deposit', p_amount, 
        'Payment: ' || p_transaction_id, 'completed'
    );
    
    RETURN TRUE;
END;
$$;

-- ============================================
-- GRANTS (Security)
-- ============================================

-- Application user (read/write to marketplace tables)
CREATE USER IF NOT EXISTS app_user WITH PASSWORD 'secure-password-here';
GRANT CONNECT ON DATABASE marketplace TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

-- Read-only user (for analytics)
CREATE USER IF NOT EXISTS analytics_user WITH PASSWORD 'secure-read-only-password';
GRANT CONNECT ON DATABASE marketplace TO analytics_user;
GRANT USAGE ON SCHEMA public TO analytics_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;
GRANT SELECT ON ALL VIEWS IN SCHEMA public TO analytics_user;

-- ============================================
-- INITIALIZATION DATA
-- ============================================

-- Create sample models entry (will be synced from registry)
-- This is populated by the backend when it starts up
INSERT INTO model_usage_stats (id, model_id, total_uses, monthly_active_users, avg_rating)
VALUES 
    ('m-001', 'gpt4-turbo', 0, 0, 4.9),
    ('m-002', 'claude-opus', 0, 0, 4.8),
    ('m-003', 'gemini-flash', 0, 0, 4.7)
ON CONFLICT (model_id) DO NOTHING;

