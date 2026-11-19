# CivicPulse — Project Overview

## 1. What is CivicPulse?

CivicPulse is a **local-first multilingual civic complaint intelligence and NLP research platform**. It is designed as a university project and runnable MVP for handling civic-service complaints written in:

- English
- Hindi (Devanagari script)
- Hinglish / Romanised Hindi
- mixed Hindi-English text

The project gives citizens a simple way to submit and track civic complaints, while giving administrators a controlled review workflow. It also provides a research workspace for demonstrating core Natural Language Processing (NLP) techniques on local datasets without requiring large cloud models or internet downloads.

The application is intentionally cautious: its NLP results are **advisory suggestions**, not official decisions. A human administrator must verify a complaint's category, urgency, routing and resolution.

## 2. Why this project is needed

Civic complaints are often expressed in informal, multilingual language. A resident may describe the same issue in English, Hindi, Hinglish or a mix of all three. This creates practical difficulties:

- Complaints can be slow to read, classify and route manually.
- Similar reports can be overlooked when they are written differently.
- Citizens may have little visibility into the progress of their complaints.
- Public-service teams need a structured queue without treating automated guesses as final decisions.
- NLP learning projects need a realistic, privacy-aware use case that works on ordinary CPU-only computers.

CivicPulse addresses these issues by structuring complaint intake, offering transparent language analysis, preserving a review trail and separating human decisions from machine-generated suggestions.

## 3. Problem being solved

The project tackles two connected problems.

### Civic-service workflow problem

Residents need a clear channel to report civic concerns such as water supply, electricity, sanitation, healthcare, roads/transport and ration/Aadhaar services. Administrators need a reliable way to review reports, update their status and keep a record of what happened.

### Multilingual NLP learning and research problem

Students and researchers need a safe environment to explore multilingual text processing, term-frequency methods, embeddings, attention and baseline evaluation. The platform provides small, transparent local implementations and clearly states where data or model evidence is insufficient for stronger claims.

## 4. Project goals

- Support complaint text in English, Hindi and Hinglish.
- Help users understand a complaint before submitting it.
- Suggest a service category and sentiment as a starting point for human review.
- Store the original complaint separately from predictions and later human corrections.
- Let citizens view their own submitted complaints.
- Let authorised administrators review all complaints and update their status.
- Keep a status-history trail for accountability.
- Provide local, CPU-friendly NLP demonstrations for academic learning.
- Preserve datasets, split boundaries and provenance limitations honestly.
- Work without mandatory external model downloads or cloud services.

## 5. Who benefits and how

| User | Benefit | How CivicPulse helps |
| --- | --- | --- |
| Citizens | Easier reporting and visibility | They can create an account, submit a complaint, see their own records and follow status updates. |
| Civic administrators | A structured review queue | They can browse complaints, search/filter them, update statuses and record administrator responses. |
| Service departments | Faster initial triage | The system proposes a likely service category and recommended next step, subject to review. |
| Students and researchers | A practical NLP learning environment | They can inspect preprocessing, TF-IDF, Word2Vec-style embeddings, attention, extractive summarisation and a reproducible baseline. |
| Project evaluators | Transparent evidence and limitations | The project documents datasets, evaluation outcomes, workflow boundaries and known limitations. |

## 6. How the project works

### A. Citizen complaint flow

1. A citizen registers or logs in.
2. The citizen writes a complaint description and may add a location.
3. Before or during submission, CivicPulse can analyse the text.
4. The NLP service identifies the likely language/script, tokenises the text and proposes a category, sentiment, summary and next step.
5. The citizen submits the report.
6. The system saves the original description, the initial NLP suggestions and an initial `Submitted` status.
7. The citizen can view only their own submitted complaints and their current status.

### B. Administrator review flow

1. An administrator signs in using the configured administrator access key.
2. The administrator opens the review queue.
3. The administrator reads the original complaint and the advisory NLP output.
4. The administrator verifies or corrects fields such as category and urgency where needed.
5. The administrator changes the complaint status, for example from `Submitted` to `Under Review`, `Assigned`, `In Progress`, `Resolved` or `Rejected`.
6. Each status change is stored in the complaint's status history.
7. An administrator can send a response linked to the complaint.

### C. NLP analysis flow

1. The submitted text is tokenised locally with Unicode-aware handling for Devanagari and Latin text.
2. The application estimates whether the text is Hindi, English, Hinglish or mixed Hindi-English.
3. Relevant stop words are removed for the detected language where appropriate.
4. Term frequencies and local TF-IDF features are calculated.
5. A transparent keyword baseline scores the complaint against six civic categories.
6. Lexical rules estimate sentiment, reported duration, references to previous action and unresolved concerns.
7. An extractive summariser selects an existing sentence from the complaint; it does not invent facts or translate the text.
8. The application returns warnings, method details and a recommendation for human review.

### D. Similar-complaint flow

1. CivicPulse tokenises the new complaint and recent stored complaints.
2. It compares their token sets using transparent lexical overlap.
3. Reports with enough overlap are shown as potentially similar.
4. They are never automatically marked as duplicates; an administrator decides what to do with them.

### E. Research-lab flow

1. A user opens the Research Lab in the frontend.
2. The user can inspect preprocessing or generate an extractive summary for text.
3. The user can train a small local CBOW or Skip-gram negative-sampling embedding demonstration on the supplied civic corpus.
4. The user can inspect a deterministic scaled dot-product attention demonstration.
5. An administrator can generate a reproducible TF-IDF + Logistic Regression civic-category baseline evaluation.
6. The result is written to `experiments/results/civic_tfidf_logreg.json` and must be interpreted as a small academic baseline, not production performance.

## 7. Main features

### Complaint intelligence

- Language and script estimation for English, Hindi, Hinglish and mixed text.
- Unicode-aware tokenisation and language-aware stop-word handling.
- Term-frequency and TF-IDF inspection.
- Transparent keyword-based category suggestions.
- Simple local sentiment estimate.
- Detection of some durations, prior complaint references and unresolved-action statements.
- Extractive summary that preserves original wording.
- Suggested next step for the likely civic service.
- Transparent lexical search for potentially similar stored complaints.
- Clear warnings that the output needs human verification.

### Citizen-facing features

- Account registration and login.
- Complaint submission with optional location.
- Personal complaint history.
- Personal dashboard with counts by status, category, language and sentiment.

### Administrator-facing features

- Separate administrator login route.
- Access to all complaints.
- Optional text/status filtering in the API.
- Status updates through a controlled set of workflow states.
- Administrator corrections retained apart from the original prediction.
- Status-history records.
- Administrator-to-citizen response records.
- Protected endpoint for generating the research baseline evaluation.

### Research and dataset features

- Read-only dataset inventory with availability and limitation notes.
- Local NumPy CBOW / Skip-gram demonstration with negative sampling.
- Deterministic scaled dot-product attention demonstration.
- Local extractive frequency-based summarisation.
- Reproducible TF-IDF + Logistic Regression evaluation for the small civic-category dataset.
- Dataset audit, data dictionary, evaluation guide and model-training documentation.

## 8. Supported civic categories

The advisory classifier currently recognises the following categories through keyword rules:

- Water Supply
- Electricity
- Healthcare
- Sanitation
- Roads/Transport
- Ration/Aadhaar

If no category keywords are found, the system returns **Needs human review** instead of forcing a category.

## 9. Technical design

```text
React + Vite browser interface
            |
            | HTTP / JSON
            v
FastAPI backend
  |- authentication and role checks
  |- complaint workflow and status history
  |- NLP analysis and research endpoints
  |- dataset inventory and evaluation endpoint
            |
            v
SQLite by default (PostgreSQL can be configured)

Local datasets + generated experiment results
```

### Frontend

The frontend is a React/Vite single-page interface. It includes views for authentication, dashboard, complaint submission, complaint intelligence, personal/admin records, Research Lab and Dataset Explorer.

### Backend

The FastAPI backend owns validation, authentication, authorisation, complaint persistence and NLP processing. The browser does not decide a user's role or an official complaint status.

### Database

SQLite is the default local database. The core records are:

| Record | Purpose |
| --- | --- |
| `User` | Stores the email, password hash, role and creation date. |
| `Complaint` | Stores the original report, optional location, reviewed fields and current status. |
| `Prediction` | Stores an NLP suggestion, method, confidence and later human correction separately. |
| `StatusHistory` | Stores the complaint-status trail, note, actor and time. |
| `CitizenResponse` | Stores an administrator message associated with a complaint. |

### Security and permissions

- Passwords are stored as hashes, not as plain text.
- Signed bearer tokens authenticate requests.
- A citizen can access only their own complaint history and dashboard scope.
- Administrator-only routes require an administrator token.
- The API, not the frontend, enforces roles and protected workflow actions.
- Deployment must use a strong `SECRET_KEY` and a secure `ADMIN_ACCESS_KEY`; the development defaults are not suitable for public deployment.

## 10. Datasets and their responsible use

The project preserves supplied source data and documents what each dataset can and cannot support.

| Dataset | Current use | Important limitation |
| --- | --- | --- |
| Civic complaint categories | Small bilingual category baseline and embedding demo | Only 120 records; provenance is unconfirmed. |
| Hindi sentiment | Future independent sentiment experiments | General-domain text, not civic complaint ground truth. |
| Hinglish sentiment | Future supplementary sentiment experiments | Noisy/mixed general-domain text, not civic ground truth. |
| Hindi NER | Future NER experiments/inference | JSON and CoNLL files are alternate versions, not separate data. |
| English-Hindi parallel text | Alignment inspection and held-out evaluation | Only development/test pairs are supplied; there is no training split. |

Important safeguards:

- `datasets/raw/source_originals/` is immutable.
- Raw source files are not silently edited or overwritten.
- Original train/validation/test split boundaries are retained where supplied.
- Hindi NER JSON and CoNLL data must not be combined as though they are extra examples.
- English-Hindi test pairs must not be used for training.
- Provenance, publisher and licence details remain unconfirmed until independently verified.

## 11. Current model and evaluation status

### Implemented, runnable methods

- Rule-based civic category suggestion.
- Rule-based sentiment estimate.
- Local preprocessing, bag-of-words-style term frequencies and TF-IDF.
- Small NumPy CBOW / Skip-gram embedding demonstration.
- Deterministic attention demonstration.
- Extractive frequency-based summarisation.
- TF-IDF + Logistic Regression civic-category baseline evaluator.

### Baseline result currently stored

The saved evaluation used a documented stratified 75/25 split of the 120-record civic dataset with random seed 42. Its recorded metrics are:

- Accuracy: **0.3333**
- Macro F1: **0.3088**
- Weighted F1: **0.3088**

These figures show why the result must be treated only as a small-data academic baseline. They are not evidence that the system is ready to make operational routing decisions automatically.

### Not implemented or not claimed as complete

- A trained RNN, LSTM, GRU or BiLSTM experiment.
- Hindi NER fine-tuning with reported evaluation metrics.
- A trained English-Hindi translation model.
- Pretrained transformer or LLM adapters.
- A validated civic urgency model.
- A validated English/Hinglish civic-sentiment model.
- Production deployment features such as uploads, maps and user administration.

## 12. Key benefits of this approach

- **Inclusive input:** people can express a civic concern in the language style most natural to them.
- **Faster first review:** administrators receive structured, readable hints without surrendering decision-making control.
- **Transparency:** the system shows its method, confidence limitations and warnings instead of presenting opaque output as fact.
- **Accountability:** original reports, predictions, corrections and status changes are separated and recorded.
- **Privacy-conscious local operation:** the core MVP can run locally without sending complaint text to a third-party model service.
- **Low hardware requirement:** demonstrations are designed to run on a normal CPU-only computer.
- **Educational value:** the project links real civic workflow concepts to practical NLP exercises.
- **Responsible research practice:** dataset limits, split rules and provenance gaps are documented rather than hidden.

## 13. Why an organisation or university would use it

A municipality, campus civic cell, NGO, academic department or student team could use CivicPulse as:

- a prototype for multilingual complaint intake;
- a teaching tool for NLP and responsible AI concepts;
- a demonstration of human-in-the-loop decision support;
- a research baseline for carefully expanded civic datasets;
- a starting point for a future, properly secured production system.

It is especially useful when the goal is to learn from real workflow patterns while retaining human responsibility for service decisions.

## 14. Important limitations and responsible-use rules

- The category and sentiment results are simple local estimates, not verified facts.
- Urgency is deliberately marked as requiring human review; it is not a validated prediction.
- The category suggestion uses transparent keywords, not a trained production classifier.
- Similarity matching is lexical overlap, not semantic duplicate detection.
- The summariser extracts existing text and cannot verify facts or fill missing details.
- The civic dataset is very small and has unconfirmed provenance.
- Dataset licences and original source information require verification before redistribution or public release.
- The translation data has no training split, so CivicPulse does not claim to provide a trained translator.
- The current application is an MVP and should not be used as a sole basis for official civic decisions.

## 15. How to run the project locally

1. Create and activate a Python virtual environment.
2. Install the backend dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and replace the example `SECRET_KEY` and `ADMIN_ACCESS_KEY` with secure local values.
4. Start the backend from the project root:

   ```powershell
   uvicorn backend.app.main:app --reload
   ```

5. Open the API documentation at `http://127.0.0.1:8000/docs`.
6. In another terminal, start the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

7. Open `http://127.0.0.1:5173` in a browser.
8. Register a citizen account, analyse a sample complaint and submit it.
9. For a local demo administrator, configure the required demo variables and run `python scripts/create_demo_admin.py`, or use the administrator access-key route if configured.

To run backend tests:

```powershell
python -m pytest backend/tests -q
```

## 16. Useful project documents

- `README.md` — quick start and current project summary.
- `docs/ARCHITECTURE.md` — component design and responsibilities.
- `docs/API_DOCUMENTATION.md` — API endpoint summary.
- `docs/DATASET_AUDIT.md` — verified dataset counts, splits and limitations.
- `docs/DATA_DICTIONARY.md` — persisted data entities.
- `docs/EVALUATION_GUIDE.md` — baseline evaluation procedure.
- `docs/NLP_MODULES.md` — NLP components and their scope.
- `docs/MODEL_TRAINING_GUIDE.md` — responsible training guidance.
- `docs/KNOWN_LIMITATIONS.md` — current product and research limitations.
- `docs/DEMO_GUIDE.md` — short demonstration sequence.

## 17. Summary

CivicPulse is not an automated civic authority. It is a local, multilingual and human-supervised platform that helps organise civic complaints, makes NLP processing understandable and supports responsible academic experimentation. Its strongest value is the combination of a practical citizen-to-administrator workflow, transparent local analysis and honest boundaries around what the current data and models can support.
