from pydantic import BaseModel, Field
from typing import List


# ── Symptom Checker ──────────────────────────────────────────────────────────

class SymptomRequest(BaseModel):
    symptoms: str = Field(..., example="fever headache body pain")


class ConditionResult(BaseModel):
    disease: str
    confidence: int


class SymptomResponse(BaseModel):
    conditions: List[ConditionResult]
    summary: str


# ── Medical Report Analyzer ──────────────────────────────────────────────────

class PatientInfo(BaseModel):
    name: str
    age: int
    gender: str


class LabParameter(BaseModel):
    name: str
    value: str
    references: str


class ReportInfo(BaseModel):
    report_name: str
    parameters: List[LabParameter]


class ReportRequest(BaseModel):
    patient_info: PatientInfo
    report_info: ReportInfo


class AbnormalParameter(BaseModel):
    name: str
    value: float
    status: str        # "Low" or "High"
    reference: str


class ReportResponse(BaseModel):
    abnormal_parameters: List[AbnormalParameter]
    english_summary: str
    hindi_summary: str


# ── Medical Chatbot ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., example="What should I do for fever?")


class ChatResponse(BaseModel):
    response: str
