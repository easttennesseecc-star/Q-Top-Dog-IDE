"""
AI Marketplace Registry Service
Manages the database of 50+ AI models with pricing, capabilities, ratings
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import json
from enum import Enum


class ModelCapability(str, Enum):
    """Available AI model capabilities"""
    CODE_GENERATION = "code_generation"
    CODE_COMPLETION = "code_completion"
    CODE_EXPLANATION = "code_explanation"
    BUG_DETECTION = "bug_detection"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    DOCUMENTATION = "documentation"
    TEXT_ANALYSIS = "text_analysis"
    REASONING = "reasoning"
    IMAGE_GENERATION = "image_generation"
    MULTI_MODAL = "multi_modal"
    EMBEDDINGS = "embeddings"
    FINE_TUNING = "fine_tuning"


class ModelProvider(str, Enum):
    """AI model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    COHERE = "cohere"
    STABILITY_AI = "stability_ai"
    TOGETHER_AI = "together_ai"


@dataclass
class ModelPricing:
    """Pricing information for a model"""
    input_cost_per_1k_tokens: float  # USD
    output_cost_per_1k_tokens: float  # USD
    supports_prepaid: bool = True
    currency: str = "USD"


@dataclass
class AIModel:
    """Represents an AI model in the marketplace"""
    id: str  # e.g., "gpt4-turbo"
    name: str  # e.g., "GPT-4 Turbo"
    provider: ModelProvider
    description: str
    version: str
    capabilities: List[ModelCapability]
    pricing: ModelPricing
    context_window: int  # tokens
    max_output_tokens: int
    rating: float  # 0-5.0
    usage_count: int  # how many users have used this
    monthly_active_users: int
    supported_languages: List[str] = field(default_factory=lambda: ["en"])
    is_available: bool = True
    launch_date: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        data = asdict(self)
        data['provider'] = self.provider.value
        data['capabilities'] = [c.value for c in self.capabilities]
        data['pricing'] = asdict(self.pricing)
        return data


class AIMarketplaceRegistry:
    """Registry for managing AI models in the marketplace"""
    
    def __init__(self):
        """Initialize the registry with default models"""
        self.models: Dict[str, AIModel] = {}
        self._initialize_models()
        self.total_usage = 0
        self.search_history: List[Dict] = []
    
    def _initialize_models(self):
        """Load all 50+ models into the registry"""
        
        # OPENAI MODELS
        self.add_model(AIModel(
            id="gpt4-turbo",
            name="GPT-4 Turbo",
            provider=ModelProvider.OPENAI,
            description="Most capable model from OpenAI. Best for complex reasoning and code.",
            version="2024-04",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.REASONING,
                ModelCapability.REFACTORING,
                ModelCapability.DOCUMENTATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.03,
                output_cost_per_1k_tokens=0.06
            ),
            context_window=128000,
            max_output_tokens=4096,
            rating=4.9,
            usage_count=125000,
            monthly_active_users=45000
        ))
        
        self.add_model(AIModel(
            id="gpt4",
            name="GPT-4",
            provider=ModelProvider.OPENAI,
            description="Highly capable model. Better cost/performance than Turbo.",
            version="2024-04",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.DOCUMENTATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.03,
                output_cost_per_1k_tokens=0.06
            ),
            context_window=8192,
            max_output_tokens=2048,
            rating=4.8,
            usage_count=89000,
            monthly_active_users=32000
        ))
        
        self.add_model(AIModel(
            id="gpt-35-turbo",
            name="GPT-3.5 Turbo",
            provider=ModelProvider.OPENAI,
            description="Fast, affordable model. Good for quick code suggestions.",
            version="2024-04",
            capabilities=[
                ModelCapability.CODE_COMPLETION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.TEXT_ANALYSIS
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0005,
                output_cost_per_1k_tokens=0.0015
            ),
            context_window=4096,
            max_output_tokens=2048,
            rating=4.5,
            usage_count=250000,
            monthly_active_users=120000
        ))
        
        # ANTHROPIC MODELS
        self.add_model(AIModel(
            id="claude-opus",
            name="Claude 3 Opus",
            provider=ModelProvider.ANTHROPIC,
            description="Anthropic's most powerful model. Best reasoning and analysis.",
            version="3.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.REFACTORING,
                ModelCapability.CODE_EXPLANATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.015,
                output_cost_per_1k_tokens=0.075
            ),
            context_window=200000,
            max_output_tokens=4096,
            rating=4.9,
            usage_count=98000,
            monthly_active_users=28000
        ))
        
        self.add_model(AIModel(
            id="claude-sonnet",
            name="Claude 3 Sonnet",
            provider=ModelProvider.ANTHROPIC,
            description="Balanced model from Anthropic. Great code output.",
            version="3.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.DOCUMENTATION,
                ModelCapability.REFACTORING
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.003,
                output_cost_per_1k_tokens=0.015
            ),
            context_window=200000,
            max_output_tokens=4096,
            rating=4.7,
            usage_count=145000,
            monthly_active_users=52000
        ))
        
        self.add_model(AIModel(
            id="claude-sonnet-3.5",
            name="Claude 3.5 Sonnet",
            provider=ModelProvider.ANTHROPIC,
            description="Latest Anthropic model with enhanced reasoning and coding. Available for all clients.",
            version="3.5",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.REASONING,
                ModelCapability.DOCUMENTATION,
                ModelCapability.REFACTORING,
                ModelCapability.DEBUGGING
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.003,
                output_cost_per_1k_tokens=0.015
            ),
            context_window=200000,
            max_output_tokens=8192,
            rating=4.9,
            usage_count=185000,
            monthly_active_users=72000
        ))
        
        self.add_model(AIModel(
            id="claude-haiku",
            name="Claude 3 Haiku",
            provider=ModelProvider.ANTHROPIC,
            description="Fast, cheap model from Anthropic. Best for quick tasks.",
            version="3.0",
            capabilities=[
                ModelCapability.CODE_COMPLETION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.TEXT_ANALYSIS
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.00025,
                output_cost_per_1k_tokens=0.00125
            ),
            context_window=200000,
            max_output_tokens=4096,
            rating=4.4,
            usage_count=180000,
            monthly_active_users=78000
        ))
        
        self.add_model(AIModel(
            id="claude-opus",
            name="Claude 3 Opus",
            provider=ModelProvider.ANTHROPIC,
            description="Most powerful Claude model. Best for complex reasoning and analysis.",
            version="3.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.REASONING,
                ModelCapability.DOCUMENTATION,
                ModelCapability.REFACTORING,
                ModelCapability.BUG_DETECTION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.015,
                output_cost_per_1k_tokens=0.075
            ),
            context_window=200000,
            max_output_tokens=4096,
            rating=4.9,
            usage_count=165000,
            monthly_active_users=68000
        ))
        
        self.add_model(AIModel(
            id="claude-3.5-haiku",
            name="Claude 3.5 Haiku",
            provider=ModelProvider.ANTHROPIC,
            description="Fastest Claude model with 3.5 enhancements. Excellent for real-time tasks.",
            version="3.5",
            capabilities=[
                ModelCapability.CODE_COMPLETION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.TEXT_ANALYSIS,
                ModelCapability.CODE_EXPLANATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0008,
                output_cost_per_1k_tokens=0.004
            ),
            context_window=200000,
            max_output_tokens=8192,
            rating=4.6,
            usage_count=195000,
            monthly_active_users=85000
        ))
        
        # GOOGLE GEMINI MODELS
        self.add_model(AIModel(
            id="gemini-pro",
            name="Gemini 1.5 Pro",
            provider=ModelProvider.GOOGLE_GEMINI,
            description="Google's flagship model. Excellent multimodal capabilities.",
            version="1.5",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.MULTI_MODAL,
                ModelCapability.CODE_EXPLANATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.00175,
                output_cost_per_1k_tokens=0.007
            ),
            context_window=1000000,
            max_output_tokens=8192,
            rating=4.8,
            usage_count=112000,
            monthly_active_users=38000
        ))
        
        self.add_model(AIModel(
            id="gemini-flash",
            name="Gemini 1.5 Flash",
            provider=ModelProvider.GOOGLE_GEMINI,
            description="Google's fastest model. Great for real-time applications.",
            version="1.5",
            capabilities=[
                ModelCapability.CODE_COMPLETION,
                ModelCapability.CODE_GENERATION,
                ModelCapability.TEXT_ANALYSIS,
                ModelCapability.MULTI_MODAL
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.000075,
                output_cost_per_1k_tokens=0.0003
            ),
            context_window=1000000,
            max_output_tokens=8192,
            rating=4.6,
            usage_count=165000,
            monthly_active_users=68000
        ))
        
        # HUGGINGFACE MODELS
        self.add_model(AIModel(
            id="mistral-7b",
            name="Mistral 7B",
            provider=ModelProvider.HUGGINGFACE,
            description="Open-source model. Fast and efficient.",
            version="1.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_COMPLETION,
                ModelCapability.TEXT_ANALYSIS
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.00015,
                output_cost_per_1k_tokens=0.0002
            ),
            context_window=32768,
            max_output_tokens=4096,
            rating=4.3,
            usage_count=89000,
            monthly_active_users=32000
        ))
        
        self.add_model(AIModel(
            id="llama2-70b",
            name="Llama 2 70B",
            provider=ModelProvider.HUGGINGFACE,
            description="Meta's 70B open-source model. Strong performance.",
            version="2.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING,
                ModelCapability.DOCUMENTATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0005,
                output_cost_per_1k_tokens=0.001
            ),
            context_window=4096,
            max_output_tokens=2048,
            rating=4.5,
            usage_count=76000,
            monthly_active_users=28000
        ))
        
        self.add_model(AIModel(
            id="codellama-34b",
            name="Code Llama 34B",
            provider=ModelProvider.HUGGINGFACE,
            description="Meta's code-specialized model. Best for programming.",
            version="1.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.BUG_DETECTION,
                ModelCapability.REFACTORING
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0004,
                output_cost_per_1k_tokens=0.0008
            ),
            context_window=16384,
            max_output_tokens=4096,
            rating=4.6,
            usage_count=95000,
            monthly_active_users=35000
        ))
        
        # OLLAMA MODELS (Local/Open)
        self.add_model(AIModel(
            id="ollama-llama2",
            name="Ollama Llama 2",
            provider=ModelProvider.OLLAMA,
            description="Open-source, run locally. Best privacy.",
            version="2.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_COMPLETION,
                ModelCapability.TEXT_ANALYSIS
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0,  # Free
                output_cost_per_1k_tokens=0.0
            ),
            context_window=4096,
            max_output_tokens=2048,
            rating=4.2,
            usage_count=45000,
            monthly_active_users=18000
        ))
        
        self.add_model(AIModel(
            id="ollama-neural-chat",
            name="Ollama Neural Chat",
            provider=ModelProvider.OLLAMA,
            description="Open-source, optimized for conversation.",
            version="1.0",
            capabilities=[
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.TEXT_ANALYSIS,
                ModelCapability.DOCUMENTATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0,
                output_cost_per_1k_tokens=0.0
            ),
            context_window=4096,
            max_output_tokens=2048,
            rating=4.1,
            usage_count=32000,
            monthly_active_users=14000
        ))
        
        # COHERE MODELS
        self.add_model(AIModel(
            id="command",
            name="Command R",
            provider=ModelProvider.COHERE,
            description="Cohere's instruction-following model. Reliable.",
            version="2024",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.TEXT_ANALYSIS,
                ModelCapability.DOCUMENTATION
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0005,
                output_cost_per_1k_tokens=0.0015
            ),
            context_window=4096,
            max_output_tokens=2048,
            rating=4.4,
            usage_count=52000,
            monthly_active_users=19000
        ))
        
        # TOGETHER AI MODELS
        self.add_model(AIModel(
            id="together-llama2",
            name="Together.ai Llama 2",
            provider=ModelProvider.TOGETHER_AI,
            description="Llama 2 via Together.ai. Cheap and fast.",
            version="2.0",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_COMPLETION,
                ModelCapability.TEXT_ANALYSIS
            ],
            pricing=ModelPricing(
                input_cost_per_1k_tokens=0.0002,
                output_cost_per_1k_tokens=0.0002
            ),
            context_window=4096,
            max_output_tokens=2048,
            rating=4.3,
            usage_count=41000,
            monthly_active_users=16000
        ))
        
        # ADDITIONAL OPENAI MODELS
        self.add_model(AIModel(id="gpt-3.5", name="GPT-3.5 Turbo", provider=ModelProvider.OPENAI, description="Fast and cheap OpenAI model", version="3.5", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0005, 0.0015), context_window=4096, max_output_tokens=2048, rating=4.5, usage_count=250000, monthly_active_users=120000))
        self.add_model(AIModel(id="gpt-4", name="GPT-4", provider=ModelProvider.OPENAI, description="Original GPT-4 model", version="4.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.03, 0.06), context_window=8192, max_output_tokens=4096, rating=4.9, usage_count=180000, monthly_active_users=95000))
        self.add_model(AIModel(id="gpt4-vision", name="GPT-4 Vision", provider=ModelProvider.OPENAI, description="GPT-4 with image understanding", version="4.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.IMAGE_GENERATION, ModelCapability.MULTI_MODAL], pricing=ModelPricing(0.01, 0.03), context_window=8192, max_output_tokens=4096, rating=4.8, usage_count=95000, monthly_active_users=52000))
        self.add_model(AIModel(id="davinci-3", name="Davinci 3", provider=ModelProvider.OPENAI, description="Powerful model for complex tasks", version="3.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.002, 0.004), context_window=4096, max_output_tokens=2048, rating=4.6, usage_count=120000, monthly_active_users=68000))
        
        # ADDITIONAL ANTHROPIC MODELS
        self.add_model(AIModel(id="claude-instant", name="Claude Instant", provider=ModelProvider.ANTHROPIC, description="Fast Claude model from Anthropic", version="2.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0008, 0.0024), context_window=100000, max_output_tokens=4096, rating=4.3, usage_count=140000, monthly_active_users=75000))
        self.add_model(AIModel(id="claude-2", name="Claude 2", provider=ModelProvider.ANTHROPIC, description="Previous generation Claude", version="2.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.008, 0.024), context_window=100000, max_output_tokens=4096, rating=4.5, usage_count=110000, monthly_active_users=58000))
        
        # ADDITIONAL GOOGLE GEMINI MODELS
        self.add_model(AIModel(id="gemini-pro", name="Gemini Pro", provider=ModelProvider.GOOGLE_GEMINI, description="Google's flagship model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING, ModelCapability.MULTI_MODAL], pricing=ModelPricing(0.0005, 0.0015), context_window=32000, max_output_tokens=4096, rating=4.7, usage_count=130000, monthly_active_users=72000))
        self.add_model(AIModel(id="gemini-ultra", name="Gemini Ultra", provider=ModelProvider.GOOGLE_GEMINI, description="Most powerful Gemini model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING, ModelCapability.MULTI_MODAL], pricing=ModelPricing(0.001, 0.003), context_window=1000000, max_output_tokens=4096, rating=4.9, usage_count=105000, monthly_active_users=58000))
        
        # ADDITIONAL HUGGINGFACE MODELS
        self.add_model(AIModel(id="mistral-7b", name="Mistral 7B", provider=ModelProvider.HUGGINGFACE, description="Mistral's 7B parameter model", version="0.1", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0001, 0.0003), context_window=8192, max_output_tokens=2048, rating=4.4, usage_count=85000, monthly_active_users=42000))
        self.add_model(AIModel(id="llama-13b", name="Llama 13B", provider=ModelProvider.HUGGINGFACE, description="Meta's Llama 2 13B", version="2.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00015, 0.0003), context_window=4096, max_output_tokens=2048, rating=4.5, usage_count=92000, monthly_active_users=48000))
        self.add_model(AIModel(id="falcon-40b", name="Falcon 40B", provider=ModelProvider.HUGGINGFACE, description="TII's powerful Falcon model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.0003, 0.0006), context_window=2048, max_output_tokens=1024, rating=4.6, usage_count=78000, monthly_active_users=35000))
        self.add_model(AIModel(id="orca-13b", name="Microsoft Orca 13B", provider=ModelProvider.HUGGINGFACE, description="Instruction-tuned model", version="2.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00012, 0.00025), context_window=4096, max_output_tokens=2048, rating=4.5, usage_count=68000, monthly_active_users=31000))
        
        # COHERE MODELS
        self.add_model(AIModel(id="cohere-command", name="Cohere Command", provider=ModelProvider.COHERE, description="Cohere's instruction-following model", version="3.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0001, 0.0003), context_window=4096, max_output_tokens=2048, rating=4.3, usage_count=55000, monthly_active_users=28000))
        self.add_model(AIModel(id="cohere-light", name="Cohere Light", provider=ModelProvider.COHERE, description="Lightweight Cohere model", version="3.0", capabilities=[ModelCapability.CODE_COMPLETION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00005, 0.00015), context_window=2048, max_output_tokens=1024, rating=4.2, usage_count=42000, monthly_active_users=20000))
        
        # STABILITY AI MODELS
        self.add_model(AIModel(id="stable-diffusion-3", name="Stable Diffusion 3", provider=ModelProvider.STABILITY_AI, description="Latest Stable Diffusion model", version="3.0", capabilities=[ModelCapability.IMAGE_GENERATION, ModelCapability.MULTI_MODAL], pricing=ModelPricing(0.01, 0.02), context_window=8192, max_output_tokens=4096, rating=4.7, usage_count=125000, monthly_active_users=68000))
        self.add_model(AIModel(id="stable-diffusion-xl", name="Stable Diffusion XL", provider=ModelProvider.STABILITY_AI, description="SDXL for high-quality images", version="1.0", capabilities=[ModelCapability.IMAGE_GENERATION, ModelCapability.MULTI_MODAL], pricing=ModelPricing(0.008, 0.016), context_window=4096, max_output_tokens=2048, rating=4.6, usage_count=98000, monthly_active_users=52000))
        
        # OLLAMA LOCAL MODELS
        self.add_model(AIModel(id="ollama-neural-chat", name="Ollama Neural Chat", provider=ModelProvider.OLLAMA, description="Neural chat model for local deployment", version="7b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0, 0.0), context_window=2048, max_output_tokens=1024, rating=4.1, usage_count=35000, monthly_active_users=18000))
        self.add_model(AIModel(id="ollama-orca-mini", name="Ollama Orca Mini", provider=ModelProvider.OLLAMA, description="Compact Orca for local use", version="13b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0, 0.0), context_window=4096, max_output_tokens=2048, rating=4.3, usage_count=42000, monthly_active_users=22000))
        
        # ADDITIONAL HIGH-VALUE MODELS
        self.add_model(AIModel(id="llama2-70b", name="Llama 2 70B", provider=ModelProvider.HUGGINGFACE, description="Meta's largest Llama 2", version="2.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.001, 0.002), context_window=4096, max_output_tokens=2048, rating=4.8, usage_count=155000, monthly_active_users=88000))
        self.add_model(AIModel(id="mixtral-8x7b", name="Mistral Mixtral 8x7B", provider=ModelProvider.HUGGINGFACE, description="MoE expert model", version="0.1", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.00024, 0.00024), context_window=32768, max_output_tokens=4096, rating=4.7, usage_count=112000, monthly_active_users=62000))
        self.add_model(AIModel(id="phi-2", name="Microsoft Phi-2", provider=ModelProvider.HUGGINGFACE, description="Small but capable model", version="2.7b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00005, 0.0001), context_window=2048, max_output_tokens=1024, rating=4.4, usage_count=65000, monthly_active_users=32000))
        self.add_model(AIModel(id="zephyr-7b", name="Zephyr 7B", provider=ModelProvider.HUGGINGFACE, description="Instruction-tuned model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00008, 0.00016), context_window=4096, max_output_tokens=2048, rating=4.5, usage_count=71000, monthly_active_users=38000))
        self.add_model(AIModel(id="neural-8b", name="Yi Neural 8B", provider=ModelProvider.HUGGINGFACE, description="Yi model for code", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_COMPLETION], pricing=ModelPricing(0.0001, 0.0002), context_window=4096, max_output_tokens=2048, rating=4.4, usage_count=58000, monthly_active_users=31000))
        self.add_model(AIModel(id="qwen-72b", name="Alibaba Qwen 72B", provider=ModelProvider.HUGGINGFACE, description="Large Chinese-optimized model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.0008, 0.0016), context_window=32768, max_output_tokens=4096, rating=4.6, usage_count=68000, monthly_active_users=35000))
        self.add_model(AIModel(id="mpt-30b", name="MPT 30B", provider=ModelProvider.HUGGINGFACE, description="MosaicML's powerful model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.0003, 0.0006), context_window=8192, max_output_tokens=2048, rating=4.5, usage_count=62000, monthly_active_users=29000))
        self.add_model(AIModel(id="deepseek-coder", name="DeepSeek Coder", provider=ModelProvider.HUGGINGFACE, description="Specialized coding model", version="33b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION, ModelCapability.BUG_DETECTION], pricing=ModelPricing(0.00015, 0.0003), context_window=4096, max_output_tokens=4096, rating=4.7, usage_count=89000, monthly_active_users=48000))
        self.add_model(AIModel(id="starcoder", name="StarCoder", provider=ModelProvider.HUGGINGFACE, description="Bigcode's StarCoder for code", version="15b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_COMPLETION], pricing=ModelPricing(0.0001, 0.0002), context_window=8192, max_output_tokens=4096, rating=4.6, usage_count=76000, monthly_active_users=41000))
        self.add_model(AIModel(id="replit-code-v1-3b", name="Replit Code V1 3B", provider=ModelProvider.HUGGINGFACE, description="Lightweight code model", version="3b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_COMPLETION], pricing=ModelPricing(0.00005, 0.0001), context_window=4096, max_output_tokens=2048, rating=4.3, usage_count=45000, monthly_active_users=22000))
        self.add_model(AIModel(id="octocoder", name="OctoC oder", provider=ModelProvider.HUGGINGFACE, description="Code-focused model for programming", version="13b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_COMPLETION, ModelCapability.BUG_DETECTION], pricing=ModelPricing(0.0001, 0.0002), context_window=8192, max_output_tokens=4096, rating=4.5, usage_count=62000, monthly_active_users=33000))
        self.add_model(AIModel(id="codeparrot", name="CodeParrot", provider=ModelProvider.HUGGINGFACE, description="Parrot.live coding model", version="1.5b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_COMPLETION], pricing=ModelPricing(0.00003, 0.00006), context_window=2048, max_output_tokens=1024, rating=4.1, usage_count=28000, monthly_active_users=14000))
        self.add_model(AIModel(id="bloom-176b", name="BLOOM 176B", provider=ModelProvider.HUGGINGFACE, description="BigScience's massive model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS, ModelCapability.REASONING], pricing=ModelPricing(0.0005, 0.001), context_window=2048, max_output_tokens=1024, rating=4.4, usage_count=51000, monthly_active_users=26000))
        self.add_model(AIModel(id="t5-11b", name="T5 11B", provider=ModelProvider.HUGGINGFACE, description="Google's text-to-text model", version="3.0", capabilities=[ModelCapability.TEXT_ANALYSIS, ModelCapability.DOCUMENTATION], pricing=ModelPricing(0.00008, 0.00016), context_window=512, max_output_tokens=512, rating=4.2, usage_count=35000, monthly_active_users=18000))
        self.add_model(AIModel(id="xlnet-large", name="XLNet Large", provider=ModelProvider.HUGGINGFACE, description="Autoregressive language model", version="1.0", capabilities=[ModelCapability.TEXT_ANALYSIS, ModelCapability.CODE_EXPLANATION], pricing=ModelPricing(0.0001, 0.0002), context_window=2048, max_output_tokens=512, rating=4.3, usage_count=42000, monthly_active_users=21000))
        self.add_model(AIModel(id="electra-large", name="ELECTRA Large", provider=ModelProvider.HUGGINGFACE, description="Efficient text model", version="1.0", capabilities=[ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00006, 0.00012), context_window=512, max_output_tokens=512, rating=4.2, usage_count=38000, monthly_active_users=19000))
        self.add_model(AIModel(id="gpt-j-6b", name="GPT-J 6B", provider=ModelProvider.HUGGINGFACE, description="EleutherAI's 6B model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00008, 0.00016), context_window=2048, max_output_tokens=1024, rating=4.4, usage_count=47000, monthly_active_users=24000))
        self.add_model(AIModel(id="gpt-neox-20b", name="GPT-NeoX 20B", provider=ModelProvider.HUGGINGFACE, description="EleutherAI's 20B model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.0002, 0.0004), context_window=2048, max_output_tokens=2048, rating=4.5, usage_count=54000, monthly_active_users=28000))
        self.add_model(AIModel(id="alphac odegen", name="AlphaCodegen", provider=ModelProvider.ANTHROPIC, description="Code generation from Anthropic", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.CODE_EXPLANATION], pricing=ModelPricing(0.005, 0.015), context_window=8000, max_output_tokens=2048, rating=4.7, usage_count=85000, monthly_active_users=45000))
        self.add_model(AIModel(id="palm-2", name="Google PaLM 2", provider=ModelProvider.GOOGLE_GEMINI, description="Large language model from Google", version="2.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.001, 0.002), context_window=32000, max_output_tokens=8000, rating=4.8, usage_count=122000, monthly_active_users=68000))
        self.add_model(AIModel(id="chinchilla", name="DeepMind Chinchilla", provider=ModelProvider.HUGGINGFACE, description="Efficiency-focused model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.00012, 0.00024), context_window=8192, max_output_tokens=2048, rating=4.6, usage_count=71000, monthly_active_users=37000))
        self.add_model(AIModel(id="aligned-instruct", name="Aligned Instruct", provider=ModelProvider.HUGGINGFACE, description="Instruction-aligned model", version="7b", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS], pricing=ModelPricing(0.0001, 0.0002), context_window=2048, max_output_tokens=1024, rating=4.3, usage_count=44000, monthly_active_users=22000))
        self.add_model(AIModel(id="solar-10.7b", name="SOLAR 10.7B", provider=ModelProvider.HUGGINGFACE, description="Korean-optimized model", version="1.0", capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.REASONING], pricing=ModelPricing(0.00015, 0.0003), context_window=4096, max_output_tokens=2048, rating=4.4, usage_count=48000, monthly_active_users=25000))
        self.add_model(AIModel(id="neural-chat-7b", name="Neural Chat 7B", provider=ModelProvider.HUGGINGFACE, description="Chat-optimized neural model", version="1.0", capabilities=[ModelCapability.TEXT_ANALYSIS, ModelCapability.CODE_GENERATION], pricing=ModelPricing(0.00012, 0.00024), context_window=4096, max_output_tokens=2048, rating=4.5, usage_count=56000, monthly_active_users=29000))
    
    def add_model(self, model: AIModel) -> str:
        """Add a model to the registry"""
        self.models[model.id] = model
        return model.id
    
    def get_model(self, model_id: str) -> Optional[AIModel]:
        """Get a specific model by ID"""
        return self.models.get(model_id)
    
    def list_all_models(self, skip: int = 0, limit: int = 50) -> Tuple[List[AIModel], int]:
        """List all models with pagination"""
        models_list = list(self.models.values())
        total = len(models_list)
        return models_list[skip:skip + limit], total
    
    def search_models(
        self,
        query: str,
        provider: Optional[ModelProvider] = None,
        min_rating: float = 0.0,
        capability: Optional[ModelCapability] = None,
        max_price: Optional[float] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[AIModel], int]:
        """Search models by various criteria"""
        
        results = []
        
        for model in self.models.values():
            # Provider filter
            if provider and model.provider != provider:
                continue
            
            # Rating filter
            if model.rating < min_rating:
                continue
            
            # Capability filter
            if capability and capability not in model.capabilities:
                continue
            
            # Price filter (average of input/output)
            if max_price:
                avg_price = (model.pricing.input_cost_per_1k_tokens + 
                           model.pricing.output_cost_per_1k_tokens) / 2
                if avg_price > max_price:
                    continue
            
            # Text search (name, description)
            query_lower = query.lower()
            if query_lower in model.name.lower() or query_lower in model.description.lower():
                results.append(model)
        
        # Sort by relevance (rating * usage)
        results.sort(key=lambda m: m.rating * (m.usage_count / 1000), reverse=True)
        
        # Log search
        self.search_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': len(results)
        })
        
        total = len(results)
        return results[skip:skip + limit], total
    
    def get_recommended_models(
        self,
        use_case: str,
        budget: str = "medium"
    ) -> List[AIModel]:
        """Get recommended models for a specific use case"""
        
        recommendations = []
        
        # Cost budgets
        budget_prices = {
            "cheap": 0.0005,
            "medium": 0.01,
            "expensive": float('inf')
        }
        
        max_price = budget_prices.get(budget, 0.01)
        
        # Use case to capabilities mapping
        use_case_capabilities = {
            "code_generation": [
                ModelCapability.CODE_GENERATION,
                ModelCapability.REASONING
            ],
            "code_completion": [
                ModelCapability.CODE_COMPLETION,
                ModelCapability.CODE_GENERATION
            ],
            "debugging": [
                ModelCapability.CODE_EXPLANATION,
                ModelCapability.BUG_DETECTION
            ],
            "refactoring": [
                ModelCapability.REFACTORING,
                ModelCapability.CODE_EXPLANATION
            ],
            "documentation": [
                ModelCapability.DOCUMENTATION,
                ModelCapability.CODE_EXPLANATION
            ]
        }
        
        required_caps = use_case_capabilities.get(use_case, [])
        
        for model in self.models.values():
            # Check if model has required capabilities
            has_required = any(cap in model.capabilities for cap in required_caps)
            if not has_required:
                continue
            
            # Check price
            avg_price = (model.pricing.input_cost_per_1k_tokens + 
                       model.pricing.output_cost_per_1k_tokens) / 2
            if avg_price > max_price and avg_price > 0:
                continue
            
            recommendations.append(model)
        
        # Sort by rating * usage
        recommendations.sort(
            key=lambda m: m.rating * (m.usage_count / 1000),
            reverse=True
        )
        
        return recommendations[:3]
    
    def update_usage_count(self, model_id: str, increment: int = 1) -> bool:
        """Update model usage count"""
        if model_id not in self.models:
            return False
        
        self.models[model_id].usage_count += increment
        self.models[model_id].monthly_active_users = max(
            self.models[model_id].monthly_active_users,
            int(self.models[model_id].usage_count * 0.3)
        )
        self.total_usage += increment
        return True
    
    def get_statistics(self) -> Dict:
        """Get registry statistics"""
        return {
            'total_models': len(self.models),
            'total_usage': self.total_usage,
            'top_model': max(
                self.models.values(),
                key=lambda m: m.usage_count
            ).name if self.models else None,
            'avg_rating': sum(m.rating for m in self.models.values()) / len(self.models) if self.models else 0,
            'providers': list(set(m.provider.value for m in self.models.values())),
            'recent_searches': len(self.search_history)
        }


# Global registry instance
registry = AIMarketplaceRegistry()
