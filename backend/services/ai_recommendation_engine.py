"""
Q Assistant Recommendation Engine
Analyzes user queries and recommends the best 3 AI models for the task
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime


class TaskCategory(str, Enum):
    """Categories of programming tasks"""
    CODE_GENERATION = "code_generation"
    CODE_COMPLETION = "code_completion"
    BUG_FIXING = "bug_fixing"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    EXPLANATION = "explanation"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    ARCHITECTURE = "architecture"
    UNKNOWN = "unknown"


@dataclass
class RecommendationScore:
    """Score for a model recommendation"""
    model_id: str
    model_name: str
    score: float  # 0-100
    reasoning: List[str]
    price_rank: int  # 1=cheapest in recommendations
    speed_rank: int  # 1=fastest in recommendations
    quality_rank: int  # 1=best quality in recommendations


class QueryAnalyzer:
    """Analyze user queries to extract intent and requirements"""
    
    # Keywords for each task category
    CATEGORY_KEYWORDS = {
        TaskCategory.CODE_GENERATION: [
            'generate', 'write', 'create', 'build', 'implement',
            'make', 'develop', 'code', 'function', 'class', 'script'
        ],
        TaskCategory.CODE_COMPLETION: [
            'complete', 'fill in', 'suggest', 'auto', 'hint',
            'autocomplete', 'finish', 'fill', 'continue'
        ],
        TaskCategory.BUG_FIXING: [
            'fix', 'debug', 'bug', 'error', 'crash', 'issue',
            'problem', 'wrong', 'not working', 'broken', 'exception'
        ],
        TaskCategory.REFACTORING: [
            'refactor', 'improve', 'clean', 'optimize', 'simplify',
            'reorganize', 'restructure', 'rewrite', 'extract'
        ],
        TaskCategory.DOCUMENTATION: [
            'document', 'comment', 'docstring', 'readme', 'javadoc',
            'explain how', 'what does', 'describe', 'doc', 'markdown'
        ],
        TaskCategory.EXPLANATION: [
            'explain', 'what is', 'how does', 'why', 'understand',
            'clarify', 'what does', 'meaning', 'example'
        ],
        TaskCategory.OPTIMIZATION: [
            'optimize', 'faster', 'performance', 'efficient', 'slow',
            'speed up', 'improve speed', 'lag'
        ],
        TaskCategory.TESTING: [
            'test', 'unit test', 'test case', 'assert', 'mock',
            'coverage', 'qunit', 'jest', 'pytest', 'verify'
        ],
        TaskCategory.ARCHITECTURE: [
            'architecture', 'design', 'pattern', 'structure', 'system',
            'component', 'module', 'library', 'framework'
        ]
    }
    
    @staticmethod
    def analyze_query(query: str) -> Tuple[TaskCategory, List[str], str]:
        """Analyze a query and extract category and keywords"""
        
        query_lower = query.lower()
        
        # Extract category
        category = TaskCategory.UNKNOWN
        max_matches = 0
        
        for cat, keywords in QueryAnalyzer.CATEGORY_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in query_lower)
            if matches > max_matches:
                max_matches = matches
                category = cat
        
        # Extract keywords (words > 4 characters, excluding common words)
        common_words = {'what', 'this', 'that', 'with', 'from', 'about', 'using', 'should'}
        keywords = [
            word for word in query_lower.split()
            if len(word) > 4 and word not in common_words
        ]
        
        # Extract language hint (Python, JavaScript, Java, etc)
        language = ""
        lang_keywords = {'python', 'javascript', 'java', 'cpp', 'csharp', 'go', 'rust'}
        for lang in lang_keywords:
            if lang in query_lower:
                language = lang
                break
        
        return category, keywords, language
    
    @staticmethod
    def extract_complexity(query: str) -> int:
        """Extract task complexity (1-5)"""
        
        query_lower = query.lower()
        complexity = 1
        
        # Simple indicators
        if any(word in query_lower for word in ['complex', 'difficult', 'advanced', 'large']):
            complexity = 4
        elif any(word in query_lower for word in ['simple', 'basic', 'easy', 'small']):
            complexity = 1
        elif any(word in query_lower for word in ['medium', 'moderate']):
            complexity = 3
        
        # By token count (rough estimate)
        token_count = len(query.split())
        if token_count > 100:
            complexity = max(complexity, 4)
        elif token_count > 50:
            complexity = max(complexity, 3)
        
        return complexity


class RecommendationEngine:
    """Generate model recommendations based on task analysis"""
    
    def __init__(self, registry):
        """Initialize with access to model registry"""
        self.registry = registry
        self.analyzer = QueryAnalyzer()
        self.recommendation_history: List[Dict] = []
    
    def get_recommendations(
        self,
        query: str,
        user_budget: str = "medium",
        user_preferences: Optional[Dict] = None
    ) -> Tuple[bool, List[RecommendationScore]]:
        """
        Get top 3 model recommendations for a query
        
        Args:
            query: User's query/task description
            user_budget: 'cheap', 'medium', or 'expensive'
            user_preferences: User's model preferences
        
        Returns:
            (success, recommendations)
        """
        
        # Analyze query
        category, keywords, language = self.analyzer.analyze_query(query)
        complexity = self.analyzer.extract_complexity(query)
        
        # Get candidate models
        candidates = self.registry.get_recommended_models(
            use_case=category.value,
            budget=user_budget
        )
        
        if not candidates:
            return False, []
        
        # Score each candidate
        scores = []
        for model in candidates[:10]:  # Consider top 10
            score = self._calculate_score(
                model,
                category,
                complexity,
                language,
                user_preferences or {}
            )
            scores.append(score)
        
        # Sort by score and take top 3
        scores.sort(key=lambda s: s.score, reverse=True)
        recommendations = scores[:3]
        
        # Assign price/speed/quality ranks
        if len(recommendations) > 0:
            # Create lookup for model data
            model_lookup = {m.id: m for m in candidates}
            
            # Sort by average price
            price_ranked = sorted(
                enumerate(recommendations),
                key=lambda x: (model_lookup[x[1].model_id].pricing.input_cost_per_1k_tokens + 
                             model_lookup[x[1].model_id].pricing.output_cost_per_1k_tokens) / 2
            )
            for rank, (idx, rec) in enumerate(price_ranked, 1):
                rec.price_rank = rank
            
            # Sort by rating
            quality_ranked = sorted(
                enumerate(recommendations),
                key=lambda x: model_lookup[x[1].model_id].rating,
                reverse=True
            )
            for rank, (idx, rec) in enumerate(quality_ranked, 1):
                rec.quality_rank = rank
            
            # Speed is inverse of context window (smaller = faster)
            speed_ranked = sorted(
                enumerate(recommendations),
                key=lambda x: model_lookup[x[1].model_id].context_window
            )
            for rank, (idx, rec) in enumerate(speed_ranked, 1):
                rec.speed_rank = rank
        
        # Log recommendation
        self.recommendation_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'category': category.value,
            'complexity': complexity,
            'recommendations': [r.model_id for r in recommendations]
        })
        
        return True, recommendations
    
    def _calculate_score(
        self,
        model,
        category: TaskCategory,
        complexity: int,
        language: str,
        user_preferences: Dict
    ) -> RecommendationScore:
        """Calculate recommendation score for a model"""
        
        score = 50.0  # Base score
        reasoning = []
        
        # 1. Capability matching (0-20 points)
        capability_bonus = 0
        if any(cap.value.startswith('code') for cap in model.capabilities):
            capability_bonus += 5
            reasoning.append("Has code capabilities")
        
        if any(cap.value == 'reasoning' for cap in model.capabilities):
            capability_bonus += 5
            reasoning.append("Strong reasoning for complex tasks")
        
        score += capability_bonus
        
        # 2. Rating (0-15 points)
        rating_bonus = (model.rating / 5.0) * 15
        score += rating_bonus
        reasoning.append(f"High quality ({model.rating}/5.0)")
        
        # 3. Cost efficiency (0-15 points)
        avg_price = (model.pricing.input_cost_per_1k_tokens + 
                    model.pricing.output_cost_per_1k_tokens) / 2
        if avg_price == 0:
            cost_bonus = 15
            reasoning.append("Free model (local/open-source)")
        elif avg_price < 0.001:
            cost_bonus = 12
            reasoning.append("Very affordable")
        elif avg_price < 0.005:
            cost_bonus = 8
            reasoning.append("Good value for money")
        else:
            cost_bonus = max(0, 5 - avg_price * 100)
        
        score += cost_bonus
        
        # 4. Context window for complexity (0-10 points)
        if complexity >= 4:
            if model.context_window >= 100000:
                score += 10
                reasoning.append("Large context for complex tasks")
            elif model.context_window >= 32000:
                score += 7
                reasoning.append("Good context window")
        
        # 5. Popularity/Trust (0-10 points)
        if model.usage_count > 100000:
            score += 10
            reasoning.append("Very popular choice")
        elif model.usage_count > 50000:
            score += 7
            reasoning.append("Trusted by many users")
        
        # 6. Provider preference (0-5 points)
        if user_preferences.get('preferred_providers'):
            if model.provider.value in user_preferences['preferred_providers']:
                score += 5
                reasoning.append("Your preferred provider")
        
        # 7. Penalty for inactive/new (0-5 points)
        if model.usage_count < 10000:
            score -= 3
        
        # Ensure score is 0-100
        score = max(0, min(100, score))
        
        return RecommendationScore(
            model_id=model.id,
            model_name=model.name,
            score=score,
            reasoning=reasoning,
            price_rank=0,  # Will be set later
            speed_rank=0,
            quality_rank=0
        )
    
    def record_user_choice(
        self,
        user_id: str,
        recommended_models: List[str],
        selected_model: str,
        query_category: str
    ) -> None:
        """Record which model user selected (for learning)"""
        
        self.recommendation_history.append({
            'type': 'user_choice',
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'recommended_models': recommended_models,
            'selected_model': selected_model,
            'query_category': query_category
        })
    
    def get_statistics(self) -> Dict:
        """Get recommendation statistics"""
        
        total_recs = len([h for h in self.recommendation_history 
                         if h.get('type') != 'user_choice'])
        user_choices = len([h for h in self.recommendation_history 
                           if h.get('type') == 'user_choice'])
        
        return {
            'total_recommendations': total_recs,
            'user_selections': user_choices,
            'accuracy': user_choices / total_recs if total_recs > 0 else 0,
            'recent_queries': len(self.recommendation_history[-100:])
        }


# Global recommendation engine instance (initialized if registry available)
# Falls back to None if registry import fails; main or routers will re-initialize as needed.
recommendation_engine = None
try:
    from backend.services.ai_marketplace_registry import registry
    recommendation_engine = RecommendationEngine(registry)
except Exception:
    recommendation_engine = None
