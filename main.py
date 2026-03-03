import os
import requests
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

# ===============================
# 🔧 Load Environment Variables
# ===============================
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set in environment variables")

BASE_URL = "https://tiwarijii7-SeHAT-AI-Brain.hf.space/gradio_api/call"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {HF_TOKEN}"
}

# ===============================
# 🚀 Initialize FastAPI
# ===============================
app = FastAPI(
    title="SeHAT AI Backend",
    description="Backend API for Report Analyzer, Symptom Checker & AI Chat",
    version="1.0.0"
)

# ===============================
# 📊 Logging Setup
# ===============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
# 🌐 Health Check Route
# ===============================
@app.get("/")
def root():
    return {"status": "SeHAT AI Backend Running Successfully 🚀"}


# ===============================
# 🔁 Helper Function (HF Caller)
# ===============================
def call_hf_space(endpoint: str, input_data: str):
    try:
        payload = {"data": [input_data]}

        response = requests.post(
            f"{BASE_URL}/{endpoint}",
            json=payload,
            headers=HEADERS,
            timeout=60  # prevent hanging
        )

        response.raise_for_status()

        result = response.json()
        output = result.get("data", ["No response received"])[0]

        return output

    except requests.exceptions.Timeout:
        logger.error("HF request timed out")
        raise HTTPException(status_code=504, detail="Model response timed out")

    except requests.exceptions.RequestException as e:
        logger.error(f"HF request failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Model service unavailable")

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# ===============================
# 🩺 1️⃣ Report Analyzer
# ===============================
@app.post("/analyze-report")
def analyze_report(request: ReportRequest):
    if not request.report_json_text.strip():
        raise HTTPException(status_code=400, detail="Report text cannot be empty")

    output = call_hf_space("run_report", request.report_json_text)

    return {
        "status": "success",
        "clinical_summary": output
    }


# ===============================
# 🤒 2️⃣ Symptom Checker
# ===============================
@app.post("/analyze-symptom")
def analyze_symptom(request: SymptomRequest):
    if not request.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms cannot be empty")

    output = call_hf_space("run_symptom", request.symptoms)

    return {
        "status": "success",
        "symptom_result": output
    }


# ===============================
# 💬 3️⃣ Chat Assistant
# ===============================
@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    output = call_hf_space("run_chat", request.message)

    return {
        "status": "success",
        "chat_response": output
    }
