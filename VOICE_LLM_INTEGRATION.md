# Q Assistant - Voice-Enabled LLM Integration

## Overview

Q Assistant is now a fully-featured voice-enabled AI assistant with real LLM integration, similar to Google Gemini. It supports:

✅ **Voice Input** - Web Speech API for voice recording/transcription
✅ **Voice Output** - Web Speech Synthesis for text-to-speech responses  
✅ **Real LLM Integration** - Streaming responses from multiple providers
✅ **Conversation Context** - Full conversation history for context awareness
✅ **Multi-Provider Support** - OpenAI, Google Gemini, Anthropic Claude, Ollama, GPT4All
✅ **Auto-Speak** - Automatically reads responses aloud

## Architecture

### Frontend Components

**QAssistantChat.tsx**
- Voice input via Web Speech Recognition API
- Voice output via Web Speech Synthesis API
- Real-time streaming UI updates
- Microphone button with listening indicator
- Conversation display with auto-scroll
- Mic-only mode for hands-free operation

### Backend Services

**llm_chat_service.py**
- `LLMChatService` class for unified LLM streaming
- Supports 5+ LLM providers
- Async streaming responses
- Automatic API key detection
- Conversation context handling

**llm_chat_routes.py**
- `/api/chat/` - Main streaming endpoint
- `/api/chat/clear-history` - Clear conversation
- `/api/chat/history/{id}` - Get conversation history
- `/api/chat/voice/transcribe` - Voice to text
- `/api/chat/voice/synthesize` - Text to voice
- Server-Sent Events (SSE) streaming

### Integration Points

1. **Frontend → Backend**
   - POST `/api/chat/` with message
   - Receives SSE stream of response chunks
   - Updates UI in real-time

2. **Backend → LLM Providers**
   - Gets assigned LLM from `/llm_config/q_assistant`
   - Uses provider-specific API (OpenAI, Google, Anthropic, etc.)
   - Streams response back to frontend

3. **Voice Pipeline**
   - Browser records audio → Web Speech API transcribes
   - Text sent to `/api/chat/`
   - Response streamed back
   - Web Speech Synthesis reads response aloud

## How to Use

### Setting Up Q Assistant

1. **Go to LLM Setup** (left sidebar)
2. **Select a Provider:**
   - **Cloud:** OpenAI, Google Gemini, Anthropic Claude, xAI, Perplexity
   - **Local:** Ollama, LLaMA.cpp, GPT4All
3. **Add Credentials** for your chosen provider
4. **Assign to "Code Generation" role** 
5. **Return to Q Assistant** - Ready to use!

### Using Voice

**Start Speaking:**
- Click the **Voice** button (microphone icon)
- Button shows "Listening" when active
- Speak your question
- Click again or say "send" to submit

**Keyboard Shortcuts:**
- `Ctrl+M` - Toggle microphone on/off
- `Ctrl+K` - Focus text input
- `Ctrl+Enter` - Send message
- `Escape` - Stop listening
- `Enter` - Send message
- `Shift+Enter` - New line in text

**Mic-Only Mode:**
- Click "Mic-only: Off/On" button
- Switches to large "Tap to Record" button
- Perfect for voice-first interaction

### Conversation Context

Q Assistant automatically maintains your conversation history:
- Last 10 messages used for context
- Full conversation stored on backend
- Maintains same conversation until cleared
- Easy to reference previous questions

## Provider Setup

### OpenAI (GPT-4 / GPT-3.5)

```
1. Go to https://platform.openai.com/api-keys
2. Create API key
3. LLM Setup → Add Credentials → OpenAI
4. Paste your API key
5. Assign GPT-4 to "Code Generation" role
```

**Models Available:**
- gpt-4 (best quality, $0.03-0.06 per 1K tokens)
- gpt-3.5-turbo (fast, $0.0005-0.0015 per 1K tokens)

### Google Gemini

```
1. Go to https://ai.google.dev/
2. Create API key
3. LLM Setup → Add Credentials → Google
4. Paste your API key
5. Assign Gemini Pro to "Code Generation" role
```

**Models Available:**
- gemini-pro (multimodal, free for most users)

### Anthropic Claude

```
1. Go to https://console.anthropic.com/
2. Create API key
3. LLM Setup → Add Credentials → Anthropic
4. Paste your API key
5. Assign Claude 3.5 Sonnet to "Code Generation" role
```

**Models Available:**
- claude-3-5-sonnet (best for coding)
- claude-3-opus (most capable)
- claude-3-haiku (fast, budget-friendly)

### Local: Ollama

```
1. Install Ollama: https://ollama.ai
2. Run: ollama serve
3. In another terminal: ollama pull mistral
4. LLM Setup → Ollama section
5. Status shows "Detected" when running
6. Assign Mistral to "Code Generation" role
```

**Models Available:**
- mistral (best balance of quality/speed)
- llama2 (good quality, larger)
- neural-chat (optimized for conversation)
- dolphin-mixtral (strong reasoning)

### Local: LLaMA.cpp

```
1. Download LLaMA.cpp: https://github.com/ggerganov/llama.cpp
2. Get a model (e.g., from Hugging Face)
3. Run: ./server -m model.gguf -ngl 33
4. LLM Setup → Detects when running
5. Assign to role
```

## Conversation Examples

### Code Help
```
User: "How do I sort a list in Python?"
Q Assistant: "You can sort a list using the sorted() function or the .sort() method.
The sorted() function returns a new sorted list, while .sort() sorts in place.

Example:
numbers = [3, 1, 4, 1, 5]
sorted_nums = sorted(numbers)  # Returns [1, 1, 3, 4, 5]

numbers.sort()  # Sorts in place
# numbers is now [1, 1, 3, 4, 5]"
```

### Architecture Questions
```
User: "How should I structure a React component?"
Q Assistant: "Here's a best-practices structure:
- Use functional components with hooks
- Props at top, component logic below
- Event handlers before render logic
- Use custom hooks for reusable logic
- Keep components focused and small

Example:
export function MyComponent({ title, onComplete }) {
  const [state, setState] = useState(null);
  
  const handleClick = () => setState(true);
  
  return <div>{title}</div>;
}"
```

### Debugging
```
User: "This code is throwing 'Cannot read property of undefined'"
Q Assistant: "This error means you're trying to access a property on something
that doesn't exist. Common causes:

1. Object is null/undefined
   Fix: Add null checks: data?.property or data?.[0]?.value

2. Response not loaded yet
   Fix: Use optional chaining or check loading state

3. Array index out of bounds
   Fix: Check array length: if (arr.length > i) { arr[i] }

Can you share the code snippet? I can help debug!"
```

## Streaming Architecture

### Frontend Flow
```
1. User speaks or types message
2. Click "Send" button
3. Frontend POSTs to /api/chat/ with message
4. Browser connects to SSE stream
5. Chunks arrive in real-time
6. UI updates character by character
7. Response auto-speaks when complete
```

### Backend Flow
```
1. Receive POST /api/chat/ request
2. Get Q Assistant's assigned LLM
3. Check if LLM has credentials
4. Stream async generator:
   - Call LLM API (OpenAI, Google, etc.)
   - Parse response stream
   - Send chunks as SSE events
   - Maintain conversation history
5. Send "done" event when complete
```

### LLM Provider Flow
```
1. Backend calls LLM API
2. LLM returns streaming response
3. Backend yields chunks immediately
4. No buffering - real-time feel
5. Complete response stored for context
```

## API Endpoints

### Main Chat Endpoint

**POST /api/chat/**

Request:
```json
{
  "message": "How do I import a module?",
  "conversation_id": "default",
  "include_history": true
}
```

Response (SSE Stream):
```
data: {"type": "chunk", "data": "You", "llm": "GPT-4"}
data: {"type": "chunk", "data": " can", "llm": "GPT-4"}
data: {"type": "chunk", "data": " import", "llm": "GPT-4"}
...
data: {"type": "done", "total_length": 245, "llm": "GPT-4"}
```

### Get Conversation History

**GET /api/chat/history/{conversation_id}**

Response:
```json
{
  "status": "ok",
  "conversation_id": "default",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ],
  "message_count": 2
}
```

### Clear Conversation

**POST /api/chat/clear-history**

Params: `conversation_id=default`

Response:
```json
{
  "status": "ok",
  "message": "Cleared history for default"
}
```

## Configuration Files

### ~/.q-ide/llm_roles.json
```json
{
  "coding": {
    "model": "gpt-4",
    "source": "openai",
    "last_updated": "2025-10-26T23:40:00Z"
  }
}
```

### Environment Variables

```bash
# OpenAI
OPENAI_API_KEY=sk-proj-xxxxx

# Google Gemini
GOOGLE_API_KEY=xxxxx

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Ollama (local)
OLLAMA_URL=http://127.0.0.1:11434

# Backend
BACKEND_URL=http://127.0.0.1:8000
ALLOWED_HOST=localhost,127.0.0.1
```

## Keyboard Shortcuts Reference

| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Focus text input |
| `Ctrl+M` | Toggle microphone |
| `Ctrl+Enter` | Send message |
| `Enter` | Send message |
| `Shift+Enter` | New line in text |
| `Escape` | Stop listening |

## Features

### Current ✅

- [x] Voice input (Web Speech API)
- [x] Voice output (Web Speech Synthesis)
- [x] OpenAI GPT-4/3.5 streaming
- [x] Google Gemini streaming
- [x] Anthropic Claude streaming
- [x] Ollama local LLM support
- [x] Conversation history
- [x] Streaming UI updates
- [x] Auto-speak responses
- [x] Error handling
- [x] Multiple provider support
- [x] LLM role assignment

### Coming Soon 🚀

- [ ] GPT4All support
- [ ] LLaMA.cpp HTTP integration
- [ ] Whisper API for better voice recognition
- [ ] Multiple conversations
- [ ] Conversation export/save
- [ ] Response quality feedback
- [ ] LLM performance analytics
- [ ] Custom system prompts
- [ ] Tool use (code execution, web search)
- [ ] Image input support
- [ ] Real-time collaboration

## Troubleshooting

### "Q Assistant is not configured"
- Go to LLM Setup
- Add credentials for a provider
- Assign a model to "Code Generation" role
- Return to Q Assistant

### "OpenAI API key not set"
- Go to LLM Setup → Providers → OpenAI
- Paste your API key
- Click "Save"

### "Ollama not running"
- Make sure Ollama is installed: https://ollama.ai
- Run: `ollama serve`
- Pull a model: `ollama pull mistral`
- Refresh Q Assistant

### Mic not working
- Allow microphone permissions in browser
- Check browser console for errors
- Try in Chrome/Edge (best Web Speech API support)
- Fallback to text input

### No response from LLM
- Check internet connection
- Verify API credentials
- Check backend logs: `tail -f backend/logs/*.log`
- Try a simpler question

### Response is cut off
- Increase max_tokens in llm_chat_service.py
- Check backend timeout settings
- Try a shorter conversation history

## Performance Tips

1. **Use GPT-3.5 for speed**, GPT-4 for quality
2. **Local Ollama** for privacy, no API calls
3. **Keep conversation history short** (max 10 messages)
4. **Enable mic-only mode** for voice-first use
5. **Use Mistral** for best local/cost balance

## Security Notes

⚠️ **API Keys**
- Never commit API keys to git
- Use environment variables
- Frontend never sees raw API keys
- All calls go through backend

⚠️ **Conversation History**
- Stored in-memory (database in production)
- Not persisted to disk by default
- Clear history when done sensitive work

⚠️ **Voice Data**
- Web Speech API processes locally
- Ollama keeps data local
- Cloud APIs follow their privacy policies

## Developer Notes

### Adding a New LLM Provider

1. **Create provider stream method in LLMChatService:**
```python
async def _stream_new_provider(self, message: str, history: list):
    api_key = os.getenv("NEW_PROVIDER_API_KEY")
    if not api_key:
        yield "[Config needed]"
        return
    
    # Your streaming logic here
    async for chunk in fetch_from_api():
        yield chunk
```

2. **Add to router dispatch:**
```python
elif self.llm_source == "new_provider":
    async for chunk in self._stream_new_provider(message, history):
        yield chunk
```

3. **Update LLM pool** (`llm_pool.py`) to detect provider

4. **Add UI configuration** (LLM Setup tab)

### Testing

```bash
# Test endpoint directly
curl -X POST http://127.0.0.1:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello"}'

# Test with Python
python -c "
import asyncio
from llm_chat_service import LLMChatService

config = {'id': 'gpt-4', 'name': 'GPT-4', 'source': 'openai', 'type': 'cloud'}
service = LLMChatService(config)

async def test():
    async for chunk in service.stream_chat('Hello'):
        print(chunk, end='', flush=True)

asyncio.run(test())
"
```

## Support

For issues or questions:
1. Check logs: `tail -f backend/logs/*.log`
2. Check browser console: F12 → Console tab
3. Try the demo response first
4. Verify LLM is configured in LLM Setup
5. Check API credentials and rate limits

## References

- [OpenAI API](https://platform.openai.com/docs)
- [Google Gemini API](https://ai.google.dev/docs)
- [Anthropic Claude API](https://docs.anthropic.com/claude/reference)
- [Ollama Documentation](https://github.com/ollama/ollama)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
