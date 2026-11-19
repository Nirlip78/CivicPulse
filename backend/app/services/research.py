"""Small, local research demonstrations that do not require model downloads."""
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import re
import numpy as np
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from backend.app.core.config import ROOT_DIR
from backend.app.nlp.preprocessing import tokenize
from backend.app.nlp.sentiment import evaluate_hindi_sentiment

DATASETS = [
    {"name":"Civic complaint categories","path":"datasets/processed/civic_complaints/civic_complaints_labeled.csv","task":"category classification","language":"English/Hindi","records":120,"splits":"no supplied split; derive only in experiment","limitations":"Small; provenance unconfirmed."},
    {"name":"Hindi sentiment","path":"datasets/processed/sentiment/hindi_sentiment_train.csv","task":"sentiment","language":"Hindi","records":4182,"splits":"train/validation/test fixed (4,182 / 523 / 523)","limitations":"General-domain, not civic. A small local classifier is available only for Hindi."},
    {"name":"Hinglish sentiment","path":"datasets/processed/sentiment/hinglish_sentiment.csv","task":"sentiment","language":"Hinglish/mixed","records":2766,"splits":"single supplied file","limitations":"Noisy general-domain data."},
    {"name":"Hindi NER","path":"datasets/raw/ner/hiner_train.json","task":"named entity recognition","language":"Hindi","records":75827,"splits":"train/validation/test fixed","limitations":"CPU fine-tuning optional; JSON/CoNLL are alternatives."},
    {"name":"English–Hindi parallel text","path":"datasets/raw/translation/parallel_dev.en","task":"translation inspection","language":"English/Hindi","records":520,"splits":"dev and held-out test only","limitations":"No supplied training split."},
]

def dataset_inventory() -> list[dict]:
    output = []
    for item in DATASETS:
        complete = ROOT_DIR / item["path"]
        output.append({**item, "available": complete.exists(), "format": complete.suffix.lstrip(".")})
    return output

def corpus() -> list[list[str]]:
    path = ROOT_DIR / "datasets/processed/civic_complaints/civic_complaints_labeled.csv"
    with path.open(encoding="utf-8", newline="") as source:
        return [tokenize(row["text"]) for row in csv.DictReader(source)]

def word2vec_demo(mode: str = "skipgram", dimensions: int = 12, window: int = 2, epochs: int = 4) -> dict:
    """Actual NumPy CBOW/Skip-gram negative-sampling training on the small civic corpus."""
    sentences = corpus()
    vocab = sorted({word for sentence in sentences for word in sentence})
    index = {word: i for i, word in enumerate(vocab)}
    if len(vocab) < 2: return {"status":"unavailable", "reason":"Corpus has insufficient vocabulary."}
    rng = np.random.default_rng(7)
    inp = rng.normal(0, .1, (len(vocab), dimensions)); out = np.zeros_like(inp)
    pairs = []
    for sentence in sentences:
        for position, target in enumerate(sentence):
            context = [index[word] for i, word in enumerate(sentence) if i != position and abs(i - position) <= window]
            if mode.lower() == "cbow" and context: pairs.append((context, index[target]))
            elif mode.lower() != "cbow": pairs.extend(([index[target]], context_word) for context_word in context)
    losses=[]; rate=.04
    def sigmoid(x): return 1 / (1 + np.exp(-np.clip(x, -30, 30)))
    for _ in range(max(1, min(epochs, 20))):
        total=0.0
        for context, target in pairs:
            vector = inp[context].mean(axis=0)
            for label, positive in [(target, 1), (int(rng.integers(len(vocab))), 0)]:
                score = float(sigmoid(vector @ out[label])); gradient = score-positive
                total += -(positive*np.log(score+1e-9)+(1-positive)*np.log(1-score+1e-9))
                old = out[label].copy(); out[label] -= rate*gradient*vector
                inp[context] -= rate*gradient*old/len(context)
        losses.append(round(total/max(1,len(pairs)),4))
    vectors = inp / np.maximum(np.linalg.norm(inp, axis=1, keepdims=True), 1e-12)
    query = next((word for word in ("water","पानी","road","electricity") if word in index), vocab[0])
    scores = vectors @ vectors[index[query]]; nearest = [vocab[i] for i in np.argsort(-scores)[1:6]]
    coordinates = PCA(n_components=2).fit_transform(vectors).round(4).tolist() if len(vocab) > 2 else []
    return {"status":"trained", "algorithm":f"NumPy {mode.upper()} with negative sampling", "corpus":"120 supplied civic transcripts", "configuration":{"dimensions":dimensions,"window":window,"epochs":epochs}, "vocabulary_size":len(vocab), "loss":losses, "query":query,"nearest":nearest,"coordinates":[{"word":word,"x":coordinates[i][0],"y":coordinates[i][1]} for i,word in enumerate(vocab[:80])]}

def attention_demo(text: str) -> dict:
    tokens = tokenize(text)[:24] or ["empty"]
    positions=np.arange(len(tokens)); embedding=np.array([[((sum(map(ord, token))+i*17)%97)/97 for i in range(8)] for token in tokens])
    scores=(embedding@embedding.T)/np.sqrt(embedding.shape[1]); weights=np.exp(scores-scores.max(axis=1,keepdims=True)); weights/=weights.sum(axis=1,keepdims=True)
    return {"tokens":tokens,"attention":weights.round(3).tolist(),"method":"deterministic scaled dot-product attention educational demonstration","limitations":"This is not a pretrained transformer or semantic NER model."}

def summarise(text: str) -> dict:
    sentences=[piece.strip() for piece in re.split(r"(?<=[.!?।])\s+", text) if piece.strip()]
    if not sentences: return {"summary":"", "method":"extractive frequency baseline", "warning":"No text supplied."}
    frequencies=Counter(token for sentence in sentences for token in tokenize(sentence))
    best=max(sentences, key=lambda sentence: sum(frequencies[token] for token in tokenize(sentence))/max(1,len(tokenize(sentence))))
    return {"summary":best,"method":"local extractive frequency baseline","warning":"Extractive output only; it does not verify facts or infer missing details."}

def evaluate_civic_baseline() -> dict:
    source=ROOT_DIR/"datasets/processed/civic_complaints/civic_complaints_labeled.csv"
    with source.open(encoding="utf-8", newline="") as handle: rows=list(csv.DictReader(handle))
    texts=[row["text"] for row in rows]; labels=[row["category"] for row in rows]
    x_train,x_test,y_train,y_test=train_test_split(texts,labels,test_size=.25,random_state=42,stratify=labels)
    model=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2))), ("classifier",LogisticRegression(max_iter=400,random_state=42))]); model.fit(x_train,y_train); prediction=model.predict(x_test)
    report=classification_report(y_test,prediction,output_dict=True,zero_division=0)
    result={"model":"TF-IDF + Logistic Regression baseline","dataset":"civic_complaints_labeled.csv","split":"documented stratified 75/25 derived split; random_state=42","timestamp":datetime.now(timezone.utc).isoformat(),"accuracy":round(float(accuracy_score(y_test,prediction)),4),"macro_f1":round(float(report["macro avg"]["f1-score"]),4),"weighted_f1":round(float(report["weighted avg"]["f1-score"]),4),"labels":sorted(set(labels)),"confusion_matrix":confusion_matrix(y_test,prediction,labels=sorted(set(labels))).tolist(),"per_class":{key:{"precision":round(value["precision"],4),"recall":round(value["recall"],4),"f1":round(value["f1-score"],4),"support":value["support"]} for key,value in report.items() if key in set(labels)},"limitations":"Small unverified-provenance dataset; use only as an academic baseline."}
    folder=ROOT_DIR/"experiments/results"; folder.mkdir(parents=True,exist_ok=True); (folder/"civic_tfidf_logreg.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result

def multilingual_quality_dashboard() -> dict:
    """Report only measurements that exist; null is never a zero score."""
    hindi = evaluate_hindi_sentiment()
    civic_path = ROOT_DIR / "experiments/results/civic_tfidf_logreg.json"
    civic = json.loads(civic_path.read_text(encoding="utf-8")) if civic_path.exists() else None
    unavailable = {"status":"unavailable", "reason":"No separate licensed evaluation set and completed measurement are available."}
    return {"language_identification": unavailable,
            "sentiment": {"Hindi": {"macro_f1":hindi["macro_f1"], "accuracy":hindi["accuracy"], "scope":"general-domain held-out Hindi"}, "other_languages":unavailable},
            "intent": unavailable,
            "complaint_category": {"English/Hindi": {"macro_f1":civic.get("macro_f1") if civic else None, "scope":"small 120-row civic baseline"}, "other_languages":unavailable},
            "sarcasm": unavailable, "translation_quality": unavailable, "summary_rouge": unavailable,
            "human_factual_consistency": unavailable,
            "runtime": {"status":"available per request", "note":"Endpoints report inference time where a model ran; no fabricated memory measurements."}}
