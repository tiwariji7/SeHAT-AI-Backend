import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR: Path = Path(__file__).parent

# ── HuggingFace ──────────────────────────────────────────────────────────────
HF_TOKEN: str = os.getenv("HF_TOKEN", "")
MODEL_ID: str = "Intelligent-Internet/II-Medical-8B"

# ── Embeddings & Vector DB ───────────────────────────────────────────────────
EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
DATASET_PATH: str = str(BASE_DIR / "vector_db" / "symptomdataset.csv")
FAISS_INDEX_PATH: str = str(BASE_DIR / "vector_db" / "faiss_index.bin")
TOP_K_RESULTS: int = 5

# ── LLM Generation ───────────────────────────────────────────────────────────
LLM_MAX_TOKENS: int = 600
LLM_TEMPERATURE: float = 0.3
LLM_TIMEOUT: int = 90  # seconds
