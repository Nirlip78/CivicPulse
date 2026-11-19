# CivicPulse — Presentation Slide Deck Outline (20 Slides)

**Target Audience:** University Project Evaluation Committee / Technical Defense / Academic Viva Examiners  
**Project:** CivicPulse — Multilingual Civic Complaint Intelligence Platform  
**Format:** 20 Structured Slides with Visual Recommendations and Presenter Script

---

### Slide 1: Title & Project Overview
- **Slide Title:** CivicPulse: Multilingual Civic Complaint Intelligence Platform
- **Main Points:**
  - Local-first, lightweight architecture for municipal grievance redressal.
  - Multilingual processing: English, Devanagari Hindi, and Romanized Hinglish.
  - Factual extractive summarization and geographic proximity clustering.
  - CPU-friendly, zero external paid APIs or mandatory cloud dependencies.
- **Recommended Visual:** Split screen: Platform logo + screenshot of the Citizen Intelligence Workspace.
- **Presenter Explanation:** *"Good morning, respected members of the evaluation committee. Today, I am presenting CivicPulse, an intelligent civic complaint platform designed specifically for multilingual developing urban centers. Our primary focus is solving real-world citizen grievance friction without relying on expensive, black-box cloud APIs or hallucination-prone generative models."*

---

### Slide 2: The Problem Statement
- **Slide Title:** The Challenges of Modern Civic Grievance Management
- **Main Points:**
  - Linguistic Diversity: Citizens file complaints in English, Hindi, and code-mixed Hinglish.
  - Operational Backlogs: Manual triage across hundreds of daily reports leads to severe delays.
  - Fragmented Geography: Multiple complaints about the same broken pipe are treated as separate tickets.
  - Generative AI Risks: Black-box LLMs risk hallucinating facts, distorting dates, or inventing details.
- **Recommended Visual:** Conceptual problem diagram: Citizens submitting multi-script messages $\rightarrow$ Overwhelmed municipal dashboard.
- **Presenter Explanation:** *"In municipalities across India, citizens communicate in multiple languages and scripts. A resident might write in formal English, Devanagari Hindi, or colloquial Hinglish like 'pichle 5 din se pani nahi aa raha'. Traditional keyword forms fail, while LLMs risk hallucinating facts. Furthermore, if three neighbors report the same broken water main, the administration rarely aggregates them into a single high-priority incident."*

---

### Slide 3: Project Objectives & Design Philosophy
- **Slide Title:** Project Objectives: Local-First, Transparent & Verifiable
- **Main Points:**
  - Build an end-to-end full-stack platform (FastAPI + React + SQLite).
  - Implement language-aware NLP without heavy model downloads.
  - Train and evaluate lightweight, reproducible sentiment models.
  - Engineer a zero-hallucination extractive summary engine.
  - Implement automatic proximity incident clustering (~330m cells).
- **Recommended Visual:** Core Pillars Icon Grid: [Local-First] [Zero Hallucination] [Multilingual] [Spatial Intelligence].
- **Presenter Explanation:** *"Our design philosophy is anchored in three non-negotiable principles: transparency, reproducibility, and local execution. We deliberately engineered CivicPulse to run on standard CPU hardware, ensuring that small town municipalities can deploy this system offline without expensive server infrastructure."*

---

### Slide 4: System Architecture Overview
- **Slide Title:** High-Level End-to-End System Architecture
- **Main Points:**
  - Client Tier: React 19 + Vite SPA with OpenStreetMap/Leaflet integration.
  - Application Tier: FastAPI asynchronous REST API with stateless JWT auth.
  - Intelligence Layer: Local NLP preprocessing, keyword scoring, in-memory ML classifiers.
  - Persistence Tier: SQLite with SQLAlchemy 2.0 ORM and composite spatial indexes.
- **Recommended Visual:** Mermaid Architecture Flowchart showing Client $\rightarrow$ API $\rightarrow$ NLP/ML $\rightarrow$ Database.
- **Presenter Explanation:** *"Here we see our four-tier architecture. The React frontend interacts with our FastAPI backend over 32 structured REST endpoints. Requests flow through our security layer, into the NLP engine for real-time intelligence, and persist into an indexed SQLite database with complete audit trails."*

---

### Slide 5: Dataset Inventory & Integrity Audit
- **Slide Title:** Rigorous Dataset Profiling & Provenance
- **Main Points:**
  - Civic Complaints: 120 bilingual records (6 balanced categories × 20).
  - Hindi Sentiment: 5,228 records (4,182 train / 523 val / 523 test).
  - Hinglish Sentiment: 2,766 code-mixed rows (45 duplicate texts documented).
  - Hindi NER: 108,335 sentences across 23 BIO labels (JSON and CoNLL formats).
  - Parallel Text: 3,027 aligned pairs (520 dev, 2,507 test; zero training split).
- **Recommended Visual:** Data inventory summary table with record counts, splits, and verified integrity badges.
- **Presenter Explanation:** *"Unlike projects that assume dataset validity, we conducted a forensic dataset audit. We independently verified every record count, identified UTF-8 BOM encoding requirements, cataloged 45 duplicate texts in the Hinglish dataset, and confirmed that the translation data contains only development and test splits, preventing data leakage."*

---

### Slide 6: Multilingual Preprocessing & Script Detection
- **Slide Title:** Unit I Alignment: Foundations & Script Identification
- **Main Points:**
  - Script Detection: Distinguishes Devanagari (`\u0900`–`\u097f`) vs Latin alphabet.
  - Language Estimation: Detects Hinglish via Romanized Hindi vocabulary intersection ($|\text{words} \cap \text{ROMAN\_HINDI}| \ge 2$).
  - Tokenization: Unicode regex `[\w\u0900-\u097f]+` preserving Hindi compound words.
  - Selective Stop-Words: Removes English/Hindi stop-words, but preserves Hinglish tokens intact.
- **Recommended Visual:** Pipeline flowchart showing a sample sentence splitting into script identification, tokenization, and filtered term frequencies.
- **Presenter Explanation:** *"Our text processing module implements Unit I curriculum principles. A custom Unicode regular expression handles Devanagari and Latin characters simultaneously. We selectively filter stop-words for English and Hindi, but intentionally bypass stop-word filtering for Hinglish so critical grammatical cues like 'nahi' or 'hua' are never lost."*

---

### Slide 7: Hindi Sentiment Analysis: Reproducibility Breakthrough
- **Slide Title:** Reproducible Hindi Sentiment Classification
- **Main Points:**
  - Pipeline: Sublinear character 3–5 grams + class-balanced Logistic Regression.
  - Scikit-learn 1.8.0 Challenge: Liblinear multiclass deprecation was diagnosed and solved.
  - Transition to `solver="lbfgs"`: Multinomial cross-entropy loss optimization.
  - Results on 523 Untouched Test Rows: **72.85% Accuracy**, **0.6963 Macro F1**.
- **Recommended Visual:** Confusion Matrix heatmap showing high true positive diagonal for Negative, Neutral, and Positive classes.
- **Presenter Explanation:** *"In Phase 4, we tackled a critical reproducibility issue. Under Scikit-learn 1.8.0, the legacy liblinear solver was deprecated for 3-class tasks. By migrating to the standard LBFGS solver, we achieved exact parity with the documented 72.85% test accuracy while improving Macro F1 to 0.6963, running in just 400 milliseconds on CPU."*

---

### Slide 8: Civic Complaint Classification Baseline & Diagnostic
- **Slide Title:** Civic Category Baseline & Forensic Error Analysis
- **Main Points:**
  - Evaluated on 120 bilingual complaints across 6 categories using stratified 75:25 split.
  - Documented Baseline Reproduced: **33.33% Accuracy**, **0.3088 Macro F1**.
  - Root Cause Analysis: Cross-lingual vocabulary sparsity (English and Hindi share 0 word features).
  - Diagnostic: Each category had only 7-8 training examples per language, causing sanitation collapse.
  - Comparative Experiments: Sublinear word unigrams reached 40.00% accuracy.
- **Recommended Visual:** Bar chart comparing Baseline (33.33%) vs Sublinear (40.00%) vs Char n-grams (36.67%).
- **Presenter Explanation:** *"We independently reproduced the 33.33% civic classification baseline. Rather than artificially inflating this metric, we conducted a rigorous mathematical error analysis. Because word-level TF-IDF creates disjoint feature spaces for English and Hindi words, 15 training examples per class effectively reduces to only 7 per language. We document this honestly as a foundational baseline."*

---

### Slide 9: Word Embeddings from Scratch (CBOW & Skip-gram)
- **Slide Title:** Unit II Alignment: Pure NumPy Word2Vec Engine
- **Main Points:**
  - Algorithmic Implementation: Continuous Bag of Words (CBOW) and Skip-gram in pure NumPy.
  - Training Mechanics: Negative sampling with sigmoid loss: $\mathcal{L} = -\log \sigma(v^T u) - \log \sigma(-v^T u_{neg})$.
  - Visual Projection: 2D Principal Component Analysis (PCA) dimensionality reduction.
  - Semantic Querying: Real-time cosine similarity search over trained dense representations.
- **Recommended Visual:** 2D PCA Scatter plot showing civic word vectors (`water`, `road`, `electricity`, `पानी`) clustering in vector space.
- **Presenter Explanation:** *"To fulfill Unit II without black-box dependencies, we built CBOW and Skip-gram engines from scratch in pure NumPy. Our implementation computes real negative sampling loss, gradient updates, and 2D PCA projections. Administrators can train the civic corpus in real time and query cosine nearest neighbors."*

---

### Slide 10: Scaled Dot-Product Attention Demonstration
- **Slide Title:** Unit IV Alignment: Attention Mechanisms
- **Main Points:**
  - Formula: $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$.
  - Purpose: Educational demonstration of query-key alignment and normalization.
  - Visual Matrix: Generates an $N \times N$ token attention heatmap.
  - Academic Boundary: Clearly documented as an algorithmic demonstration, not a pretrained BERT/Transformer.
- **Recommended Visual:** Token-by-token attention heat matrix with color gradients reflecting softmax attention weights.
- **Presenter Explanation:** *"For Unit IV, we demonstrate the mathematical core of the Transformer: Scaled Dot-Product Attention. Our service projects input tokens into query and key spaces, divides by the square root of the dimension, and computes row-wise softmax normalization. We are completely transparent with examiners: this is an educational mathematical calculator, not a multi-billion parameter foundation model."*

---

### Slide 11: Zero-Hallucination Extractive Summarization
- **Slide Title:** Unit VI Alignment: Factual Extractive Summarization
- **Main Points:**
  - Civic Necessity: Abstractive generative LLMs risk hallucinating dates, quantities, and locations.
  - Extractive Approach: Ranks source sentences by token informativeness and position.
  - Sentence-Level Provenance: Emits exact citation indices linking summary claims to source text.
  - Validation Mode: Passes 100% factual validation check (`passed: true`).
- **Recommended Visual:** Side-by-side view: Full citizen report $\rightarrow$ Extractive 1-sentence summary with source sentence citation pill.
- **Presenter Explanation:** *"In municipal dispatch, hallucinating an address or duration can be catastrophic. Instead of using a generative LLM that might invent details, CivicPulse deploys a factual extractive summarizer. Every generated summary sentence links directly to its source sentence index, guaranteeing 100% factual fidelity."*

---

### Slide 12: Proximity Incident Clustering & Dynamic Escalation
- **Slide Title:** Geographic Intelligence & Automated Crisis Escalation
- **Main Points:**
  - Spatio-temporal Grid: Bounded coordinate comparison ($\Delta = 0.003^\circ \approx 330\text{m}$).
  - Cluster Detection: Matches active reports sharing the exact same predicted category.
  - Dynamic Priority Rules:
    - 1 Report: `Normal` Priority
    - 2 Active Reports: `High` Priority
    - $\ge 3$ Active Reports: `Very High — Critical` Priority
  - Bidirectional Escalation: Elevates existing pending complaints in the cluster when threshold is breached.
- **Recommended Visual:** Map graphic showing 3 red circular pins clustering within 330m triggering a 'Critical Priority' banner.
- **Presenter Explanation:** *"Here is our core civic innovation: Proximity Incident Clustering. When multiple residents report the same problem—such as water contamination in a 330-meter radius—the system detects the cluster, escalates all participating reports to 'Critical', and flags the incident at the top of the administrative queue."*

---

### Slide 13: Citizen Portal & Geospatial Submission UI
- **Slide Title:** Citizen Experience: Pinning, Geocoding & Photo Uploads
- **Main Points:**
  - Automated short English title generation from citizen description.
  - OpenStreetMap Nominatim search box with auto-filling locality and address.
  - Interactive Leaflet map with draggable pin and reverse geocoding.
  - Multi-image photo upload (JPEG, PNG, WebP) with client-side 5MB validation.
  - Clean, accessible dark-mode UI built with React 19.
- **Recommended Visual:** Screenshot of the Citizen Complaint Form showing the interactive map picker, geocoded fields, and attached photos.
- **Presenter Explanation:** *"The citizen portal provides an intuitive experience. Citizens can type an address, click 'Use my GPS location', or drag a pin on the map. The system automatically performs reverse geocoding to populate the locality, generates a concise English overview title, and securely uploads photo attachments."*

---

### Slide 14: Administrator Dashboard & Incident Review Queue
- **Slide Title:** Administrator Oversight: Triage, Tracking & Human-in-the-Loop
- **Main Points:**
  - Filtered Queue: Displays active complaints sorted by incident priority (Critical first).
  - Category Color Coding: Colored status indicators matching map markers.
  - Audited Status Workflow: Transitions from `Submitted` $\rightarrow$ `Under Review` $\rightarrow$ `Assigned` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved`.
  - Timestamp Automation: Resolving a report automatically logs UTC `resolved_at`.
  - Human Corrections: Allows administrators to correct category or urgency predictions.
- **Recommended Visual:** Screenshot of the Admin Review Queue showing complaint cards with 'Very High — Critical' badges and status dropdowns.
- **Presenter Explanation:** *"On the administrator dashboard, incoming complaints are organized by incident priority. Administrators can update complaint status, append official two-way messages to the citizen, and correct any model prediction. Resolving a report automatically logs the resolution timestamp and recalculates the surrounding cluster priority."*

---

### Slide 15: Nationwide Geographic Map & Privacy Protection
- **Slide Title:** Geospatial Visualizations & Privacy Safeguards
- **Main Points:**
  - Interactive Map: Renders active reports across India with category-specific colored markers.
  - Residential Privacy: Coordinates are rounded to 3 decimal places (~110m) on the public view.
  - Heatmap Aggregation: Displays density circles for recurring issues.
  - Single-Report Suppression: Density points representing only 1 report are suppressed to prevent re-identification.
- **Recommended Visual:** Full-screen Leaflet map screenshot showing colored category circle markers and density heatmap rings.
- **Presenter Explanation:** *"Our geographic interface provides administrators with immediate spatial situational awareness. To protect citizen privacy, coordinates are rounded to 3 decimal places on map views, and single-report points are suppressed from the density heatmap to prevent residential re-identification."*

---

### Slide 16: Research Lab & Dataset Explorer
- **Slide Title:** Academic Research Lab & Dataset Catalog
- **Main Points:**
  - Interactive Research Lab: Run tokenization inspection, train Skip-gram embeddings, and view attention matrices in the browser.
  - Read-Only Dataset Catalog: Transparently displays all 5 bundled datasets, verified counts, formats, and limitations.
  - Separation of Concerns: Educational research demonstrations are strictly segregated from operational civic triage.
- **Recommended Visual:** Screenshot of the Research Lab showing the Skip-gram training controls and JSON output viewer.
- **Presenter Explanation:** *"The Research Lab exposes the underlying NLP algorithms to students and researchers. From this tab, evaluators can train Word2Vec embeddings with custom dimensions and epochs, inspect real-time attention weights, and review our dataset inventory without altering production database records."*

---

### Slide 17: Quality Assurance & Automated Testing
- **Slide Title:** Comprehensive QA Verification & Test Coverage
- **Main Points:**
  - 17 Automated Backend Tests: 100% pass rate in 9.13 seconds.
  - Test Suites: `test_core.py` (NLP algorithms) and `test_api_direct.py` (API workflows, auth, and security).
  - Production Build: Frontend bundles cleanly with Vite in 467ms.
  - Database Integrity: Verified foreign key cascading deletes and SQLite thread safety.
- **Recommended Visual:** Terminal screenshot showing pytest output: `17 passed in 9.13s` and Vite build success.
- **Presenter Explanation:** *"Our platform is thoroughly tested. We have 17 automated tests covering authentication, complaint lifecycle, proximity clustering, and NLP pipelines. Every test passes cleanly in under 10 seconds, and the React frontend builds with zero warnings."*

---

### Slide 18: Security, Access Control & Privacy
- **Slide Title:** Security Architecture & Role-Based Access Control
- **Main Points:**
  - Password Security: Salted PBKDF2-SHA256 password hashing; no plaintext storage.
  - Stateless Token Auth: HMAC-SHA256 JWT tokens with configurable expiration.
  - Strict Authorization: Citizen ownership checks prevent unauthorized viewing of other citizens' reports.
  - Upload Validation: MIME-type whitelist (JPEG, PNG, WebP), 5MB size limit, UUID file renaming.
  - Injection Immunity: Parameterized SQLAlchemy ORM queries prevent SQL injection.
- **Recommended Visual:** Security flow diagram showing JWT verification and role checking (`citizen` vs `admin`).
- **Presenter Explanation:** *"Security was designed from day one. Passwords use PBKDF2 with SHA-256. Access tokens are cryptographically signed JWTs with constant-time signature verification. Strict ownership guards prevent citizens from inspecting other citizens' grievances, and uploaded images are scanned and renamed to random UUIDs."*

---

### Slide 19: Limitations & Future Research Roadmap
- **Slide Title:** Honest Limitations & Future Research Directions
- **Main Points:**
  - Current Limitations: Small civic training corpus (120 rows); general-domain Hindi sentiment; no trained NER model.
  - Planned Enhancement 1: Deploy cross-lingual dense sentence encoders (e.g., IndicBERT, MiniLM).
  - Planned Enhancement 2: Fine-tune token classification models on the 108K HiNER corpus.
  - Planned Enhancement 3: Acquire large-scale parallel corpora for trained Seq2Seq translation.
  - Planned Enhancement 4: Expand annotated civic complaints to 5,000+ real-world multilingual samples.
- **Recommended Visual:** Chronological Roadmap Gantt chart: Phase 1 (Current Core) $\rightarrow$ Phase 2 (Dense Embeddings) $\rightarrow$ Phase 3 (Sequence Models).
- **Presenter Explanation:** *"We are technically candid about our current limitations. Our civic dataset is small, and our Hinglish analysis is rule-based. In future iterations, we plan to leverage our 108,000-record NER dataset to extract infrastructure entities and integrate lightweight multilingual sentence transformers to bridge the vocabulary gap between English and Hindi."*

---

### Slide 20: Conclusion & Summary of Deliverables
- **Slide Title:** Conclusion & Academic Deliverables
- **Main Points:**
  - Fully functional, verifiable platform ready for demonstration, viva, and paper submission.
  - Solves real civic grievance friction across English, Hindi, and Hinglish.
  - Verified benchmarks: 72.85% Hindi sentiment accuracy; 33.33% civic baseline.
  - Deliverables: Complete source code, automated test suite, IEEE paper draft, and 12-part comprehensive project report.
- **Recommended Visual:** Summary cards showing key achievements: [17/17 Tests Passed] [72.85% Sentiment Acc] [Zero Hallucination] [100% Local CPU].
- **Presenter Explanation:** *"To conclude, CivicPulse proves that transparent, local-first NLP can provide powerful decision support for urban governance without expensive cloud infrastructure. The application is completely stable, fully tested, and ready for live demonstration. Thank you, and I look forward to your questions."*
