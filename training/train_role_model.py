from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


DATA_PATH = Path("training/data/role_dataset.csv")
MODEL_DIR = Path("models")
REPORTS_DIR = Path("reports")

MODEL_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)


def _can_stratify(y: list[str], n_test: int) -> bool:
    """
    Stratify is only valid if:
    - more than 1 class
    - each class has at least 2 samples (so train/test can both contain it)
    - test set has at least 1 sample per class
    """
    classes = set(y)
    if len(classes) <= 1:
        return False

    counts: dict[str, int] = {}
    for label in y:
        counts[label] = counts.get(label, 0) + 1

    # each class must appear at least twice
    if any(c < 2 for c in counts.values()):
        return False

    # test set must be large enough to include at least 1 per class
    if n_test < len(classes):
        return False

    return True


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    if "label" not in df.columns or "text" not in df.columns:
        raise ValueError("CSV must contain columns: label,text")

    df = df.dropna(subset=["label", "text"])
    X = df["text"].astype(str).tolist()
    y = df["label"].astype(str).tolist()

    n_samples = len(y)
    n_classes = len(set(y))

    if n_samples < 4:
        raise ValueError("Dataset too small. Add more rows before training.")

    # Ensure test set is large enough for stratification (if possible)
    min_test = max(n_classes, 2)
    test_size = max(0.25, min_test / n_samples)
    n_test = max(1, int(round(n_samples * test_size)))

    stratify = y if _can_stratify(y, n_test) else None

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=42,
        stratify=stratify,
    )

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    macro_f1 = f1_score(y_test, preds, average="macro") if len(set(y_test)) > 1 else 0.0
    report = classification_report(y_test, preds, output_dict=True, zero_division=0)

    # Versioned model save
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    model_path = MODEL_DIR / f"role_pipeline_v{stamp}.joblib"
    joblib.dump(pipeline, model_path)

    # Track latest model path
    latest_path = MODEL_DIR / "latest_role_model.txt"
    latest_path.write_text(str(model_path), encoding="utf-8")

    # Save metrics report
    report_path = REPORTS_DIR / "role_metrics.json"
    payload = {
        "timestamp": stamp,
        "dataset": str(DATA_PATH),
        "n_samples": n_samples,
        "n_classes": n_classes,
        "test_size": float(test_size),
        "stratified": bool(stratify is not None),
        "model_path": str(model_path),
        "latest_model_pointer": str(latest_path),
        "macro_f1": float(macro_f1),
        "classes": sorted(list(set(y))),
        "classification_report": report,
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"✅ Saved model: {model_path}")
    print(f"✅ Updated latest pointer: {latest_path}")
    print(f"✅ Saved report: {report_path}")
    print(f"📊 Macro F1: {macro_f1:.3f}")


if __name__ == "__main__":
    main()
