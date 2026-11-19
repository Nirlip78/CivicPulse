import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer

EN_STOP = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has", "have", "in", "is", "it", "of", "on", "or", "that", "the", "to", "with"}
HI_STOP = {"और", "का", "की", "के", "को", "में", "से", "है", "हैं", "था", "थे", "यह", "वह", "पर", "एक", "भी"}

def script_of(text: str) -> str:
    devanagari = sum("\u0900" <= char <= "\u097f" for char in text)
    latin = sum(char.isascii() and char.isalpha() for char in text)
    if devanagari and latin: return "Mixed (Devanagari/Latin)"
    if devanagari: return "Devanagari"
    if latin: return "Latin"
    return "Unknown"

ROMAN_HINDI = {"hai", "nahi", "mein", "mera", "hamare", "pani", "baar", "din", "se", "kiya", "raha", "hua", "area", "pichle"}

def language_of(text: str) -> tuple[str, str]:
    script = script_of(text)
    if script == "Devanagari": return "Hindi (estimated)", script
    if script.startswith("Mixed"): return "Mixed Hindi/English (estimated)", script
    words = set(re.findall(r"[a-z]+", text.lower()))
    return ("Hinglish (estimated)" if len(words & ROMAN_HINDI) >= 2 else "English (estimated)"), script

def tokenize(text: str) -> list[str]:
    return re.findall(r"[\w\u0900-\u097f]+", text.lower(), flags=re.UNICODE)

def analyse(text: str) -> dict:
    language, script = language_of(text)
    tokens = tokenize(text)
    # Preserve Romanised Hindi intact: English-looking stop words can carry its meaning.
    stop_words = HI_STOP if language.startswith("Hindi") else EN_STOP if language.startswith("English") else set()
    removed = [token for token in tokens if token in stop_words]
    kept = [token for token in tokens if token not in stop_words]
    terms = Counter(kept)
    vectorizer = TfidfVectorizer(ngram_range=(1, 3), token_pattern=r"(?u)\b\w+\b")
    matrix = vectorizer.fit_transform([" ".join(kept) or "empty"])
    scores = dict(zip(vectorizer.get_feature_names_out().tolist(), matrix.toarray()[0].round(4).tolist()))
    return {"original": text, "language": language, "script": script, "normalised": " ".join(tokens), "tokens": tokens, "removed_stop_words": removed, "processed_tokens": kept, "term_frequencies": dict(terms), "vocabulary_size": len(terms), "tfidf": scores, "method": "language-aware local tokenisation and TF-IDF", "human_review_required": True}
