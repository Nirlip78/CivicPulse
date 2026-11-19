# Evaluation guide

An administrator can call `POST /research/evaluate/civic-baseline` to create
`experiments/results/civic_tfidf_logreg.json`. It uses a documented stratified
75/25 split (random seed 42) of the small civic data and reports measured
accuracy, macro/weighted F1, per-class results and a confusion matrix. It must
not be described as a production estimate. Hindi sentiment and Hindi NER retain
their supplied splits for future training scripts.
