import logging

from fastapi import APIRouter, HTTPException

from ai_engine.lab_logic import build_abnormal_summary, detect_abnormal_parameters
from ai_engine.llm_engine import call_model
from prompts.prompts import (
    REPORT_ENGLISH_PROMPT,
    REPORT_ENGLISH_SYSTEM,
    REPORT_HINDI_PROMPT,
    REPORT_HINDI_SYSTEM,
)
from schemas.request_schema import ReportRequest, ReportResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Medical Report Analyzer"])


@router.post("/analyze-report", response_model=ReportResponse)
def analyze_report(request: ReportRequest):
    """
    Parses a structured lab report, detects out-of-range parameters, and
    generates bilingual (English + Hindi) clinical interpretations.
    """
    if not request.report_info.parameters:
        raise HTTPException(
            status_code=400,
            detail="No lab parameters were provided in the report.",
        )

    # ── Steps 1–4: Validate, normalize, compare to reference ranges ──────────
    abnormal = detect_abnormal_parameters(request.report_info.parameters)

    # ── All-normal fast path ──────────────────────────────────────────────────
    if not abnormal:
        patient = request.patient_info
        report_name = request.report_info.report_name
        return ReportResponse(
            abnormal_parameters=[],
            english_summary=(
                f"All parameters in {patient.name}'s {report_name} are within "
                "the normal reference range. No clinical concerns detected. "
                "Continue regular health monitoring."
            ),
            hindi_summary=(
                f"{patient.name} की {report_name} के सभी पैरामीटर सामान्य "
                "सीमा में हैं। कोई नैदानिक चिंता नहीं पाई गई। "
                "नियमित स्वास्थ्य जांच जारी रखें।"
            ),
        )

    # ── Step 5: Build abnormal parameter summary ─────────────────────────────
    abnormal_text = build_abnormal_summary(abnormal)

    common_kwargs = dict(
        name=request.patient_info.name,
        age=request.patient_info.age,
        gender=request.patient_info.gender,
        report_name=request.report_info.report_name,
        abnormal_list=abnormal_text,
    )

    # ── Step 6a: English clinical interpretation ──────────────────────────────
    try:
        english_summary = call_model(
            prompt=REPORT_ENGLISH_PROMPT.format(**common_kwargs),
            system_instruction=REPORT_ENGLISH_SYSTEM,
        )
    except Exception as exc:
        logger.error("English report generation failed: %s", exc)
        english_summary = (
            f"Abnormal parameters detected in {request.patient_info.name}'s report:\n"
            + abnormal_text
            + "\nPlease consult a doctor for further evaluation."
        )

    # ── Step 6b: Hindi clinical interpretation ────────────────────────────────
    try:
        hindi_summary = call_model(
            prompt=REPORT_HINDI_PROMPT.format(**common_kwargs),
            system_instruction=REPORT_HINDI_SYSTEM,
        )
    except Exception as exc:
        logger.error("Hindi report generation failed: %s", exc)
        hindi_summary = (
            "रिपोर्ट में असामान्य पैरामीटर पाए गए हैं। "
            "कृपया उचित मूल्यांकन के लिए डॉक्टर से परामर्श करें।"
        )

    return ReportResponse(
        abnormal_parameters=abnormal,
        english_summary=english_summary,
        hindi_summary=hindi_summary,
    )
