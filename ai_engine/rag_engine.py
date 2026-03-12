"""Symptom similarity search using TF-IDF + cosine similarity.

Replaces sentence-transformers + FAISS to remove the torch/CUDA dependency
that caused Render free-tier port-scan timeouts.
Only requires scikit-learn which is already in requirements.txt.
"""
from config import DATASET_PATH

_vectorizer = None
_symptom_matrix = None
_diseases: list = []


def initialize_rag() -> None:
    """Eagerly build the TF-IDF index at startup."""
    _build()


def get_embedding_model():
    """Return the singleton TF-IDF vectorizer, lazy-built on first call."""
    global _vectorizer
    if _vectorizer is None:
        _build()
    return _vectorizer


def _build() -> None:
    """Fit TF-IDF on the symptom dataset. Called once on first request."""
    global _vectorizer, _symptom_matrix, _diseases
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer

    df = pd.read_csv(DATASET_PATH)
    _diseases = df["Disease"].tolist()
    symptom_texts = df["Symptoms"].astype(str).tolist()

    _vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2), sublinear_tf=True)
    _symptom_matrix = _vectorizer.fit_transform(symptom_texts)


def search(query: str = None, top_k: int = 5, query_embedding=None) -> list:
    """
    Return top-k most similar diseases with confidence scores (0-100).
    query_embedding: pre-computed sparse TF-IDF vector (skips re-vectorizing).
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    if _vectorizer is None:
        _build()

    query_vec = query_embedding if query_embedding is not None else _vectorizer.transform([query])
    sims = cosine_similarity(query_vec, _symptom_matrix)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]

    return [
        {"disease": _diseases[i], "confidence": round(float(sims[i]) * 100, 1)}
        for i in top_indices
        if sims[i] > 0.01
    ]


# Alias for backward compatibility with symptom_engine imports
search_symptoms = search

