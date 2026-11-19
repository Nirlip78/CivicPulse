"""IndicTrans2 deployment gate.  Never returns a fabricated translation."""
from __future__ import annotations
from backend.app.nlp.multilingual import model_status

def translate(text: str, source_language: str, target_language: str) -> dict:
    status = model_status()["indictrans2"]
    if not status["available"]:
        return {"available":False, "original_text":text, "translated_text":None, "source_language":source_language,
                "target_language":target_language, "engine":"IndicTrans2", "warning":"IndicTrans2 is not installed locally. No translation was generated.",
                "installation_requirement":"Install CTranslate2, IndicTrans2 preprocessing dependencies, and approved local IndicTrans2 model artifacts."}
    # The model layout is deliberately explicit: deployments supply the tested
    # adapter rather than downloading opaque weights during a citizen request.
    return {"available":False, "original_text":text, "translated_text":None, "source_language":source_language,
            "target_language":target_language, "engine":"IndicTrans2", "warning":"IndicTrans2 artifacts are present but no deployment adapter has been configured.",
            "installation_requirement":"Set CIVICPULSE_INDIC_TRANS_ADAPTER to a tested deployment adapter."}
