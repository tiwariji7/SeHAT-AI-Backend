import logging

from fastapi import APIRouter, HTTPException

from ai_engine.symptom_engine import check_symptoms
from schemas.request_schema import SymptomRequest, SymptomResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Symptom Checker"])


@router.post("/symptom-check", response_model=SymptomResponse)
def symptom_check(request: SymptomRequest):
    """
    Analyzes user-reported symptoms and returns the most likely matching
    medical conditions along with a clinical summary.
    """
    if not request.symptoms.strip():
        raise HTTPException(status_code=400, detail="The 'symptoms' field cannot be empty.")

    try:
        result = check_symptoms(request.symptoms.strip())
        return result
    except Exception as exc:
        logger.error("Symptom check error: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Symptom analysis failed. Please try again later.",
        )
