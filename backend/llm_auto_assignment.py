"""
LLM Auto-Assignment System
Automatically discovers available LLM models and assigns them to the best roles
"""

import logging
from typing import Dict, List, Optional
from enum import Enum
from backend.llm_roles_descriptor import LLMRole, ROLE_SPECIFICATIONS

logger = logging.getLogger("q-ide-topdog")


class ModelCapability(Enum):
    """Model capability categories"""
    PLANNING = "planning"              # Requirements extraction, planning
    CODING = "coding"                  # Code generation, implementation
    TESTING = "testing"                # Test writing, validation
    VERIFICATION = "verification"      # Hallucination detection, fact-checking
    RELEASE = "release"                # Documentation, deployment planning


class ModelProfile:
    """Profile for an LLM model"""
    
    def __init__(self, model_id: str, provider: str, capabilities: List[ModelCapability], 
                 cost_per_1k_tokens: float = 0.01, speed: str = "medium"):
        self.model_id = model_id
        self.provider = provider
        self.capabilities = capabilities
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.speed = speed  # "fast", "medium", "slow"
        self.score = 0.0
    
    def __repr__(self):
        return f"{self.model_id} ({self.provider})"


# Known LLM Model Profiles (can be extended)
KNOWN_MODELS = {
    # OpenAI
    "gpt-4": ModelProfile(
        "gpt-4",
        "openai",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING, 
         ModelCapability.VERIFICATION, ModelCapability.RELEASE],
        cost_per_1k_tokens=0.03,
        speed="medium"
    ),
    "gpt-4-turbo": ModelProfile(
        "gpt-4-turbo",
        "openai",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING,
         ModelCapability.VERIFICATION, ModelCapability.RELEASE],
        cost_per_1k_tokens=0.01,
        speed="fast"
    ),
    "gpt-3.5-turbo": ModelProfile(
        "gpt-3.5-turbo",
        "openai",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING,
         ModelCapability.RELEASE],
        cost_per_1k_tokens=0.0005,
        speed="very_fast"
    ),
    
    # Anthropic Claude
    "claude-3-opus": ModelProfile(
        "claude-3-opus",
        "anthropic",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING,
         ModelCapability.VERIFICATION, ModelCapability.RELEASE],
        cost_per_1k_tokens=0.015,
        speed="medium"
    ),
    "claude-3-sonnet": ModelProfile(
        "claude-3-sonnet",
        "anthropic",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING,
         ModelCapability.VERIFICATION],
        cost_per_1k_tokens=0.003,
        speed="fast"
    ),
    "claude-3-haiku": ModelProfile(
        "claude-3-haiku",
        "anthropic",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING],
        cost_per_1k_tokens=0.00025,
        speed="very_fast"
    ),
    
    # Google Gemini
    "gemini-pro": ModelProfile(
        "gemini-pro",
        "google",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING,
         ModelCapability.VERIFICATION, ModelCapability.RELEASE],
        cost_per_1k_tokens=0.0005,
        speed="fast"
    ),
    
    # Mistral
    "mistral-large": ModelProfile(
        "mistral-large",
        "mistral",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING,
         ModelCapability.VERIFICATION],
        cost_per_1k_tokens=0.002,
        speed="fast"
    ),
    
    # Meta Llama (via Together, Replicate, etc)
    "llama-2-70b": ModelProfile(
        "llama-2-70b",
        "meta",
        [ModelCapability.PLANNING, ModelCapability.CODING, ModelCapability.TESTING],
        cost_per_1k_tokens=0.0008,
        speed="medium"
    ),
}


class LLMAutoAssignment:
    """Automatically assign LLM models to roles"""
    
    def __init__(self):
        self.available_models: List[ModelProfile] = []
        self.assignments: Dict[LLMRole, ModelProfile] = {}
    
    def discover_available_models(self, available_providers: Dict[str, bool]) -> List[ModelProfile]:
        """
        Discover which models are available based on authenticated providers
        
        Args:
            available_providers: Dict of provider names to authentication status
                Example: {"openai": True, "anthropic": False, "google": True}
        
        Returns:
            List of available ModelProfile objects
        """
        self.available_models = []
        
        for model_id, profile in KNOWN_MODELS.items():
            if available_providers.get(profile.provider, False):
                self.available_models.append(profile)
                logger.info(f"[LLM Discovery] Available: {profile.model_id} from {profile.provider}")
        
        if not self.available_models:
            logger.warning("[LLM Discovery] No models available - no providers authenticated")
        
        logger.info(f"[LLM Discovery] Total available models: {len(self.available_models)}")
        return self.available_models
    
    def score_model_for_role(self, model: ModelProfile, role: LLMRole) -> float:
        """
        Score how well a model fits a specific role (0-100)
        
        Args:
            model: ModelProfile to evaluate
            role: LLMRole to evaluate for
        
        Returns:
            Score 0-100 (higher is better)
        """
        score = 0.0
        
        # Define what capabilities each role needs most
        role_priorities = {
            LLMRole.Q_ASSISTANT: {
                ModelCapability.PLANNING: 0.5,      # Must be excellent at planning
                ModelCapability.VERIFICATION: 0.3,  # Should verify requirements
                ModelCapability.RELEASE: 0.2,
            },
            LLMRole.CODE_WRITER: {
                ModelCapability.CODING: 0.6,        # Must excel at coding
                ModelCapability.TESTING: 0.2,
                ModelCapability.PLANNING: 0.2,
            },
            LLMRole.TEST_AUDITOR: {
                ModelCapability.TESTING: 0.5,       # Primary: write/audit tests
                ModelCapability.CODING: 0.3,        # Needs to understand code
                ModelCapability.VERIFICATION: 0.2,
            },
            LLMRole.VERIFICATION_OVERSEER: {
                ModelCapability.VERIFICATION: 0.6,  # Primary: detect hallucinations
                ModelCapability.TESTING: 0.2,
                ModelCapability.PLANNING: 0.2,
            },
            LLMRole.RELEASE_MANAGER: {
                ModelCapability.RELEASE: 0.5,       # Documentation & deployment
                ModelCapability.PLANNING: 0.3,
                ModelCapability.VERIFICATION: 0.2,
            },
        }
        
        priorities = role_priorities.get(role, {})
        
        # Score based on capability match
        for capability, weight in priorities.items():
            if capability in model.capabilities:
                score += weight * 100
        
        # Adjust for cost (prefer cheaper models when capabilities are similar)
        if model.cost_per_1k_tokens < 0.001:
            score += 5  # Bonus for very cheap
        elif model.cost_per_1k_tokens > 0.02:
            score -= 10  # Penalty for expensive
        
        # Adjust for speed
        speed_bonus = {
            "very_fast": 5,
            "fast": 3,
            "medium": 0,
            "slow": -5,
        }
        score += speed_bonus.get(model.speed, 0)
        
        return min(100, max(0, score))  # Clamp 0-100
    
    def auto_assign_models(self, 
                           available_providers: Dict[str, bool],
                           prefer_cheap: bool = True,
                           prefer_fast: bool = False) -> Dict[LLMRole, Optional[ModelProfile]]:
        """
        Automatically assign best-fit models to each role
        
        Args:
            available_providers: Dict of authenticated providers
            prefer_cheap: Prefer lower-cost models if performance is similar
            prefer_fast: Prefer faster models if performance is similar
        
        Returns:
            Dict mapping LLMRole to best-fit ModelProfile
        """
        # Discover available models
        self.discover_available_models(available_providers)
        
        if not self.available_models:
            logger.error("[LLM Auto-Assignment] No available models to assign")
            return {role: None for role in LLMRole}
        
        # Score each model for each role
        role_scores: Dict[LLMRole, List[tuple]] = {}
        for role in LLMRole:
            role_scores[role] = []
            for model in self.available_models:
                score = self.score_model_for_role(model, role)
                role_scores[role].append((score, model))
            
            # Sort by score (highest first)
            role_scores[role].sort(reverse=True, key=lambda x: x[0])
        
        # Assign best model to each role
        self.assignments = {}
        assigned_models = set()  # Track which models are used
        
        for role in LLMRole:
            top_models = role_scores[role]
            
            # Try to assign best model that hasn't been used
            assigned = False
            for score, model in top_models:
                if model.model_id not in assigned_models:
                    self.assignments[role] = model
                    assigned_models.add(model.model_id)
                    logger.info(
                        f"[LLM Auto-Assignment] {role.value} -> {model.model_id} "
                        f"(score: {score:.0f}, cost: ${model.cost_per_1k_tokens}/1K tokens)"
                    )
                    assigned = True
                    break
            
            if not assigned:
                # All models used, assign same model again
                if top_models:
                    self.assignments[role] = top_models[0][1]
                    logger.info(
                        f"[LLM Auto-Assignment] {role.value} -> {top_models[0][1].model_id} "
                        f"(reused, score: {top_models[0][0]:.0f})"
                    )
                else:
                    self.assignments[role] = None
                    logger.warning(f"[LLM Auto-Assignment] {role.value} -> NO MODEL AVAILABLE")
        
        return self.assignments
    
    def get_assignment_summary(self) -> Dict:
        """Get a human-readable summary of assignments"""
        if not self.assignments:
            return {"error": "No assignments made yet"}
        
        summary = {
            "total_available_models": len(self.available_models),
            "assignments": {},
            "total_monthly_cost_estimate": 0.0,
        }
        
        for role, model in self.assignments.items():
            if model:
                summary["assignments"][role.value] = {
                    "model": model.model_id,
                    "provider": model.provider,
                    "capabilities": [c.value for c in model.capabilities],
                    "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    "speed": model.speed,
                }
                # Rough estimate: 1M tokens per month per role
                summary["total_monthly_cost_estimate"] += (model.cost_per_1k_tokens * 1000)
            else:
                summary["assignments"][role.value] = {"model": None, "error": "No suitable model available"}
        
        return summary


def register_auto_assignment_routes(app):
    """Register auto-assignment endpoints to FastAPI app"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/api/llm", tags=["LLM Auto-Assignment"])
    assignment_system = LLMAutoAssignment()
    
    @router.get("/auto-assign")
    async def auto_assign():
        """
        Automatically discover available LLMs and assign to roles
        
        Returns:
            Assignment results with model-to-role mapping
        """
        try:
            # Get authenticated providers
            from backend.llm_auth import get_authenticated_providers
            providers = get_authenticated_providers()
            
            # Auto-assign
            assignments = assignment_system.auto_assign_models(providers)
            
            return {
                "status": "success",
                "assignments": {
                    role.value: (model.model_id if model else None)
                    for role, model in assignments.items()
                },
                "summary": assignment_system.get_assignment_summary(),
            }
        except Exception as e:
            logger.error(f"[LLM Auto-Assignment] Error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to auto-assign LLM models. Make sure you have at least one provider authenticated."
            }
    
    @router.get("/available-models")
    async def get_available_models():
        """Get list of all known LLM models and their capabilities"""
        return {
            "known_models": {
                model_id: {
                    "provider": profile.provider,
                    "capabilities": [c.value for c in profile.capabilities],
                    "cost_per_1k_tokens": profile.cost_per_1k_tokens,
                    "speed": profile.speed,
                }
                for model_id, profile in KNOWN_MODELS.items()
            },
            "total": len(KNOWN_MODELS),
        }
    
    @router.get("/assignment-summary")
    async def get_summary():
        """Get current assignment summary"""
        if not assignment_system.assignments:
            return {
                "status": "no_assignment",
                "message": "Run /api/llm/auto-assign first to generate assignments"
            }
        return assignment_system.get_assignment_summary()
    
    app.include_router(router)
    
    return assignment_system
