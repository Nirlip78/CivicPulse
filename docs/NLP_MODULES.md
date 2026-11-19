# NLP modules

Unit I uses local regex tokenisation, language-specific stop lists and
scikit-learn TF-IDF. Unit II is a transparent NumPy implementation of
negative-sampling CBOW/Skip-gram over the supplied small civic corpus; it is a
demonstration, not a semantic production embedding. Unit IV/V provide
deterministic scaled dot-product attention. Unit VI has a local extractive
frequency summariser. All outputs name their method and limitations.

The CPU PyTorch dependency is available for later Unit III RNN/LSTM/GRU and
Unit V NER experiments. No performance claim is made before a saved run.
