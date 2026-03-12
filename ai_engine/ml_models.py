"""
SeHAT ML Ensemble — Random Forest + XGBoost (free-tier optimised)
All heavy imports are inside train() / predict_ensemble() so they
never run at module import time, keeping startup instant on Render.
"""
from config import DATASET_PATH

_AUGMENT_N: int = 3
_NOISE_STD: float = 0.02


def _augment(X, y, np, n=_AUGMENT_N, noise_std=_NOISE_STD):
    X_out, y_out = [], []
    for emb, label in zip(X, y):
        for _ in range(n):
            noise = np.random.randn(*emb.shape).astype("float32") * noise_std
            aug = emb + noise
            X_out.append(aug)
            y_out.append(label)
    return np.array(X_out, dtype="float32"), np.array(y_out)


class SymptomMLEngine:
    def __init__(self):
        self.rf = None
        self.xgb_clf = None
        self.label_encoder = None
        self.diseases: list = []
        self._trained: bool = False

    def train(self) -> None:
        try:
            import numpy as np
            import pandas as pd
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.preprocessing import LabelEncoder
            import xgboost as xgb
            from ai_engine.rag_engine import get_embedding_model

            df = pd.read_csv(DATASET_PATH)
            diseases = df["Disease"].tolist()
            symptoms = df["Symptoms"].astype(str).tolist()
            self.diseases = diseases

            lenc = LabelEncoder()
            y_base = lenc.fit_transform(diseases)
            self.label_encoder = lenc

            vectorizer = get_embedding_model()
            X_base = vectorizer.transform(symptoms).toarray().astype("float32")

            X, y = _augment(X_base, y_base, np)

            self.rf = RandomForestClassifier(
                n_estimators=30, max_depth=20, n_jobs=1, random_state=42
            )
            self.rf.fit(X, y)

            self.xgb_clf = xgb.XGBClassifier(
                n_estimators=30, max_depth=6, learning_rate=0.15,
                eval_metric="mlogloss", tree_method="hist",
                nthread=1, random_state=42, verbosity=0,
            )
            self.xgb_clf.fit(X, y)
            self._trained = True

        except Exception:
            self._trained = False

    def predict_ensemble(self, query_embedding) -> dict:
        if not self._trained:
            return {}
        import numpy as np
        if hasattr(query_embedding, "toarray"):
            x = query_embedding.toarray().astype("float32")
        else:
            x = np.array(query_embedding).reshape(1, -1).astype("float32")

        rf_proba = self.rf.predict_proba(x)[0]
        xgb_proba = self.xgb_clf.predict_proba(x)[0]
        ensemble = (rf_proba + xgb_proba) / 2.0
        return {
            self.label_encoder.inverse_transform([i])[0]: float(p)
            for i, p in enumerate(ensemble)
        }


_ml_engine: SymptomMLEngine = None


def get_ml_engine() -> SymptomMLEngine:
    global _ml_engine
    if _ml_engine is None:
        _ml_engine = SymptomMLEngine()
        _ml_engine.train()
    return _ml_engine
