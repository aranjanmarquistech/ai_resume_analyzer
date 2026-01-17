from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import joblib


@dataclass(frozen=True)
class RolePrediction:
    label: str
    confidence: float


class RolePredictor:
    def __init__(self, model_path: str | Path | None = None):
        """
        If model_path is None:
        - Try models/latest_role_model.txt
        - Fallback to models/role_pipeline.joblib
        """
        if model_path is None:
            latest = Path("models/latest_role_model.txt")
            if latest.exists():
                model_path = latest.read_text(encoding="utf-8").strip()
            else:
                model_path = "models/role_pipeline.joblib"

        self.model_path = Path(model_path)
        if not self.model_path.exists():
            raise FileNotFoundError(f"Role model not found: {self.model_path}")

        self.pipeline = joblib.load(self.model_path)

    def predict(self, text: str) -> RolePrediction:
        """
        Single best prediction.
        """
        top = self.predict_topk(text, k=1)
        return top[0] if top else RolePrediction(label="unknown", confidence=0.0)

    def predict_topk(self, text: str, k: int = 3) -> list[RolePrediction]:
        """
        Top-k predictions with confidence using predict_proba (if available).
        """
        if not text or not text.strip():
            return [RolePrediction(label="unknown", confidence=0.0)]

        # If pipeline doesn't support proba, fallback to hard prediction
        if not hasattr(self.pipeline, "predict_proba"):
            label = str(self.pipeline.predict([text])[0])
            return [RolePrediction(label=label, confidence=1.0)]

        proba = self.pipeline.predict_proba([text])[0]
        classes = list(self.pipeline.classes_)

        pairs = sorted(
            [(str(classes[i]), float(proba[i])) for i in range(len(classes))],
            key=lambda x: x[1],
            reverse=True,
        )

        k = max(1, int(k))
        topk = pairs[:k]
        return [RolePrediction(label=lbl, confidence=conf) for lbl, conf in topk]
