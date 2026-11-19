import pytest
from datetime import datetime
from fastapi import HTTPException
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models import User, Complaint, Attachment, Prediction, StatusHistory, CitizenResponse
from backend.app.schemas.contracts import (
    RegisterRequest, LoginRequest, AdminLoginRequest,
    ComplaintCreate, ComplaintUpdate, ResponseCreate
)
from backend.app.core.security import hash_password, current_user, require_admin
from backend.app import main as api

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_registration_and_login_flow(db):
    # Register citizen
    email = f"test_citizen_{int(datetime.utcnow().timestamp())}@civicpulse.invalid"
    reg_req = RegisterRequest(email=email, password="ValidPassword123!")
    token_resp = api.register(reg_req, db)
    assert token_resp.access_token

    # Duplicate registration should raise 409
    with pytest.raises(HTTPException) as exc:
        api.register(reg_req, db)
    assert exc.value.status_code == 409

    # Login with valid credentials
    log_req = LoginRequest(email=email, password="ValidPassword123!")
    log_resp = api.login(log_req, db)
    assert log_resp.access_token

    # Login with invalid password raises 401
    bad_req = LoginRequest(email=email, password="WrongPassword123!")
    with pytest.raises(HTTPException) as exc:
        api.login(bad_req, db)
    assert exc.value.status_code == 401

def test_admin_login(db):
    # Valid admin key
    adm_req = AdminLoginRequest(access_key="9099")
    resp = api.admin_login(adm_req, db)
    assert resp.access_token

    # Invalid admin key
    bad_adm = AdminLoginRequest(access_key="wrong_key")
    with pytest.raises(HTTPException) as exc:
        api.admin_login(bad_adm, db)
    assert exc.value.status_code == 401

def test_complaint_submission_workflow(db):
    # Create citizen user
    citizen = User(email=f"cit_{int(datetime.utcnow().timestamp())}@civicpulse.invalid", password_hash=hash_password("password1234"), role="citizen")
    db.add(citizen); db.commit(); db.refresh(citizen)

    # Submit complaint
    req = ComplaintCreate(
        description="Hamare area mein pichle 5 din se pani nahi aa raha hai. Pipeline is broken near main road.",
        location="Ward 12, Main Street",
        locality="Ward 12",
        latitude=28.6139,
        longitude=77.2090
    )
    complaint = api.create_complaint(req, db, citizen)
    assert complaint.id is not None
    assert complaint.reference.startswith("CP-")
    assert complaint.category == "Water Supply"
    assert complaint.priority in ("Normal", "High", "Critical")

    # Citizen list own complaints
    my_list = api.my_complaints(db, citizen)
    assert any(c.id == complaint.id for c in my_list)

    # Admin user
    admin = User(email=f"adm_{int(datetime.utcnow().timestamp())}@civicpulse.invalid", password_hash=hash_password("adminpass1234"), role="admin")
    db.add(admin); db.commit(); db.refresh(admin)

    # Admin list active complaints
    admin_list = api.all_complaints(query=None, status=None, category=None, locality=None, db=db, _=admin)
    assert any(c.id == complaint.id for c in admin_list)

    # Admin update status to Under Review
    upd_req = ComplaintUpdate(status="Under Review", admin_note="Inspecting pipeline")
    updated = api.update_complaint(complaint.id, upd_req, db, admin)
    assert updated.status == "Under Review"

    # Admin response
    resp_req = ResponseCreate(message="Field team has been notified.")
    response_out = api.respond(complaint.id, resp_req, db, admin)
    assert response_out["message"] == "Field team has been notified."

    # Admin resolves complaint -> check resolved_at
    res_req = ComplaintUpdate(status="Resolved")
    resolved = api.update_complaint(complaint.id, res_req, db, admin)
    assert resolved.status == "Resolved"
    assert resolved.resolved_at is not None

def test_complaint_access_control(db):
    citizen1 = User(email=f"c1_{int(datetime.utcnow().timestamp())}@civicpulse.invalid", password_hash=hash_password("password1234"), role="citizen")
    citizen2 = User(email=f"c2_{int(datetime.utcnow().timestamp())}@civicpulse.invalid", password_hash=hash_password("password1234"), role="citizen")
    db.add_all([citizen1, citizen2]); db.commit()

    req = ComplaintCreate(description="Streetlight is not working since Monday night.", locality="Sector 5")
    c1_comp = api.create_complaint(req, db, citizen1)

    # Citizen 1 can access own complaint
    assert api.complaint_for_user(c1_comp.id, citizen1, db).id == c1_comp.id

    # Citizen 2 gets 403 on Citizen 1's complaint
    with pytest.raises(HTTPException) as exc:
        api.complaint_for_user(c1_comp.id, citizen2, db)
    assert exc.value.status_code == 403

def test_geographic_and_analytics_queries(db):
    admin = User(email=f"adm_geo_{int(datetime.utcnow().timestamp())}@civicpulse.invalid", password_hash=hash_password("adminpass1234"), role="admin")
    db.add(admin); db.commit()

    # Geo complaints
    geo = api.geographic_complaints(None, None, None, db, admin)
    assert isinstance(geo, list)

    # Geo heatmap
    heat = api.geographic_heatmap(None, None, None, db, admin)
    assert "points" in heat
    assert "privacy" in heat

    # Analytics
    ana = api.analytics(None, None, None, db, admin)
    assert "total" in ana
    assert "by_category" in ana
    assert "by_status" in ana

    # Assistant
    ast = api.civic_assistant("what is the most common problem?", None, db, admin)
    assert "answer" in ast
    assert ast["method"] == "permission-scoped structured database aggregation"

def test_research_service_endpoints(db):
    admin = User(email=f"adm_res_{int(datetime.utcnow().timestamp())}@civicpulse.invalid", password_hash=hash_password("adminpass1234"), role="admin")
    db.add(admin); db.commit()

    # Word2Vec demo
    w2v = api.embeddings(mode="skipgram", dimensions=4, window=2, epochs=1, _=admin)
    assert w2v["status"] == "trained"
    assert "loss" in w2v

    # Attention demo
    att = api.attention(ComplaintCreate(description="shortage of drinking water in town"), admin)
    assert "attention" in att
    assert att["method"].startswith("deterministic")

    # Civic baseline evaluation
    civ = api.evaluate(admin)
    assert civ["accuracy"] == 0.3333
    assert civ["macro_f1"] == 0.3088

    # Hindi sentiment evaluation
    hnd = api.evaluate_hindi_sentiment_model(admin)
    assert hnd["accuracy"] == 0.7285
    assert hnd["macro_f1"] == 0.6963

    # Quality dashboard
    qd = api.quality_dashboard(admin)
    assert "sentiment" in qd
    assert qd["sentiment"]["Hindi"]["accuracy"] == 0.7285

def test_nlp_direct_endpoints(db):
    # Analyse
    analysis = api.nlp_analyse(ComplaintCreate(description="Pani ki samasya pichle 4 din se hai"), db)
    assert analysis["category"] == "Water Supply"
    assert analysis["sentiment"] in ("Negative", "Neutral", "Positive")

    # Preprocess
    pre_mixed = api.nlp_preprocess(ComplaintCreate(description="English and Devanagari text पानी बिजली सड़क"))
    assert pre_mixed["script"] == "Mixed (Devanagari/Latin)"
    pre_deva = api.nlp_preprocess(ComplaintCreate(description="पानी बिजली सड़क समस्या"))
    assert pre_deva["script"] == "Devanagari"
    assert "पानी" in pre_deva["tokens"]

    # Language identify
    lid = api.language_identify(ComplaintCreate(description="Some English civic complaint"))
    assert "language" in lid
