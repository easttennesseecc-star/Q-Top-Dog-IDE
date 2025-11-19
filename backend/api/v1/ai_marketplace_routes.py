"""
AI Marketplace REST & WebSocket API Endpoints
Marketplace routes for browsing models + Agent routes for chat
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== MARKETPLACE ROUTES ====================

class MarketplaceRoutes:
    """REST API routes for marketplace browsing"""
    
    def __init__(self, registry, auth_service, recommendation_engine):
        """Initialize with services"""
        self.registry = registry
        self.auth_service = auth_service
        self.recommendation_engine = recommendation_engine
        self.blueprint = Blueprint('marketplace', __name__, url_prefix='/api/v1/marketplace')
        self._register_routes()
    
    def _register_routes(self):
        """Register all marketplace routes"""
        
        @self.blueprint.route('/models', methods=['GET'])
        @cross_origin()
        def list_models():
            """GET /marketplace/models - List all available models"""
            try:
                skip = request.args.get('skip', 0, type=int)
                limit = request.args.get('limit', 50, type=int)
                
                models, total = self.registry.list_all_models(skip, limit)
                
                return jsonify({
                    'success': True,
                    'data': [m.to_dict() for m in models],
                    'pagination': {
                        'skip': skip,
                        'limit': limit,
                        'total': total
                    }
                }), 200
            except Exception as e:
                logger.error(f"Error listing models: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/models/<model_id>', methods=['GET'])
        @cross_origin()
        def get_model(model_id):
            """GET /marketplace/models/<id> - Get specific model details"""
            try:
                model = self.registry.get_model(model_id)
                
                if not model:
                    return jsonify({
                        'success': False,
                        'error': 'Model not found'
                    }), 404
                
                return jsonify({
                    'success': True,
                    'data': model.to_dict()
                }), 200
            except Exception as e:
                logger.error(f"Error getting model: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/models/search', methods=['POST'])
        @cross_origin()
        def search_models():
            """POST /marketplace/models/search - Search models"""
            try:
                data = request.get_json()
                query = data.get('query', '')
                provider = data.get('provider')
                min_rating = data.get('min_rating', 0.0)
                max_price = data.get('max_price')
                capability = data.get('capability')
                skip = data.get('skip', 0)
                limit = data.get('limit', 50)
                
                models, total = self.registry.search_models(
                    query=query,
                    provider=provider,
                    min_rating=min_rating,
                    capability=capability,
                    max_price=max_price,
                    skip=skip,
                    limit=limit
                )
                
                return jsonify({
                    'success': True,
                    'data': [m.to_dict() for m in models],
                    'pagination': {'skip': skip, 'limit': limit, 'total': total}
                }), 200
            except Exception as e:
                logger.error(f"Error searching models: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/recommendations', methods=['POST'])
        @cross_origin()
        def get_recommendations():
            """POST /marketplace/recommendations - Get AI-powered recommendations"""
            try:
                data = request.get_json()
                query = data.get('query', '')
                budget = data.get('budget', 'medium')
                
                # Verify user token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                
                if not is_valid:
                    return jsonify({
                        'success': False,
                        'error': 'Unauthorized'
                    }), 401
                
                # Get user preferences
                user = self.auth_service.get_user(user_id)
                preferences = user.preferences if user else {}
                
                # Get recommendations
                success, recommendations = self.recommendation_engine.get_recommendations(
                    query=query,
                    user_budget=budget,
                    user_preferences=preferences
                )
                
                if not success:
                    return jsonify({
                        'success': False,
                        'error': 'Could not generate recommendations'
                    }), 500
                
                return jsonify({
                    'success': True,
                    'data': [
                        {
                            'model_id': rec.model_id,
                            'model_name': rec.model_name,
                            'score': rec.score,
                            'reasoning': rec.reasoning,
                            'price_rank': rec.price_rank,
                            'quality_rank': rec.quality_rank
                        }
                        for rec in recommendations
                    ]
                }), 200
            except Exception as e:
                logger.error(f"Error getting recommendations: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/select-model', methods=['POST'])
        @cross_origin()
        def select_model():
            """POST /marketplace/select-model - User selects a model"""
            try:
                data = request.get_json()
                model_id = data.get('model_id')
                
                if not model_id:
                    return jsonify({
                        'success': False,
                        'error': 'Model ID required'
                    }), 400
                
                # Verify token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                
                # Update model usage
                self.registry.update_usage_count(model_id)
                
                return jsonify({
                    'success': True,
                    'message': f'Model {model_id} selected'
                }), 200
            except Exception as e:
                logger.error(f"Error selecting model: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/stats', methods=['GET'])
        @cross_origin()
        def get_marketplace_stats():
            """GET /marketplace/stats - Get marketplace statistics"""
            try:
                stats = self.registry.get_statistics()
                
                return jsonify({
                    'success': True,
                    'data': stats
                }), 200
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500


# ==================== AGENT ROUTES ====================

class AgentRoutes:
    """WebSocket + REST routes for agent chat interaction"""
    
    def __init__(self, auth_service, router, registry):
        """Initialize with services"""
        self.auth_service = auth_service
        self.router = router
        self.registry = registry
        self.blueprint = Blueprint('agent', __name__, url_prefix='/api/v1/agent')
        self.active_sessions: dict[str, dict] = {}
        self._register_routes()
    
    def _register_routes(self):
        """Register all agent routes"""
        
        @self.blueprint.route('/chat', methods=['POST'])
        @cross_origin()
        def send_chat_message():
            """POST /agent/chat - Send a chat message (non-streaming)"""
            try:
                data = request.get_json()
                model_id = data.get('model_id')
                messages = data.get('messages', [])
                
                if not model_id:
                    return jsonify({
                        'success': False,
                        'error': 'Model ID required'
                    }), 400
                
                # Verify token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                
                # Get model and check balance
                model = self.registry.get_model(model_id)
                if not model:
                    return jsonify({'success': False, 'error': 'Model not found'}), 404
                
                user = self.auth_service.get_user(user_id)
                if not user:
                    return jsonify({'success': False, 'error': 'User not found'}), 404
                
                # Estimate cost (simple heuristic)
                total_chars = sum(len(m.get('content', '')) for m in messages)
                estimated_tokens = max(1, total_chars // 4)
                input_cost = (estimated_tokens / 1000) * model.pricing.input_cost_per_1k_tokens

                founder_bypass = getattr(user, 'is_founder', False)
                if not founder_bypass and user.balance.available_balance < input_cost:
                    return jsonify({
                        'success': False,
                        'error': 'Insufficient balance',
                        'required': input_cost,
                        'available': user.balance.available_balance
                    }), 402

                # Simulated response; replace with router.send_message() in production
                response = "This is a simulated response. In production, call router.send_message()"
                output_tokens = 100
                total_cost = 0.0
                if not founder_bypass:
                    total_cost = input_cost + (output_tokens / 1000) * model.pricing.output_cost_per_1k_tokens
                    self.auth_service.deduct_balance(
                        user_id,
                        total_cost,
                        model_id,
                        estimated_tokens + output_tokens
                    )

                return jsonify({
                    'success': True,
                    'data': {
                        'response': response,
                        'tokens_used': estimated_tokens + output_tokens,
                        'cost': total_cost,
                        'remaining_balance': user.balance.available_balance if not founder_bypass else 'founder-unlimited',
                        'founder_bypass': founder_bypass
                    }
                }), 200
            except Exception as e:
                logger.error(f"Error sending chat message: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/chat/stream', methods=['POST'])
        @cross_origin()
        def stream_chat_message():
            """POST /agent/chat/stream - Stream chat response"""
            try:
                data = request.get_json()
                model_id = data.get('model_id')
                data.get('messages', [])
                
                if not model_id:
                    return jsonify({
                        'success': False,
                        'error': 'Model ID required'
                    }), 400
                
                # Verify token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                
                user = self.auth_service.get_user(user_id)
                founder_bypass = getattr(user, 'is_founder', False) if user else False
                # Streaming not implemented; founder bypass surfaced
                return jsonify({
                    'success': True,
                    'message': 'Streaming initialized. Use WebSocket for live streaming.',
                    'founder_bypass': founder_bypass
                }), 200
            except Exception as e:
                logger.error(f"Error streaming chat: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/history', methods=['GET'])
        @cross_origin()
        def get_chat_history():
            """GET /agent/history - Get user's chat history"""
            try:
                # Verify token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                
                # In production, retrieve from database
                return jsonify({
                    'success': True,
                    'data': []
                }), 200
            except Exception as e:
                logger.error(f"Error getting history: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/usage', methods=['GET'])
        @cross_origin()
        def get_usage_stats():
            """GET /agent/usage - Get user's usage statistics"""
            try:
                # Verify token
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                
                user = self.auth_service.get_user(user_id)
                if not user:
                    return jsonify({'success': False, 'error': 'User not found'}), 404
                
                # Calculate stats from transactions
                total_spent = user.balance.spent_balance
                transaction_count = len(user.balance.transactions)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'total_spent': total_spent,
                        'transaction_count': transaction_count,
                        'current_balance': user.balance.available_balance,
                        'total_balance': user.balance.total_balance
                    }
                }), 200
            except Exception as e:
                logger.error(f"Error getting usage: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500


# ==================== AUTH ROUTES ====================

class AuthRoutes:
    """Authentication endpoints"""
    
    def __init__(self, auth_service):
        """Initialize with auth service"""
        self.auth_service = auth_service
        self.blueprint = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
        self._register_routes()
    
    def _register_routes(self):
        """Register auth routes"""
        
        @self.blueprint.route('/register', methods=['POST'])
        @cross_origin()
        def register():
            """POST /auth/register - Register new user"""
            try:
                data = request.get_json()
                email = data.get('email')
                username = data.get('username')
                password = data.get('password')
                
                if not all([email, username, password]):
                    return jsonify({
                        'success': False,
                        'error': 'Email, username, and password required'
                    }), 400
                
                success, message, user = self.auth_service.register_user(
                    email, username, password
                )
                
                if not success:
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 400
                
                return jsonify({
                    'success': True,
                    'data': user.to_dict_safe()
                }), 201
            except Exception as e:
                logger.error(f"Error registering: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/login', methods=['POST'])
        @cross_origin()
        def login():
            """POST /auth/login - Login user"""
            try:
                data = request.get_json()
                email = data.get('email')
                password = data.get('password')
                
                if not all([email, password]):
                    return jsonify({
                        'success': False,
                        'error': 'Email and password required'
                    }), 400
                
                success, message, token = self.auth_service.login_user(email, password)
                
                if not success:
                    return jsonify({
                        'success': False,
                        'error': message
                    }), 401
                
                return jsonify({
                    'success': True,
                    'data': token.to_dict()
                }), 200
            except Exception as e:
                logger.error(f"Error logging in: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/credentials/add', methods=['POST'])
        @cross_origin()
        def add_credentials():
            """POST /auth/credentials/add?user_id= - Add an API credential for a provider
            Frontend compatibility endpoint (UnifiedSignInHub)
            Body: { service: string, api_key: string, is_active?: bool }
            """
            try:
                user_id = request.args.get('user_id')
                if not user_id:
                    return jsonify({'success': False, 'error': 'user_id required'}), 400
                data = request.get_json() or {}
                service = data.get('service')
                api_key = data.get('api_key')
                if not service or not api_key:
                    return jsonify({'success': False, 'error': 'service and api_key required'}), 400
                # Map service string to ProviderType
                from backend.services.ai_auth_service import ProviderType  # local import to avoid circular at module load
                mapping = {
                    'openai': ProviderType.OPENAI,
                    'anthropic': ProviderType.ANTHROPIC,
                    'google_gemini': ProviderType.GOOGLE_GEMINI,
                    'google': ProviderType.GOOGLE_OAUTH,
                    'github': ProviderType.GITHUB,
                    'github_copilot': ProviderType.GITHUB_COPILOT,
                    'huggingface': ProviderType.HUGGINGFACE,
                    'cohere': ProviderType.COHERE,
                }
                provider = mapping.get(service)
                if not provider:
                    return jsonify({'success': False, 'error': f'Unsupported provider: {service}'}), 400
                success, message, key_obj = self.auth_service.add_api_key(user_id, provider, api_key, daily_limit=None)
                if not success:
                    return jsonify({'success': False, 'error': message}), 400
                return jsonify({'success': True, 'data': key_obj.to_dict_safe()}), 200
            except Exception as e:
                logger.error(f"Error /auth/credentials/add: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/me', methods=['GET'])
        @cross_origin()
        def me():
            """GET /auth/me - Return current user profile (safe)"""
            try:
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                user = self.auth_service.get_user(user_id)
                if not user:
                    return jsonify({'success': False, 'error': 'User not found'}), 404
                # Derive connected providers from existing API keys (OAuth and others)
                try:
                    connected = sorted({k.provider.value for k in user.api_keys.values() if k.status.value == 'active'})
                except Exception:
                    connected = []
                data = user.to_dict_safe()
                data['connected_providers'] = connected
                return jsonify({'success': True, 'data': data}), 200
            except Exception as e:
                logger.error(f"Error /auth/me: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/api-keys', methods=['GET'])
        @cross_origin()
        def list_api_keys():
            """GET /auth/api-keys - List active API keys (safe)"""
            try:
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                _ok, keys = self.auth_service.get_api_keys(user_id)
                return jsonify({'success': True, 'data': keys}), 200
            except Exception as e:
                logger.error(f"Error /auth/api-keys: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/credentials/revoke', methods=['POST'])
        @cross_origin()
        def revoke_api_key():
            """POST /auth/credentials/revoke - Revoke a specific API key by id"""
            try:
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                data = request.get_json() or {}
                key_id = data.get('key_id')
                if not key_id:
                    return jsonify({'success': False, 'error': 'key_id required'}), 400
                ok, msg = self.auth_service.remove_api_key(user_id, key_id)
                if not ok:
                    return jsonify({'success': False, 'error': msg}), 400
                return jsonify({'success': True, 'message': msg}), 200
            except Exception as e:
                logger.error(f"Error /auth/credentials/revoke: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/credentials/rotate', methods=['POST'])
        @cross_origin()
        def rotate_api_key():
            """POST /auth/credentials/rotate - Rotate a key by replacing with a new value for the same provider
            Body: { key_id: string, new_api_key: string }
            """
            try:
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                is_valid, user_id = self.auth_service.verify_token(token)
                if not is_valid:
                    return jsonify({'success': False, 'error': 'Unauthorized'}), 401
                data = request.get_json() or {}
                key_id = data.get('key_id')
                new_api_key = data.get('new_api_key')
                if not key_id or not new_api_key:
                    return jsonify({'success': False, 'error': 'key_id and new_api_key required'}), 400
                user = self.auth_service.get_user(user_id)
                if not user or key_id not in user.api_keys:
                    return jsonify({'success': False, 'error': 'API key not found'}), 404
                provider = user.api_keys[key_id].provider
                # Revoke old
                try:
                    from backend.services.ai_auth_service import APIKeyStatus
                    user.api_keys[key_id].status = APIKeyStatus.REVOKED
                except Exception:
                    user.api_keys[key_id].status = user.api_keys[key_id].status.__class__('revoked')
                # Add new
                ok, msg, new_key = self.auth_service.add_api_key(user_id, provider, new_api_key, daily_limit=None)
                if not ok:
                    return jsonify({'success': False, 'error': msg}), 400
                return jsonify({'success': True, 'data': new_key.to_dict_safe()}), 200
            except Exception as e:
                logger.error(f"Error /auth/credentials/rotate: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/grant-founder', methods=['POST'])
        @cross_origin()
        def grant_founder():
            """POST /auth/grant-founder - Admin route to grant founder status & paid access"""
            try:
                admin_token = request.headers.get('X-Admin-Key')
                expected = os.getenv('ADMIN_FOUNDER_GRANT_KEY')
                if not expected or admin_token != expected:
                    return jsonify({'success': False, 'error': 'Forbidden'}), 403
                data = request.get_json() or {}
                email = data.get('email')
                if not email:
                    return jsonify({'success': False, 'error': 'Email required'}), 400
                user = self.auth_service.get_user_by_email(email)
                if not user:
                    return jsonify({'success': False, 'error': 'User not found'}), 404
                user.is_founder = True
                user.paid = True
                # Optionally seed large balance
                if user.balance.total_balance < 1000:
                    user.balance.total_balance = 1000.0
                return jsonify({'success': True, 'data': user.to_dict_safe()}), 200
            except Exception as e:
                logger.error(f"Error /auth/grant-founder: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500

        @self.blueprint.route('/admin/set-password', methods=['POST'])
        @cross_origin()
        def admin_set_password():
            """POST /auth/admin/set-password - Admin: ensure user exists and set password (DEV ONLY)
            Headers: X-Admin-Key matches ADMIN_FOUNDER_GRANT_KEY
            Body: { email: string, password: string, ensure_founder?: bool }
            """
            try:
                admin_token = request.headers.get('X-Admin-Key')
                expected = os.getenv('ADMIN_FOUNDER_GRANT_KEY')
                if not expected or admin_token != expected:
                    return jsonify({'success': False, 'error': 'Forbidden'}), 403
                data = request.get_json() or {}
                email = (data.get('email') or '').strip().lower()
                password = data.get('password')
                ensure_founder = bool(data.get('ensure_founder'))
                if not email or not password:
                    return jsonify({'success': False, 'error': 'email and password required'}), 400
                user = self.auth_service.get_user_by_email(email)
                if not user:
                    # Create user bypassing min-length (hash directly)
                    username = email.split('@')[0]
                    from backend.services.ai_auth_service import PasswordHasher, User, UserBalance
                    uid = __import__('secrets').token_hex(8)
                    user = User(id=uid, email=email, username=username, password_hash=PasswordHasher.hash_password(password))
                    user.balance = UserBalance(user_id=uid)
                    self.auth_service.users[uid] = user
                    self.auth_service.email_index[email] = uid
                    self.auth_service.username_index[username] = uid
                else:
                    # Reset password directly
                    from backend.services.ai_auth_service import PasswordHasher
                    user.password_hash = PasswordHasher.hash_password(password)
                # Founder/paid flags
                if ensure_founder or email.lower() == getattr(self.auth_service, 'FOUNDER_EMAIL', '').lower():
                    user.is_founder = True
                    user.paid = True
                return jsonify({'success': True, 'data': user.to_dict_safe()}), 200
            except Exception as e:
                logger.error(f"Error /auth/admin/set-password: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.blueprint.route('/verify-token', methods=['POST'])
        @cross_origin()
        def verify_token():
            """POST /auth/verify-token - Verify token validity"""
            try:
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                
                is_valid, user_id = self.auth_service.verify_token(token)
                
                return jsonify({
                    'success': is_valid,
                    'user_id': user_id
                }), 200 if is_valid else 401
            except Exception as e:
                logger.error(f"Error verifying token: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500


# ==================== INITIALIZATION ====================

def create_marketplace_api(app, registry, auth_service, recommendation_engine, router):
    """Create and register all marketplace API routes"""
    
    # Create route handlers
    marketplace_routes = MarketplaceRoutes(registry, auth_service, recommendation_engine)
    agent_routes = AgentRoutes(auth_service, router, registry)
    auth_routes = AuthRoutes(auth_service)
    
    # Register blueprints
    app.register_blueprint(marketplace_routes.blueprint)
    app.register_blueprint(agent_routes.blueprint)
    app.register_blueprint(auth_routes.blueprint)
    
    logger.info("✅ Marketplace API initialized with 14 endpoints")
    
    return {
        'marketplace': marketplace_routes,
        'agent': agent_routes,
        'auth': auth_routes
    }
