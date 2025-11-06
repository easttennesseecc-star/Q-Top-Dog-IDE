# backend/media_routes.py
"""
API endpoints for media generation
Endpoints:
- POST /api/media/generate - Generate media
- GET /api/media/estimate - Get cost estimate
- GET /api/media/status - Provider status
- GET /api/media/history - Generation history
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import logging

from backend.media_service import get_media_service, MediaType, MediaTier, MediaGenerationResult
from backend.services.media_requirements_resolver import resolve_requirements

logger = logging.getLogger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    """Request to generate media"""
    description: str
    media_type: str = "image"
    tier: Optional[str] = None
    project_id: Optional[str] = None
    resolution: Optional[str] = None  # e.g., "1024x1024" or "1280x720"
    format: Optional[str] = None      # e.g., "png", "jpg", "mp4"


class EstimateRequest(BaseModel):
    """Request to estimate cost"""
    description: str
    media_type: str = "image"
    tier: Optional[str] = None


class MediaResponse(BaseModel):
    """Response with generated media"""
    url: str
    media_type: str
    tier: str
    cost: float
    time_ms: int
    timestamp: str
    format: Optional[str] = None


class EstimateResponse(BaseModel):
    """Response with cost estimate"""
    tier: str
    media_type: str
    estimated_cost: float
    estimated_time_ms: int
    description: str


class ProviderStatus(BaseModel):
    """Status of a provider"""
    enabled: bool
    cost_per_image: Optional[float] = None
    generation_time_ms: Optional[int] = None
    note: Optional[str] = None
    configured: Optional[bool] = None
    provider: Optional[str] = None


class StatusResponse(BaseModel):
    """Response with provider status"""
    free: dict
    budget: dict
    premium: dict


class UsageStats(BaseModel):
    """Usage statistics"""
    total_generated: int
    total_cost: float
    by_tier: dict
    last_generation: Optional[str] = None


@router.post("/media/generate", response_model=MediaResponse)
async def generate_media(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
) -> MediaResponse:
    """
    Generate media using specified tier or auto-select cheapest available
    
    Args:
        description: Text description of media to generate
        media_type: "image", "video", or "audio"
        tier: Optional tier selection ("free", "budget", "premium")
        project_id: Optional project ID for tracking
    
    Returns:
        Generated media with URL and metadata
    """
    try:
        # Validate inputs
        try:
            media_type = MediaType[request.media_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid media_type. Must be: {', '.join(mt.value for mt in MediaType)}"
            )
        
        selected_tier = None
        if request.tier:
            try:
                selected_tier = MediaTier[request.tier.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid tier. Must be: {', '.join(t.value for t in MediaTier)}"
                )
        
        # Resolve missing requirements from plan/heuristics
        target_resolution = request.resolution
        target_format = request.format
        if not target_resolution or not target_format:
            try:
                resolved = resolve_requirements(
                    project_id=request.project_id,
                    description=request.description,
                    media_type=media_type.value,
                )
                target_resolution = target_resolution or resolved.get("resolution")
                target_format = target_format or resolved.get("format")
            except Exception as re:
                logger.warning(f"Failed to resolve media requirements: {re}")

        # Generate media
        service = get_media_service()
        result = await service.generate(
            description=request.description,
            media_type=media_type,
            tier=selected_tier,
            resolution=target_resolution,
            format=target_format,
        )

        # Log generation for analytics
        logger.info(
            f"Media generated: {result.media_type.value} via {result.tier.value} "
            f"({result.time_ms}ms, ${result.cost}) res={target_resolution} format={target_format}"
        )

        return MediaResponse(
            url=result.url,
            media_type=result.media_type.value,
            tier=result.tier.value,
            cost=result.cost,
            time_ms=result.time_ms,
            timestamp=result.timestamp.isoformat(),
            format=target_format,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Media generation failed: {str(e)}"
        )


@router.post("/media/estimate", response_model=EstimateResponse)
async def estimate_cost(request: EstimateRequest) -> EstimateResponse:
    """
    Estimate cost for media generation
    
    Args:
        description: Text description of media
        media_type: "image", "video", or "audio"
        tier: Optional tier selection
    
    Returns:
        Cost estimate and generation time
    """
    try:
        # Validate inputs
        try:
            media_type = MediaType[request.media_type.upper()]
        except KeyError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid media_type. Must be: {', '.join(mt.value for mt in MediaType)}"
            )
        
        selected_tier = None
        if request.tier:
            try:
                selected_tier = MediaTier[request.tier.upper()]
            except KeyError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid tier. Must be: {', '.join(t.value for t in MediaTier)}"
                )
        
        # Get estimate
        service = get_media_service()
        estimate = await service.estimate_cost(
            description=request.description,
            media_type=media_type,
            tier=selected_tier
        )
        
        return EstimateResponse(
            tier=estimate["tier"],
            media_type=estimate["media_type"],
            estimated_cost=estimate["estimated_cost"],
            estimated_time_ms=estimate["estimated_time_ms"],
            description=estimate["description"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cost estimation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Cost estimation failed: {str(e)}"
        )


@router.get("/media/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """
    Get status of all media generation providers
    
    Returns:
        Availability and capabilities of each tier
    """
    try:
        service = get_media_service()
        status = service.get_provider_status()
        
        return StatusResponse(
            free=status["free"],
            budget=status["budget"],
            premium=status["premium"]
        )
    
    except Exception as e:
        logger.error(f"Failed to get provider status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get provider status: {str(e)}"
        )


@router.get("/media/history")
async def get_history(
    limit: int = 50,
    tier: Optional[str] = None,
    media_type: Optional[str] = None
) -> dict:
    """
    Get generation history
    
    Args:
        limit: Maximum number of records to return
        tier: Filter by tier (free, budget, premium)
        media_type: Filter by media type (image, video, audio)
    
    Returns:
        List of recent generations with metadata
    """
    try:
        service = get_media_service()
        history = service.generation_history[-limit:]
        
        # Filter
        if tier:
            history = [g for g in history if g.tier.value == tier]
        if media_type:
            history = [g for g in history if g.media_type.value == media_type]
        
        # Reverse for newest first
        history.reverse()
        
        return {
            "count": len(history),
            "items": [g.to_dict() for g in history]
        }
    
    except Exception as e:
        logger.error(f"Failed to get generation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get generation history: {str(e)}"
        )


@router.get("/media/usage", response_model=UsageStats)
async def get_usage() -> UsageStats:
    """
    Get usage statistics
    
    Returns:
        Total generated, total cost, and breakdown by tier
    """
    try:
        service = get_media_service()
        stats = service.get_usage_stats()
        
        return UsageStats(
            total_generated=stats["total_generated"],
            total_cost=stats["total_cost"],
            by_tier=stats["by_tier"],
            last_generation=stats.get("last_generation")
        )
    
    except Exception as e:
        logger.error(f"Failed to get usage stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get usage stats: {str(e)}"
        )


@router.post("/media/configure")
async def configure_provider(
    provider: str,
    api_key: str,
    test: bool = True,
    endpoint: str | None = None,
) -> dict:
    """
    Configure media generation provider
    
    Args:
        provider: "stable_diffusion" | "runway" | "dalle3" | "midjourney"
        api_key: Provider API key
        test: Test key validity before saving
    
    Returns:
        Configuration status
    """
    import os
    
    try:
        if provider == "stable_diffusion":
            env_var = "STABLE_DIFFUSION_KEY"
        elif provider == "runway":
            env_var = "RUNWAY_API_KEY"
        elif provider == "dalle3":
            env_var = "OPENAI_API_KEY"
        elif provider == "midjourney":
            env_var = "MIDJOURNEY_API_KEY"
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid provider. Must be 'stable_diffusion' | 'runway' | 'dalle3' | 'midjourney'"
            )
        
        # Test the key if requested
        if test:
            success = await _test_provider_key(provider, api_key)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid {provider} API key"
                )
        
        # Save to environment (in production, use secrets manager)
        os.environ[env_var] = api_key
        if provider == "midjourney" and endpoint:
            os.environ["MIDJOURNEY_ENDPOINT"] = endpoint
        
        logger.info(f"Configured {provider} provider")
        
        return {
            "success": True,
            "provider": provider,
            "message": f"Successfully configured {provider}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to configure {provider}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to configure {provider}: {str(e)}"
        )


async def _test_provider_key(provider: str, api_key: str) -> bool:
    """Test if provider API key is valid"""
    import aiohttp
    
    try:
        if provider == "stable_diffusion":
            # Test HuggingFace key
            url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with aiohttp.ClientSession() as session:
                payload = {"inputs": "test"}
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status in [200, 503]  # 503 means overloaded but key is valid
        
        elif provider == "runway":
            # Test Runway key
            url = "https://api.runwayml.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        elif provider == "dalle3":
            # Test OpenAI key by listing models (lightweight)
            url = "https://api.openai.com/v1/models"
            headers = {"Authorization": f"Bearer {api_key}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return resp.status == 200
        elif provider == "midjourney":
            # If endpoint provided via env, try a lightweight GET
            import os
            endpoint = os.getenv("MIDJOURNEY_ENDPOINT")
            if not endpoint:
                return bool(api_key)
            url = f"{endpoint.rstrip('/')}/health"
            headers = {"Authorization": f"Bearer {api_key}"}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                        return resp.status in (200, 404)  # allow 404 if health not implemented
            except Exception:
                return bool(api_key)
    
    except Exception as e:
        logger.warning(f"Error testing {provider} key: {str(e)}")
        return False
    
    return False
