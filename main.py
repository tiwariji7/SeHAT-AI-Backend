from fastapi import FastAPI
from pydantic import BaseModel
from utils import clean_text, extract_patient_info, extract_parameters

app = FastAPI()

class OCRRequest(BaseModel):
    ocr_text: str


@app.post("/analyze-report")
async def analyze_report(data: OCRRequest):

    raw_text = data.ocr_text
    cleaned = clean_text(raw_text)

    patient_info = extract_patient_info(cleaned)
    parameters = extract_parameters(cleaned)

    return {
        "patient_info": patient_info,
        "parameters": parameters
    }