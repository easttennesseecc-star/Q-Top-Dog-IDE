"""
Multi-Provider AI API Router
Routes requests to OpenAI, Anthropic, Gemini, HuggingFace, Ollama
"""

from typing import Optional, Dict, List, AsyncIterator, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import json
from datetime import datetime


class ProviderType(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE_GEMINI = "google_gemini"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


@dataclass
class ChatMessage:
    """Represents a message in conversation"""
    role: str  # "user", "assistant", "system"
    content: str


@dataclass
class ProviderConfig:
    """Configuration for a provider"""
    type: ProviderType
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


class TokenCounter(ABC):
    """Base class for token counting"""
    
    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass
    
    @abstractmethod
    def estimate_completion_tokens(self, prompt_tokens: int) -> int:
        """Estimate tokens in completion"""
        pass


class OpenAITokenCounter(TokenCounter):
    """Token counter for OpenAI models"""
    
    def count_tokens(self, text: str) -> int:
        """Rough approximation: ~4 chars per token"""
        return len(text) // 4
    
    def estimate_completion_tokens(self, prompt_tokens: int) -> int:
        """Estimate completion tokens (typically 30% of prompt)"""
        return int(prompt_tokens * 0.3)


class AnthropicTokenCounter(TokenCounter):
    """Token counter for Anthropic models"""
    
    def count_tokens(self, text: str) -> int:
        """Rough approximation: ~3.5 chars per token"""
        return int(len(text) / 3.5)
    
    def estimate_completion_tokens(self, prompt_tokens: int) -> int:
        return int(prompt_tokens * 0.25)


class AIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, config: ProviderConfig):
        """Initialize provider with config"""
        self.config = config
        self.token_counter: Optional[TokenCounter] = None
        self.request_count = 0
        self.total_tokens = 0
    
    @abstractmethod
    async def send_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, int]:
        """Send message and get response"""
        pass
    
    @abstractmethod
    def stream_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream message response"""
        raise NotImplementedError
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.token_counter:
            return self.token_counter.count_tokens(text)
        return len(text) // 4  # Default approximation


class OpenAIProvider(AIProvider):
    """OpenAI API provider"""
    
    MODELS = {
        "gpt4-turbo": "gpt-4-turbo-preview",
        "gpt4": "gpt-4",
        "gpt-35-turbo": "gpt-3.5-turbo"
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize OpenAI provider"""
        super().__init__(config)
        self.token_counter = OpenAITokenCounter()
        # Set default headers
        self.config.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, int]:
        """Send request to OpenAI"""
        
        # In real implementation, use httpx or aiohttp
        payload = {
            "model": self.MODELS.get(model, model),
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Simulate API call
        self.request_count += 1
        
        # Count tokens for billing
        prompt_text = "\n".join([msg.content for msg in messages])
        prompt_tokens = self.count_tokens(prompt_text)
        completion_tokens = (
            self.token_counter.estimate_completion_tokens(prompt_tokens)
            if self.token_counter else int(prompt_tokens * 0.3)
        )
        
        self.total_tokens += prompt_tokens + completion_tokens
        
        # Simulated response
        response_text = "This is a simulated OpenAI response. In production, call the actual API."
        
        return response_text, prompt_tokens + completion_tokens
    
    async def stream_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream response from OpenAI"""
        
        payload = {
            "model": self.MODELS.get(model, model),
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True
        }
        
        # Simulate streaming response
        self.request_count += 1
        
        # In real implementation, iterate over streaming response
        sample_response = "This is a simulated streaming response. In production, implement streaming."
        for word in sample_response.split():
            yield word + " "


class AnthropicProvider(AIProvider):
    """Anthropic API provider"""
    
    MODELS = {
        "claude-opus": "claude-3-opus-20240229",
        "claude-sonnet": "claude-3-sonnet-20240229",
        "claude-haiku": "claude-3-haiku-20240307"
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize Anthropic provider"""
        super().__init__(config)
        self.token_counter = AnthropicTokenCounter()
        self.config.headers = {
            "x-api-key": config.api_key or "",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def send_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, int]:
        """Send request to Anthropic"""
        
        payload = {
            "model": self.MODELS.get(model, model),
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        self.request_count += 1
        
        prompt_text = "\n".join([msg.content for msg in messages])
        prompt_tokens = self.count_tokens(prompt_text)
        completion_tokens = (
            self.token_counter.estimate_completion_tokens(prompt_tokens)
            if self.token_counter else int(prompt_tokens * 0.25)
        )
        
        self.total_tokens += prompt_tokens + completion_tokens
        
        response_text = "Anthropic simulated response."
        
        return response_text, prompt_tokens + completion_tokens
    
    async def stream_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream response from Anthropic"""
        
        self.request_count += 1
        
        sample_response = "Anthropic streaming response simulation."
        for word in sample_response.split():
            yield word + " "


class GoogleGeminiProvider(AIProvider):
    """Google Gemini API provider"""
    
    MODELS = {
        "gemini-pro": "gemini-1.5-pro",
        "gemini-flash": "gemini-1.5-flash"
    }
    
    def __init__(self, config: ProviderConfig):
        """Initialize Google Gemini provider"""
        super().__init__(config)
        self.config.headers = {
            "x-goog-api-key": config.api_key or "",
            "content-type": "application/json"
        }
    
    async def send_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, int]:
        """Send request to Gemini"""
        
        self.request_count += 1
        prompt_text = "\n".join([msg.content for msg in messages])
        tokens = self.count_tokens(prompt_text)
        
        return "Gemini simulated response.", tokens
    
    async def stream_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream response from Gemini"""
        
        self.request_count += 1
        for word in "Gemini streaming response.".split():
            yield word + " "


class HuggingFaceProvider(AIProvider):
    """HuggingFace Inference API provider"""
    
    def __init__(self, config: ProviderConfig):
        """Initialize HuggingFace provider"""
        super().__init__(config)
        self.config.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json"
        }
    
    async def send_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, int]:
        """Send request to HuggingFace"""
        
        self.request_count += 1
        prompt_text = "\n".join([msg.content for msg in messages])
        tokens = self.count_tokens(prompt_text)
        
        return "HuggingFace simulated response.", tokens
    
    async def stream_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream response from HuggingFace"""
        
        self.request_count += 1
        for word in "HuggingFace streaming response.".split():
            yield word + " "


class OllamaProvider(AIProvider):
    """Ollama local provider"""
    
    def __init__(self, config: ProviderConfig):
        """Initialize Ollama provider"""
        super().__init__(config)
        self.config.api_url = config.api_url or "http://localhost:11434"
        self.config.headers = {"Content-Type": "application/json"}
    
    async def send_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> Tuple[str, int]:
        """Send request to Ollama"""
        
        self.request_count += 1
        prompt_text = "\n".join([msg.content for msg in messages])
        tokens = self.count_tokens(prompt_text)
        
        return "Ollama local response.", tokens
    
    async def stream_message(
        self,
        messages: List[ChatMessage],
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncIterator[str]:
        """Stream response from Ollama"""
        
        self.request_count += 1
        for word in "Ollama streaming response.".split():
            yield word + " "


class AIAPIRouter:
    """Routes requests to the appropriate AI provider"""
    
    def __init__(self):
        """Initialize the router"""
        self.providers: Dict[ProviderType, AIProvider] = {}
        self.model_provider_map: Dict[str, ProviderType] = {}
        self.request_log: List[Dict] = []
    
    def register_provider(self, provider: AIProvider, provider_type: ProviderType):
        """Register a provider"""
        self.providers[provider_type] = provider
    
    def register_model(self, model_id: str, provider_type: ProviderType):
        """Register which provider handles a model"""
        self.model_provider_map[model_id] = provider_type
    
    def get_provider_for_model(self, model_id: str) -> Optional[AIProvider]:
        """Get provider for a model"""
        provider_type = self.model_provider_map.get(model_id)
        if provider_type:
            return self.providers.get(provider_type)
        return None
    
    async def send_message(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        user_id: Optional[str] = None
    ) -> Tuple[bool, str, int]:
        """Send message via appropriate provider"""
        
        provider = self.get_provider_for_model(model_id)
        if not provider:
            return False, f"No provider for model {model_id}", 0
        
        response, tokens = await provider.send_message(
            messages, model_id, temperature, max_tokens
        )
        
        # Log request
        self._log_request(model_id, user_id, tokens)
        
        return True, response, tokens
    
    async def stream_message(
        self,
        model_id: str,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        user_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Stream message via appropriate provider"""
        
        provider = self.get_provider_for_model(model_id)
        if not provider:
            yield f"Error: No provider for model {model_id}"
            return
        
        async for chunk in provider.stream_message(
            messages, model_id, temperature, max_tokens
        ):
            yield chunk
        
        # Log request
        self._log_request(model_id, user_id, 0)  # Token count would be tracked separately
    
    def _log_request(self, model_id: str, user_id: Optional[str], tokens: int):
        """Log an API request"""
        self.request_log.append({
            'timestamp': datetime.now().isoformat(),
            'model_id': model_id,
            'user_id': user_id,
            'tokens': tokens
        })
    
    def get_statistics(self) -> Dict:
        """Get router statistics"""
        total_requests = len(self.request_log)
        total_tokens = sum(r['tokens'] for r in self.request_log)
        
        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'registered_providers': len(self.providers),
            'registered_models': len(self.model_provider_map),
            'avg_tokens_per_request': total_tokens / total_requests if total_requests > 0 else 0
        }


# Global router instance
router = AIAPIRouter()
