from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import random

router = APIRouter(prefix="/med/trials", tags=["Medical Virtual Trials"])


class Arm(BaseModel):
    name: str
    size: int = Field(gt=0)
    effect_mean: float = 0.0
    effect_std: float = 1.0


class TrialDesign(BaseModel):
    title: str
    population_size: int = Field(gt=0)
    arms: List[Arm]
    duration_days: int = Field(gt=0)
    seed: Optional[int] = None


class TrialOutcome(BaseModel):
    status: str
    title: str
    summary: Dict[str, Any]
    arms: List[Dict[str, Any]]


@router.post("/simulate", response_model=TrialOutcome)
async def simulate_trial(design: TrialDesign = Body(...)):
    """Simulate a simple two-arm (or multi-arm) virtual trial (stub).

    Contract:
    - Input: TrialDesign with arms and sizes
    - Output: aggregate effect sizes and confidence-like ranges (toy model)
    """
    try:
        rng = random.Random(design.seed)
        total = sum(a.size for a in design.arms)
        if total != design.population_size:
            raise ValueError("Sum of arm sizes must equal population_size")

        arm_results = []
        for a in design.arms:
            samples = [rng.gauss(a.effect_mean, a.effect_std) for _ in range(a.size)]
            mean = sum(samples) / len(samples)
            # Toy "interval"
            ci_low = mean - 1.96 * (a.effect_std / max(1, len(samples)) ** 0.5)
            ci_high = mean + 1.96 * (a.effect_std / max(1, len(samples)) ** 0.5)
            arm_results.append({
                "arm": a.name,
                "n": a.size,
                "mean_effect": round(mean, 4),
                "approx_ci95": [round(ci_low, 4), round(ci_high, 4)],
            })

        summary = {
            "duration_days": design.duration_days,
            "population_size": design.population_size,
            "arms": len(design.arms)
        }
        return TrialOutcome(status="ok", title=design.title, summary=summary, arms=arm_results)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
