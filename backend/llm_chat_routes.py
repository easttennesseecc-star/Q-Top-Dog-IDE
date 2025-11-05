"""
Q Assistant Chat API Routes - Real LLM integration with streaming
"""

from fastapi import APIRouter, Body, HTTPException, Header, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import os
import json
import logging
from typing import Optional, List, Dict, Any, Tuple
import time
from backend.llm_chat_service import get_q_assistant_chat_service, LLMChatService
from backend.simple_q_assistant import get_simple_response
from backend.middleware.tier_validator import require_tier_access
from backend.llm_pool import get_best_llms_for_operations
from backend.llm_config import get_q_assistant_llm, get_model_for_role
from backend.metrics import LLM_TTFT, LLM_LATENCY, OVERWATCH_FLAGGED, LLM_TOKENS, LLM_COST_USD

logger = logging.getLogger("q-ide-topdog")
router = APIRouter(prefix="/api/chat", tags=["Q Assistant Chat"])

# Simple in-memory conversation storage (use database for production)
_conversations: Dict[str, List[Dict[str, str]]] = {}
_provider_failures: Dict[str, Dict[str, float]] = {}
_provider_circuit_open_until: Dict[str, float] = {}


def _map_source(name: str) -> str:
    n = (name or "").lower()
    if any(x in n for x in ["openai", "gpt", "chatgpt"]):
        return "openai"
    if "gemini" in n or "google" in n:
        return "google"
    if "claude" in n or "anthropic" in n:
        return "anthropic"
    if "ollama" in n or "llama" in n:
        return "ollama"
    if "gpt4all" in n:
        return "gpt4all"
    return "unknown"


def _env_cost_rate(model_name: str, provider: str) -> tuple[Optional[float], Optional[float]]:
    """Return (in_cost_per_1k, out_cost_per_1k) from env for model/provider.
    Looks up COST_PER_1K_INPUT_{MODEL_KEY} then provider fallback COST_PER_1K_INPUT_{PROVIDER}.
    Same for output. Returns None if not configured.
    """
    def norm(s: str) -> str:
        return "".join(ch if ch.isalnum() else "_" for ch in (s or "")).upper()
    mkey = norm(model_name)
    pkey = norm(provider)
    in_rate = os.getenv(f"COST_PER_1K_INPUT_{mkey}") or os.getenv(f"COST_PER_1K_INPUT_{pkey}")
    out_rate = os.getenv(f"COST_PER_1K_OUTPUT_{mkey}") or os.getenv(f"COST_PER_1K_OUTPUT_{pkey}")
    try:
        in_v = float(in_rate) if in_rate is not None else None
    except Exception:
        in_v = None
    try:
        out_v = float(out_rate) if out_rate is not None else None
    except Exception:
        out_v = None
    return in_v, out_v


def _estimate_tokens(text: str) -> int:
    """Cheap heuristic: ~4 characters per token. Avoids provider-specific libraries.
    This is only used if providers don't return usage; override with true values when available.
    """
    if not text:
        return 0
    return max(1, int(len(text) / 4))


def _is_circuit_open(llm_name: str) -> bool:
    until = _provider_circuit_open_until.get(llm_name)
    return until is not None and until > time.time()


def _record_failure(llm_name: str, threshold: int = 3, ttl_secs: int = 300):
    now = time.time()
    rec = _provider_failures.setdefault(llm_name, {"count": 0, "last": 0.0})
    rec["count"] = (rec.get("count", 0) + 1)
    rec["last"] = now
    if rec["count"] >= threshold:
        _provider_circuit_open_until[llm_name] = now + ttl_secs
        rec["count"] = 0  # reset after opening circuit
        logger.warning(f"Circuit opened for {llm_name} for {ttl_secs}s")


def _record_success(llm_name: str):
    _provider_failures.pop(llm_name, None)
    _provider_circuit_open_until.pop(llm_name, None)


def _resolve_domain_triads(domain: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Read env-configured primary/secondary/overwatch for a domain."""
    dom = domain.upper()
    p = os.getenv(f"{dom}_PRIMARY_LLM")
    s = os.getenv(f"{dom}_SECONDARY_LLM")
    o = os.getenv(f"{dom}_OVERWATCH_LLM")
    return (p, s, o)


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    include_history: bool = True


def _tier_dep(user_id: str = Header(None, alias="X-User-ID")):
    """Wrapper dependency to validate tier access using the X-User-ID header."""
    return require_tier_access(feature='code_execution', user_id=user_id)


@router.post("/")
async def chat_stream(
    request: ChatRequest = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    x_domain: Optional[str] = Header(None, alias="X-Domain"),
    x_overwatch: Optional[str] = Header(None, alias="X-Overwatch-LLM"),
    tier_info = Depends(_tier_dep),
    x_edition: Optional[str] = Header(None, alias="X-Edition")
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
        # Determine edition per request: header overrides env
        if x_edition and x_edition.lower() in ("dev","regulated"):
            regulated_enabled = (x_edition.lower() == "regulated")
        else:
            regulated_enabled = str(os.getenv("ENABLE_REGULATED_DOMAINS", "true")).lower() in ("1","true","yes")
        if not request.message or not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        logger.info(f"Chat request: {request.message[:100]}")
        overall_sw_start = time.time()

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

        # Resolve domain triad and chosen overwatch
        triad_p = triad_s = triad_o = None
        if x_domain and regulated_enabled:
            triad_p, triad_s, triad_o = _resolve_domain_triads(x_domain)
        # Overwatch policy: edition-specific defaults with header override
        if regulated_enabled:
            default_ow = os.getenv("DEFAULT_OVERWATCH_LLM")
            require_overwatch = str(os.getenv("REQUIRE_OVERWATCH", "true")).lower() in ("1","true","yes")
            block_on_ow_fail = str(os.getenv("BLOCK_ON_OVERWATCH_FAIL", "true")).lower() in ("1","true","yes")
        else:
            default_ow = os.getenv("DEFAULT_OVERWATCH_LLM_DEV")
            require_overwatch = str(os.getenv("REQUIRE_OVERWATCH_DEV", "true")).lower() in ("1","true","yes")
            block_on_ow_fail = str(os.getenv("BLOCK_ON_OVERWATCH_FAIL_DEV", "false")).lower() in ("1","true","yes")

        # Choose overwatch model by header > triad (regulated) > edition default
        if regulated_enabled:
            chosen_overwatch = x_overwatch or triad_o or default_ow
        else:
            chosen_overwatch = x_overwatch or default_ow
        disclaimer_text = os.getenv("FORCE_DISCLAIMER_TEXT") if regulated_enabled else None

        async def stream_response(overwatch_llm: Optional[str] = None):
            """Generator for streaming response chunks"""
            try:
                full_response = ""

                # Build candidate list (domain triad first, then assigned/best available)
                candidates: List[Dict[str, Any]] = []
                if regulated_enabled:
                    # Prefer domain triad; else regulated defaults
                    for name in (triad_p, triad_s):
                        if name:
                            candidates.append({"id": name, "name": name, "source": _map_source(name)})
                    if not candidates:
                        for name in (os.getenv("DEFAULT_PRIMARY_LLM_REGULATED"), os.getenv("DEFAULT_SECONDARY_LLM_REGULATED")):
                            if name:
                                candidates.append({"id": name, "name": name, "source": _map_source(name)})
                else:
                    # Dev edition: assemble a pool ~4-5 models from role assignments and dev defaults
                    # Roles: coding (Q Assistant), security, testing, analysis, documentation
                    dev_roles = ["coding", "security", "testing", "analysis", "documentation"]
                    for r in dev_roles:
                        try:
                            m = get_model_for_role(r)
                        except Exception:
                            m = None
                        if m:
                            candidates.append({"id": m, "name": m, "source": _map_source(m)})
                    # Then include DEV primary/secondary fallbacks (env)
                    for name in (os.getenv("DEV_PRIMARY_LLM"), os.getenv("DEV_SECONDARY_LLM")):
                        if name:
                            candidates.append({"id": name, "name": name, "source": _map_source(name)})
                primary = get_q_assistant_llm()
                if primary:
                    candidates.append(primary)
                for c in get_best_llms_for_operations(5):
                    # Normalize to llm_config-like dict
                    cand = {
                        "id": c.get("name"),
                        "name": c.get("name"),
                        "source": c.get("name", "").lower(),
                    }
                    candidates.append(cand)

                # Deduplicate by id/name
                seen = set()
                uniq = []
                for c in candidates:
                    k = c.get("id") or c.get("name")
                    if not k or k in seen:
                        continue
                    seen.add(k)
                    uniq.append(c)

                used_llm_name = None
                # Try each candidate until one yields output promptly
                for cand in uniq:
                    llm_name = cand.get("name") or cand.get("id") or "unknown"
                    if _is_circuit_open(llm_name):
                        continue
                    llm_source = _map_source(llm_name)
                    chat_service = LLMChatService({
                        "id": llm_name,
                        "name": llm_name,
                        "type": "cloud" if llm_source in ["openai","google","anthropic"] else "local",
                        "source": llm_source,
                    }) if llm_source != "unknown" else None

                    if not chat_service:
                        continue

                    try:
                        gen = chat_service.stream_chat(request.message, history)
                        # Try to get first chunk quickly; fallback otherwise
                        try:
                            first_chunk = await asyncio.wait_for(gen.__anext__(), timeout=6)
                        except StopAsyncIteration:
                            continue
                        except asyncio.TimeoutError:
                            # No response in time; try next candidate
                            continue
                        used_llm_name = chat_service.llm_name
                        # Observe TTFT
                        try:
                            LLM_TTFT.labels(endpoint="/api/chat", llm=used_llm_name).observe(time.time() - overall_sw_start)
                        except Exception:
                            pass
                        full_response += first_chunk or ""
                        yield f"data: {json.dumps({'type':'chunk','data': first_chunk, 'llm': used_llm_name})}\n\n"

                        async for chunk in gen:
                            full_response += chunk
                            yield f"data: {json.dumps({'type':'chunk','data': chunk, 'llm': used_llm_name})}\n\n"
                            await asyncio.sleep(0)

                        _record_success(llm_name)
                        break  # Successful candidate
                    except Exception:
                        # Try next candidate
                        _record_failure(llm_name)
                        continue

                if not full_response:
                    # Fallback to simple intelligent responses if all candidates failed
                    full_response = get_simple_response(request.message, history)
                    for char in full_response:
                        yield f"data: {json.dumps({'type':'chunk','data': char, 'llm': 'Q Assistant (Smart Responses)'})}\n\n"
                        await asyncio.sleep(0.01)
                
                # Add to conversation history
                assistant_msg = {"role": "assistant", "content": full_response}
                _conversations[conv_id].append(assistant_msg)
                
                # Overwatch verification (optional/required)
                flagged = False
                if overwatch_llm or require_overwatch:
                    try:
                        ow_model = overwatch_llm or (default_ow)
                        ow_source = _map_source(ow_model)
                        if ow_source != "unknown":
                            overseer = LLMChatService({
                                "id": ow_model,
                                "name": ow_model,
                                "type": "cloud" if ow_source in ["openai","google","anthropic"] else "local",
                                "source": ow_source,
                            })
                            if regulated_enabled:
                                critique_prompt = (
                                    "You are Overwatch (regulated). Task: strictly review the assistant answer for: "
                                    "1) factual errors/hallucinations, 2) unsafe medical/scientific claims, 3) missing citations, "
                                    "4) PHI leakage, 5) regulatory tone (no diagnosis without disclaimers). "
                                    "Return concise JSON: {ok:boolean, issues:[{type,summary,severity}], suggestions:string}.\n\n"
                                    f"Question: {request.message}\n\nAnswer: {full_response}"
                                )
                            else:
                                critique_prompt = (
                                    "You are Overwatch (developer). Focus on hallucination prevention and correctness for software/game dev. "
                                    "Check: 1) factual accuracy, 2) code/config validity, 3) presence of references if making claims. "
                                    "Avoid clinical/regulatory checks. Return JSON: {ok:boolean, issues:[{type,summary,severity}], suggestions:string}.\n\n"
                                    f"Question: {request.message}\n\nAnswer: {full_response}"
                                )
                            chunks = []
                            async for ch in overseer.stream_chat(critique_prompt, []):
                                chunks.append(ch)
                            critique = "".join(chunks).strip()
                            # Try to parse result to detect flagging
                            try:
                                parsed = json.loads(critique)
                                if isinstance(parsed, dict) and parsed.get("ok") is False:
                                    flagged = True
                            except Exception:
                                if '"ok"' in critique and 'false' in critique.lower():
                                    flagged = True
                            event = {"type": "verification", "overwatch": ow_model, "result_raw": critique}
                            yield f"data: {json.dumps(event)}\n\n"
                    except Exception as e:
                        yield f"data: {json.dumps({'type':'verification','overwatch': overwatch_llm or 'default', 'error': str(e)})}\n\n"

                # In regulated mode, optionally block on Overwatch failure
                if regulated_enabled and flagged and block_on_ow_fail:
                    yield f"data: {json.dumps({'type':'blocked','reason':'overwatch_failed','message':'Response blocked by verification policy'})}\n\n"
                    return

                # Inject disclaimer in regulated mode (if configured)
                if regulated_enabled and disclaimer_text:
                    full_response = f"{full_response}\n\n{disclaimer_text}"

                # Send completion event
                # Record final latency metric
                try:
                    LLM_LATENCY.labels(endpoint="/api/chat", llm=used_llm_name or "smart").observe(time.time() - overall_sw_start)
                except Exception:
                    pass
                # Record Overwatch flagged metric
                try:
                    if flagged and (overwatch_llm or require_overwatch):
                        domain = x_domain or "unknown"
                        OVERWATCH_FLAGGED.labels(endpoint="/api/chat", domain=domain, overwatch=overwatch_llm or 'default').inc()
                except Exception:
                    pass

                # Tokens and cost SLI metrics (best-effort if rates configured)
                try:
                    if used_llm_name:
                        provider = _map_source(used_llm_name)
                        # Build prompt text similar to service usage (recent history + current)
                        prompt_parts = [m.get("content", "") for m in (history[-6:] if history else [])]
                        prompt_parts.append(request.message)
                        prompt_text = "\n".join(prompt_parts)
                        tokens_in = _estimate_tokens(prompt_text)
                        tokens_out = _estimate_tokens(full_response)
                        LLM_TOKENS.labels(model=used_llm_name, provider=provider, direction="in").inc(tokens_in)
                        LLM_TOKENS.labels(model=used_llm_name, provider=provider, direction="out").inc(tokens_out)
                        in_rate, out_rate = _env_cost_rate(used_llm_name, provider)
                        if in_rate is not None and out_rate is not None:
                            cost = (tokens_in / 1000.0) * in_rate + (tokens_out / 1000.0) * out_rate
                            if cost > 0:
                                LLM_COST_USD.labels(model=used_llm_name, provider=provider).inc(cost)
                except Exception:
                    # Don't break user flow if metrics fail
                    pass

                completion_event = {
                    "type": "done",
                    "message": "Response complete",
                    "total_length": len(full_response),
                    "llm": used_llm_name or "Q Assistant (Smart Responses)"
                }
                yield f"data: {json.dumps(completion_event)}\n\n"
                
                logger.info(
                    "Chat response completed",
                    extra={
                        "llm": used_llm_name or "SmartResponses",
                        "message_length": len(request.message),
                        "response_length": len(full_response)
                    }
                )
                
            except Exception as e:
                logger.error(f"Error in chat stream: {str(e)}")
                error_event = {"type": "error", "error": str(e)}
                yield f"data: {json.dumps(error_event)}\n\n"
        
        return StreamingResponse(
            stream_response(overwatch_llm=chosen_overwatch),
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


@router.post("/science")
async def chat_stream_science(
    request: ChatRequest = Body(...),
    user_id: str = Header(None, alias="X-User-ID"),
    tier_info = Depends(_tier_dep)
):
    """Deprecated: use '/' with X-Domain: science header. Kept for backward compatibility."""
    regulated_enabled = str(os.getenv("ENABLE_REGULATED_DOMAINS", "true")).lower() in ("1","true","yes")
    if not regulated_enabled:
        raise HTTPException(status_code=404, detail="Not found")
    return await chat_stream(request=request, user_id=user_id, x_domain="science")


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


# End of file
