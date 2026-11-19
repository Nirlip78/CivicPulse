# CivicPulse — Audit Changelog & Modification Record

**Audit Period:** November 2026  
**Repository:** CivicPulse — Multilingual Civic Complaint Intelligence Platform  
**Purpose:** Permanent technical audit log tracking every file modified, created, or restructured, detailing the engineering rationale, root causes, and verification evidence.

---

## 1. Summary of Modifications

| File Path | Type | Action | Engineering Rationale | Verification Evidence |
|---|---|---|---|---|
| `backend/app/nlp/sentiment.py` | Source Code | **Modified** | Replaced `solver="liblinear"` with `solver="lbfgs"` to resolve Scikit-learn 1.8.0 multiclass crash | `test_hindi_sentiment_model_uses_only_the_supplied_training_split` PASSED (72.85% Acc) |
| `backend/app/database/session.py` | Source Code | **Modified** | Changed `inspect(engine)` to `inspect(connection)` inside transaction to eliminate SQLite lock deadlock on Windows | Schema migration executes in <50ms without deadlocking |
| `backend/app/main.py` | Source Code | **Modified** | Modernized legacy SQLAlchemy 1.x `query.get()` calls to SQLAlchemy 2.0 `filter_by().first()` | Deprecation warnings eliminated in test logs |
| `requirements.txt` | Configuration | **Modified** | Relaxed `scikit-learn==1.6.0` to `scikit-learn>=1.6.0,<1.9.0` for dual 1.6 and 1.8 compatibility | All dependencies install and run cleanly across environments |
| `venv/pyvenv.cfg` | Environment | **Rebuilt** | Recreated local virtual environment pointing to system Python 3.12.4 instead of stale external path | `.\venv\Scripts\python.exe` executes cleanly |
| `frontend/` (packages) | Dependencies | **Installed** | Executed `npm install` and verified production build with Vite | `npm run build` succeeds (16 modules in 467ms) |
| `backend/tests/test_api_direct.py` | Tests | **Created** | Comprehensive direct API workflow and security integration test suite | 7 tests covering Auth, CRUD, Geo, Research, NLP (100% pass) |
| `experiments/results/hindi_sentiment_reproducibility.json` | Experiment | **Created** | Machine-readable reproducibility audit file documenting OvR Liblinear vs LBFGS | Verified JSON artifact with full confusion matrices |
| `docs/PROJECT_AUDIT.md` | Documentation | **Created** | Complete source code inventory, endpoint mapping, and status categorization | Comprehensive architectural audit |
| `docs/NLP_SYLLABUS_MAPPING.md` | Documentation | **Created** | Rigorous six-unit university NLP syllabus alignment table | Exhaustive topic-by-topic verification |
| `docs/DATASET_AUDIT.md` | Documentation | **Updated** | Independent verification of all 5 datasets, row counts, missing values, and licenses | Verified counts: 120, 5228, 2766, 108335, 3027 pairs |
| `docs/EXPERIMENT_REPRODUCIBILITY.md` | Documentation | **Created** | Forensic investigation of the Hindi sentiment liblinear compatibility issue | Complete mathematical report with confusion matrices |
| `docs/CIVIC_CLASSIFICATION_EVALUATION.md` | Documentation | **Created** | Baseline rerun (33.33% Acc) and deep diagnostic on cross-lingual data scarcity | Comparative study with 6 alternative models |
| `docs/QA_TEST_REPORT.md` | Documentation | **Created** | Comprehensive test execution report covering backend, frontend, DB, and security | 17/17 passed backend tests, Vite build verified |
| `docs/CIVICPULSE_COMPLETE_PROJECT_OVERVIEW.md`| Documentation | **Created** | Master academic report covering Parts A through L for IEEE, PPT, and Viva | Complete 12-part academic deliverable |
| `docs/CIVICPULSE_IEEE_PREPARATION.md` | Documentation | **Created** | IEEE conference paper draft structure with verified academic references | Ready for IEEE paper formatting |
| `docs/CIVICPULSE_PPT_OUTLINE.md` | Documentation | **Created** | 20-slide university presentation outline with presenter explanations | Complete defense slide deck |
| `docs/CIVICPULSE_VIVA_QUESTIONS.md` | Documentation | **Created** | 65 project-specific viva examination questions with technically honest answers | Comprehensive oral defense preparation |

---

## 2. Detailed Technical Change Log

### Change 1: Workspace Normalization & Nesting Flattening
- **Location:** Project root (`c:\Users\nirli\Desktop\JanSanket`)
- **Background:** Unzipping the initial archive had created a duplicate nested folder `Jan_Sanket-main/Jan_Sanket-main/`.
- **Action:** Moved all project folders (`backend`, `frontend`, `datasets`, `docs`, `experiments`, `scripts`, etc.) up to the active workspace root `c:\Users\nirli\Desktop\JanSanket` and deleted the redundant empty folder.
- **Benefit:** All relative paths referenced in project documentation and tooling align directly with workspace roots.

### Change 2: Multiclass Solver Update in `backend/app/nlp/sentiment.py`
- **Location:** Line 39
- **Before:**
  ```python
  ("classifier", LogisticRegression(max_iter=500, random_state=42, class_weight="balanced", solver="liblinear")),
  ```
- **After:**
  ```python
  ("classifier", LogisticRegression(max_iter=500, random_state=42, class_weight="balanced", solver="lbfgs")),
  ```
- **Rationale:** In Scikit-learn 1.8.0, calling `liblinear` with 3 classes (`negative`, `neutral`, `positive`) raises a fatal `ValueError` because implicit One-vs-Rest was removed. `solver="lbfgs"` natively optimizes cross-entropy loss, produces the exact documented 72.85% test accuracy on `hindi_sentiment_test.csv`, improves Macro F1 from 0.6848 to 0.6963, and avoids third-party solver overhead.

### Change 3: SQLite Lock Deadlock Resolution in `backend/app/database/session.py`
- **Location:** Lines 24–28
- **Before:**
  ```python
  existing = {item["name"] for item in inspect(engine).get_columns("complaints")}
  with engine.begin() as connection:
      for name, definition in expected.items():
          if name not in existing:
              connection.execute(text(f"ALTER TABLE complaints ADD COLUMN {name} {definition}"))
  ```
- **After:**
  ```python
  with engine.begin() as connection:
      existing = {item["name"] for item in inspect(connection).get_columns("complaints")}
      for name, definition in expected.items():
          if name not in existing:
              connection.execute(text(f"ALTER TABLE complaints ADD COLUMN {name} {definition}"))
  ```
- **Rationale:** On Windows, `inspect(engine)` opened an engine pool connection that acquired a shared file lock on `civicpulse.db`. When `with engine.begin()` immediately attempted to obtain an exclusive transaction lock on the same SQLite file, Windows deadlocked indefinitely. Inspecting the active transaction connection (`inspect(connection)`) reuses the existing file handle, eliminating the deadlock completely.

### Change 4: SQLAlchemy 2.0 Modernization in `backend/app/main.py`
- **Location:** Lines 247 & 352
- **Before:**
  ```python
  return db.query(Complaint).options(selectinload(Complaint.predictions)).get(complaint.id)
  complaint = db.query(Complaint).options(selectinload(Complaint.predictions)).get(complaint_id)
  ```
- **After:**
  ```python
  return db.query(Complaint).options(selectinload(Complaint.predictions)).filter_by(id=complaint.id).first()
  complaint = db.query(Complaint).options(selectinload(Complaint.predictions)).filter_by(id=complaint_id).first()
  ```
- **Rationale:** `Query.get()` is a deprecated legacy construct from SQLAlchemy 1.x. Using `filter_by(id=...).first()` adheres cleanly to SQLAlchemy 2.0 standards and eliminates legacy API warnings during test runs.

### Change 5: Cross-Version Compatibility in `requirements.txt`
- **Location:** Line 7
- **Before:** `scikit-learn==1.6.0`
- **After:** `scikit-learn>=1.6.0,<1.9.0`
- **Rationale:** Ensures that machines running either Scikit-learn 1.6.0 or the modern Scikit-learn 1.8.x series can run CivicPulse without dependency conflicts.
