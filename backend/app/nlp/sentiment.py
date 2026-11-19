"""Small, local Hindi sentiment model with an explicit evidence boundary.

The classifier is trained in memory from the supplied *training* split only.
It is intentionally not persisted so the repository never gains a hidden model
artifact or modifies the provided datasets.  Validation and test data are read
only when an administrator asks for a measurement.
"""
import csv
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline

from backend.app.core.config import ROOT_DIR


_SENTIMENT_DIR = ROOT_DIR / "datasets" / "processed" / "sentiment"


def _rows(filename: str) -> list[dict[str, str]]:
    # The supplied CSV files have a UTF-8 BOM.  utf-8-sig keeps the public
    # schema stable instead of creating a separate \ufeffsentiment column.
    with (_SENTIMENT_DIR / filename).open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


@lru_cache(maxsize=1)
def hindi_sentiment_model() -> Pipeline:
    rows = _rows("hindi_sentiment_train.csv")
    texts = [row["text"] for row in rows]
    labels = [row["sentiment"] for row in rows]
    # Character n-grams handle Hindi morphology and spelling variation without
    # a tokenizer download.  The small regularised linear model is suitable for
    # a CPU-only machine and the supplied 4,182-row training split.
    model = Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2, sublinear_tf=True)),
        ("classifier", LogisticRegression(max_iter=500, random_state=42, class_weight="balanced", solver="lbfgs")),
    ])
    model.fit(texts, labels)
    return model


def predict_hindi_sentiment(text: str) -> dict[str, object]:
    model = hindi_sentiment_model()
    probabilities = model.predict_proba([text])[0]
    classes = model.named_steps["classifier"].classes_
    index = int(probabilities.argmax())
    return {
        "label": str(classes[index]).title(),
        "confidence": round(float(probabilities[index]), 3),
        "method": "Hindi character TF-IDF + Logistic Regression (supplied training split)",
        "limitations": "Measured on general-domain Hindi, not civic complaints; use as advisory guidance only.",
    }


@lru_cache(maxsize=1)
def evaluate_hindi_sentiment() -> dict[str, object]:
    """Measure the cached model on the untouched supplied held-out test split."""
    rows = _rows("hindi_sentiment_test.csv")
    labels = [row["sentiment"] for row in rows]
    predicted = hindi_sentiment_model().predict([row["text"] for row in rows])
    return {
        "model": "Hindi character TF-IDF + Logistic Regression",
        "training_data": "hindi_sentiment_train.csv (4,182 rows)",
        "evaluation_data": "hindi_sentiment_test.csv (523 supplied held-out rows)",
        "accuracy": round(float(accuracy_score(labels, predicted)), 4),
        "macro_f1": round(float(f1_score(labels, predicted, average="macro")), 4),
        "limitations": "General-domain Hindi sentiment only; it is not a civic-complaint sentiment validation.",
    }
