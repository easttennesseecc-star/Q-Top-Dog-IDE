from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional, List

router = APIRouter(prefix="/med/interop", tags=["Medical Interoperability"])


class FHIRBundle(BaseModel):
    resourceType: str
    entry: Optional[list] = None
    # Accept arbitrary fields to keep flexible
    def model_post_init(self, __context: Any) -> None:
        pass


class OMOPPayload(BaseModel):
    data: Dict[str, Any]


class TranslationResult(BaseModel):
    status: str
    format: str
    data: Dict[str, Any]
    note: Optional[str] = None


@router.post("/fhir/to-omop", response_model=TranslationResult)
async def fhir_to_omop(bundle: Dict[str, Any] = Body(...)):
    """Translate FHIR JSON to OMOP-like normalized structure (stub).

    Contract:
    - Input: FHIR bundle JSON
    - Output: { status, format: "omop", data: normalized }
    """
    try:
        # Stub normalization: pick key fields if present
        patient = None
        entry_val = bundle.get("entry", []) if isinstance(bundle, dict) else []
        entries: List[Dict[str, Any]] = entry_val if isinstance(entry_val, list) else []
        for e in entries:
            res_raw = e.get("resource") if isinstance(e, dict) else None
            res = res_raw if isinstance(res_raw, dict) else {}
            if res.get("resourceType") == "Patient":
                pid = res.get("id") if isinstance(res.get("id"), str) else None
                gender_raw = res.get("gender")
                gender = gender_raw.lower() if isinstance(gender_raw, str) else "unknown"
                birth_dt = res.get("birthDate") if isinstance(res.get("birthDate"), str) else None
                patient = {
                    "person_source_value": pid,
                    "gender_concept": gender,
                    "birth_datetime": birth_dt,
                }
                break

        normalized: Dict[str, Any] = {"patient": patient, "observations": []}
        return TranslationResult(status="ok", format="omop", data=normalized)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/omop/to-fhir", response_model=TranslationResult)
async def omop_to_fhir(payload: OMOPPayload = Body(...)):
    """Translate OMOP-like JSON to FHIR bundle (stub)."""
    try:
        patient = payload.data.get("patient", {}) if isinstance(payload.data, dict) else {}
        fhir = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": patient.get("person_source_value") or "unknown",
                        "gender": patient.get("gender_concept") or "unknown",
                        "birthDate": patient.get("birth_datetime"),
                    }
                }
            ],
        }
        return TranslationResult(status="ok", format="fhir", data=fhir)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
