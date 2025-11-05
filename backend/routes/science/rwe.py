from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

router = APIRouter(prefix="/science/rwe", tags=["Science - RWE Synthesis"])


class RWENote(BaseModel):
    text: str
    source_id: Optional[str] = None
    timestamp: Optional[str] = None


class RWESynthesisRequest(BaseModel):
    notes: List[RWENote]
    deidentify: bool = True


class RWESynthesisResponse(BaseModel):
    status: str
    omop_like: Dict[str, Any]
    fhir_like: Dict[str, Any]
    risk_of_bias: Dict[str, Any]


@router.post("/synthesize", response_model=RWESynthesisResponse)
async def synthesize_rwe(req: RWESynthesisRequest = Body(...)):
    """Synthesize structured signals from raw notes (stub).

    Contract:
    - Input: array of notes (text) and deidentify flag
    - Output: OMOP/FHIR-like structures + toy risk-of-bias scores per field
    """
    try:
        # Stub mapping: count keywords as signals
        conditions = []
        for n in req.notes:
            text = (n.text or "").lower()
            if "diabetes" in text:
                conditions.append({"condition": "diabetes", "date": n.timestamp or None})
            if "hypertension" in text:
                conditions.append({"condition": "hypertension", "date": n.timestamp or None})

        omop_like = {"conditions": conditions}
        fhir_like = {"resourceType": "Bundle", "type": "collection", "entry": []}
        for c in conditions:
            fhir_like["entry"].append({
                "resource": {
                    "resourceType": "Condition",
                    "code": {"text": c["condition"]},
                    "onsetDateTime": c.get("date")
                }
            })

        risk_of_bias = {"heuristic": "keyword-count", "score": 0.4 + 0.1 * len(conditions)}
        return RWESynthesisResponse(status="ok", omop_like=omop_like, fhir_like=fhir_like, risk_of_bias=risk_of_bias)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
