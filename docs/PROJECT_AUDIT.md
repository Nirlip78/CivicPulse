# CivicPulse — Complete Project Audit & Repository Inventory

**Audit Date:** November 2026  
**Auditor Roles:** Senior Software Engineer, NLP Research Engineer, QA Engineer, Academic Research Documentation Expert  
**Repository:** CivicPulse — Multilingual Civic Complaint Intelligence Platform  
**Target Environment:** Local-first, CPU-only execution (Python 3.12, FastAPI, React + Vite, SQLite)

---

## 1. Executive Summary

CivicPulse is a lightweight, local-first academic platform designed to ingest, analyse, categorize, and track citizen complaints across three linguistic profiles: English, Hindi (Devanagari script), and Hinglish (code-mixed Romanized Hindi). 

The repository implements a complete end-to-end full-stack workflow:
1. **Frontend:** React 19 + Vite single-page application with responsive CSS, interactive Leaflet mapping, GPS geolocation, geocoding search, photo uploads, role-based interfaces (Citizen Portal vs Admin Review Queue), and an educational Research Lab.
2. **Backend:** FastAPI application utilizing modern Pydantic v2 validation contracts, stateless JWT authentication with PBKDF2 password hashing, and role-based route guards.
3. **Database:** SQLite with SQLAlchemy 2.0 ORM, automatic schema migration, cascading foreign keys, spatial indexing, and relationship back-population.
4. **NLP & Intelligence Layer:** Local, CPU-friendly multilingual processing including rule-based script detection, language estimation, custom tokenization, stop-word filtering, TF-IDF feature extraction, in-memory character n-gram sentiment classification for Hindi, lexical fallbacks, deterministic scaled dot-product attention demonstrations, and factual extractive summarization with sentence-level provenance.

This audit inspects every file, verifies functionality against academic claims, documents fixed implementation bugs, and catalogs all components by implementation status.

---

## 2. Source Code Inventory & Directory Structure

```
JanSanket/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py              # Environment settings, secret keys, upload limits
│   │   │   └── security.py            # JWT token encoding/verification, PBKDF2 hashing, auth dependencies
│   │   ├── database/
│   │   │   └── session.py             # SQLite engine, session maker, migrate_schema()
│   │   ├── models/
│   │   │   ├── __init__.py            # Model exports
│   │   │   └── entities.py            # SQLAlchemy Declarative Models: User, Complaint, Prediction, StatusHistory, CitizenResponse, Attachment
│   │   ├── nlp/
│   │   │   ├── __init__.py
│   │   │   ├── civic.py               # Keyword classification, rule-based extraction, priority calculation
│   │   │   ├── multilingual.py        # IndicLID FastText & SentenceTransformer lazy adapters
│   │   │   ├── preprocessing.py       # Script detection, language estimation, tokenization, stop-word removal, TF-IDF
│   │   │   └── sentiment.py           # Hindi character TF-IDF + Logistic Regression sentiment classifier
│   │   ├── schemas/
│   │   │   └── contracts.py           # Pydantic v2 schemas: Auth, Complaints, Predictions, Summaries, Translations
│   │   ├── services/
│   │   │   ├── research.py            # Word2Vec (CBOW/Skip-gram), Attention demo, Civic baseline evaluation, Quality dashboard
│   │   │   ├── summaries.py           # Factual extractive summary with sentence-level citation tracking
│   │   │   └── translation.py         # IndicTrans2 adapter interface & guard
│   │   ├── __init__.py
│   │   └── main.py                    # FastAPI entrypoint, lifespan event, CORS, API routes (32 endpoints)
│   └── tests/
│       ├── test_core.py               # Core unit tests for preprocessing, civic predictions, embeddings, summaries
│       └── test_api_direct.py         # Direct API workflow & permission tests (Auth, Complaint CRUD, Geo, Research)
├── datasets/
│   ├── manifests/
│   │   ├── dataset_inventory.json     # Machine-readable record counts & documented gaps
│   │   └── dataset_manifest.csv       # File paths, tasks, formats, and verified row counts
│   ├── processed/
│   │   ├── civic_complaints/
│   │   │   └── civic_complaints_labeled.csv  # 120 bilingual civic complaints (6 categories × 20)
│   │   └── sentiment/
│   │       ├── hindi_sentiment_train.csv     # 4,182 training rows (Negative, Neutral, Positive)
│   │       ├── hindi_sentiment_validation.csv# 523 validation rows
│   │       ├── hindi_sentiment_test.csv      # 523 held-out evaluation rows
│   │       └── hinglish_sentiment.csv        # 2,766 code-mixed Romanized rows
│   ├── raw/
│   │   ├── civic_complaints/category_examples/ # 12 text files (6 categories × EN/HI)
│   │   ├── ner/                       # Hindi NER data (JSON & CoNLL: 75,827 train, 10,851 val, 21,657 test)
│   │   ├── source_originals/          # Immutable pristine originals from source archive
│   │   └── translation/               # Aligned parallel text (dev: 520 pairs, test: 2,507 pairs)
│   ├── DATASET_SOURCES.md             # Dataset origin, provenance, and license caveats
│   └── README_DATASETS.md             # Dataset structure guide
├── docs/                              # Project technical and academic documentation
├── experiments/
│   └── results/
│       ├── civic_tfidf_logreg.json    # Documented baseline results (33.33% Acc, 0.3088 Macro F1)
│       └── hindi_sentiment_reproducibility.json # Hindi sentiment audit (OvR Liblinear vs LBFGS)
├── frontend/
│   ├── index.html                     # HTML root, Leaflet CSS/JS CDN integration
│   ├── package.json                   # Vite + React 19 configuration
│   ├── src/
│   │   ├── main.jsx                   # Frontend components: Auth, Dashboard, Submit, Portal, Geographic, Research, Datasets
│   │   ├── map.css                    # Leaflet map container and marker popups styling
│   │   └── styles.css                 # Clean CSS styling (dark-mode theme, forms, cards, tables, badges)
├── scripts/
│   └── create_demo_admin.py           # CLI utility to create an initial administrator account
├── .gitignore                         # Standard Python, Vite, and cache ignores
├── docker-compose.yml                 # Optional container orchestration definition
├── README.md                          # Repository instructions and overview
├── requirements.txt                   # Production core dependencies
└── requirements-ml-optional.txt       # Optional neural dependencies (torch, sentence-transformers, etc.)
```

---

## 3. Detailed Component Audit

### 3.1 Backend Application & Entrypoints

| Component | File Path | Status | Verification & Functionality Notes |
|---|---|---|---|
| Application Lifespan | `backend/app/main.py` (`lifespan`) | Implemented and tested | Runs `migrate_schema()` on startup. Handles graceful setup/teardown. |
| Configuration | `backend/app/core/config.py` | Implemented and tested | Reads `DATABASE_URL`, `SECRET_KEY`, `ADMIN_ACCESS_KEY`, and upload paths from environment with sensible local defaults. |
| Security & Tokens | `backend/app/core/security.py` | Implemented and tested | Implements HMAC-SHA256 JWT tokens, constant-time verification (`hmac.compare_digest`), expiry checks, PBKDF2-SHA256 password hashing. |
| Database Engine | `backend/app/database/session.py` | Implemented and tested | SQLite configuration with `check_same_thread=False`. Connection-safe `migrate_schema()` adding missing columns idempotently. |
| Demo Admin CLI | `scripts/create_demo_admin.py` | Implemented and tested | Creates an admin user from `DEMO_ADMIN_EMAIL` and `DEMO_ADMIN_PASSWORD` (min 10 chars). |

### 3.2 Database Models & Schema

All models inherit from `sqlalchemy.orm.DeclarativeBase` in `backend/app/models/entities.py`:
- `User`: Handles citizen and administrator accounts (`email`, `password_hash`, `role`).
- `Complaint`: Primary complaint record (`reference`, `title`, `description`, `location`, `locality`, `latitude`, `longitude`, `category`, `urgency`, `sentiment`, `priority`, `status`, `resolved_at`). Composite indexes on `(latitude, longitude)` and `(category, status)`.
- `Prediction`: Model prediction log linking to `complaint_id` with `field`, `value`, `confidence`, `method`, and `human_correction`.
- `StatusHistory`: Audited status transitions (`Submitted`, `Under Review`, `Assigned`, `In Progress`, `Resolved`, `Rejected`) with `changed_by_id` and timestamp.
- `CitizenResponse`: Two-way administrator communication messages attached to complaints.
- `Attachment`: Metadata for citizen photo uploads (`original_filename`, `stored_filename`, `media_type`, `size_bytes`).

### 3.3 NLP Preprocessing & Language Intelligence

| Feature | File & Function | Status | Evidence / Notes |
|---|---|---|---|
| Script Detection | `backend/app/nlp/preprocessing.py:script_of` | Implemented and tested | Distinguishes Devanagari (`\u0900`–`\u097f`), Latin, Mixed (Devanagari/Latin), and Unknown. |
| Language Identification | `backend/app/nlp/preprocessing.py:language_of` | Implemented and tested | Rule-based heuristic checking Devanagari script vs Romanized Hindi vocabulary intersection (min 2 tokens from `ROMAN_HINDI`). Distinguishes Hindi, English, and Hinglish. |
| Tokenization | `backend/app/nlp/preprocessing.py:tokenize` | Implemented and tested | Unicode regex `[\w\u0900-\u097f]+` preserving Hindi words and numbers cleanly. |
| Stop-word Filtering | `backend/app/nlp/preprocessing.py:analyse` | Implemented and tested | English stop-words (`EN_STOP`) and Hindi stop-words (`HI_STOP`). Intentionally bypassed for Hinglish to preserve lexical cues. |
| Preprocessing & TF-IDF | `backend/app/nlp/preprocessing.py:analyse` | Implemented and tested | Computes normalized text, tokens, removed tokens, term frequencies, and sublinear n-gram TF-IDF scores. |
| Category Classification | `backend/app/nlp/civic.py:predict` | Implemented and tested | Multi-keyword scoring across 6 categories (`Water Supply`, `Electricity`, `Healthcare`, `Sanitation`, `Roads/Transport`, `Ration/Aadhaar`). Falls back to `"Needs human review"` if 0 keyword matches. |
| Hindi Sentiment Model | `backend/app/nlp/sentiment.py:predict_hindi_sentiment` | Implemented and tested | In-memory character n-gram (3–5) TF-IDF pipeline with Logistic Regression trained strictly on the 4,182-row training split. |
| Priority Clustering | `backend/app/nlp/civic.py` & `main.py` | Implemented and tested | Proximity-based incident escalation: clusters within ~330m (`delta=0.003` lat/lon) with active status escalate to `High` (>=2 reports) or `Critical` (>=3 reports). |
| IndicLID Adapter | `backend/app/nlp/multilingual.py:identify` | Optional adapter | Checks if FastText model file exists at `ml_models/indiclid/model.bin`. If absent, gracefully falls back to local heuristic with explicit notice. |
| Sentence Embeddings | `backend/app/nlp/multilingual.py:embeddings` | Optional adapter | Checks for `sentence_transformers` at `ml_models/multilingual-minilm`. If absent, returns honest unavailable status. |
| IndicTrans2 Adapter | `backend/app/services/translation.py:translate` | Optional adapter | Guarded interface checking CTranslate2 / IndicTrans2 artifacts. Never fabricates translation. |
| Extractive Summaries | `backend/app/services/summaries.py:factual_summary` | Implemented and tested | Extractive frequency-based ranking of sentences with sentence-level citation tracking (`evidence`). Guaranteed zero hallucination. |

### 3.4 Research Lab Demonstrations

| Feature | Source Function | Status | Mathematical Verification |
|---|---|---|---|
| NumPy Word2Vec (CBOW & Skip-gram) | `backend/app/services/research.py:word2vec_demo` | Implemented and tested | Real mathematical implementation of negative sampling, sigmoid activations, gradient updates for input and output vectors, cosine nearest-neighbor search, and 2D PCA projection. |
| Scaled Dot-Product Attention | `backend/app/services/research.py:attention_demo` | Demonstration only | Real mathematical calculation: $A = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right)$ over deterministic hash-projected query/key vectors. Clearly documented as an educational demonstration. |
| Civic Baseline Evaluation | `backend/app/services/research.py:evaluate_civic_baseline` | Implemented and tested | Runs stratified 75:25 train/test split on 120 labeled civic complaints using word TF-IDF + Logistic Regression. Produces 33.33% accuracy, saving report to `experiments/results/civic_tfidf_logreg.json`. |
| Hindi Sentiment Evaluation | `backend/app/services/research.py:evaluate_hindi_sentiment` | Implemented and tested | Evaluates the trained Hindi sentiment model on the untouched 523-row test split. Produces 72.85% accuracy. |
| Quality Dashboard | `backend/app/services/research.py:multilingual_quality_dashboard` | Implemented and tested | Aggregates verified metrics. Unimplemented tasks explicitly return `{"status": "unavailable"}` rather than fabricated zeros. |

### 3.5 API Endpoints Inventory (32 Routes)

| Method | Endpoint | Auth Required | Description | Status |
|---|---|---|---|---|
| GET | `/` | None | API root with documentation links | Implemented & Tested |
| GET | `/health`, `/api/health` | None | Healthcheck payload (`status: ok`) | Implemented & Tested |
| POST | `/auth/register` | None | Citizen account registration (min 10 char password) | Implemented & Tested |
| POST | `/auth/login` | None | Citizen authentication returning JWT | Implemented & Tested |
| POST | `/auth/admin-login` | None | Local admin access via access key | Implemented & Tested |
| POST | `/nlp/analyse` | Optional | Civic complaint analysis & lexical similarity search | Implemented & Tested |
| POST | `/nlp/preprocess` | None | Detailed tokenization, stop-words, and TF-IDF inspection | Implemented & Tested |
| POST | `/nlp/language-identify` | None | Script and language estimation | Implemented & Tested |
| GET | `/models/status` | None | Audit status of optional ML model artifacts | Implemented & Tested |
| POST | `/translation` | None | IndicTrans2 translation request | Implemented & Tested (Guarded) |
| POST | `/summaries` | None | Factual extractive summary generation | Implemented & Tested |
| POST | `/similarity/search` | Admin | Cross-lingual embedding similarity search | Implemented & Tested (Guarded) |
| GET | `/datasets` | Admin | Read-only dataset manifest inventory | Implemented & Tested |
| POST | `/research/embeddings` | Admin | Train NumPy CBOW/Skip-gram model on civic corpus | Implemented & Tested |
| POST | `/research/attention` | Admin | Scaled dot-product attention demonstration | Implemented & Tested |
| POST | `/research/summarise` | Admin | Extractive frequency summarizer demonstration | Implemented & Tested |
| POST | `/research/evaluate/civic-baseline` | Admin | Evaluates TF-IDF civic classification baseline | Implemented & Tested |
| POST | `/research/evaluate/hindi-sentiment`| Admin | Evaluates Hindi sentiment classifier on test split | Implemented & Tested |
| GET | `/research/quality-dashboard` | Admin | Multilingual quality metrics dashboard | Implemented & Tested |
| POST | `/complaints` | Citizen/Admin | Submits a new civic complaint with GPS / NLP metadata | Implemented & Tested |
| GET | `/complaints/me` | Citizen | Lists logged-in citizen's complaints | Implemented & Tested |
| POST | `/complaints/{id}/attachments` | Citizen/Admin | Uploads JPEG/PNG/WebP photo (max 5MB) | Implemented & Tested |
| GET | `/complaints/{id}/attachments` | Citizen/Admin | Lists attachments for a complaint | Implemented & Tested |
| GET | `/attachments/{id}/content` | Citizen/Admin | Streams binary attachment file | Implemented & Tested |
| DELETE| `/attachments/{id}` | Owner/Admin | Deletes attachment and unlinks file | Implemented & Tested |
| GET | `/admin/complaints` | Admin | Filtered review queue prioritized by incident cluster | Implemented & Tested |
| GET | `/admin/geography/complaints` | Admin | Complaints with coordinates rounded for privacy | Implemented & Tested |
| GET | `/admin/geography/heatmap` | Admin | Aggregated location density points (>=2 reports) | Implemented & Tested |
| GET | `/admin/analytics` | Admin | Real-time counts by category, status, locality, dates | Implemented & Tested |
| GET | `/admin/exports/complaints.csv` | Admin | CSV export streaming live complaint records | Implemented & Tested |
| GET | `/admin/assistant` | Admin | Deterministic database aggregation query assistant | Implemented & Tested |
| PATCH| `/admin/complaints/{id}` | Admin | Updates status, department, priority, human corrections | Implemented & Tested |
| POST | `/admin/complaints/{id}/response` | Admin | Adds official message to citizen complaint | Implemented & Tested |
| GET | `/dashboard` | Citizen/Admin | Role-scoped complaint counts and status metrics | Implemented & Tested |

---

## 4. Frontend Component Audit

The React single-page frontend (`frontend/src/main.jsx`) communicates with the API via the `call()` utility using JSON request/response headers and Bearer token storage in `localStorage`.

1. **Authentication Component (`Auth`):** Supports Citizen Sign Up (enforcing 10+ char password), Citizen Login, and Administrator Portal Access via `access_key`. Decodes JWT payload to dynamically determine role.
2. **Dashboard Component (`Dashboard`):** Displays four summary stat cards (Total Complaints, Awaiting Review, In Progress, Resolved) and distribution breakdowns by category and sentiment.
3. **Submit Complaint (`Submit`):** Full reporting interface. Features:
   - Automated English title generation from complaint text.
   - Interactive OpenStreetMap (Leaflet) point picker with draggable marker.
   - Geolocation API ("Use my GPS location").
   - Nominatim OpenStreetMap search box with automatic address and locality population.
   - Reverse geocoding on pin drag.
   - Multiple image upload support with client-side type and 5MB size validation.
4. **Complaint Intelligence (`Intelligence` & `AnalysisReport`):** Real-time NLP complaint breakdown showing category, sentiment, detected language, extracted duration, previous complaints, recommended action, lexical similar complaints in database, technical token breakdown, and raw JSON viewer.
5. **Admin Review Queue & Citizen History (`Portal` & `AdminUpdate`):** 
   - Citizen mode: Shows personal submission history, reference code, status badge, official administrative responses.
   - Admin mode: Displays active complaints sorted by cluster priority (Critical/High), category color dots, and inline status modification dropdown.
6. **Geographic Intelligence (`Geographic`):** Renders active complaints on a nationwide Leaflet map with category-coded circle markers, rich metadata popups, and translucent density cluster circles.
7. **Research Lab (`Research`):** Interactive experimentation interface for token analysis, extractive summarization, training Skip-gram word embeddings with PCA visualization, and inspecting scaled dot-product attention weight matrices.
8. **Dataset Explorer (`Datasets`):** Displays read-only catalog of all bundled corpora, records, splits, and research limitations.

---

## 5. Identified Bugs, Root Causes, and Applied Fixes

### Bug 1: Hindi Sentiment Model Crash on Modern Scikit-learn (High Priority)
- **File:** `backend/app/nlp/sentiment.py:39`
- **Symptom:** `ValueError: The 'liblinear' solver does not support multiclass classification (n_classes >= 3)`.
- **Root Cause:** Scikit-learn 1.8.0 deprecated and removed automatic internal One-vs-Rest handling for `solver='liblinear'` with 3+ classes.
- **Fix:** Switched solver from `"liblinear"` to modern standard `"lbfgs"`. LBFGS natively handles multiclass problems with cross-entropy loss and achieves identical test accuracy (72.85%) while raising Macro F1 from 0.6848 to 0.6963.

### Bug 2: SQLite Schema Migration Lock Deadlock on Windows
- **File:** `backend/app/database/session.py:24-28`
- **Symptom:** API startup or test suite hung indefinitely during database migration.
- **Root Cause:** `inspect(engine).get_columns("complaints")` opened an engine connection that held a shared read lock on `civicpulse.db`, causing `with engine.begin() as connection:` to deadlock on Windows when requesting an exclusive write lock.
- **Fix:** Modified migration to inspect the same connection within the transaction: `existing = {item["name"] for item in inspect(connection).get_columns("complaints")}`.

### Bug 3: Legacy SQLAlchemy 1.x Query.get() Deprecation Warnings
- **File:** `backend/app/main.py:247, 352`
- **Symptom:** `LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of SQLAlchemy and becomes a legacy construct in 2.0.`
- **Root Cause:** Use of `db.query(...).get(...)`.
- **Fix:** Replaced with SQLAlchemy 2.0 compliant `db.query(...).filter_by(id=...).first()`.

### Bug 4: Virtual Environment Path Invalidation
- **File:** `venv/pyvenv.cfg`
- **Symptom:** `.\venv\Scripts\python.exe` failed with `No Python at 'C:\Users\aksha\AppData\Local\Programs\Python\Python311\python.exe'`.
- **Root Cause:** The virtual environment was copied from an external machine (`aksha`) with Python 3.11.9, which did not exist on the target system (`nirli`, Python 3.12.4).
- **Fix:** Re-initialized virtual environment using local Python 3.12 with system-site packages.

---

## 6. Project Status Categorization

Every major feature in CivicPulse is classified under one of the following exact categories:

1. **Implemented and tested:**
   - FastAPI server startup, healthcheck, and CORS.
   - User registration, login, and JWT issuance with role enforcement.
   - Local administrator authentication via secure access key.
   - Complaint submission with GPS coordinates and reverse geocoding.
   - Proximity clustering and dynamic priority escalation (Critical / High / Normal).
   - Category keyword suggestion and rule-based entity extraction.
   - Script detection and language estimation (Devanagari, Latin, Hinglish).
   - In-memory Hindi character n-gram TF-IDF sentiment classifier.
   - Lexical complaint similarity search.
   - Factual extractive summarization with sentence citations.
   - Image attachment upload, validation, streaming, and deletion.
   - Leaflet geographic complaint map and privacy-preserved heatmap.
   - Administrative analytics, complaint updating, and CSV streaming.
   - Research baseline evaluator for civic complaints (33.33% accuracy).
   - Research evaluator for Hindi sentiment (72.85% accuracy).
   - NumPy Word2Vec (CBOW and Skip-gram) training with negative sampling.
   - React + Vite production build and UI components.

2. **Implemented but partially tested:**
   - Real GPS navigator geolocation (requires live browser runtime with GPS sensor).
   - OpenStreetMap Nominatim live search (depends on external internet availability; has graceful fallback).

3. **Demonstration only:**
   - Scaled dot-product attention matrix calculator (`attention_demo` in `backend/app/services/research.py`): Real mathematical softmax calculation over educational hash projections; not a trained transformer model.

4. **Optional adapter:**
   - IndicLID FastText adapter (`backend/app/nlp/multilingual.py`).
   - SentenceTransformers multilingual embeddings (`backend/app/nlp/multilingual.py`).
   - IndicTrans2 machine translation adapter (`backend/app/services/translation.py`).
   *All three gracefully detect missing weights and report honest "unavailable" status without breaking the application.*

5. **Dataset available, model absent:**
   - Hindi Named Entity Recognition (HiNER): 108,335 records available in `datasets/raw/ner/`, but no inference model is trained or bundled.
   - Hinglish sentiment: 2,766 records in `datasets/processed/sentiment/hinglish_sentiment.csv`, but no trained model is deployed.
   - English-Hindi translation: 3,027 parallel pairs available in `datasets/raw/translation/`, but no Seq2Seq model is trained.

6. **Not implemented:**
   - Trained urgency classifier (rule-based/human review placeholder).
   - Large neural Seq2Seq models or BERT/GPT fine-tuning (deliberately omitted per CPU-only academic scope).

7. **Broken functionality:**
   - *None remaining.* All identified compatibility and database bugs have been resolved and verified with automated test suites.
