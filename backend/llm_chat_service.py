"""
LLM Chat Service - Unified interface for streaming chat responses
Supports OpenAI, Google Gemini, Anthropic Claude, and local LLMs (Ollama, etc.)
"""

import os
import json
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any
from pathlib import Path
import urllib.request
import urllib.error


class LLMChatService:
    """Unified service for streaming LLM responses"""
    
    def __init__(self, llm_config: Dict[str, Any]):
        """
        Initialize chat service with LLM configuration
        
        Args:
            llm_config: Dict with keys: id, name, type (cloud|local), source, has_credentials
        """
        self.llm_config = llm_config
        self.llm_id = llm_config.get("id")
        self.llm_name = llm_config.get("name")
        self.llm_type = llm_config.get("type", "cloud")
        self.llm_source = llm_config.get("source", "unknown")
        
    async def stream_chat(self, message: str, conversation_history: list = None) -> AsyncGenerator[str, None]:
        """
        Stream a chat response from the LLM
        
        Args:
            message: User message to send to LLM
            conversation_history: List of prior messages for context
            
        Yields:
            Text chunks from the LLM response
        """
        if self.llm_source == "openai":
            async for chunk in self._stream_openai(message, conversation_history or []):
                yield chunk
        elif self.llm_source == "google":
            async for chunk in self._stream_google_gemini(message, conversation_history or []):
                yield chunk
        elif self.llm_source == "anthropic":
            async for chunk in self._stream_anthropic_claude(message, conversation_history or []):
                yield chunk
        elif self.llm_source == "ollama":
            async for chunk in self._stream_ollama(message, conversation_history or []):
                yield chunk
        elif self.llm_source == "gpt4all":
            async for chunk in self._stream_gpt4all(message, conversation_history or []):
                yield chunk
        else:
            # Fallback demo response
            async for chunk in self._stream_demo(message):
                yield chunk
    
    async def _stream_openai(self, message: str, history: list) -> AsyncGenerator[str, None]:
        """Stream response from OpenAI GPT-4/3.5"""
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                yield "[Q Assistant] OpenAI API key not set. Go to LLM Setup to configure credentials."
                return
            
            # Prepare messages with conversation history
            messages = [
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                for msg in history[-6:]  # Keep last 6 messages for context
            ]
            messages.append({"role": "user", "content": message})
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = json.dumps({
                "model": "gpt-4" if "gpt-4" in self.llm_id.lower() else "gpt-3.5-turbo",
                "messages": messages,
                "stream": True,
                "temperature": 0.7,
                "max_tokens": 2000
            })
            
            req = urllib.request.Request(url, data=data.encode('utf-8'), headers=headers, method='POST')
            
            loop = asyncio.get_event_loop()
            
            def fetch_stream():
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        buffer = ""
                        while True:
                            chunk = response.read(1024)
                            if not chunk:
                                break
                            buffer += chunk.decode('utf-8', errors='ignore')
                            lines = buffer.split('\n')
                            buffer = lines[-1]  # Keep incomplete line
                            
                            for line in lines[:-1]:
                                if line.startswith('data: '):
                                    data_str = line[6:].strip()
                                    if data_str and data_str != '[DONE]':
                                        try:
                                            data = json.loads(data_str)
                                            if 'choices' in data and len(data['choices']) > 0:
                                                delta = data['choices'][0].get('delta', {})
                                                if 'content' in delta:
                                                    yield delta['content']
                                        except json.JSONDecodeError:
                                            pass
                except Exception as e:
                    yield f"\n\n[Error: {str(e)}]"
            
            for chunk in fetch_stream():
                yield chunk
                await asyncio.sleep(0)  # Allow other tasks to run
                
        except Exception as e:
            yield f"[Error connecting to OpenAI: {str(e)}]"
    
    async def _stream_google_gemini(self, message: str, history: list) -> AsyncGenerator[str, None]:
        """Stream response from Google Gemini"""
        try:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                yield "[Q Assistant] Google API key not set. Go to LLM Setup to configure credentials."
                return
            
            messages = [
                {"role": "user" if msg.get("role") == "user" else "model", "parts": [{"text": msg.get("content", "")}]}
                for msg in history[-6:]
            ]
            messages.append({"role": "user", "parts": [{"text": message}]})
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            data = json.dumps({
                "contents": messages,
                "generation_config": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2000
                }
            })
            
            req = urllib.request.Request(url, data=data.encode('utf-8'), headers=headers, method='POST')
            
            def fetch_stream():
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        for line in response:
                            line_str = line.decode('utf-8', errors='ignore').strip()
                            if line_str.startswith('data: '):
                                try:
                                    data = json.loads(line_str[6:])
                                    if 'candidates' in data and len(data['candidates']) > 0:
                                        content = data['candidates'][0].get('content', {})
                                        if 'parts' in content and len(content['parts']) > 0:
                                            text = content['parts'][0].get('text', '')
                                            if text:
                                                yield text
                                except json.JSONDecodeError:
                                    pass
                except Exception as e:
                    yield f"\n\n[Error: {str(e)}]"
            
            loop = asyncio.get_event_loop()
            for chunk in fetch_stream():
                yield chunk
                await asyncio.sleep(0)
                
        except Exception as e:
            yield f"[Error connecting to Google Gemini: {str(e)}]"
    
    async def _stream_anthropic_claude(self, message: str, history: list) -> AsyncGenerator[str, None]:
        """Stream response from Anthropic Claude"""
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                yield "[Q Assistant] Anthropic API key not set. Go to LLM Setup to configure credentials."
                return
            
            messages = [
                {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                for msg in history[-6:]
            ]
            messages.append({"role": "user", "content": message})
            
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = json.dumps({
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 2000,
                "stream": True,
                "messages": messages,
                "system": "You are Q Assistant, a helpful AI coding assistant integrated into the Q-IDE development environment. Provide clear, concise, and helpful responses."
            })
            
            req = urllib.request.Request(url, data=data.encode('utf-8'), headers=headers, method='POST')
            
            def fetch_stream():
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        buffer = ""
                        while True:
                            chunk = response.read(1024)
                            if not chunk:
                                break
                            buffer += chunk.decode('utf-8', errors='ignore')
                            lines = buffer.split('\n')
                            buffer = lines[-1]
                            
                            for line in lines[:-1]:
                                if line.startswith('data: '):
                                    data_str = line[6:].strip()
                                    if data_str:
                                        try:
                                            data = json.loads(data_str)
                                            if data.get('type') == 'content_block_delta':
                                                delta = data.get('delta', {})
                                                if 'text' in delta:
                                                    yield delta['text']
                                        except json.JSONDecodeError:
                                            pass
                except Exception as e:
                    yield f"\n\n[Error: {str(e)}]"
            
            for chunk in fetch_stream():
                yield chunk
                await asyncio.sleep(0)
                
        except Exception as e:
            yield f"[Error connecting to Anthropic Claude: {str(e)}]"
    
    async def _stream_ollama(self, message: str, history: list) -> AsyncGenerator[str, None]:
        """Stream response from local Ollama"""
        try:
            ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
            model = "mistral"  # Default model, can be configured
            
            # Build context from history
            context = ""
            for msg in history[-6:]:
                role = msg.get("role", "user")
                context += f"{role}: {msg.get('content', '')}\n"
            
            prompt = context + f"assistant: Based on the above conversation, respond to: {message}"
            
            url = f"{ollama_url}/api/generate"
            headers = {"Content-Type": "application/json"}
            data = json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": True,
                "temperature": 0.7
            })
            
            req = urllib.request.Request(url, data=data.encode('utf-8'), headers=headers, method='POST')
            
            def fetch_stream():
                try:
                    with urllib.request.urlopen(req, timeout=60) as response:
                        while True:
                            chunk = response.read(1024)
                            if not chunk:
                                break
                            lines = chunk.decode('utf-8', errors='ignore').split('\n')
                            for line in lines:
                                if line.strip():
                                    try:
                                        data = json.loads(line)
                                        if 'response' in data:
                                            yield data['response']
                                    except json.JSONDecodeError:
                                        pass
                except urllib.error.URLError:
                    yield "[Q Assistant] Ollama not running on http://127.0.0.1:11434. Start Ollama or configure OLLAMA_URL."
                except Exception as e:
                    yield f"\n\n[Error: {str(e)}]"
            
            for chunk in fetch_stream():
                yield chunk
                await asyncio.sleep(0)
                
        except Exception as e:
            yield f"[Error connecting to Ollama: {str(e)}]"
    
    async def _stream_gpt4all(self, message: str, history: list) -> AsyncGenerator[str, None]:
        """Stream response from GPT4All local model"""
        try:
            # GPT4All requires local model files
            yield "[Q Assistant] GPT4All support coming soon. Use Ollama for local models."
        except Exception as e:
            yield f"[Error with GPT4All: {str(e)}]"
    
    async def _stream_demo(self, message: str) -> AsyncGenerator[str, None]:
        """Stream a demo response"""
        demo_response = f"""I'm your Q Assistant powered by {self.llm_name}! 

You asked: "{message}"

I'm ready to help with:
• Code generation and debugging
• Architecture and design decisions
• Documentation and comments
• Testing and optimization
• Questions about your codebase

Since the LLM backend isn't fully connected yet, I'm in demo mode. When you configure your LLM (OpenAI, Google Gemini, Anthropic Claude, or local Ollama), I'll provide real AI responses!

To get started:
1. Go to LLM Setup in the sidebar
2. Add your provider credentials
3. Assign an LLM to the "Code Generation" role
4. Come back here and ask away!"""
        
        for chunk in demo_response:
            yield chunk
            await asyncio.sleep(0.02)  # Simulate streaming


async def get_q_assistant_chat_service() -> Optional[LLMChatService]:
    """Get initialized chat service for Q Assistant"""
    from llm_config import get_q_assistant_llm
    
    llm_config = get_q_assistant_llm()
    if not llm_config:
        return None
    
    return LLMChatService(llm_config)
