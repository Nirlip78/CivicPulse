# Build status — 2026-11-03

The project is runnable as a browser/API MVP. Verified: backend compilation,
five core NLP tests, and production frontend build. The measured civic baseline
result is stored under `experiments/results/`.

The remaining research extensions are intentionally not marked complete:
trained RNN/LSTM/GRU variants, NER fine-tuning, trained Seq2Seq translation,
and pretrained transformer/LLM adapters. The blockers are not a hidden bug:
the supplied translation data has no training split, and no valid training run
for those models has been executed yet. Local Unit I/II/attention/summarisation
fallbacks remain fully usable without those extensions.
