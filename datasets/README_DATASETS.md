# CivicPulse dataset package

This package was organised from the uploaded `Akshay_2.zip`.

## Folder layout

- `raw/source_originals/` — every file from the uploaded archive, preserved without modification.
- `raw/ner/` — canonical Hindi NER JSON/CoNLL files and BIO label mapping.
- `raw/translation/` — supplied English/Hindi aligned development and test files.
- `raw/civic_complaints/category_examples/` — bilingual category text examples.
- `processed/civic_complaints/` — canonical CSV derived from `metadata.csv`.
- `processed/sentiment/` — canonical sentiment CSVs with explicit column names.
- `manifests/dataset_manifest.csv` — dataset inventory and recommended usage.
- `DATASET_SOURCES.md` — provenance notes, limitations and usage rules.

## Important rules for Codex

1. Treat `raw/source_originals/` as immutable.
2. Use the canonical copies under `processed/` and the explicitly mapped files under `raw/`.
3. Do not assume that the civic metadata is non-synthetic: the supplied metadata does not establish provenance. Keep `is_synthetic` unknown/blank unless the user confirms its origin.
4. The Hindi sentiment files are general-domain sentiment data, not civic complaints.
5. The Hinglish sentiment file is supplementary, mixed/general-domain data. Inspect text and label mapping before training.
6. NER JSON and CoNLL files are alternate formats of the same splits; do not concatenate them as separate examples.
7. Translation files have `dev` and `test` pairs only. There is no supplied training split. Never train on `parallel_test.*`. Do not silently rename `dev` as `train`.
8. Do not mix datasets from different tasks into a single classifier without a clearly defined label schema.
9. Create new experiment-specific splits only with explicit documentation, and do not overwrite source splits.
10. Record actual counts, class distributions, missing values, duplicates, and evaluation metrics in generated reports.

## Current coverage

This upload supports civic category classification (small set), Hindi sentiment, supplementary Hinglish sentiment, Hindi NER, and English-Hindi parallel-text inspection. It does not contain a dedicated labelled civic urgency dataset, civic summarisation references, or an English/Hinglish civic sentiment gold-standard dataset. These need to be collected, carefully labelled, or explicitly marked as synthetic/weakly labelled.
