# CivicPulse

Multilingual Civic Complaint Intelligence & NLP Research Platform — a
local-first university project for English, Hindi and Hinglish.

## Current state

The supplied datasets were inspected rather than assumed; the audit is in
[docs/DATASET_AUDIT.md](docs/DATASET_AUDIT.md). The runnable MVP includes a
React research interface, FastAPI/SQLite citizen-and-admin workflow, protected
status history, safe dataset inventory, local multilingual preprocessing,
trainable small NumPy CBOW/Skip-gram embeddings, attention visualisation,
extractive summarisation and a reproducible civic TF-IDF baseline evaluator.

## Run locally

Create an isolated Python environment, install `requirements.txt`, copy
`.env.example` to `.env` and set a strong `SECRET_KEY`, then run the API:

```powershell
uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the API interface. Run the available
tests with:

```powershell
python -m pytest backend/tests -q
```

In a second terminal, start the interface:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. Register an account; no default administrator is
created. For an intentional local demo administrator, set
`DEMO_ADMIN_EMAIL` and `DEMO_ADMIN_PASSWORD`, then run
`python scripts/create_demo_admin.py`.

`requirements.txt` is the lightweight, working core. The optional
`requirements-ml-optional.txt` is reserved for future CPU neural experiments;
the current runnable demonstration deliberately does not require a large model
download.

## Comprehensive Academic Documentation

The repository includes a complete academic documentation and verification suite:

- **Master Technical Report:** [docs/CIVICPULSE_COMPLETE_PROJECT_OVERVIEW.md](docs/CIVICPULSE_COMPLETE_PROJECT_OVERVIEW.md) (12-part master report covering Parts A–L)
- **Source Code & API Audit:** [docs/PROJECT_AUDIT.md](docs/PROJECT_AUDIT.md)
- **University NLP Syllabus Mapping:** [docs/NLP_SYLLABUS_MAPPING.md](docs/NLP_SYLLABUS_MAPPING.md) (Units I–VI)
- **Dataset Audit & Manifest:** [docs/DATASET_AUDIT.md](docs/DATASET_AUDIT.md)
- **Experiment Reproducibility Report:** [docs/EXPERIMENT_REPRODUCIBILITY.md](docs/EXPERIMENT_REPRODUCIBILITY.md) (Hindi Sentiment 72.85% reproduction)
- **Civic Classification Evaluation:** [docs/CIVIC_CLASSIFICATION_EVALUATION.md](docs/CIVIC_CLASSIFICATION_EVALUATION.md) (Baseline & cross-lingual diagnostic)
- **QA Test Report:** [docs/QA_TEST_REPORT.md](docs/QA_TEST_REPORT.md) (17/17 tests passing)
- **IEEE Research Paper Draft:** [docs/CIVICPULSE_IEEE_PREPARATION.md](docs/CIVICPULSE_IEEE_PREPARATION.md)
- **Presentation Slide Deck (20 Slides):** [docs/CIVICPULSE_PPT_OUTLINE.md](docs/CIVICPULSE_PPT_OUTLINE.md)
- **Viva Voce Examination Prep (65 Questions):** [docs/CIVICPULSE_VIVA_QUESTIONS.md](docs/CIVICPULSE_VIVA_QUESTIONS.md)
- **Audit Changelog:** [docs/CHANGELOG_AUDIT.md](docs/CHANGELOG_AUDIT.md)

## Dataset safeguards

- `datasets/raw/source_originals/` is immutable.
- Hindi sentiment and NER retain their supplied splits.
- NER JSON and CoNLL are alternatives, not additional data.
- Translation data has development and test pairs only; neither is silently
  treated as a training set.
- Civic transcript provenance, licences and synthetic status are unconfirmed.

See [docs/IMPLEMENTATION_CHECKLIST.md](docs/IMPLEMENTATION_CHECKLIST.md) and
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the phased plan. Also consult
[docs/KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) before presenting the
research outputs as results.
