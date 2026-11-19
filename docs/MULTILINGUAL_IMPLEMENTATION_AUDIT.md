# Multilingual implementation audit

Audit date: 2026-11-15.  This review read every project source file and every
file under `datasets/`.  It made no changes to any dataset file.

## Verified data coverage

| Data | Actual coverage | Safe implemented use |
| --- | --- | --- |
| Civic complaints | 120 unique, balanced English/Hindi civic transcripts; six categories, 20 each | Small category baseline and local embedding demonstration only |
| Hindi sentiment | 4,182 training, 523 validation, 523 test; negative/neutral/positive | Trained local Hindi sentiment estimate and held-out test measurement |
| Hinglish sentiment | 2,766 Roman/mixed general-domain rows; no supplied splits | Inventory only; no validated inference claim |
| Hindi NER | 75,827/10,851/21,657 records in train/validation/test; 23 BIO labels | Inventory only; no trained inference model |
| English-Hindi parallel text | 520 aligned development and 2,507 aligned held-out test pairs | Alignment inspection only; no training split exists |

The `raw/source_originals` copies duplicate the canonical NER, translation,
and category-example files. JSON and CoNLL NER are alternate representations,
not extra training rows. The civic metadata refers to audio paths that are not
included. Dataset provenance and licence remain unverified.

## Implemented model choice

Hindi input now uses an in-memory character 3–5 gram TF-IDF plus balanced
Logistic Regression classifier. It trains only from the supplied Hindi training
split, has no model download, creates no model file, and uses the existing
`scikit-learn`, `numpy`, and Python standard-library dependencies. On this
machine the measured supplied held-out test result is accuracy **0.7285** and
macro F1 **0.6848**. This is general-domain Hindi sentiment, not validated
civic sentiment.

The remaining live analyses deliberately retain their existing transparent,
advisory methods: keyword civic category suggestion, lexical English/Hinglish
sentiment fallback, Unicode-aware preprocessing, extractive summary, lexical
similarity, and educational NumPy embedding/attention demonstrations.

## Resource and download check

The datasets occupy about 220.15 MiB (raw originals about 109.95 MiB). The
new classifier needs no network access or persisted disk space; it is trained
once per API process from 4,182 short texts and is practical on an 8 GB,
CPU-only computer. `torch` is present as an optional CPU package but is not
used by the application. No transformer, NER, or translation model has been
downloaded or enabled.

For a future NER or translation addition, a separately licensed model/weights
and a reproducible evaluation run are required before exposing the capability.
For translation, a permitted training corpus is additionally essential because
the current files provide only development and held-out test pairs.

## Feature status

Implemented: FastAPI/SQLite complaint workflow, citizen/admin permissions,
status history, responses, React UI, dataset inventory, local preprocessing,
Hindi trained sentiment, civic category baseline, summary, similarity, and
research demonstrations.

Missing by design: trained civic urgency; evaluated English/Hinglish civic
sentiment; NER inference; translation; semantic retrieval; uploads/maps; and
production deployment hardening. These are not presented as supported.
