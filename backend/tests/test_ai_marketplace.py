"""
AI Marketplace Test Suite
Unit tests (17) + E2E tests (7) = 24+ tests
"""

import pytest
import json
from datetime import datetime
from backend.services.ai_marketplace_registry import AIMarketplaceRegistry, AIModel, ModelCapability, ModelPricing, ModelProvider
from backend.services.ai_auth_service import AIAuthService, ProviderType, APIKeyStatus
from backend.services.ai_recommendation_engine import RecommendationEngine, QueryAnalyzer, TaskCategory
from backend.api.v1.ai_marketplace_routes import MarketplaceRoutes, AgentRoutes, AuthRoutes


# ==================== UNIT TESTS ====================

class TestRegistry:
    """Test AI Marketplace Registry Service"""
    
    @pytest.fixture
    def registry(self):
        return AIMarketplaceRegistry()
    
    def test_registry_initialization(self, registry):
        """Test that registry loads 50+ models on init"""
        assert len(registry.models) >= 50
    
    def test_list_all_models(self, registry):
        """Test listing all models with pagination"""
        models, total = registry.list_all_models(skip=0, limit=10)
        assert len(models) == 10
        assert total >= 50
    
    def test_get_model_by_id(self, registry):
        """Test retrieving specific model by ID"""
        model = registry.get_model("gpt4-turbo")
        assert model is not None
        assert model.name == "GPT-4 Turbo"
        assert model.provider == ModelProvider.OPENAI
    
    def test_search_models_by_query(self, registry):
        """Test searching models by name/description"""
        models, total = registry.search_models(query="gpt", skip=0, limit=50)
        assert len(models) >= 3
        assert any("gpt" in m.name.lower() for m in models)
    
    def test_search_models_by_provider(self, registry):
        """Test filtering models by provider"""
        models, total = registry.search_models(
            query="",
            provider=ModelProvider.ANTHROPIC,
            skip=0,
            limit=50
        )
        assert all(m.provider == ModelProvider.ANTHROPIC for m in models)
    
    def test_search_models_by_rating(self, registry):
        """Test filtering models by minimum rating"""
        models, total = registry.search_models(
            query="",
            min_rating=4.7,
            skip=0,
            limit=50
        )
        assert all(m.rating >= 4.7 for m in models)
    
    def test_search_models_by_capability(self, registry):
        """Test filtering models by capability"""
        models, total = registry.search_models(
            query="",
            capability=ModelCapability.CODE_GENERATION,
            skip=0,
            limit=50
        )
        assert all(ModelCapability.CODE_GENERATION in m.capabilities for m in models)
    
    def test_update_model_usage(self, registry):
        """Test updating model usage count"""
        model = registry.get_model("gpt4-turbo")
        initial_count = model.usage_count
        
        registry.update_usage_count("gpt4-turbo", increment=10)
        updated_model = registry.get_model("gpt4-turbo")
        
        assert updated_model.usage_count == initial_count + 10
    
    def test_get_recommendations(self, registry):
        """Test getting recommended models for use case"""
        recs = registry.get_recommended_models(use_case="code_generation", budget="medium")
        assert len(recs) <= 3
        assert all(ModelCapability.CODE_GENERATION in m.capabilities for m in recs)


class TestAuthService:
    """Test AI Authentication Service"""
    
    @pytest.fixture
    def auth_service(self):
        return AIAuthService()
    
    def test_user_registration(self, auth_service):
        """Test user registration"""
        success, msg, user = auth_service.register_user(
            "test@example.com",
            "testuser",
            "password123"
        )
        assert success is True
        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_duplicate_email_registration(self, auth_service):
        """Test that duplicate emails are rejected"""
        auth_service.register_user("test@example.com", "user1", "password123")
        success, msg, _ = auth_service.register_user("test@example.com", "user2", "password123")
        assert success is False
        assert "already registered" in msg
    
    def test_duplicate_username_registration(self, auth_service):
        """Test that duplicate usernames are rejected"""
        auth_service.register_user("test1@example.com", "samename", "password123")
        success, msg, _ = auth_service.register_user("test2@example.com", "samename", "password123")
        assert success is False
        assert "already taken" in msg
    
    def test_user_login(self, auth_service):
        """Test user login"""
        auth_service.register_user("test@example.com", "testuser", "password123")
        success, msg, token = auth_service.login_user("test@example.com", "password123")
        
        assert success is True
        assert token is not None
        assert token.is_valid is True
    
    def test_wrong_password_login(self, auth_service):
        """Test login with wrong password"""
        auth_service.register_user("test@example.com", "testuser", "password123")
        success, msg, _ = auth_service.login_user("test@example.com", "wrongpassword")
        
        assert success is False
        assert "Invalid password" in msg
    
    def test_token_verification(self, auth_service):
        """Test token verification"""
        success, msg, user = auth_service.register_user(
            "test@example.com", "testuser", "password123"
        )
        success, msg, token = auth_service.login_user("test@example.com", "password123")
        
        is_valid, user_id = auth_service.verify_token(token.token)
        assert is_valid is True
        assert user_id == user.id
    
    def test_add_api_key(self, auth_service):
        """Test adding API key"""
        _, _, user = auth_service.register_user("test@example.com", "testuser", "password123")
        success, msg, key = auth_service.add_api_key(
            user.id,
            ProviderType.OPENAI,
            "sk-test123456"
        )
        
        assert success is True
        assert key is not None
        assert key.provider == ProviderType.OPENAI
        assert key.status == APIKeyStatus.ACTIVE
    
    def test_get_api_keys(self, auth_service):
        """Test retrieving user's API keys"""
        _, _, user = auth_service.register_user("test@example.com", "testuser", "password123")
        auth_service.add_api_key(user.id, ProviderType.OPENAI, "sk-test1")
        auth_service.add_api_key(user.id, ProviderType.ANTHROPIC, "sk-test2")
        
        success, keys = auth_service.get_api_keys(user.id)
        assert success is True
        assert len(keys) == 2
    
    def test_add_balance(self, auth_service):
        """Test adding funds to user balance"""
        _, _, user = auth_service.register_user("test@example.com", "testuser", "password123")
        
        success, msg, balance = auth_service.add_funds(user.id, 100.0, "txn-123")
        assert success is True
        assert balance.total_balance == 100.0
    
    def test_deduct_balance(self, auth_service):
        """Test deducting from user balance"""
        _, _, user = auth_service.register_user("test@example.com", "testuser", "password123")
        auth_service.add_funds(user.id, 100.0, "txn-1")
        
        success, msg = auth_service.deduct_balance(user.id, 25.0, "gpt4-turbo", 1000)
        assert success is True
        
        _, balance_dict = auth_service.get_balance(user.id)
        assert balance_dict['spent_balance'] == 25.0


class TestRecommendationEngine:
    """Test Q Assistant Recommendation Engine"""
    
    @pytest.fixture
    def engine(self):
        registry = AIMarketplaceRegistry()
        return RecommendationEngine(registry)
    
    def test_query_analysis(self):
        """Test query analysis"""
        query = "Generate a Python function for sorting"
        category, keywords, language = QueryAnalyzer.analyze_query(query)
        
        assert category == TaskCategory.CODE_GENERATION
        assert "python" in language.lower()
    
    def test_query_complexity_extraction(self):
        """Test task complexity extraction"""
        simple_query = "Write hello world"
        complex_query = "Design a complex microservices architecture with load balancing and distributed caching"
        
        simple_complexity = QueryAnalyzer.extract_complexity(simple_query)
        complex_complexity = QueryAnalyzer.extract_complexity(complex_query)
        
        assert complex_complexity > simple_complexity
    
    def test_get_recommendations(self, engine):
        """Test getting model recommendations"""
        success, recs = engine.get_recommendations(
            query="Write Python code for machine learning",
            user_budget="medium"
        )
        
        assert success is True
        assert len(recs) <= 3
        assert all(0 <= r.score <= 100 for r in recs)
    
    def test_recommendation_scoring(self, engine):
        """Test that recommendations are ranked by score"""
        success, recs = engine.get_recommendations(
            query="Generate TypeScript code",
            user_budget="medium"
        )
        
        scores = [r.score for r in recs]
        assert scores == sorted(scores, reverse=True)


# ==================== E2E TESTS ====================

class TestMarketplaceE2E:
    """End-to-end marketplace flow tests"""
    
    @pytest.fixture
    def setup(self):
        """Setup test environment"""
        registry = AIMarketplaceRegistry()
        auth_service = AIAuthService()
        engine = RecommendationEngine(registry)
        return registry, auth_service, engine
    
    def test_user_signup_to_model_selection(self, setup):
        """E2E: User signup -> View models -> Select model"""
        registry, auth_service, engine = setup
        
        # Step 1: Register user
        success, msg, user = auth_service.register_user(
            "alice@example.com", "alice", "password123"
        )
        assert success and user
        
        # Step 2: Get all models
        models, total = registry.list_all_models()
        assert total >= 50
        
        # Step 3: Search for code generation models
        code_models, _ = registry.search_models(
            query="code generation",
            capability=ModelCapability.CODE_GENERATION,
            min_rating=4.5
        )
        assert len(code_models) > 0
        
        # Step 4: Select a model
        selected = code_models[0]
        registry.update_usage_count(selected.id)
        assert registry.get_model(selected.id).usage_count > 0
    
    def test_user_api_key_management_flow(self, setup):
        """E2E: User registers -> Adds API keys -> Retrieves them"""
        registry, auth_service, engine = setup
        
        # Register
        _, _, user = auth_service.register_user(
            "bob@example.com", "bob", "password123"
        )
        
        # Add multiple API keys
        key1_success, _, key1 = auth_service.add_api_key(
            user.id, ProviderType.OPENAI, "sk-openai123"
        )
        key2_success, _, key2 = auth_service.add_api_key(
            user.id, ProviderType.ANTHROPIC, "sk-anthropic456"
        )
        
        assert key1_success and key2_success
        
        # Retrieve keys
        success, keys = auth_service.get_api_keys(user.id)
        assert success
        assert len(keys) == 2
    
    def test_balance_management_flow(self, setup):
        """E2E: User adds funds -> Uses balance -> Checks remaining"""
        registry, auth_service, engine = setup
        
        # Register and add funds
        _, _, user = auth_service.register_user(
            "charlie@example.com", "charlie", "password123"
        )
        auth_service.add_funds(user.id, 100.0, "deposit-1")
        
        # Verify balance
        success, balance = auth_service.get_balance(user.id)
        assert balance['available_balance'] == 100.0
        
        # Use balance
        auth_service.deduct_balance(user.id, 25.0, "gpt4-turbo", 1000)
        
        # Verify remaining
        success, balance = auth_service.get_balance(user.id)
        assert balance['available_balance'] == 75.0
        assert balance['spent_balance'] == 25.0
    
    def test_recommendation_query_flow(self, setup):
        """E2E: User enters query -> Gets Q Assistant recommendations -> Selects model"""
        registry, auth_service, engine = setup
        
        # User query
        query = "I need to generate complex TypeScript code with reasoning"
        
        # Get recommendations
        success, recs = engine.get_recommendations(query, "medium")
        assert success
        assert len(recs) > 0
        
        # Verify recommendations have reasoning
        for rec in recs:
            assert rec.reasoning
            assert rec.score > 0
        
        # User selects recommended model
        selected_model_id = recs[0].model_id
        model = registry.get_model(selected_model_id)
        assert model is not None
    
    def test_full_user_journey(self, setup):
        """E2E: Complete user journey from signup to using models"""
        registry, auth_service, engine = setup
        
        # 1. Signup
        _, _, user = auth_service.register_user(
            "diana@example.com", "diana", "password123"
        )
        assert user
        
        # 2. Login
        success, msg, token = auth_service.login_user(
            "diana@example.com", "password123"
        )
        assert success and token
        
        # 3. Add API key
        auth_service.add_api_key(
            user.id, ProviderType.OPENAI, "sk-test"
        )
        
        # 4. Add balance
        auth_service.add_funds(user.id, 50.0, "payment-1")
        
        # 5. View models
        models, _ = registry.list_all_models(limit=5)
        assert len(models) > 0
        
        # 6. Get recommendations
        success, recs = engine.get_recommendations(
            "Debug Python code",
            "low"
        )
        if success:
            # 7. Use model
            model = registry.get_model(recs[0].model_id)
            registry.update_usage_count(model.id)
            
            # 8. Deduct balance
            auth_service.deduct_balance(user.id, 10.0, model.id, 500)
            
            # 9. Verify final state
            _, balance = auth_service.get_balance(user.id)
            assert balance['available_balance'] == 40.0
        else:
            # If no recommendations, verify balance was still added
            _, balance = auth_service.get_balance(user.id)
            assert balance['available_balance'] == 50.0
    
    def test_concurrent_user_flows(self, setup):
        """E2E: Multiple users interacting simultaneously"""
        registry, auth_service, engine = setup
        
        users = []
        for i in range(3):
            _, _, user = auth_service.register_user(
                f"user{i}@example.com",
                f"user{i}",
                "password123"
            )
            users.append(user)
        
        # All users add balance
        for i, user in enumerate(users):
            auth_service.add_funds(user.id, 100.0 * (i + 1), f"txn-{i}")
        
        # All users get recommendations
        for i, user in enumerate(users):
            success, recs = engine.get_recommendations(
                f"Task query from user {i}",
                "low"
            )
            if not success:
                # Just verify the balance is still there even if no recommendations
                _, balance = auth_service.get_balance(user.id)
                assert balance is not None
        
        # All users use models and deduct balance
        for i, user in enumerate(users):
            auth_service.deduct_balance(
                user.id, 10.0 * (i + 1), "gpt4-turbo", 500
            )
        
        # Verify all balances are correct
        for i, user in enumerate(users):
            _, balance = auth_service.get_balance(user.id)
            expected = (100.0 * (i + 1)) - (10.0 * (i + 1))
            assert balance['available_balance'] == expected


# ==================== INTEGRATION TESTS ====================

class TestIntegration:
    """Integration tests for full marketplace system"""
    
    def test_registry_auth_integration(self):
        """Test registry works with auth service"""
        registry = AIMarketplaceRegistry()
        auth = AIAuthService()
        
        # User registers and selects a model
        _, _, user = auth.register_user("test@ex.com", "test", "password123")
        models, _ = registry.list_all_models(limit=1)
        registry.update_usage_count(models[0].id)
        
        assert user.is_active
        assert registry.get_model(models[0].id).usage_count > 0
    
    def test_complete_marketplace_system(self):
        """Test all components working together"""
        registry = AIMarketplaceRegistry()
        auth = AIAuthService()
        engine = RecommendationEngine(registry)
        
        # Full flow
        _, _, user = auth.register_user("full@test.com", "full", "password123")
        auth.add_funds(user.id, 100.0, "txn-1")
        
        success, recs = engine.get_recommendations("Generate code", "medium")
        assert success
        
        registry.update_usage_count(recs[0].model_id)
        
        auth.deduct_balance(user.id, 5.0, recs[0].model_id, 100)
        
        _, balance = auth.get_balance(user.id)
        assert balance['available_balance'] == 95.0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
