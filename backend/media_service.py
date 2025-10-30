# backend/media_service.py
"""
Unified media generation service supporting 3 tiers:
1. FREE: Q Assistant SVG generation
2. BUDGET: Stable Diffusion (HuggingFace)
3. PREMIUM: Runway AI
"""

import asyncio
import os
from typing import Optional, Literal, Dict, Any
from enum import Enum
import aiohttp
import base64
from datetime import datetime


class MediaTier(str, Enum):
    """Media generation tier"""
    FREE = "free"
    BUDGET = "budget"
    PREMIUM = "premium"


class MediaType(str, Enum):
    """Type of media to generate"""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"


class MediaGenerationResult:
    """Result of media generation"""
    def __init__(self, url: str, media_type: MediaType, tier: MediaTier, cost: float, time_ms: int):
        self.url = url
        self.media_type = media_type
        self.tier = tier
        self.cost = cost
        self.time_ms = time_ms
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "media_type": self.media_type.value,
            "tier": self.tier.value,
            "cost": self.cost,
            "time_ms": self.time_ms,
            "timestamp": self.timestamp.isoformat()
        }


class MediaService:
    """Main media generation service"""
    
    def __init__(self):
        self.stable_diffusion_key = os.getenv("STABLE_DIFFUSION_KEY")
        self.runway_key = os.getenv("RUNWAY_API_KEY")
        self.generation_history = []
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers"""
        return {
            "free": {
                "enabled": True,
                "cost_per_image": 0,
                "generation_time_ms": 0,
                "note": "Q Assistant SVG generation"
            },
            "budget": {
                "enabled": bool(self.stable_diffusion_key),
                "cost_per_image": 0.005,
                "generation_time_ms": 3500,
                "provider": "Stable Diffusion (HuggingFace)",
                "configured": bool(self.stable_diffusion_key)
            },
            "premium": {
                "enabled": bool(self.runway_key),
                "cost_per_image_estimate": 0.05,
                "generation_time_ms": 5000,
                "provider": "Runway AI",
                "configured": bool(self.runway_key)
            }
        }
    
    async def estimate_cost(
        self,
        description: str,
        tier: Optional[MediaTier] = None,
        media_type: MediaType = MediaType.IMAGE
    ) -> Dict[str, Any]:
        """Estimate cost for generation"""
        
        # Cost mapping
        costs = {
            MediaTier.FREE: {
                MediaType.IMAGE: 0,
                MediaType.VIDEO: 0,
                MediaType.AUDIO: 0
            },
            MediaTier.BUDGET: {
                MediaType.IMAGE: 0.005,
                MediaType.VIDEO: 0.05,
                MediaType.AUDIO: 0.002
            },
            MediaTier.PREMIUM: {
                MediaType.IMAGE: 0.05,
                MediaType.VIDEO: 0.25,
                MediaType.AUDIO: 0.02
            }
        }
        
        times = {
            MediaTier.FREE: {
                MediaType.IMAGE: 100,
                MediaType.VIDEO: 100,
                MediaType.AUDIO: 100
            },
            MediaTier.BUDGET: {
                MediaType.IMAGE: 3500,
                MediaType.VIDEO: 10000,
                MediaType.AUDIO: 2000
            },
            MediaTier.PREMIUM: {
                MediaType.IMAGE: 2000,
                MediaType.VIDEO: 5000,
                MediaType.AUDIO: 1500
            }
        }
        
        selected_tier = tier or self._select_best_tier()
        
        return {
            "tier": selected_tier.value,
            "media_type": media_type.value,
            "estimated_cost": costs[selected_tier].get(media_type, 0),
            "estimated_time_ms": times[selected_tier].get(media_type, 0),
            "description": description[:100] + "..." if len(description) > 100 else description
        }
    
    async def generate(
        self,
        description: str,
        media_type: MediaType = MediaType.IMAGE,
        tier: Optional[MediaTier] = None,
        **kwargs
    ) -> MediaGenerationResult:
        """Generate media"""
        
        selected_tier = tier or self._select_best_tier()
        
        if selected_tier == MediaTier.FREE:
            return await self._generate_free(description, media_type)
        elif selected_tier == MediaTier.BUDGET:
            return await self._generate_budget(description, media_type)
        elif selected_tier == MediaTier.PREMIUM:
            return await self._generate_premium(description, media_type)
    
    async def _generate_free(
        self,
        description: str,
        media_type: MediaType
    ) -> MediaGenerationResult:
        """Generate free SVG via Q Assistant"""
        import time
        start = time.time()
        
        # Import simple image generators from Q Assistant
        from q_assistant_scope import (
            generate_simple_wireframe,
            generate_simple_user_flow,
            generate_simple_database_schema,
            generate_simple_architecture_diagram
        )
        
        # Parse description to choose generator
        desc_lower = description.lower()
        
        if "wireframe" in desc_lower or "layout" in desc_lower:
            svg = generate_simple_wireframe(1200, 800)
        elif "flow" in desc_lower or "diagram" in desc_lower:
            svg = generate_simple_user_flow(description[:50])
        elif "database" in desc_lower or "schema" in desc_lower:
            svg = generate_simple_database_schema(["users", "posts", "comments"])
        elif "architecture" in desc_lower or "system" in desc_lower:
            svg = generate_simple_architecture_diagram()
        else:
            svg = generate_simple_wireframe(1200, 800)
        
        # Store as data URI for browser viewing
        svg_b64 = base64.b64encode(svg.encode()).decode()
        data_uri = f"data:image/svg+xml;base64,{svg_b64}"
        
        elapsed = (time.time() - start) * 1000
        
        result = MediaGenerationResult(
            url=data_uri,
            media_type=media_type,
            tier=MediaTier.FREE,
            cost=0,
            time_ms=int(elapsed)
        )
        
        self.generation_history.append(result)
        return result
    
    async def _generate_budget(
        self,
        description: str,
        media_type: MediaType
    ) -> MediaGenerationResult:
        """Generate via Stable Diffusion (HuggingFace)"""
        import time
        start = time.time()
        
        if not self.stable_diffusion_key:
            raise ValueError("Stable Diffusion API key not configured")
        
        # Use HuggingFace Inference API
        api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        headers = {"Authorization": f"Bearer {self.stable_diffusion_key}"}
        
        async with aiohttp.ClientSession() as session:
            payload = {"inputs": description}
            
            async with session.post(api_url, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    image_data = await resp.read()
                    img_b64 = base64.b64encode(image_data).decode()
                    url = f"data:image/jpeg;base64,{img_b64}"
                else:
                    raise ValueError(f"Stable Diffusion API error: {resp.status}")
        
        elapsed = (time.time() - start) * 1000
        
        result = MediaGenerationResult(
            url=url,
            media_type=media_type,
            tier=MediaTier.BUDGET,
            cost=0.005,  # Approximate cost
            time_ms=int(elapsed)
        )
        
        self.generation_history.append(result)
        return result
    
    async def _generate_premium(
        self,
        description: str,
        media_type: MediaType
    ) -> MediaGenerationResult:
        """Generate via Runway AI"""
        import time
        start = time.time()
        
        if not self.runway_key:
            raise ValueError("Runway API key not configured")
        
        # Runway API endpoint varies by media type
        if media_type == MediaType.IMAGE:
            endpoint = "https://api.runwayml.com/v1/image_generations"
            cost = 0.05
        elif media_type == MediaType.VIDEO:
            endpoint = "https://api.runwayml.com/v1/video_generations"
            cost = 0.25
        elif media_type == MediaType.AUDIO:
            endpoint = "https://api.runwayml.com/v1/audio_generations"
            cost = 0.02
        else:
            raise ValueError(f"Unsupported media type: {media_type}")
        
        headers = {
            "Authorization": f"Bearer {self.runway_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": description,
            "duration": 5 if media_type == MediaType.VIDEO else None,
            "resolution": "1280x720" if media_type == MediaType.VIDEO else "1024x1024"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=headers) as resp:
                if resp.status == 201:
                    data = await resp.json()
                    # Runway returns task_id; typically need polling
                    # For now, return the task URL
                    url = data.get("output", "https://runway.runwayml.com/task-pending")
                else:
                    raise ValueError(f"Runway API error: {resp.status}")
        
        elapsed = (time.time() - start) * 1000
        
        result = MediaGenerationResult(
            url=url,
            media_type=media_type,
            tier=MediaTier.PREMIUM,
            cost=cost,
            time_ms=int(elapsed)
        )
        
        self.generation_history.append(result)
        return result
    
    def _select_best_tier(self) -> MediaTier:
        """Auto-select best available tier"""
        # Prefer budget, fall back to free
        if self.stable_diffusion_key:
            return MediaTier.BUDGET
        elif self.runway_key:
            return MediaTier.PREMIUM
        else:
            return MediaTier.FREE
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        if not self.generation_history:
            return {"total_generated": 0, "total_cost": 0, "by_tier": {}}
        
        total_cost = sum(g.cost for g in self.generation_history)
        by_tier = {}
        
        for tier in MediaTier:
            tier_gens = [g for g in self.generation_history if g.tier == tier]
            if tier_gens:
                by_tier[tier.value] = {
                    "count": len(tier_gens),
                    "total_cost": sum(g.cost for g in tier_gens),
                    "avg_time_ms": sum(g.time_ms for g in tier_gens) // len(tier_gens)
                }
        
        return {
            "total_generated": len(self.generation_history),
            "total_cost": total_cost,
            "by_tier": by_tier,
            "last_generation": self.generation_history[-1].timestamp.isoformat()
        }


# Singleton instance
_media_service = None


def get_media_service() -> MediaService:
    """Get or create media service"""
    global _media_service
    if _media_service is None:
        _media_service = MediaService()
    return _media_service
