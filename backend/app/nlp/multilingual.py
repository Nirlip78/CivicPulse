"""Lazy, local adapters for optional multilingual model artifacts.

No model is fetched at request time.  This keeps CivicPulse usable offline and
prevents a CPU-only 8 GB deployment from accidentally loading every model.
"""
from __future__ import annotations
import importlib.util
import os
from functools import lru_cache
from pathlib import Path
from time import perf_counter

from backend.app.core.config import ROOT_DIR
from backend.app.nlp.preprocessing import language_of, script_of

MODEL_ROOT = Path(os.getenv("CIVICPULSE_MODEL_DIR", ROOT_DIR / "ml_models"))
INDIC_LID_PATH = Path(os.getenv("INDICLID_MODEL_PATH", MODEL_ROOT / "indiclid" / "model.bin"))
EMBEDDING_PATH = Path(os.getenv("MULTILINGUAL_EMBEDDING_PATH", MODEL_ROOT / "multilingual-minilm"))
INDICTRANS_ROOT = Path(os.getenv("INDICTRANS2_MODEL_DIR", MODEL_ROOT / "indictrans2"))

SCHEDULED = {
    "asm_Beng":"Assamese", "ben_Beng":"Bengali", "brx_Deva":"Bodo", "doi_Deva":"Dogri",
    "guj_Gujr":"Gujarati", "hin_Deva":"Hindi", "kan_Knda":"Kannada", "kas_Arab":"Kashmiri",
    "kok_Deva":"Konkani", "mai_Deva":"Maithili", "mal_Mlym":"Malayalam", "mni_Mtei":"Manipuri",
    "mar_Deva":"Marathi", "npi_Deva":"Nepali", "ory_Orya":"Odia", "pan_Guru":"Punjabi",
    "san_Deva":"Sanskrit", "sat_Olck":"Santali", "snd_Arab":"Sindhi", "tam_Taml":"Tamil",
    "tel_Telu":"Telugu", "urd_Arab":"Urdu", "eng_Latn":"English",
}

def _available(package: str) -> bool:
    return importlib.util.find_spec(package) is not None

@lru_cache(maxsize=1)
def _indiclid():
    if not (INDIC_LID_PATH.exists() and _available("fasttext")):
        return None
    import fasttext
    return fasttext.load_model(str(INDIC_LID_PATH))

def identify(text: str) -> dict:
    """Use local IndicLID when installed; otherwise give an explicit estimate."""
    started = perf_counter(); model = _indiclid()
    if model:
        labels, scores = model.predict(text.replace("\n", " "), k=1)
        raw = labels[0].replace("__label__", "")
        code = raw if raw in SCHEDULED else raw.replace("_Latn", "")
        return {"language_code": raw, "language": SCHEDULED.get(code, raw), "script": script_of(text),
                "confidence": round(float(scores[0]), 4), "method": "IndicLID FastText", "available": True,
                "inference_time_ms": round((perf_counter()-started)*1000, 2)}
    language, script = language_of(text)
    return {"language_code": None, "language": language, "script": script, "confidence": None,
            "method": "heuristic fallback; IndicLID model unavailable", "available": False,
            "inference_time_ms": round((perf_counter()-started)*1000, 2),
            "warning": "Install the licensed local IndicLID artifact to validate 22-language and Romanised identification."}

@lru_cache(maxsize=1)
def _embedder():
    if not (EMBEDDING_PATH.exists() and _available("sentence_transformers")):
        return None
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(str(EMBEDDING_PATH), device="cpu")

def embeddings(texts: list[str]) -> tuple[list[list[float]] | None, dict]:
    started = perf_counter(); model = _embedder()
    if not model:
        return None, {"available": False, "method":"unavailable", "reason":"Install a local multilingual sentence-transformers model at MULTILINGUAL_EMBEDDING_PATH."}
    values = model.encode(texts, normalize_embeddings=True, batch_size=min(16, max(1, len(texts)),), show_progress_bar=False)
    return values.tolist(), {"available": True, "method":"local multilingual sentence embeddings", "inference_time_ms":round((perf_counter()-started)*1000,2)}

def model_status() -> dict:
    return {
        "indic_lid": {"available": bool(INDIC_LID_PATH.exists() and _available("fasttext")), "path": str(INDIC_LID_PATH)},
        "semantic_embeddings": {"available": bool(EMBEDDING_PATH.exists() and _available("sentence_transformers")), "path": str(EMBEDDING_PATH)},
        "indictrans2": {"available": INDICTRANS_ROOT.exists() and _available("ctranslate2"), "path": str(INDICTRANS_ROOT)},
    }
