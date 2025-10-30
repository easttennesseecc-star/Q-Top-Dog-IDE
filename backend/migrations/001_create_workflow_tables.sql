-- Alembic migration script for workflow orchestration tables
-- Created for Q Assistant Orchestration system
-- Run: psql -U postgres -d topdog_ide -f migrations/001_create_workflow_tables.sql

-- Create build_workflows table
CREATE TABLE IF NOT EXISTS build_workflows (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    build_id VARCHAR(36) UNIQUE NOT NULL,
    project_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    
    -- Workflow state
    current_state VARCHAR(50) DEFAULT 'discovery' NOT NULL,
    
    -- Timing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    
    -- Phase outputs (JSON storage)
    discovery_phase JSONB,
    planning_phase JSONB,
    implementation_phase JSONB,
    testing_phase JSONB,
    verification_phase JSONB,
    deployment_phase JSONB,
    
    -- Additional metadata
    workflow_metadata JSONB
);

-- Create indexes for performance
CREATE INDEX idx_build_workflows_build_id ON build_workflows(build_id);
CREATE INDEX idx_build_workflows_project_id ON build_workflows(project_id);
CREATE INDEX idx_build_workflows_user_id ON build_workflows(user_id);
CREATE INDEX idx_build_workflows_current_state ON build_workflows(current_state);
CREATE INDEX idx_build_workflows_created_at ON build_workflows(created_at DESC);


-- Create workflow_handoffs table
CREATE TABLE IF NOT EXISTS workflow_handoffs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    workflow_id VARCHAR(36) NOT NULL REFERENCES build_workflows(id) ON DELETE CASCADE,
    
    -- Handoff details
    from_role VARCHAR(50) NOT NULL,
    to_role VARCHAR(50),
    from_state VARCHAR(50) NOT NULL,
    to_state VARCHAR(50) NOT NULL,
    
    -- Data transferred
    data_transferred JSONB,
    notes VARCHAR(500),
    
    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_workflow_handoffs_workflow_id ON workflow_handoffs(workflow_id);
CREATE INDEX idx_workflow_handoffs_from_role ON workflow_handoffs(from_role);
CREATE INDEX idx_workflow_handoffs_timestamp ON workflow_handoffs(timestamp DESC);


-- Create workflow_events table
CREATE TABLE IF NOT EXISTS workflow_events (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    workflow_id VARCHAR(36) NOT NULL REFERENCES build_workflows(id) ON DELETE CASCADE,
    
    -- Event details
    event_type VARCHAR(100) NOT NULL,
    triggered_by VARCHAR(100),
    event_data JSONB,
    
    -- Timing
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- Create indexes for performance
CREATE INDEX idx_workflow_events_workflow_id ON workflow_events(workflow_id);
CREATE INDEX idx_workflow_events_event_type ON workflow_events(event_type);
CREATE INDEX idx_workflow_events_timestamp ON workflow_events(timestamp DESC);


-- Add comments to tables for documentation
COMMENT ON TABLE build_workflows IS 'Tracks complete build workflows from discovery through deployment';
COMMENT ON TABLE workflow_handoffs IS 'Records handoffs between AI roles during workflow execution';
COMMENT ON TABLE workflow_events IS 'Audit trail of all workflow events';

COMMENT ON COLUMN build_workflows.current_state IS 'Current workflow state: discovery, planning, implementation, testing, verification, deployment, complete, error';
COMMENT ON COLUMN workflow_handoffs.from_role IS 'Role completing the work: q_assistant, code_writer, test_auditor, verification_overseer, release_manager';
COMMENT ON COLUMN workflow_handoffs.data_transferred IS 'JSON data passed from current role to next role';
