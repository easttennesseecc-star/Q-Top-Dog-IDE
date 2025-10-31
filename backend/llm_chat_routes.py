"""
Q Assistant Chat API Routes - Real LLM integration with streaming
"""

from fastapi import APIRouter, Body, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
from llm_chat_service import get_q_assistant_chat_service
from simple_q_assistant import get_simple_response
from middleware.tier_validator import require_tier_access

logger = logging.getLogger("q-ide-topdog")
router = APIRouter(prefix="/api/chat", tags=["Q Assistant Chat"])

# Simple in-memory conversation storage (use database for production)
_conversations: Dict[str, List[Dict[str, str]]] = {}


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    include_history: bool = True


@router.post("/")
async def chat_stream(
    request: ChatRequest = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(lambda: require_tier_access(
        feature='code_execution',
        user_id=user_id
    ))
):
    """
    Stream a response from Q Assistant's assigned LLM
    
    Request body:
    {
      "message": "Your question here",
      "conversation_id": "optional-id-for-context",
      "include_history": true
    }
    
    Response: Server-sent events stream with chunks of the response
    
    Tier Requirements: PRO or higher (code_execution feature)
    """
    try:
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        logger.info(f"Chat request: {request.message[:100]}")
        
        # Get conversation history if requested
        history = []
        conv_id = request.conversation_id or "default"
        
        if request.include_history and conv_id in _conversations:
            history = _conversations[conv_id][-10:]  # Last 10 messages for context
        
        # Add user message to history
        user_msg = {"role": "user", "content": request.message}
        if conv_id not in _conversations:
            _conversations[conv_id] = []
        _conversations[conv_id].append(user_msg)
        
        async def stream_response():
            """Generator for streaming response chunks"""
            try:
                full_response = ""
                
                # Try to get real LLM response first
                chat_service = await get_q_assistant_chat_service()
                
                if chat_service:
                    # Stream response from real LLM
                    async for chunk in chat_service.stream_chat(request.message, history):
                        full_response += chunk
                        
                        # Send as SSE (Server-Sent Events)
                        event = {
                            "type": "chunk",
                            "data": chunk,
                            "llm": chat_service.llm_name
                        }
                        yield f"data: {json.dumps(event)}\n\n"
                        await asyncio.sleep(0)  # Allow other tasks
                else:
                    # Fallback to simple intelligent responses
                    full_response = get_simple_response(request.message, history)
                    
                    # Stream the response character by character for natural feeling
                    for char in full_response:
                        event = {
                            "type": "chunk",
                            "data": char,
                            "llm": "Q Assistant (Smart Responses)"
                        }
                        yield f"data: {json.dumps(event)}\n\n"
                        await asyncio.sleep(0.01)  # Slight delay for natural streaming
                
                # Add to conversation history
                assistant_msg = {"role": "assistant", "content": full_response}
                _conversations[conv_id].append(assistant_msg)
                
                # Send completion event
                completion_event = {
                    "type": "done",
                    "message": "Response complete",
                    "total_length": len(full_response),
                    "llm": chat_service.llm_name if chat_service else "Q Assistant (Smart Responses)"
                }
                yield f"data: {json.dumps(completion_event)}\n\n"
                
                logger.info(
                    "Chat response completed",
                    extra={
                        "llm": chat_service.llm_name if chat_service else "SmartResponses",
                        "message_length": len(request.message),
                        "response_length": len(full_response)
                    }
                )
                
            except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}")
                error_event = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_event)}\n\n"
        
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/clear-history")
async def clear_conversation(conversation_id: str = "default"):
    """Clear conversation history for a given conversation ID"""
    if conversation_id in _conversations:
        _conversations.pop(conversation_id)
    return {"status": "ok", "message": f"Cleared history for {conversation_id}"}


@router.get("/history/{conversation_id}")
async def get_conversation_history(conversation_id: str = "default"):
    """Get conversation history"""
    history = _conversations.get(conversation_id, [])
    return {
        "status": "ok",
        "conversation_id": conversation_id,
        "messages": history,
        "message_count": len(history)
    }


@router.post("/voice/transcribe")
async def transcribe_audio(audio_base64: str = Body(...)):
    """
    Transcribe voice to text using assigned LLM's speech-to-text
    
    For now, uses browser's Web Speech API
    Production: Use Whisper API or other speech-to-text service
    """
    try:
        # In production, decode base64 audio and send to speech-to-text service
        # For now, this is handled by browser's Web Speech API in frontend
        return {
            "status": "ok",
            "message": "Use browser Web Speech API (frontend) or configure Whisper for backend transcription"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice/synthesize")
async def text_to_speech(text: str = Body(...)):
    """
    Convert text to speech using assigned LLM's text-to-speech
    
    For now, uses browser's Web Speech Synthesis API
    Production: Use Google Text-to-Speech or other TTS service
    """
    try:
        # In production, use a TTS service
        # For now, this is handled by browser's Web Speech Synthesis API
        return {
            "status": "ok",
            "message": "Use browser Web Speech Synthesis API (frontend) or configure Google TTS for backend"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Import at end to avoid circular imports
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    include_history: bool = True
