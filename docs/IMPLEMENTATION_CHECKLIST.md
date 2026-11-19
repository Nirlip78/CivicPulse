# CivicPulse implementation checklist

## Phase 1 — audited

- [x] Inspect workspace and preserve raw originals.
- [x] Verify manifests, canonical files, schemas, counts and label mappings.
- [x] Record distributions, duplicates, gaps and provenance limits.
- [x] Define task-to-dataset boundaries and leakage safeguards.

## Phase 2 — application foundation

- [ ] FastAPI service, SQLite default and environment configuration.
- [ ] Password hashing, signed access tokens and citizen/admin authorization.
- [ ] Complaint, prediction, correction and status-history persistence.
- [ ] Citizen and administrator API workflows.
- [ ] React/Vite interface and responsive navigation.

## Phase 3 — data and preprocessing

- [ ] English, Hindi and Hinglish script/language-aware preprocessing.
- [ ] Safe dataset inspection/import flow with explicit column mapping.
- [ ] Documented synthetic/manual annotation format for missing civic tasks.

## Phase 4 — Units I and II

- [ ] Interactive preprocessing, BoW and TF-IDF.
- [ ] Small corpus Word2Vec CBOW/Skip-Gram training and similarity.

## Phase 5 — Unit III

- [ ] CPU RNN/LSTM/GRU/BiLSTM experiments with fixed split safeguards.

## Phase 6 — Unit IV

- [ ] Clearly labelled educational Seq2Seq/attention demonstration.
- [ ] Local extractive summarisation.

## Phase 7 — Units V and VI

- [ ] Educational transformer attention, NER inference and lazy optional models.
- [ ] Hallucination-aware generation controls.

## Phase 8 — integration

- [ ] Unified playground, semantic retrieval, dataset and evaluation dashboards.

## Phase 9 — verification

- [ ] Backend, NLP, privacy and fallback tests.
- [ ] Frontend build and CPU-only launch verification.
- [ ] Complete user/developer documentation and demo rehearsal.
