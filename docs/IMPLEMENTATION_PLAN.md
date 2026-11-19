# Implementation plan and build evidence

## Completed working scope

- **0 — Audit:** Canonical files, counts, labels, split boundaries, duplicates
  and provenance gaps are recorded in `DATASET_AUDIT.md`.
- **1 — Foundation:** FastAPI, SQLite schema initialization, password hashing,
  signed tokens, CORS, citizen/admin roles and a Vite/React interface exist.
- **2 — Unit I:** Unicode-aware tokenisation, script/language estimates,
  language-specific stop words, term frequencies and local TF-IDF are served
  by the API and Playground.
- **3 — Unit II:** CPU NumPy negative-sampling CBOW/Skip-gram training,
  cosine neighbour lookup and PCA coordinates run on the supplied civic corpus.
- **5 — Units IV/V educational pieces:** local scaled dot-product attention and
  extractive summarisation are interactive and do not need downloads.
- **8–10 — civic workflow:** NLP advice is persisted separately from human
  correction, citizen privacy filtering and admin-only review/status updates
  are backend-enforced.
- **11 — research UI:** dataset inventory and playground are connected to live
  endpoints; admin can generate a real reproducible TF-IDF baseline result.

## Acceptance evidence

`python -m pytest backend/tests/test_core.py -q` passed 5 tests on 2026-11-03.
`npm run build` completed successfully on 2026-11-03.

## Deliberately limited / next CPU experiments

PyTorch CPU wheels are declared for local sequence-model work, but no RNN,
BiLSTM, transformer fine-tuning or NER metric is presented as completed until
its separate training run is executed and saved. The supplied translation
corpus has no training split; the platform therefore provides only educational
attention and local extractive fallback, never a falsely-trained translator.
