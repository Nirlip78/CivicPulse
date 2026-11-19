"""Cautious, local complaint-intelligence helpers."""
import re
from time import perf_counter
from backend.app.nlp.preprocessing import analyse
from backend.app.nlp.sentiment import predict_hindi_sentiment
from backend.app.nlp.multilingual import identify
from backend.app.services.summaries import factual_summary

CATEGORY_KEYWORDS = {
    "Water Supply": {"water", "pani", "पानी", "supply", "tap", "जल", "pipeline"},
    "Electricity": {"electricity", "power", "bill", "light", "bijli", "बिजली", "current"},
    "Healthcare": {"hospital", "doctor", "health", "medicine", "अस्पताल", "दवा", "clinic"},
    "Sanitation": {"garbage", "waste", "drain", "toilet", "कचरा", "सफाई", "sewage"},
    "Roads/Transport": {"road", "roads", "pothole", "bus", "traffic", "सड़क", "transport"},
    "Ration/Aadhaar": {"ration", "aadhaar", "aadhar", "card", "राशन", "आधार", "biometric"},
}
RECOMMENDATIONS = {
    "Water Supply": "Verify the affected locality, check existing water-supply complaints, and assign the report to the relevant department.",
    "Electricity": "Check the affected connection or locality, review related outage reports, and route the report to the electricity team.",
    "Healthcare": "Verify the service concern and route the report to the relevant health-service administrator for review.",
    "Sanitation": "Check whether a sanitation request already exists for the area and assign it to the appropriate sanitation team.",
    "Roads/Transport": "Verify the reported road or transport issue, review related reports, and route it to the responsible civic team.",
    "Ration/Aadhaar": "Verify the reported service issue and route it to the responsible ration or identity-service team.",
}
NEGATIVE = {"not", "no", "nahi", "नहीं", "unavailable", "broken", "bad", "terrible", "problem", "issue", "action", "hua"}
POSITIVE = {"thanks", "thank", "resolved", "fixed", "good", "helpful", "धन्यवाद"}

def _duration(text: str) -> str | None:
    for pattern in (r"\b(?:for|since|from)\s+(\d+\s+(?:day|days|week|weeks|month|months|hour|hours))\b", r"\b(?:pichle|pichhle)\s+(\d+\s+(?:din|hafte|mahine|ghante))\b", r"\b(\d+\s+(?:din|hafte|mahine|ghante))\s+se\b", r"\b(\d+\s+दिन|\d+\s+हफ्ते|\d+\s+महीने)\s+से\b"):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match: return re.sub(r"\bdin\b", "days", match.group(1), flags=re.I)
    return None

def _previous_action(text: str) -> str | None:
    if re.search(r"\b(kai|several|multiple|many|repeat(?:ed|edly)?)\b.{0,30}\b(complain|complaint|report)", text, re.I) or re.search(r"complain\s+kiya", text, re.I): return "Complaints reportedly submitted several times."
    if re.search(r"\bcomplain(?:t)?\b|\breport(?:ed)?\b|शिकायत", text, re.I): return "A previous complaint or report is mentioned."
    return None

def _unresolved(text: str) -> str | None:
    return "No action is reported by the resident." if re.search(r"\b(no|not|nahi|नहीं)\b.{0,25}\b(action|response|solution|resolve|hua|हुआ)", text, re.I) else None

def _locations(text: str) -> list[str]:
    found = re.findall(r"\b(?:in|at|near)\s+([A-Z][A-Za-z .'-]{2,40})(?=[,.!?]|\s+(?:for|since|and|but)|$)", text)
    return list(dict.fromkeys(item.strip() for item in found))

def predict(text: str) -> dict:
    started = perf_counter(); technical = analyse(text); language_identity = identify(text)
    # The legacy heuristic remains a transparent fallback only.  When IndicLID
    # is installed its result is surfaced and drives language-specific routing.
    if language_identity["available"]:
        technical["language"] = language_identity["language"]
        technical["script"] = language_identity["script"]
    technical["language_identification"] = language_identity
    observed = set(technical["tokens"])
    scored = {label: len(observed & keys) for label, keys in CATEGORY_KEYWORDS.items()}
    category, hits = max(scored.items(), key=lambda item: item[1]); category = category if hits else "Needs human review"
    confidence = round(hits / max(1, len(observed)), 2) if hits else None
    duration, previous_action, unresolved = _duration(text), _previous_action(text), _unresolved(text)
    negative_hits, positive_hits = sum(token in NEGATIVE for token in observed), sum(token in POSITIVE for token in observed)
    if technical["language"].startswith("Hindi"):
        sentiment_result = predict_hindi_sentiment(text)
        sentiment = sentiment_result["label"]
        sentiment_explanation = f"{sentiment_result['method']}; confidence {sentiment_result['confidence']:.0%}. {sentiment_result['limitations']}"
        sentiment_method = sentiment_result["method"]
    else:
        sentiment = "Negative" if negative_hits > positive_hits else "Positive" if positive_hits > negative_hits else "Neutral"
        sentiment_explanation = "A local lexical estimate based on words in the submitted text; it requires human review."
        sentiment_method = "Transparent lexical baseline (not trained for this language/task)"
    issue = f"{category} concern" if category != "Needs human review" else "Civic service concern"
    finding = f"{issue} reported" + (f" for {duration}" if duration else "") + "."
    if previous_action and unresolved: finding += " The resident states that repeated complaints have not resulted in action."
    elif unresolved: finding += " The resident reports that no action has occurred."
    elif previous_action: finding += " A previous complaint is mentioned."
    summary_result = factual_summary(text)
    technical.update({"model": "Transparent keyword baseline (not a trained civic classifier)", "model_version": "rules-1.1", "category_scores": scored, "processing_time_ms": round((perf_counter() - started) * 1000, 2)})
    warnings = ["Model-generated suggestions are not verified facts.", "This local baseline has not been validated for operational decisions."]
    if summary_result.get("warning"): warnings.append(summary_result["warning"])
    return {"original_text": text, "detected_language": technical["language"], "category": category, "category_confidence": confidence, "sentiment": sentiment, "sentiment_explanation": sentiment_explanation, "sentiment_method": sentiment_method, "main_finding": finding, "summary": summary_result["summary"], "summary_method": summary_result["method"], "summary_evidence": summary_result["evidence"], "extracted_information": {"issue": issue, "affected_service": category if category != "Needs human review" else "Not mentioned", "reported_duration": duration or "Not mentioned", "previous_action": previous_action or "Not mentioned", "unresolved_concern": unresolved or "Not mentioned", "named_locations_or_organisations": _locations(text) or ["Not mentioned"]}, "reported_duration": duration, "previous_action": previous_action, "current_unresolved_concern": unresolved, "recommended_next_step": RECOMMENDATIONS.get(category, "Review the report, verify the details with the resident, and route it to the appropriate service team."), "urgency": "Needs human review", "similar_complaints": [], "model_metadata": {"name": "Transparent keyword baseline", "version": "rules-1.3", "confidence_supported": True}, "warnings": warnings, "technical_details": technical}
