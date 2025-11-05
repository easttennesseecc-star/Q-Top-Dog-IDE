from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

router = APIRouter(prefix="/med/diagnostic", tags=["Medical Narrative Diagnostics"])


class DiagnosticInput(BaseModel):
    # Accept either raw text or a FHIR Observation bundle
    text: Optional[str] = None
    fhir: Optional[Dict[str, Any]] = None
    reading_level: str = "patient-friendly"  # or "professional"


class DiagnosticNarrative(BaseModel):
    status: str
    audience: str
    narrative: str


@router.post("/narrative", response_model=DiagnosticNarrative)
async def generate_narrative(payload: DiagnosticInput = Body(...)):
    """Generate a patient-friendly narrative summarizing labs or imaging (stub).

    Contract:
    - Input: { text?: string, fhir?: object, reading_level: 'patient-friendly'|'professional' }
    - Output: { status: 'ok', audience, narrative }
    """
    try:
        source = payload.text or ""
        if not source and payload.fhir:
            # Minimal extraction
            source = str(payload.fhir)[:2000]

        if not source:
            raise ValueError("No diagnostic content provided")

        # Stub narrative; in production, call LLM with safety and guardrails
        base = "This report summarizes your results in clear, non-technical terms. "
        narrative = (
            base
            + "Key points: your care team will review these findings with you. "
            + "If anything is out of range, they will explain options and next steps."
        )
        return DiagnosticNarrative(status="ok", audience=payload.reading_level, narrative=narrative)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
