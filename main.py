import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_engine.llm_engine import initialize_llm
from ai_engine.rag_engine import initialize_rag
from api.chat_api import router as chat_router
from api.report_api import router as report_router
from api.symptom_api import router as symptom_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize heavyweight resources once at startup; release on shutdown."""
    logger.info("SeHAT AI Backend starting up …")
    initialize_llm()   # HuggingFace InferenceClient
    initialize_rag()   # Sentence-Transformer + FAISS index
    logger.info("All engines ready.")
    yield
    logger.info("SeHAT AI Backend shutting down.")


app = FastAPI(
    title="SeHAT SmartCare AI Backend",
    description=(
        "AI-powered healthcare analysis backend.\n\n"
        "Modules: Symptom Checker | Medical Report Analyzer | Medical Chatbot"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(symptom_router)
app.include_router(report_router)
app.include_router(chat_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "SeHAT SmartCare AI Backend"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)