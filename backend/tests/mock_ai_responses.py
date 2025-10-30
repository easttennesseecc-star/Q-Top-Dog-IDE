"""
Mock AI Responses for Testing

Simulates AI responses from each role to enable end-to-end testing
without requiring actual LLM API calls.
"""

from enum import Enum
from typing import Dict, Any


class MockAIRole(Enum):
    """Mock AI roles"""
    Q_ASSISTANT = "q_assistant"
    CODE_WRITER = "code_writer"
    TEST_AUDITOR = "test_auditor"
    VERIFICATION_OVERSEER = "verification_overseer"
    RELEASE_MANAGER = "release_manager"


class MockAIResponses:
    """Stores and retrieves mock AI responses"""

    # Q ASSISTANT RESPONSES
    DISCOVERY_RESPONSE = {
        "role": "Q_ASSISTANT",
        "phase": "DISCOVERY",
        "content": """# Requirements Analysis

## Project: Test Feature
### Build ID: build-123

## Discovered Requirements

1. **Authentication**
   - OAuth2 support
   - JWT token management
   - Rate limiting (100 req/min)

2. **API Endpoints**
   - GET /api/features (list)
   - POST /api/features (create)
   - PUT /api/features/{id} (update)
   - DELETE /api/features/{id} (delete)

3. **Database Schema**
   - Features table with columns: id, name, description, created_at, updated_at
   - User permissions table: user_id, feature_id, permission_type

4. **Performance Requirements**
   - API response time < 200ms
   - Support 1000 concurrent users
   - 99.9% uptime SLA

## Next Steps
Ready for planning phase.
""",
        "structured_data": {
            "requirements": [
                "OAuth2 authentication",
                "JWT token support",
                "Rate limiting",
                "RESTful API",
                "User permissions",
                "Database persistence",
                "Performance monitoring"
            ],
            "api_endpoints": [
                {"method": "GET", "path": "/api/features"},
                {"method": "POST", "path": "/api/features"},
                {"method": "PUT", "path": "/api/features/{id}"},
                {"method": "DELETE", "path": "/api/features/{id}"}
            ],
            "database_tables": ["features", "user_permissions"],
            "performance_targets": {
                "response_time_ms": 200,
                "concurrent_users": 1000,
                "uptime_percent": 99.9
            }
        }
    }

    PLANNING_RESPONSE = {
        "role": "Q_ASSISTANT",
        "phase": "PLANNING",
        "content": """# Implementation Plan

## Architecture Overview

### Tech Stack
- Backend: Python/FastAPI
- Database: PostgreSQL
- Authentication: JWT with OAuth2
- Caching: Redis (for rate limiting)

### Component Breakdown

1. **Authentication Module**
   - OAuth2 provider integration
   - JWT token generation/validation
   - Rate limiter middleware

2. **API Layer**
   - FastAPI routes for CRUD operations
   - Request validation with Pydantic
   - Error handling and logging

3. **Database Layer**
   - SQLAlchemy ORM models
   - Migration scripts
   - Query optimization

4. **Testing**
   - Unit tests (70% coverage minimum)
   - Integration tests for API
   - End-to-end workflow tests

## Implementation Timeline
1. Database setup: 1-2 hours
2. Authentication: 2-3 hours
3. API endpoints: 2-3 hours
4. Testing: 2-3 hours
5. Deployment: 1-2 hours

## Risk Mitigation
- Database backups before each migration
- Feature flag for new endpoints
- Staged rollout to 10% → 50% → 100% users

## Success Criteria
- All tests passing
- API response times < 200ms
- 99.9% uptime in staging
- Code review approval from 2+ reviewers
""",
        "structured_data": {
            "tech_stack": {
                "backend": "Python/FastAPI",
                "database": "PostgreSQL",
                "authentication": "OAuth2/JWT",
                "caching": "Redis"
            },
            "components": [
                "Authentication",
                "API Layer",
                "Database Layer",
                "Testing",
                "Deployment"
            ],
            "timeline_hours": 11,
            "success_criteria": [
                "All tests passing",
                "Response time < 200ms",
                "99.9% uptime",
                "Code review approved"
            ]
        }
    }

    # CODE WRITER RESPONSES
    IMPLEMENTATION_RESPONSE = {
        "role": "CODE_WRITER",
        "phase": "IMPLEMENTATION",
        "content": """# Implementation Complete

## Files Created

### Backend Code
- `backend/models/feature.py` (127 lines) - SQLAlchemy model
- `backend/routes/features.py` (245 lines) - FastAPI endpoints
- `backend/services/feature_service.py` (189 lines) - Business logic
- `backend/auth/oauth.py` (156 lines) - OAuth2 integration
- `backend/auth/jwt_handler.py` (98 lines) - JWT management

### Database
- `migrations/001_create_features_table.sql` (42 lines)
- `migrations/002_create_permissions_table.sql` (38 lines)

### Configuration
- `config/oauth_config.py` (34 lines)
- `.env.example` (12 variables)

## Code Quality
- Type hints: 100% coverage
- Docstrings: All functions documented
- Error handling: Comprehensive try/catch blocks
- Logging: All operations logged

## Statistics
- Total lines of code: 941 lines
- Functions implemented: 24
- Classes: 5
- Code complexity: Low (all functions < 20 cyclomatic complexity)

## Testing
- All imports verified
- All syntax correct
- Ready for integration tests
""",
        "structured_data": {
            "files_created": 9,
            "lines_of_code": 941,
            "functions": 24,
            "classes": 5,
            "test_coverage_target": 80,
            "ready_for_testing": True
        }
    }

    # TEST AUDITOR RESPONSES
    TESTING_RESPONSE = {
        "role": "TEST_AUDITOR",
        "phase": "TESTING",
        "content": """# Testing Report

## Test Results: PASSED ✓

### Unit Tests: 24/24 PASSING
- Model tests: 8/8 passing
- Service tests: 10/10 passing
- Route tests: 6/6 passing

### Integration Tests: 15/15 PASSING
- OAuth2 flow: PASS
- JWT validation: PASS
- Database transactions: PASS
- Error handling: PASS
- Concurrent requests: PASS

### Performance Tests: ALL PASS
- Average response time: 145ms (target: <200ms) ✓
- P99 response time: 185ms ✓
- Throughput: 520 req/sec (target: >400) ✓
- 1000 concurrent users: Handled successfully ✓

### Code Coverage: 89%
- Statements: 89%
- Branches: 87%
- Functions: 91%
- Lines: 89%

## Issues Found: 0 CRITICAL, 0 HIGH, 2 MEDIUM

### Medium Issues (Non-blocking)
1. Add rate limit headers to response (INFO level)
2. Add cache headers for GET requests (OPTIMIZATION)

## Test Coverage by Module
- Models: 94%
- Routes: 88%
- Services: 91%
- Auth: 85%

## Recommendations
✓ Code is production-ready
✓ Performance meets requirements
✓ Security checks passed
✓ Recommend for verification phase
""",
        "structured_data": {
            "unit_tests": {"passed": 24, "failed": 0, "total": 24},
            "integration_tests": {"passed": 15, "failed": 0, "total": 15},
            "code_coverage": 89,
            "avg_response_time_ms": 145,
            "critical_issues": 0,
            "high_issues": 0,
            "status": "PASSED",
            "ready_for_verification": True
        }
    }

    # VERIFICATION OVERSEER RESPONSES
    VERIFICATION_RESPONSE = {
        "role": "VERIFICATION_OVERSEER",
        "phase": "VERIFICATION",
        "content": """# Production Readiness Verification

## Verification Checklist: PASSED ✓

### Code Quality Review
✓ All coding standards met
✓ No security vulnerabilities detected
✓ Error handling comprehensive
✓ Logging appropriate and detailed
✓ Documentation complete
✓ Type hints 100% coverage

### Performance Verification
✓ Response times acceptable (145ms avg vs 200ms target)
✓ Memory usage stable (no leaks detected)
✓ Database queries optimized
✓ Caching strategy effective
✓ Load testing passed (1000 concurrent users)

### Security Review
✓ OAuth2 implementation correct
✓ JWT tokens properly validated
✓ SQL injection prevention verified
✓ CORS properly configured
✓ Rate limiting functional
✓ No sensitive data in logs

### Operational Readiness
✓ Deployment automation ready
✓ Health check endpoints functional
✓ Monitoring configured
✓ Alerting configured
✓ Backup strategy verified
✓ Rollback procedure documented

### Compliance
✓ GDPR compliance verified
✓ Data privacy met
✓ Audit trail logged
✓ Access control verified

## Production Sign-Off: APPROVED ✓

### Deployment Window
- Recommended: Any time (low-risk deployment)
- Rollback time: ~5 minutes if needed
- Estimated deployment time: 15 minutes

### Post-Deployment Monitoring
- Monitor error rates for 24 hours
- Watch performance metrics
- Alert on anomalies
- Plan post-launch review meeting

## Sign-Off
✓ VERIFIED - READY FOR PRODUCTION DEPLOYMENT

Verified by: Verification Overseer AI
Date: 2025-10-29
Status: APPROVED FOR RELEASE
""",
        "structured_data": {
            "code_quality": "PASSED",
            "security": "PASSED",
            "performance": "PASSED",
            "operations": "PASSED",
            "compliance": "PASSED",
            "overall_status": "APPROVED",
            "risk_level": "LOW",
            "deployment_ready": True
        }
    }

    # RELEASE MANAGER RESPONSES
    DEPLOYMENT_RESPONSE = {
        "role": "RELEASE_MANAGER",
        "phase": "DEPLOYMENT",
        "content": """# Deployment Summary

## Deployment Complete: SUCCESS ✓

### Deployment Details
- Release Version: 1.0.0
- Deployment Time: 2025-10-29 14:30:00 UTC
- Duration: 12 minutes
- Status: SUCCESSFUL
- Rollback Required: NO

### Pre-Deployment Checks
✓ Backup created
✓ Health checks passed
✓ Database migrations completed
✓ Cache warmed
✓ Dependencies verified

### Deployment Steps Executed
1. ✓ Code deployed to production
2. ✓ Database migrations applied
3. ✓ Configuration updated
4. ✓ Services restarted
5. ✓ Health checks passed
6. ✓ Smoke tests passed
7. ✓ Monitoring enabled

### Post-Deployment Verification
✓ All endpoints responding
✓ Database connections healthy
✓ API rate limiting working
✓ Authentication functional
✓ Logging active
✓ Performance metrics nominal

### Release Notes
- New feature: OAuth2 authentication
- Improved: API performance optimization
- Fixed: Rate limit edge case
- Updated: Security policies

### Monitoring Status
- Error rate: 0.01% (expected: <0.1%) ✓
- Response time: 142ms avg (target: <200ms) ✓
- CPU usage: 35% (threshold: 80%) ✓
- Memory usage: 62% (threshold: 90%) ✓
- Database connections: 125/500 ✓

### Next Steps
- Monitor for 24 hours
- Plan feedback review in 48 hours
- Schedule optimization session
- Plan next feature release

## Deployment Status: LIVE IN PRODUCTION ✓

The feature is now live and available to all users.
Monitoring is active and alerting is configured.

Deployed by: Release Manager AI
Time: 2025-10-29 14:30 UTC
Status: OPERATIONAL
""",
        "structured_data": {
            "version": "1.0.0",
            "deployment_status": "SUCCESS",
            "duration_minutes": 12,
            "rollback_required": False,
            "health_check": "PASSED",
            "performance": {
                "avg_response_time_ms": 142,
                "error_rate_percent": 0.01,
                "cpu_percent": 35,
                "memory_percent": 62
            },
            "production_ready": True,
            "monitoring_active": True
        }
    }

    @staticmethod
    def get_mock_response(role: MockAIRole, phase: str) -> Dict[str, Any]:
        """Get mock response for a role and phase"""
        if role == MockAIRole.Q_ASSISTANT:
            if "discovery" in phase.lower():
                return MockAIResponses.DISCOVERY_RESPONSE
            elif "planning" in phase.lower():
                return MockAIResponses.PLANNING_RESPONSE

        elif role == MockAIRole.CODE_WRITER:
            if "implementation" in phase.lower() or "coding" in phase.lower():
                return MockAIResponses.IMPLEMENTATION_RESPONSE

        elif role == MockAIRole.TEST_AUDITOR:
            if "testing" in phase.lower():
                return MockAIResponses.TESTING_RESPONSE

        elif role == MockAIRole.VERIFICATION_OVERSEER:
            if "verification" in phase.lower():
                return MockAIResponses.VERIFICATION_RESPONSE

        elif role == MockAIRole.RELEASE_MANAGER:
            if "deployment" in phase.lower() or "release" in phase.lower():
                return MockAIResponses.DEPLOYMENT_RESPONSE

        # Default response
        return {
            "role": role.value,
            "phase": phase,
            "content": f"Processing {phase} phase...",
            "structured_data": {"status": "processing"}
        }

    @staticmethod
    def get_all_mock_responses() -> Dict[str, Dict[str, Any]]:
        """Get all mock responses"""
        return {
            "discovery": MockAIResponses.DISCOVERY_RESPONSE,
            "planning": MockAIResponses.PLANNING_RESPONSE,
            "implementation": MockAIResponses.IMPLEMENTATION_RESPONSE,
            "testing": MockAIResponses.TESTING_RESPONSE,
            "verification": MockAIResponses.VERIFICATION_RESPONSE,
            "deployment": MockAIResponses.DEPLOYMENT_RESPONSE,
        }
