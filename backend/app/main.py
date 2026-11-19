from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import case
from sqlalchemy.orm import Session, selectinload
from backend.app.core.config import ADMIN_ACCESS_KEY
from backend.app.core.security import create_access_token, current_user, hash_password, require_admin, verify_password
from backend.app.database.session import migrate_schema, get_db
from backend.app.models import Attachment, CitizenResponse, Complaint, Prediction, StatusHistory, User
from backend.app.nlp.civic import predict
from backend.app.nlp.preprocessing import analyse, tokenize
from backend.app.nlp.multilingual import embeddings as multilingual_embeddings, identify, model_status
from backend.app.schemas.contracts import AdminLoginRequest, ComplaintCreate, ComplaintOut, ComplaintUpdate, LoginRequest, RegisterRequest, ResponseCreate, SummaryRequest, TokenResponse, TranslationRequest
from backend.app.services.research import attention_demo, dataset_inventory, evaluate_civic_baseline, evaluate_hindi_sentiment, multilingual_quality_dashboard, summarise, word2vec_demo
from backend.app.services.summaries import factual_summary
from backend.app.services.translation import translate
from datetime import datetime
from pathlib import Path
from collections import Counter, defaultdict
import csv
import io
import mimetypes
import os
import uuid

VALID_STATUSES = {"Submitted", "Under Review", "Assigned", "In Progress", "Resolved", "Rejected"}
ACTIVE_STATUSES = {"Submitted", "Under Review", "Assigned", "In Progress"}
CRITICAL_PRIORITY = "Critical"
HIGH_PRIORITY = "High"
HIGH_PRIORITY_REPORT_COUNT = 2
CRITICAL_REPORT_COUNT = 3
# Coordinates are compared before the dashboard's privacy rounding.  This is
# roughly a 330m cell at the equator and is deliberately conservative.
NEARBY_LOCATION_DELTA = 0.003
UPLOAD_ROOT = Path(os.getenv("CIVICPULSE_UPLOAD_DIR", Path(__file__).resolve().parents[2] / "uploads")).resolve()
UPLOAD_MAX_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", "5242880"))
ALLOWED_IMAGES = {"image/jpeg", "image/png", "image/webp"}

@asynccontextmanager
async def lifespan(_: FastAPI):
    migrate_schema()
    yield

app = FastAPI(title="CivicPulse API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def health_payload():
    return {"status": "ok", "service": "CivicPulse", "mode": "local-first"}

@app.get("/", tags=["system"])
def root():
    return {"message": "CivicPulse API is running.", "docs": "/docs", "health": "/api/health"}

@app.get("/health", tags=["system"])
@app.get("/api/health", tags=["system"])
def health():
    return health_payload()

@app.post("/auth/register", response_model=TokenResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter_by(email=request.email.lower()).first():
        raise HTTPException(409, "Email already registered")
    user = User(email=request.email.lower(), password_hash=hash_password(request.password))
    db.add(user); db.commit(); db.refresh(user)
    return TokenResponse(access_token=create_access_token(user))

@app.post("/auth/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=request.email.lower()).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return TokenResponse(access_token=create_access_token(user))

@app.post("/auth/admin-login", response_model=TokenResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Local-lab admin access. Configure ADMIN_ACCESS_KEY outside development."""
    if request.access_key != ADMIN_ACCESS_KEY:
        raise HTTPException(401, "Incorrect administrator access key")
    user = db.query(User).filter_by(email="local-admin@civicpulse.invalid").first()
    if user is None:
        user = User(email="local-admin@civicpulse.invalid", password_hash=hash_password("system-admin-" + ADMIN_ACCESS_KEY), role="admin")
        db.add(user); db.commit(); db.refresh(user)
    elif user.role != "admin":
        user.role = "admin"; db.commit()
    return TokenResponse(access_token=create_access_token(user))

def related_complaints(text: str, db: Session, limit: int = 5) -> list[dict]:
    """Return transparent lexical similarity matches from actual stored reports."""
    source = set(tokenize(text))
    matches = []
    for item in db.query(Complaint).order_by(Complaint.created_at.desc()).limit(250):
        target = set(tokenize(item.description))
        score = len(source & target) / max(1, len(source | target))
        if score >= .12:
            matches.append({"reference": f"#{item.id}", "category": item.category or "Not classified", "date": item.created_at.isoformat(), "status": item.status, "similarity_score": round(score, 2), "short_description": " ".join(item.description.split()[:20])})
    return sorted(matches, key=lambda match: match["similarity_score"], reverse=True)[:limit]

def complaint_for_user(complaint_id: int, user: User, db: Session) -> Complaint:
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(404, "Complaint not found")
    if user.role != "admin" and complaint.citizen_id != user.id:
        raise HTTPException(403, "You do not have access to this complaint")
    return complaint

def filtered_complaints(db: Session, category: str | None = None, status: str | None = None, locality: str | None = None, start: datetime | None = None, end: datetime | None = None):
    query = db.query(Complaint)
    if category: query = query.filter(Complaint.category == category)
    if status: query = query.filter(Complaint.status == status)
    if locality: query = query.filter(Complaint.locality.ilike(f"%{locality}%"))
    if start: query = query.filter(Complaint.created_at >= start)
    if end: query = query.filter(Complaint.created_at <= end)
    return query

def is_same_nearby_problem(candidate: Complaint, category: str | None, latitude: float | None, longitude: float | None) -> bool:
    """Return whether a report is the same classified issue in a nearby area.

    Only active complaints participate: a previously resolved report should
    not make a fresh incident appear critical.  Category comparison makes the
    escalation deterministic and avoids treating unrelated nearby reports as
    the same problem.
    """
    return (
        latitude is not None and longitude is not None
        and candidate.status in ACTIVE_STATUSES
        and candidate.category == category
        and candidate.latitude is not None and candidate.longitude is not None
        and abs(candidate.latitude - latitude) <= NEARBY_LOCATION_DELTA
        and abs(candidate.longitude - longitude) <= NEARBY_LOCATION_DELTA
    )

def active_nearby_reports(db: Session, category: str | None, latitude: float | None, longitude: float | None) -> list[Complaint]:
    if latitude is None or longitude is None or not category:
        return []
    candidates = db.query(Complaint).filter(
        Complaint.status.in_(ACTIVE_STATUSES),
        Complaint.category == category,
        Complaint.latitude.is_not(None),
        Complaint.longitude.is_not(None),
        Complaint.latitude.between(latitude - NEARBY_LOCATION_DELTA, latitude + NEARBY_LOCATION_DELTA),
        Complaint.longitude.between(longitude - NEARBY_LOCATION_DELTA, longitude + NEARBY_LOCATION_DELTA),
    ).all()
    return [row for row in candidates if is_same_nearby_problem(row, category, latitude, longitude)]

def priority_for_report_count(report_count: int) -> str:
    if report_count >= CRITICAL_REPORT_COUNT:
        return CRITICAL_PRIORITY
    if report_count >= HIGH_PRIORITY_REPORT_COUNT:
        return HIGH_PRIORITY
    return "Normal"

def concise_english_title(analysis: dict) -> str:
    """Create a brief English overview, not a restatement of the report."""
    category = analysis.get("category")
    subject = f"{category} issue" if category and category != "Needs human review" else "Civic service issue"
    duration = analysis.get("reported_duration")
    return f"{subject} — {duration}"[:80] if duration else subject[:80]

@app.post("/nlp/analyse")
def nlp_analyse(payload: ComplaintCreate, db: Session = Depends(get_db)):
    result = predict(payload.description)
    result["similar_complaints"] = related_complaints(payload.description, db)
    return result

@app.post("/nlp/preprocess")
def nlp_preprocess(payload: ComplaintCreate): return analyse(payload.description)

@app.post("/nlp/language-identify")
def language_identify(payload: ComplaintCreate): return identify(payload.description)

@app.get("/models/status")
def models_status(): return model_status()

@app.post("/translation")
def translation(payload: TranslationRequest): return translate(payload.text, payload.source_language, payload.target_language)

@app.post("/summaries")
def summaries(payload: SummaryRequest): return factual_summary(payload.text, payload.output_language, payload.detail)

@app.post("/similarity/search")
def semantic_similarity(payload: ComplaintCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    query_vectors, metadata = multilingual_embeddings([payload.description])
    if query_vectors is None:
        return {"matches": [], **metadata, "warning":"No lexical fallback is presented as cross-language semantic similarity."}
    # Embeddings are computed in a bounded batch; no automatic merge is ever performed.
    rows = db.query(Complaint).order_by(Complaint.created_at.desc()).limit(250).all()
    vectors, row_metadata = multilingual_embeddings([row.description for row in rows])
    import numpy as np
    scores = np.dot(np.asarray(vectors), np.asarray(query_vectors[0]))
    matches = [{"reference":f"#{row.id}","similarity_score":round(float(score),4),"description":row.description} for row, score in zip(rows, scores) if score >= .55]
    return {"matches":sorted(matches,key=lambda item:item["similarity_score"],reverse=True)[:10], **metadata,
            "candidate_count":len(rows), "warning":"Semantic matches are review candidates only and are never merged automatically."}

@app.get("/datasets")
def datasets(_: User = Depends(require_admin)): return dataset_inventory()

@app.post("/research/embeddings")
def embeddings(mode: str = "skipgram", dimensions: int = Query(12, ge=2, le=64), window: int = Query(2, ge=1, le=5), epochs: int = Query(4, ge=1, le=20), _: User = Depends(require_admin)):
    if mode.lower() not in {"skipgram", "cbow"}: raise HTTPException(422, "mode must be skipgram or cbow")
    return word2vec_demo(mode, dimensions, window, epochs)

@app.post("/research/attention")
def attention(payload: ComplaintCreate, _: User = Depends(require_admin)): return attention_demo(payload.description)

@app.post("/research/summarise")
def local_summary(payload: ComplaintCreate, _: User = Depends(require_admin)): return summarise(payload.description)

@app.post("/research/evaluate/civic-baseline")
def evaluate(_: User = Depends(require_admin)): return evaluate_civic_baseline()

@app.post("/research/evaluate/hindi-sentiment")
def evaluate_hindi_sentiment_model(_: User = Depends(require_admin)): return evaluate_hindi_sentiment()

@app.get("/research/quality-dashboard")
def quality_dashboard(_: User = Depends(require_admin)): return multilingual_quality_dashboard()

@app.post("/complaints", response_model=ComplaintOut, status_code=201)
def create_complaint(request: ComplaintCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    analysis = predict(request.description)
    category = request.category or analysis["category"]
    nearby_reports = active_nearby_reports(db, category, request.latitude, request.longitude)
    nearby_report_count = len(nearby_reports) + 1
    priority = priority_for_report_count(nearby_report_count)
    priority_note = (
        f"Very high — Critical: {nearby_report_count} active reports of the same category are within approximately 330m."
        if priority == CRITICAL_PRIORITY else
        f"High priority: {nearby_report_count} active reports of the same category are within approximately 330m."
        if priority == HIGH_PRIORITY else None
    )
    # When a cluster reaches the critical threshold, elevate its existing active
    # reports too, so the queue prioritises the incident rather than just the
    # most recently submitted complaint.
    if priority != "Normal":
        for nearby in nearby_reports:
            nearby.priority = priority
            nearby.admin_note = priority_note
    # Store a brief English overview rather than a potentially multilingual
    # source sentence or a long restatement of the complaint.
    complaint = Complaint(citizen_id=user.id, title=concise_english_title(analysis), description=request.description, location=request.location, original_location=request.location, locality=request.locality, landmark=request.landmark, latitude=request.latitude, longitude=request.longitude, location_source="gps" if request.latitude is not None else "manual" if request.location else None, preferred_language=request.preferred_language, detected_language=analysis["detected_language"], supporting_information=request.supporting_information, category=category, urgency=analysis["urgency"], sentiment=analysis["sentiment"], priority=priority, admin_note=priority_note)
    db.add(complaint); db.flush()
    complaint.reference = f"CP-{complaint.created_at:%Y}-{complaint.id:06d}"
    for field, value, confidence in (("category", analysis["category"], str(analysis["category_confidence"]) if analysis["category_confidence"] is not None else None), ("sentiment", analysis["sentiment"], None), ("urgency", analysis["urgency"], None)):
        db.add(Prediction(complaint_id=complaint.id, field=field, value=value, confidence=confidence, method=analysis["model_metadata"]["name"]))
    db.add(StatusHistory(complaint_id=complaint.id, status="Submitted", note="Complaint submitted" + (f"; {priority_note}" if priority_note else "")))
    db.commit()
    return db.query(Complaint).options(selectinload(Complaint.predictions)).filter_by(id=complaint.id).first()

@app.post("/complaints/{complaint_id}/attachments", status_code=201)
async def upload_attachment(complaint_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    complaint_for_user(complaint_id, user, db)
    if file.content_type not in ALLOWED_IMAGES:
        raise HTTPException(415, "Only JPEG, PNG, and WebP images are accepted")
    payload = await file.read(UPLOAD_MAX_BYTES + 1)
    if not payload or len(payload) > UPLOAD_MAX_BYTES:
        raise HTTPException(413, f"Image must be between 1 byte and {UPLOAD_MAX_BYTES} bytes")
    extension = {"image/jpeg":".jpg", "image/png":".png", "image/webp":".webp"}[file.content_type]
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    stored = f"{uuid.uuid4().hex}{extension}"
    (UPLOAD_ROOT / stored).write_bytes(payload)
    record = Attachment(complaint_id=complaint_id, uploaded_by_id=user.id, original_filename=Path(file.filename or "image").name[:255], stored_filename=stored, media_type=file.content_type, size_bytes=len(payload))
    db.add(record); db.commit(); db.refresh(record)
    return {"id":record.id, "filename":record.original_filename, "media_type":record.media_type, "size_bytes":record.size_bytes}

@app.get("/complaints/{complaint_id}/attachments")
def list_attachments(complaint_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    complaint_for_user(complaint_id, user, db)
    rows = db.query(Attachment).filter_by(complaint_id=complaint_id).order_by(Attachment.created_at).all()
    return [{"id":row.id, "filename":row.original_filename, "media_type":row.media_type, "size_bytes":row.size_bytes, "url":f"/attachments/{row.id}/content"} for row in rows]

@app.get("/attachments/{attachment_id}/content")
def attachment_content(attachment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    attachment = db.get(Attachment, attachment_id)
    if not attachment: raise HTTPException(404, "Attachment not found")
    complaint_for_user(attachment.complaint_id, user, db)
    path = (UPLOAD_ROOT / attachment.stored_filename).resolve()
    if UPLOAD_ROOT not in path.parents or not path.exists(): raise HTTPException(404, "Attachment content not found")
    return FileResponse(path, media_type=attachment.media_type, filename=attachment.original_filename)

@app.delete("/attachments/{attachment_id}", status_code=204)
def delete_attachment(attachment_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    attachment = db.get(Attachment, attachment_id)
    if not attachment: raise HTTPException(404, "Attachment not found")
    complaint = complaint_for_user(attachment.complaint_id, user, db)
    if user.role != "admin" and attachment.uploaded_by_id != user.id: raise HTTPException(403, "Only the uploader or an administrator may remove this image")
    path = (UPLOAD_ROOT / attachment.stored_filename).resolve()
    if UPLOAD_ROOT in path.parents and path.exists(): path.unlink()
    db.delete(attachment); db.commit()

@app.get("/complaints/me", response_model=list[ComplaintOut])
def my_complaints(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(Complaint).options(selectinload(Complaint.predictions)).filter_by(citizen_id=user.id).order_by(Complaint.created_at.desc()).all()

@app.get("/admin/complaints", response_model=list[ComplaintOut])
def all_complaints(query: str | None = None, status: str | None = None, category: str | None = None, locality: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    statement = db.query(Complaint).options(selectinload(Complaint.predictions)).filter(Complaint.status.in_(ACTIVE_STATUSES))
    if query: statement = statement.filter(Complaint.description.ilike(f"%{query}%"))
    if status: statement = statement.filter(Complaint.status == status)
    if category: statement = statement.filter(Complaint.category == category)
    if locality: statement = statement.filter(Complaint.locality.ilike(f"%{locality}%"))
    # Queue the most frequently reported nearby incidents before individual reports.
    priority_order = case((Complaint.priority == CRITICAL_PRIORITY, 0), (Complaint.priority == HIGH_PRIORITY, 1), else_=2)
    return statement.order_by(priority_order, Complaint.created_at.desc()).limit(200).all()

@app.get("/admin/geography/complaints")
def geographic_complaints(category: str | None = None, status: str | None = None, locality: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = filtered_complaints(db, category, status, locality).filter(Complaint.status.in_(ACTIVE_STATUSES), Complaint.latitude.is_not(None), Complaint.longitude.is_not(None)).all()
    # Coordinates are deliberately rounded for the dashboard so a map does not
    # expose a citizen's precise residence.
    return [{"reference":row.reference, "category":row.category, "status":row.status, "priority":row.priority, "summary":row.title or row.description[:120], "short_description":" ".join(row.description.split())[:180], "latitude":round(row.latitude, 3), "longitude":round(row.longitude, 3), "locality":row.locality, "created_at":row.created_at} for row in rows]

@app.get("/admin/geography/heatmap")
def geographic_heatmap(category: str | None = None, status: str | None = None, locality: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = filtered_complaints(db, category, status, locality).filter(Complaint.status.in_(ACTIVE_STATUSES), Complaint.latitude.is_not(None), Complaint.longitude.is_not(None)).all()
    buckets: dict[tuple[float,float], int] = Counter((round(row.latitude, 3), round(row.longitude, 3)) for row in rows)
    # A bucket is emitted only for at least two reports to reduce re-identification risk.
    return {"points":[{"latitude":lat,"longitude":lon,"weight":count} for (lat,lon), count in buckets.items() if count >= 2], "suppressed_single_report_points":sum(1 for count in buckets.values() if count < 2), "source_records":len(rows), "privacy":"Coordinates rounded to 3 decimals; single-report buckets suppressed."}

@app.get("/admin/analytics")
def analytics(category: str | None = None, status: str | None = None, locality: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = filtered_complaints(db, category, status, locality).all()
    def counts(field): return dict(Counter((getattr(row, field) or "Unspecified") for row in rows))
    dates = Counter(row.created_at.date().isoformat() for row in rows)
    unresolved = {"Submitted", "Under Review", "Assigned", "In Progress"}
    return {"total":len(rows), "by_category":counts("category"), "by_status":counts("status"), "by_locality":counts("locality"), "by_language":counts("detected_language"), "by_sentiment":counts("sentiment"), "by_department":counts("department"), "over_time":[{"date":date,"count":count} for date,count in sorted(dates.items())], "unresolved":sum(row.status in unresolved for row in rows), "high_priority":sum(row.priority in {"High", CRITICAL_PRIORITY} for row in rows), "critical":sum(row.priority == CRITICAL_PRIORITY for row in rows), "filters":{"category":category,"status":status,"locality":locality}, "source":"live complaint records"}

@app.get("/admin/exports/complaints.csv")
def export_complaints(category: str | None = None, status: str | None = None, locality: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = filtered_complaints(db, category, status, locality).all()
    buffer = io.StringIO(); writer = csv.writer(buffer)
    writer.writerow(["reference","title","category","status","locality","department","priority","created_at","resolved_at"])
    for row in rows: writer.writerow([row.reference,row.title,row.category,row.status,row.locality,row.department,row.priority,row.created_at.isoformat(),row.resolved_at.isoformat() if row.resolved_at else ""])
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=civicpulse-complaints.csv"})

@app.get("/admin/assistant")
def civic_assistant(question: str = Query(min_length=3, max_length=500), locality: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    rows = filtered_complaints(db, locality=locality).all()
    # Database aggregation is intentionally deterministic; there is no LLM that
    # could invent counts or statuses.
    category_counts = Counter(row.category or "Unspecified" for row in rows)
    locality_counts = Counter(row.locality or "Unspecified" for row in rows)
    references = [row.reference for row in sorted(rows, key=lambda item:item.created_at, reverse=True)[:10]]
    q = question.lower()
    if not rows: answer = "No matching complaint records are available for the requested scope."
    elif "localit" in q or locality: answer = f"{len(rows)} complaint record(s) match. Most reported locality: {locality_counts.most_common(1)[0][0]} ({locality_counts.most_common(1)[0][1]})."
    elif "common" in q or "category" in q or "problem" in q: answer = f"{len(rows)} complaint record(s) match. Most frequent category: {category_counts.most_common(1)[0][0]} ({category_counts.most_common(1)[0][1]})."
    else: answer = f"{len(rows)} complaint record(s) match the current scope. Ask about the most common category or locality for a grounded aggregate."
    return {"answer":answer, "references":references, "date_range":{"start":min((row.created_at for row in rows),default=None),"end":max((row.created_at for row in rows),default=None)}, "method":"permission-scoped structured database aggregation", "warning":"Counts are complaint reports, not confirmed civic incidents."}

@app.patch("/admin/complaints/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: int, request: ComplaintUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    complaint = db.query(Complaint).options(selectinload(Complaint.predictions)).filter_by(id=complaint_id).first()
    if not complaint: raise HTTPException(404, "Complaint not found")
    values = request.model_dump(exclude_unset=True)
    if "status" in values and values["status"] not in VALID_STATUSES: raise HTTPException(422, "Invalid status")
    for field, value in values.items(): setattr(complaint, field, value)
    if "status" in values:
        if values["status"] == "Resolved": complaint.resolved_at = datetime.utcnow()
        elif complaint.status != "Resolved": complaint.resolved_at = None
        db.add(StatusHistory(complaint_id=complaint.id, status=values["status"], note=request.admin_note, changed_by_id=admin.id))
        # A resolved report no longer contributes to the active incident count.
        # Recompute the remaining nearby reports so they can fall back from
        # Critical/High when the cluster quantity decreases.
        nearby_active = active_nearby_reports(db, complaint.category, complaint.latitude, complaint.longitude)
        if nearby_active:
            cluster_priority = priority_for_report_count(len(nearby_active))
            cluster_note = (
                f"Very high — Critical: {len(nearby_active)} active reports of the same category are within approximately 330m."
                if cluster_priority == CRITICAL_PRIORITY else
                f"High priority: {len(nearby_active)} active reports of the same category are within approximately 330m."
                if cluster_priority == HIGH_PRIORITY else None
            )
            for nearby in nearby_active:
                nearby.priority = cluster_priority
                nearby.admin_note = cluster_note
    for field in ("category", "urgency"):
        if field in values:
            original = next((item for item in complaint.predictions if item.field == field), None)
            if original: original.human_correction = values[field]
    db.commit(); db.refresh(complaint)
    return complaint

@app.post("/admin/complaints/{complaint_id}/response")
def respond(complaint_id: int, request: ResponseCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if not db.get(Complaint, complaint_id): raise HTTPException(404, "Complaint not found")
    item=CitizenResponse(complaint_id=complaint_id, author_id=admin.id, message=request.message); db.add(item); db.commit()
    return {"id":item.id,"message":item.message,"created_at":item.created_at}

@app.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(current_user)):
    statement=db.query(Complaint)
    if user.role != "admin": statement=statement.filter(Complaint.citizen_id==user.id)
    rows=statement.all()
    def distribution(field):
        values={}
        for row in rows:
            value=getattr(row,field) or "Unspecified"; values[value]=values.get(value,0)+1
        return values
    return {"total":len(rows),"by_status":distribution("status"),"by_category":distribution("category"),"by_language":{analyse(row.description)["language"]:sum(1 for other in rows if analyse(other.description)["language"]==analyse(row.description)["language"]) for row in rows},"by_sentiment":distribution("sentiment"),"scope":"all complaints" if user.role=="admin" else "your complaints"}
