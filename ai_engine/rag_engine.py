import logging
import os
from typing import List, Optional

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from config import DATASET_PATH, EMBEDDING_MODEL, FAISS_INDEX_PATH, TOP_K_RESULTS

logger = logging.getLogger(__name__)

# Module-level singletons — loaded once at startup
_model: Optional[SentenceTransformer] = None
_index: Optional[faiss.IndexFlatIP] = None
_diseases: List[str] = []


def initialize_rag() -> None:
    """
    Load the embedding model, build (or restore) the FAISS index, and cache
    disease labels. Must be called exactly once during application startup.
    """
    global _model, _index, _diseases

    logger.info("Loading sentence-transformer: %s", EMBEDDING_MODEL)
    _model = SentenceTransformer(EMBEDDING_MODEL)

    df = pd.read_csv(DATASET_PATH)
    _diseases = df["Disease"].tolist()
    symptom_texts: List[str] = df["Symptoms"].astype(str).tolist()

    if os.path.exists(FAISS_INDEX_PATH):
        logger.info("Restoring FAISS index from disk: %s", FAISS_INDEX_PATH)
        _index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        logger.info("Building FAISS index for %d diseases …", len(_diseases))
        embeddings: np.ndarray = _model.encode(
            symptom_texts,
            show_progress_bar=False,
            normalize_embeddings=True,  # cosine similarity via inner product
        ).astype(np.float32)

        dim: int = embeddings.shape[1]
        _index = faiss.IndexFlatIP(dim)
        _index.add(embeddings)

        os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(_index, FAISS_INDEX_PATH)
        logger.info(
            "FAISS index built and saved — %d vectors, dim=%d", len(_diseases), dim
        )


def search_symptoms(query: str, top_k: int = TOP_K_RESULTS) -> List[dict]:
    """
    Perform a cosine-similarity search against the symptom index.

    Args:
        query: Free-text symptom description from the user.
        top_k: Number of top results to return.

    Returns:
        List of dicts with keys 'disease' (str) and 'confidence' (int 0–100),
        sorted by descending confidence.

    Raises:
        RuntimeError: If the RAG engine has not been initialized.
    """
    if _model is None or _index is None:
        raise RuntimeError(
            "RAG engine is not initialized. Ensure initialize_rag() ran at startup."
        )

    query_vec: np.ndarray = _model.encode(
        [query], normalize_embeddings=True
    ).astype(np.float32)

    scores, indices = _index.search(query_vec, top_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        # Cosine similarity in [0, 1] after normalization → scale to percentage
        confidence = int(min(100, max(0, float(score) * 100)))
        results.append({"disease": _diseases[idx], "confidence": confidence})

    return results
