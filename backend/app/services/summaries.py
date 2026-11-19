"""Factual, evidence-linked summary fallback used when no generator is installed."""
from __future__ import annotations
import re
from backend.app.nlp.preprocessing import tokenize

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?।])\s+", text) if s.strip()]

def factual_summary(text: str, output_language: str = "original", detail: str = "short") -> dict:
    sentences = _sentences(text)
    if not sentences:
        return {"summary":"", "evidence":[], "status":"unavailable", "reason":"No text supplied."}
    # Extractive summaries preserve negation, names, numbers and dates because
    # they contain verbatim source sentences.  Generation is intentionally not
    # substituted when a checked local generator is unavailable.
    ranked = sorted(enumerate(sentences), key=lambda pair: (-len(tokenize(pair[1])), pair[0]))
    wanted = 1 if detail == "short" else min(3, len(sentences))
    selected = sorted(ranked[:wanted])
    evidence = [{"statement": sentence, "source_sentence": sentence, "sentence_index": index} for index, sentence in selected]
    warning = None if output_language == "original" else "Requested output language is unavailable without a configured translation model; returning the original-language extractive summary."
    return {"summary":" ".join(s for _, s in selected), "evidence":evidence, "method":"verbatim extractive factual fallback",
            "output_language":"original" if warning else output_language, "warning":warning,
            "factual_validation":{"passed":True,"mode":"verbatim evidence match","unknown_fields":"All facts not stated in the cited sentences are unknown."}}
