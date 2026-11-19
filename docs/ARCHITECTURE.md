# CivicPulse architecture

CivicPulse will use a local-first three-layer design suitable for a CPU-only
laboratory computer:

```text
React/Vite browser UI
        │ HTTPS/JSON
FastAPI application
 ├─ authentication and role checks
 ├─ complaint workflow and audit history
 ├─ dataset inspection and experiment registry
 └─ NLP service layer
     ├─ deterministic preprocessing and TF-IDF baseline
     ├─ optional small local ML checkpoints
     └─ optional lazy pretrained adapters
        │
SQLite (default) / PostgreSQL (optional)
datasets/ (immutable raw, canonical processed, documented synthetic)
ml_models/ (generated, never shipped as fabricated results)
```

The API owns authorization and persistence; the browser never decides roles or
official complaint status. NLP outputs are advisory records with their model,
method, confidence and review requirement. Human corrections are separate from
the original predictions. SQLite is the out-of-the-box development choice;
PostgreSQL is configured only when a deployment provides it.

Raw source files remain immutable. Canonical datasets are read through a
registry that declares task, split and provenance. Training code must reject
invalid split combinations (especially translation test data and duplicated NER
representations). Heavy or internet-dependent models are optional and lazy.
