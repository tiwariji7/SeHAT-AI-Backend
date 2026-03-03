import os
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

HF_TOKEN = os.getenv("HF_TOKEN")

BASE_URL = "https://tiwarijii7-SeHAT-AI-Brain.hf.space/gradio_api/call"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {HF_TOKEN}"
}

# ===============================
# 📄 Request Models
# ===============================

class ReportRequest(BaseModel):
    report_json_text: str


class SymptomRequest(BaseModel):
    symptoms: str


class ChatRequest(BaseModel):
    message: str


# ===============================
# 🩺 1. Report Analyzer
# ===============================

@app.post("/analyze-report")
def analyze_report(request: ReportRequest):

    payload = {
        "data": [request.report_json_text]
    }

    response = requests.post(f"{BASE_URL}/run_report", json=payload, headers=headers)

    result = response.json()
    output = result.get("data", ["No response"])[0]

    return {"clinical_summary": output}


# ===============================
# 🤒 2. Symptom Checker
# ===============================

@app.post("/analyze-symptom")
def analyze_symptom(request: SymptomRequest):

    payload = {
        "data": [request.symptoms]
    }

    response = requests.post(f"{BASE_URL}/run_symptom", json=payload, headers=headers)

    result = response.json()
    output = result.get("data", ["No response"])[0]

    return {"symptom_result": output}


# ===============================
# 💬 3. Chat Assistant
# ===============================

@app.post("/chat")
def chat(request: ChatRequest):

    payload = {
        "data": [request.message]
    }

    response = requests.post(f"{BASE_URL}/run_chat", json=payload, headers=headers)

    result = response.json()
    output = result.get("data", ["No response"])[0]

    return {"chat_response": output}
