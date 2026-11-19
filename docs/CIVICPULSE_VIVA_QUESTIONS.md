# CivicPulse — Master Viva Examination Questions & Comprehensive Technical Answers (65 Questions)

**Project:** CivicPulse — Multilingual Civic Complaint Intelligence Platform  
**Target:** Academic Project Defense, Technical Interviews, and University Viva Voce  
**Examiner Focus Areas:** Fundamentals, Architecture, Database, NLP, ML Algorithms, Security, Datasets, and Honest Academic Limitations.

---

## 1. Project Fundamentals & Motivation

### Q1: What is the primary problem that CivicPulse solves?
**Answer:** CivicPulse addresses the friction in municipal grievance redressal in multilingual societies. Citizens submit grievances in English, Hindi (Devanagari), or colloquial Romanized Hindi (Hinglish). Traditional portals either fail on non-English text or rely on closed cloud APIs that can leak citizen location data and hallucinate critical facts. CivicPulse provides a local-first, lightweight platform that categorizes, prioritizes, and maps complaints while linking summaries directly to source evidence.

### Q2: Why did you choose a "local-first" architecture instead of deploying LLMs via cloud APIs?
**Answer:** Three reasons:
1. **Cost & Infrastructure:** Small municipalities often operate on standard CPU hardware with unreliable internet and cannot sustain recurring API billing ($0.01–$0.05 per call).
2. **Citizen Privacy:** Transmitting citizen complaints with home addresses and phone numbers to third-party cloud servers raises serious data protection and re-identification issues.
3. **Deterministic Accountability:** Generative LLMs are prone to hallucinating facts or altering quantities (e.g., turning "5 days" into "5 weeks"). A local deterministic pipeline guarantees 100% evidentiary fidelity.

### Q3: What languages and scripts does CivicPulse currently handle?
**Answer:** It handles English in Latin script, Hindi in Devanagari script (`\u0900`–`\u097f`), and Hinglish (code-mixed Hindi written in Latin script, such as *"Hamare area mein pani nahi aa raha hai"*).

### Q4: What are the primary user roles in CivicPulse, and how do their workflows differ?
**Answer:** There are two roles:
- **Citizen:** Can register an account, file complaints with GPS coordinates and photos, view automated NLP intelligence suggestions, track personal submission statuses, and read official administrative responses.
- **Administrator:** Can log in using a secured access key, inspect the prioritized review queue, filter complaints by locality or category, update statuses (with automatic resolution timestamps), reply to citizens, view the geographic complaint map and heatmap, run analytics, export CSV reports, and conduct experiments in the Research Lab.

### Q5: How does the system handle an unclassified or ambiguous complaint?
**Answer:** If the keyword scoring algorithm finds 0 hits across all six categories, it deliberately classifies the category as `"Needs human review"` with a confidence of `None`. It does not guess or force a classification.

---

## 2. Technical Architecture & Full-Stack Implementation

### Q6: What is the complete technology stack of CivicPulse?
**Answer:**
- **Frontend:** React 19, Vite, Leaflet.js, OpenStreetMap, Vanilla CSS.
- **Backend:** FastAPI, Python 3.12, Pydantic v2, Uvicorn, Passlib (PBKDF2), Python-jose/HMAC-SHA256 JWT.
- **Database:** SQLite 3 with SQLAlchemy 2.0 ORM.
- **Machine Learning & NLP:** Scikit-learn (Logistic Regression, TF-IDF, PCA), NumPy, Regex Unicode tokenizers.

### Q7: Why did you choose FastAPI over Flask or Django?
**Answer:** FastAPI offers native asynchronous ASGI request processing, automatic OpenAPI/Swagger interactive documentation (`/docs`), and rigorous compile-time and runtime data validation via Pydantic v2 schemas. It is much faster and lighter than Django, while providing structured type safety that Flask lacks.

### Q8: How does the frontend communicate with the backend?
**Answer:** The frontend communicates via standard RESTful JSON HTTP calls using the native browser `fetch` API wrapped in an asynchronous `call()` utility. For authenticated endpoints, it attaches the JWT in the `Authorization: Bearer <token>` HTTP header.

### Q9: How is the database schema initialized and migrated?
**Answer:** Via `migrate_schema()` in `backend/app/database/session.py`. When the FastAPI application starts up in its `lifespan` handler, it calls `Base.metadata.create_all(bind=engine)`. For SQLite, it then inspects the active transaction connection (`inspect(connection)`) and idempotently adds any missing columns to existing tables using `ALTER TABLE ADD COLUMN`.

### Q10: How did you solve the SQLite lock deadlock issue on Windows during your QA audit?
**Answer:** In the original code, `inspect(engine).get_columns("complaints")` acquired an unclosed shared read lock from the engine pool. When `with engine.begin() as connection:` immediately requested an exclusive write lock to run DDL statements, Windows deadlocked. We fixed it by calling `inspect(connection)` on the *same* transaction connection inside `with engine.begin()`, eliminating competing connection locks.

---

## 3. Database & Data Modeling

### Q11: Explain the database models and their relationships in CivicPulse.
**Answer:**
- `User` (1-to-many with `Complaint`).
- `Complaint` (1-to-many with `Prediction`, `StatusHistory`, `CitizenResponse`, and `Attachment`).
All foreign keys link back to `complaints.id` with `cascade="all, delete-orphan"` so deleting a complaint cleans up its entire dependency graph.

### Q12: Why did you create a separate `Prediction` table instead of storing predictions directly on the `Complaint` table?
**Answer:** To maintain an explicit audit trail between machine suggestions and human decisions. The `Prediction` table stores the predicted `field`, `value`, `confidence`, `method`, and an optional `human_correction`. This allows machine learning researchers to measure model accuracy against human corrections over time.

### Q13: What does the `StatusHistory` table track?
**Answer:** It records an immutable historical log of every status transition (`Submitted`, `Under Review`, `Assigned`, `In Progress`, `Resolved`, `Rejected`), the timestamp of change, the administrator ID who made the change, and optional audit notes.

### Q14: How are spatial queries optimized in the SQLite database?
**Answer:** We created composite index `Index("ix_complaints_geo", Complaint.latitude, Complaint.longitude)` to accelerate range queries used in proximity clustering and geographic bounding box searches.

### Q15: What happens when a complaint is marked as "Resolved"?
**Answer:** The API sets `complaint.resolved_at = datetime.utcnow()`. Furthermore, because a resolved report no longer represents an active hazard, the system re-evaluates all neighboring active complaints in that coordinate cell, automatically de-escalating the cluster priority if the active report count drops below the threshold.

---

## 4. NLP Preprocessing & Linguistic Foundations (Unit I)

### Q16: How does CivicPulse distinguish between Devanagari Hindi and Latin English?
**Answer:** Through `script_of()` in `preprocessing.py`. It inspects character Unicode code points: characters between `\u0900` and `\u097f` are Devanagari, while ASCII alphabetic characters are Latin. If both are present, it classifies the text as `Mixed (Devanagari/Latin)`.

### Q17: How is Hinglish detected without a full machine learning classifier?
**Answer:** In `language_of()`, if the script is Latin, the text is tokenized into words and checked for set intersection against a curated list of common Romanized Hindi markers (`ROMAN_HINDI = {"hai", "nahi", "mein", "mera", "hamare", "pani", ...}`). If the intersection contains two or more distinct tokens, it is estimated as `Hinglish (estimated)`; otherwise, it defaults to `English (estimated)`.

### Q18: Explain the regex used for tokenization and why it is Unicode-safe.
**Answer:** The regex is `re.findall(r"[\w\u0900-\u097f]+", text.lower(), flags=re.UNICODE)`. Standard `\w+` in ASCII mode drops Indian script characters. By explicitly including the Unicode range `\u0900-\u097f` and setting `re.UNICODE`, Devanagari vowels, consonants, and diacritics (matras) are cleanly preserved as intact tokens.

### Q19: Why do you avoid removing stop-words from Hinglish text?
**Answer:** In standard English or Hindi, stop-words like "the" or "है" carry little semantic category signal. However, in Romanized Hindi (Hinglish), words like *"nahi"* (negation), *"hai"* (presence), and *"se"* (temporal duration) are essential for sentiment and duration extraction. Stripping them could invert a negative complaint into a neutral or positive statement.

### Q20: What is TF-IDF and what mathematical formula does CivicPulse use?
**Answer:** Term Frequency-Inverse Document Frequency evaluates token importance in a document relative to a corpus:
$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D)$$
CivicPulse uses sublinear term frequency scaling:
$$\text{TF}_{sublinear}(t, d) = 1 + \log(\text{TF}(t, d)) \quad \text{for } \text{TF} > 0$$
and smooth inverse document frequency:
$$\text{IDF}(t) = \log\left(\frac{1 + N}{1 + \text{DF}(t)}\right) + 1$$
This prevents repetitive words from dominating the feature vector.

---

## 5. Word Embeddings & Vector Spaces (Unit II)

### Q21: What is the fundamental difference between Bag-of-Words and dense Word Embeddings?
**Answer:** Bag-of-Words represents words as sparse, orthogonal one-hot vectors of vocabulary size $V$, where every word is equidistant and semantic similarity cannot be computed ($v_i^T v_j = 0$). Word Embeddings project words into a low-dimensional continuous space $\mathbb{R}^d$ ($d \ll V$) where semantically similar words have high cosine similarity ($v_{water}^T v_{pani} > 0$).

### Q22: Explain the architecture of Continuous Bag of Words (CBOW).
**Answer:** CBOW predicts a target center word $w_t$ given its surrounding context words within a window $m$: $\{w_{t-m}, \dots, w_{t+m}\} \setminus \{w_t\}$. It averages the context input vectors:
$$\bar{v} = \frac{1}{2m} \sum_{-m \le j \le m, j \ne 0} v_{w_{t+j}}$$
and uses $\bar{v}$ to calculate probabilities over output embeddings.

### Q23: Explain the architecture of Skip-gram.
**Answer:** Skip-gram inverts CBOW: it takes the center word $w_t$ as input and attempts to maximize the probability of predicting each context word $w_c$ within the window $m$.

### Q24: What is Negative Sampling and why is it necessary?
**Answer:** Standard softmax requires computing a normalization sum over the entire vocabulary $V$:
$$P(w_O | w_I) = \frac{\exp(v'_{w_O}{}^T v_{w_I})}{\sum_{w=1}^V \exp(v'_{w}{}^T v_{w_I})}$$
For large vocabularies ($V > 10,000$), calculating the denominator for every gradient step is computationally prohibitive ($\mathcal{O}(V)$). Negative sampling transforms this multiclass task into binary logistic regressions:
$$\mathcal{L} = -\log \sigma(v'_{w_O}{}^T v_{w_I}) - \sum_{k=1}^K \mathbb{E}_{w_{n_k} \sim P_n(w)} [\log \sigma(-v'_{w_{n_k}}{}^T v_{w_I})]$$
It maximizes the probability of the true target while minimizing the probability of $K$ randomly sampled noise words, reducing complexity to $\mathcal{O}(K)$.

### Q25: How does your pure NumPy implementation of Skip-gram work?
**Answer:** In `backend/app/services/research.py:word2vec_demo`:
1. It builds a vocabulary from the 120 civic complaint sentences.
2. Initializes input weights $W_{in} \sim \mathcal{N}(0, 0.1)$ and output weights $W_{out} = 0$.
3. Generates positive (center, context) pairs and draws negative random noise samples.
4. Computes dot products, applies the sigmoid function, evaluates binary cross-entropy loss, and computes analytical gradients.
5. Updates $W_{in}$ and $W_{out}$ using gradient descent with a learning rate of 0.04.
6. Normalizes final vectors and applies 2D PCA for visual plotting in the Research Lab.

### Q26: Does your project implement GloVe or t-SNE?
**Answer:** No. We do not implement GloVe (which relies on global co-occurrence matrix factorization) or t-SNE (which has high stochastic computational complexity on CPU). We honestly state this in our documentation and use PCA for 2D embedding projections.

---

## 6. Sequence Models & Attention Mechanisms (Units III & IV)

### Q27: Are Recurrent Neural Networks (RNN/LSTM/GRU) implemented in CivicPulse?
**Answer:** No. They are explicitly cataloged as planned future work. CivicPulse was designed under a strict lightweight constraint to run out-of-the-box on commodity CPU laptops without requiring heavy PyTorch/TensorFlow deep learning dependencies during standard execution.

### Q28: How does your Attention demonstration work mathematically?
**Answer:** In `attention_demo()` in `backend/app/services/research.py`, we implement the exact Scaled Dot-Product Attention formula from Vaswani et al. (2017):
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$$
For educational purposes, tokens are mapped to deterministic 8-dimensional query and key vectors using character ASCII ordinal hashing modulated by sequence index. The query-key dot product is divided by $\sqrt{8} \approx 2.828$, and row-wise softmax normalization is applied to produce the visual attention weight matrix.

### Q29: Is your attention module a trained Transformer model?
**Answer:** No. It is a deterministic mathematical demonstration illustrating query-key alignment, scale division, and softmax normalization. It is not a trained neural network or fine-tuned BERT model, which we state clearly to examiners.

### Q30: What is the difference between Bahdanau (additive) and Luong (multiplicative) attention?
**Answer:**
- **Bahdanau Attention:** Computes alignment score using a single-hidden-layer feedforward network with hyperbolic tangent activation:
  $$e_{ij} = v_a^T \tanh(W_a s_{i-1} + U_a h_j)$$
- **Luong Attention:** Uses multiplicative inner products between decoder state $s_i$ and encoder state $h_j$:
  $$e_{ij} = s_i^T W_a h_j \quad \text{(general)} \quad \text{or} \quad e_{ij} = s_i^T h_j \quad \text{(dot)}$$
  Multiplicative attention is faster and more space-efficient because it leverages optimized matrix multiplication.

---

## 7. Machine Learning Classifiers & Sentiment Analysis

### Q31: How is the Hindi Sentiment model trained and evaluated?
**Answer:**
- **Training Corpus:** 4,182 training rows in `hindi_sentiment_train.csv`.
- **Feature Pipeline:** Character n-gram TF-IDF (`analyzer="char_wb"`, `ngram_range=(3, 5)`, `min_df=2`, `sublinear_tf=True`).
- **Classifier:** Logistic Regression (`solver="lbfgs"`, `class_weight="balanced"`, `max_iter=500`, `random_state=42`).
- **Evaluation:** Evaluated on the 523 supplied test rows (`hindi_sentiment_test.csv`), achieving **72.85% accuracy** and **0.6963 Macro F1**.
- **Memory Boundary:** The model is trained dynamically in memory and cached via `@lru_cache(maxsize=1)`. No binary weights are stored on disk.

### Q32: Why did you use character n-grams instead of word n-grams for Hindi sentiment?
**Answer:** Hindi is a morphologically rich, inflectional language where words change endings based on gender, tense, and case (e.g., *karta*, *karti*, *karte*). Word-level tokenizers suffer from high Out-Of-Vocabulary rates on small datasets. Subword character n-grams (3–5 characters) naturally capture root morphemes, suffixes, and spelling variations without requiring a dictionary lemmatizer.

### Q33: What is the difference between Liblinear and LBFGS solvers?
**Answer:**
- **Liblinear:** A coordinate descent algorithm tailored for small-to-medium binary classification problems with linear penalties. For multiclass problems, it requires decomposing into $K$ separate binary One-vs-Rest models.
- **LBFGS (Limited-memory Broyden–Fletcher–Goldfarb–Shanno):** A quasi-Newton second-order optimization method that approximates the inverse Hessian matrix. It naturally optimizes multinomial cross-entropy across all $K$ classes simultaneously, converging faster on multiclass problems.

### Q34: What was the Scikit-learn 1.8.0 bug in your sentiment model, and how did you resolve it?
**Answer:** In Scikit-learn 1.8.0, the developers deprecated and removed automatic One-vs-Rest decomposition inside `solver="liblinear"` when $K \ge 3$, causing `LogisticRegression.fit()` to throw a `ValueError`. We resolved it by upgrading the solver to `"lbfgs"`, which natively handles multinomial loss, eliminates the crash, and achieves the exact 72.85% test accuracy.

### Q35: What are the precision, recall, and F1-scores for the Hindi Sentiment model?
**Answer:**
- `Negative`: Precision = 0.4804, Recall = 0.7206, F1 = 0.5765 (Support: 68)
- `Neutral`: Precision = 0.7463, Recall = 0.7009, F1 = 0.7229 (Support: 214)
- `Positive`: Precision = 0.8273, Recall = 0.7552, F1 = 0.7896 (Support: 241)
- `Macro Average`: Precision = 0.6846, Recall = 0.7256, F1 = **0.6963**
- `Accuracy`: **72.85%** (381 / 523 correct).

---

## 8. Civic Classification Experiment & Error Analysis

### Q36: What is the accuracy of the baseline civic complaint classifier?
**Answer:** **33.33% accuracy** and **0.3088 Macro F1** on a 75:25 stratified split of 120 complaints (90 train, 30 test).

### Q37: Why is 33.33% accuracy acceptable as a research baseline?
**Answer:** Because across 6 balanced classes, random baseline accuracy is $1/6 \approx 16.67\%$. 33.33% is double random chance. More importantly, it represents a verified, reproducible baseline on a tiny 120-row bilingual dataset without artificial synthetic data manipulation.

### Q38: Why does the baseline model fail completely on the "Sanitation" class (0% F1)?
**Answer:** In the 15 training samples for sanitation, complaints described garbage heaps and waste. In the 5 test samples, complaints mentioned *"overflowing sewage near dispensary"* and *"drainage water on road"*. The model associated *"dispensary"* with `healthcare` and *"drainage water"* with `water_supply`. Lacking cross-sentence context, sanitation was completely misclassified into neighboring departments.

### Q39: What is the "Cross-Lingual Vocabulary Disjoint" problem in your civic dataset?
**Answer:** The 120 complaints are split 50% English and 50% Hindi. In the 15 training examples per category, ~7 are English and ~7 are Hindi. Standard word-level TF-IDF treats `"water"` and `"पानी"` as completely independent orthogonal features. There is zero feature weight transfer between English and Hindi, so each language effectively trains on only 7 samples per class, leading to severe sparsity and OOV errors.

### Q40: What feature engineering improvement achieved 40% accuracy on the civic dataset?
**Answer:** Switching from word unigram+bigram TF-IDF to single unigrams with sublinear term frequency scaling (`TfidfVectorizer(ngram_range=(1, 1), sublinear_tf=True)`) improved accuracy from 33.33% to **40.00%** (Macro F1: 0.3687). Sublinear scaling dampens the impact of repetitive common words in short texts.

---

## 9. Extractive Summarization & Hallucination Prevention (Unit VI)

### Q41: Why does CivicPulse use extractive summarization instead of generative abstractive summarization?
**Answer:** In municipal operations, factual precision is legally and operationally vital. An abstractive LLM might rephrase *"pothole near school on 5th street for 3 days"* into *"hazardous crater on 3rd avenue for 5 weeks"*. Extractive summarization extracts verbatim source sentences, completely eliminating the possibility of hallucinating non-existent facts or mutating dates and names.

### Q42: How does the extractive summarizer rank sentences?
**Answer:** In `backend/app/services/summaries.py:factual_summary`:
1. It splits text into sentences using punctuation boundaries (`[.!?।]\s+`).
2. It ranks sentences based on length of informative tokens and structural position.
3. For short summaries, it selects the top-ranked sentence; for detailed summaries, it selects up to 3 sentences in chronological sequence.
4. Generates an `evidence` array linking each selected statement to its original `sentence_index`.

### Q43: How does the system validate factual fidelity?
**Answer:** It runs a programmatic verification check confirming that 100% of the sentences in the summary string are identical substrings of the source text. It emits `factual_validation: {"passed": true, "mode": "verbatim evidence match"}`.

---

## 10. Geospatial Intelligence & Incident Clustering

### Q44: What is Proximity Incident Clustering?
**Answer:** It is a geospatial clustering mechanism that identifies recurring civic issues within a neighborhood. If multiple active complaints share the exact same predicted category and fall within approximately 330 meters of each other, the system groups them into a single incident cluster and escalates their priority.

### Q45: How is the 330-meter threshold calculated in code?
**Answer:** In `backend/app/main.py:NEARBY_LOCATION_DELTA = 0.003`. At the equator, 1 degree of latitude is approximately 111 km. Therefore, $0.003^\circ \times 111\text{km} \approx 333\text{ meters}$. A square bounding box check:
$$|\text{lat}_1 - \text{lat}_2| \le 0.003 \quad \text{and} \quad |\text{lon}_1 - \text{lon}_2| \le 0.003$$
provides a conservative, computationally trivial Euclidean filter suitable for CPU execution.

### Q46: What are the dynamic priority thresholds?
**Answer:**
- 1 Active Report: `Normal` priority.
- 2 Active Reports in 330m: `High` priority.
- 3 or More Active Reports in 330m: `Very High — Critical` priority.

### Q47: How does the system handle bidirectional priority escalation?
**Answer:** When a 3rd citizen submits a complaint that breaches the Critical threshold, the system not only marks the incoming complaint as Critical, but also iterates through the existing active neighbors in that cluster and elevates them to Critical as well (`nearby.priority = "Critical"`). This ensures older pending complaints from that area are prioritized in the queue.

### Q48: How does CivicPulse protect citizen residential privacy on the public map?
**Answer:**
1. Coordinates are rounded to 3 decimal places on map views, introducing an intentional uncertainty radius of ~110 meters.
2. In the geographic heatmap, coordinate buckets containing only 1 report are suppressed to prevent residential re-identification.

---

## 11. Security, Authorization & Privacy

### Q49: How are passwords secured in CivicPulse?
**Answer:** Passwords are never stored in plaintext. They are hashed using salted PBKDF2 with SHA-256 via Passlib (`passlib.hash.pbkdf2_sha256.hash(password)`), providing strong resistance to rainbow table and brute-force attacks.

### Q50: How does the authentication token work?
**Answer:** CivicPulse uses stateless JSON Web Tokens (JWT). When a user logs in, the backend encodes the user ID (`sub`), user role (`citizen` or `admin`), and expiration timestamp (`exp`). It signs the header and payload using HMAC-SHA256 with the server's `SECRET_KEY`. Subsequent requests authenticate via HTTP Bearer token headers.

### Q51: How does the system prevent timing attacks during token signature verification?
**Answer:** In `backend/app/core/security.py`, instead of standard string equality (`expected == signature`), it verifies the signature using `hmac.compare_digest(expected, signature)`, which runs in constant time regardless of how many bytes match.

### Q52: What prevents Citizen A from reading or modifying Citizen B's complaints?
**Answer:** The `complaint_for_user(complaint_id, user, db)` dependency in `backend/app/main.py`. It inspects the record: if `user.role != "admin"` and `complaint.citizen_id != user.id`, it immediately raises an HTTP 403 Forbidden exception.

### Q53: What file upload protections are implemented?
**Answer:**
1. **MIME-type whitelist:** Only `image/jpeg`, `image/png`, and `image/webp` are permitted (HTTP 415 on mismatch).
2. **Size constraint:** Bounded to 5,242,880 bytes (5MB) (HTTP 413 if exceeded).
3. **Randomized UUID storage:** Uploaded files are renamed to random hexadecimal UUIDs (e.g., `4a1b9e...jpg`) before writing to disk, neutralizing directory traversal (`../`) and executable script execution attacks.

---

## 12. Evaluation Metrics & Experimental Methodology

### Q54: What is the difference between Macro F1 and Weighted F1?
**Answer:**
- **Macro F1:** The unweighted arithmetic mean of F1-scores across all classes:
  $$\text{Macro F1} = \frac{1}{K} \sum_{k=1}^K F1_k$$
  It treats all classes equally, penalizing models that perform poorly on minority classes.
- **Weighted F1:** Averages F1-scores weighted by class support ($N_k$):
  $$\text{Weighted F1} = \sum_{k=1}^K \frac{N_k}{N} F1_k$$
  It reflects overall population accuracy but can mask severe failure on minority classes.

### Q55: Why is Accuracy alone an unreliable metric in imbalanced text classification?
**Answer:** In an imbalanced dataset where 90% of samples belong to the majority class, a trivial model that always predicts the majority class achieves 90% accuracy while having an F1-score of 0 on minority classes. Macro F1 is necessary to expose whether all classes are learned fairly.

### Q56: How is Lexical Complaint Similarity computed in CivicPulse?
**Answer:** In `related_complaints()` in `backend/app/main.py`, it computes the Jaccard similarity index between token sets of the incoming complaint and existing active reports:
$$J(A, B) = \frac{|A \cap B|}{|A \cup B|}$$
If $J(A, B) \ge 0.12$, it is surfaced as a potential related complaint to help administrators spot duplicate reports without merging them automatically.

### Q57: Why doesn't CivicPulse report ROUGE scores for its summaries?
**Answer:** Because ROUGE measures n-gram overlap between a generated summary and a human reference summary. CivicPulse does not bundle human gold-standard civic reference summaries; therefore, claiming a ROUGE score would be academic fabrication.

---

## 13. Tough Examiner Questions & Technically Honest Answers

### Q58: "Why didn't you fine-tune BERT or RoBERTa to achieve 90%+ accuracy on the civic dataset?"
**Answer:** *"That is a fair question, sir. Fine-tuning a 110-million parameter BERT model on a dataset of only 120 samples leads to catastrophic overfitting. In small-sample regimes ($N=120$), deep neural networks memorize training noise and perform poorly on out-of-domain test inputs. Furthermore, our design constraint required CPU execution on local municipal machines without high-end GPUs. A linear model provides an honest, fast, and reproducible baseline."*

### Q59: "Is your language detection robust against spelling mistakes in Hinglish?"
**Answer:** *"Our current language detection uses set intersection against high-frequency Roman Hindi marker words. While it reliably detects standard Roman spellings (like 'pani', 'nahi', 'mein'), severe phonetic misspellings (e.g., 'paaniii' or 'ny') can bypass the threshold. In future work, we plan to incorporate subword character n-gram language identifiers or enable the optional IndicLID FastText adapter."*

### Q60: "Why is your civic dataset only 120 records? Isn't that too small for a Master's or university-level project?"
**Answer:** *"The 120-record dataset was the verified benchmark provided in the project archive. Rather than fabricating synthetic data or scraping unverified internet text to artificially boost sample counts, we conducted a rigorous academic evaluation on the authentic benchmark. We augmented this with a 5,228-record Hindi sentiment dataset and a 108,000-record Hindi NER dataset, demonstrating our platform's capacity to handle both small baselines and large-scale corpora."*

### Q61: "Why don't you translate Hindi complaints into English using Google Translate before classifying?"
**Answer:** *"Relying on Google Translate would violate two foundational project constraints: it introduces a mandatory paid external cloud API dependency, and it transmits private citizen grievance texts over the public internet to third-party servers. CivicPulse was deliberately designed to process Hindi natively using Devanagari character n-grams and local models."*

### Q62: "How do you know your extractive summary doesn't miss the most important sentence?"
**Answer:** *"Our extractive heuristic ranks sentences by informative token length and structural position, prioritizing sentences that contain specific grievance terms and durations. In our technical report, we explicitly state that this is an extractive baseline; to ensure human oversight, the full original text and technical breakdown are always displayed directly alongside the summary in the interface."*

### Q63: "What happens if two complaints are 350 meters apart? Does your proximity clustering fail?"
**Answer:** *"The 330-meter threshold ($0.003^\circ$) is a hard boundary chosen as a conservative neighborhood cell equivalent to approximately one city block. Complaints 350 meters apart will fall into adjacent cells. In future work, this can be improved by replacing the square bounding box with density-based spatial clustering of applications with noise (DBSCAN) or Haversine geodesic distance calculations."*

### Q64: "Why did you keep the Hinglish sentiment dataset if you didn't train a classifier on it?"
**Answer:** *"To maintain complete scientific integrity. The Hinglish dataset (2,766 records) was part of the source archive. However, our audit revealed that it lacked official train/test splits and contained 45 duplicate texts. Rather than silently training on noisy uncurated data to make unverified claims, we cataloged it in our read-only dataset inventory and documented Hinglish model training as future scope once gold-standard validation splits are established."*

### Q65: "What makes CivicPulse ready for a live university demonstration today?"
**Answer:** *"CivicPulse is completely functional, verified, and stable. The FastAPI backend runs locally without crashes, all 17 automated tests pass, the React frontend builds cleanly in 467ms, the database handles schema migrations without locks, photo uploads and Leaflet map rendering work seamlessly, and both our Hindi sentiment (72.85%) and civic baseline (33.33%) experiments are 100% reproducible with machine-readable result logs."*
