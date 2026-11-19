# Model training guide

The immediately runnable research training command is the protected API action
`POST /research/evaluate/civic-baseline`, which writes the measured TF-IDF +
Logistic Regression result to `experiments/results/`.

The Unit II Playground control trains a small NumPy negative-sampling CBOW or
Skip-gram model in memory on the 120 civic transcripts. It is deliberately
small for CPU demonstrations.

For future PyTorch Unit III work, install a compatible CPU wheel, preserve the
provided Hindi sentiment split boundaries, and write the model configuration,
checkpoint and metrics to `experiments/`. Do not report RNN/LSTM/GRU results
until that run has actually completed. Hindi NER uses its supplied JSON split;
never concatenate it with the equivalent CoNLL source.
