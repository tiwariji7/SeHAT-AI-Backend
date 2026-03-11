import logging
from typing import List

from ai_engine.llm_engine import call_model
from ai_engine.rag_engine import search_symptoms
from prompts.prompts import (
    SYMPTOM_EXTRACTION_PROMPT,
    SYMPTOM_EXTRACTION_SYSTEM,
    SYMPTOM_SUMMARY_PROMPT,
    SYMPTOM_SUMMARY_SYSTEM,
)

logger = logging.getLogger(__name__)

# Keywords that should immediately trigger an emergency warning
_EMERGENCY_KEYWORDS = {
    "heart attack",
    "cardiac arrest",
    "chest pain radiating",
    "cannot breathe",
    "can't breathe",
    "difficulty breathing",
    "stroke",
    "sudden numbness",
    "loss of consciousness",
    "unconscious",
    "unresponsive",
    "severe bleeding",
    "anaphylaxis",
    "severe allergic reaction",
    "poisoning",
    "overdose",
}

_EMERGENCY_RESPONSE = {
    "conditions": [],
    "summary": (
        "EMERGENCY: Your symptoms may indicate a life-threatening condition. "
        "Please call emergency services (112) or go to the nearest emergency "
        "room immediately. Do not wait."
    ),
}


def check_symptoms(symptoms: str) -> dict:
    """
    Full symptom-checking pipeline:
      1. Emergency keyword detection
      2. LLM-based symptom extraction / cleaning
      3. FAISS similarity search
      4. LLM-generated clinical summary

    Args:
        symptoms: Raw symptom text from the user.

    Returns:
        Dict with 'conditions' (list of disease/confidence) and 'summary' (str).
    """
    # ── Step 1: Emergency detection ──────────────────────────────────────────
    lower = symptoms.lower()
    for keyword in _EMERGENCY_KEYWORDS:
        if keyword in lower:
            logger.warning("Emergency keyword detected: '%s'", keyword)
            return _EMERGENCY_RESPONSE

    # ── Step 2: Extract clean symptom keywords via LLM ───────────────────────
    try:
        clean_symptoms: str = call_model(
            prompt=SYMPTOM_EXTRACTION_PROMPT.format(user_input=symptoms),
            system_instruction=SYMPTOM_EXTRACTION_SYSTEM,
        )
    except Exception as exc:
        logger.warning("LLM symptom extraction failed (%s); using raw input.", exc)
        clean_symptoms = symptoms

    # ── Step 3: FAISS similarity search ──────────────────────────────────────
    matches: List[dict] = search_symptoms(clean_symptoms)

    if not matches:
        return {
            "conditions": [],
            "summary": (
                "No matching conditions could be identified from the provided symptoms. "
                "Please consult a qualified doctor for a proper clinical evaluation."
            ),
        }

    # ── Step 4: Format conditions list ───────────────────────────────────────
    conditions = [
        {"disease": m["disease"], "confidence": m["confidence"]} for m in matches
    ]

    # ── Step 5: Generate LLM clinical summary ────────────────────────────────
    conditions_text = "\n".join(
        f"- {m['disease']} (confidence: {m['confidence']}%)" for m in matches
    )
    try:
        summary: str = call_model(
            prompt=SYMPTOM_SUMMARY_PROMPT.format(
                symptoms=clean_symptoms,
                conditions=conditions_text,
            ),
            system_instruction=SYMPTOM_SUMMARY_SYSTEM,
        )
    except Exception as exc:
        logger.error("LLM summary generation failed: %s", exc)
        summary = (
            f"Your symptoms most closely match {conditions[0]['disease']}. "
            "Please consult a doctor for a proper diagnosis."
        )

    return {"conditions": conditions, "summary": summary}
