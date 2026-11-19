# CivicPulse — NLP Syllabus Mapping & Curriculum Alignment

**Course Alignment:** Natural Language Processing (University Curriculum / Six-Unit Structure)  
**Platform:** CivicPulse — Multilingual Civic Complaint Intelligence Platform  
**Purpose:** Precise, technically rigorous academic mapping showing exactly how each syllabus topic is addressed in the codebase, distinguishing implemented algorithms, educational demonstrations, optional adapters, and future research scope.

---

## 1. Curriculum Coverage Overview

| Syllabus Unit | Core Topics | Coverage Level in CivicPulse | Primary Implementation Method |
|---|---|---|---|
| **UNIT I: Foundations & Text Processing** | Tokenization, Normalization, Stop-Words, N-grams, TF-IDF, BoW, Script/Language ID | **Comprehensive (90%)** | Custom Unicode tokenizers, script detectors, TF-IDF pipelines (`backend/app/nlp/`) |
| **UNIT II: Word Embeddings** | Vector spaces, CBOW, Skip-gram, Negative Sampling, PCA, Cosine Similarity | **Substantial (75%)** | Pure NumPy Word2Vec engine with negative sampling & 2D PCA (`research.py`) |
| **UNIT III: Sequence Models** | RNN, LSTM, GRU, BiRNN, BPTT, Teacher Forcing | **Theoretical / Future Scope (0%)** | Not implemented (documented future scope; lightweight local CPU constraint) |
| **UNIT IV: Seq2Seq & Attention** | Encoder-Decoder, Bahdanau/Luong, Scaled Dot-Product Attention, Alignment | **Educational Demonstration (40%)** | Mathematical Scaled Dot-Product Attention matrix calculator (`research.py`) |
| **UNIT V: Transformers** | Self-Attention, Multi-Head Attention, BERT, GPT, BPE, WordPiece | **Adapter Stubs / Future Scope (15%)** | Lazy SentenceTransformer & IndicLID adapter stubs; no heavy downloads |
| **UNIT VI: Generative NLP & LLMs** | Decoding strategies, Perplexity, Summarization, Hallucination handling | **Extractive Alternative (30%)** | Zero-hallucination Extractive Summarizer with sentence-level citations |

---

## 2. Exhaustive Unit-by-Unit Syllabus Mapping

### UNIT I — Foundations and Text Processing

| Syllabus Topic | Status | Source File | Function / Class | Verification Evidence | Academic Limitations & Notes |
|---|---|---|---|---|---|
| **NLP Foundations** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `analyse(text)` | Pipeline produces normalized text, tokens, stop-words, and TF-IDF metrics | Focused on civic text domain across English, Hindi, and Hinglish. |
| **Script Identification** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `script_of(text)` | Verified by `test_hindi_preprocessing` and `test_api_direct.py` | Checks Unicode code points: `\u0900`–`\u097f` (Devanagari) vs ASCII alpha (Latin). Returns Devanagari, Latin, Mixed, or Unknown. |
| **Language Identification** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `language_of(text)` | Verified by `test_hinglish_detection_and_category` | Distinguishes Hindi, Hinglish, and English using script check and Romanized Hindi vocabulary intersection (>=2 tokens from `ROMAN_HINDI`). |
| **Tokenization** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `tokenize(text)` | Verified by `test_english_preprocessing` | Unicode-aware regex `r"[\w\u0900-\u097f]+"` preserving Devanagari characters, Latin letters, and numbers. |
| **Text Normalization** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `analyse(text)` | Verified in analysis output (`normalised` field) | Case folding (`text.lower()`), punctuation stripping, and token joining. |
| **Stop-word Removal** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `analyse(text)` | Verified by `test_english_preprocessing` | Explicit sets for English (`EN_STOP`) and Hindi (`HI_STOP`). Hinglish intentionally bypasses stop-words to preserve semantic tokens like *nahi*, *hai*. |
| **Punctuation Handling** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `tokenize(text)` | Regex removes non-word characters | Punctuation is stripped during feature extraction but preserved during sentence segmentation for summarization. |
| **OOV Handling** | Implemented and tested | `backend/app/nlp/sentiment.py` | `hindi_sentiment_model()` | Char n-grams (`char_wb`, range 3–5) | Character n-grams naturally handle unseen words, morphological inflections, and spelling variations in Hindi without requiring an explicit OOV token. |
| **Bag of Words (BoW)** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `analyse(text)` | `term_frequencies` dictionary | Direct term frequency count using Python `Counter` on filtered tokens. |
| **N-grams** | Implemented and tested | `backend/app/nlp/preprocessing.py` & `sentiment.py` | `TfidfVectorizer(ngram_range=...)` | Word (1,3)-grams in preprocessing; Char (3,5)-grams in sentiment | Captures local syntactic and morphological contexts. |
| **TF-IDF** | Implemented and tested | `backend/app/nlp/preprocessing.py` | `analyse(text)` | Verified by `test_tfidf_has_features` | Computes term frequency-inverse document frequency vectors with sublinear scaling. |
| **Stemming / Lemmatization** | Absent / Alternative | `backend/app/nlp/sentiment.py` | Character n-grams (`char_wb`) | Evaluated via Hindi test accuracy (72.85%) | Explicit dictionary lemmatizers (like NLTK WordNet or Hindi morph analyzers) are not used to maintain zero external downloads. Subword character n-grams serve as the empirical equivalent. |

---

### UNIT II — Word Embeddings

| Syllabus Topic | Status | Source File | Function / Class | Verification Evidence | Academic Limitations & Notes |
|---|---|---|---|---|---|
| **Vector Space Representations** | Implemented and tested | `backend/app/services/research.py` | `word2vec_demo` | Verified by `test_small_word2vec_and_attention_demonstrations` | Generates dense continuous embedding matrices $W_{in} \in \mathbb{R}^{V \times d}$ and $W_{out} \in \mathbb{R}^{V \times d}$. |
| **Continuous Bag of Words (CBOW)** | Implemented and tested | `backend/app/services/research.py` | `word2vec_demo(mode="cbow")` | Unit tested with `dimensions=4, epochs=1` | Averages context vectors $\bar{v} = \frac{1}{|C|}\sum_{c \in C} v_c$ to predict target center word $w_t$. |
| **Skip-gram** | Implemented and tested | `backend/app/services/research.py` | `word2vec_demo(mode="skipgram")` | Unit tested; loss strictly decreases per epoch | Uses target center vector $v_t$ to predict context words $w_c$ within window $m$. |
| **Negative Sampling** | Implemented and tested | `backend/app/services/research.py` | `word2vec_demo` | Explicit sigmoid loss: $-( \log \sigma(v^T u) + \log \sigma(-v^T u_{neg}) )$ | Draws random noise words from vocabulary to avoid full denominator softmax calculation over vocabulary $V$. |
| **Semantic Similarity** | Implemented and tested | `backend/app/services/research.py` | `word2vec_demo` | Nearest neighbor query ranking (`scores = vectors @ vectors[index[query]]`) | Computes normalized dot-product (cosine similarity) against query vectors. |
| **Analogy Relationships** | Planned Future Work | N/A | N/A | Documented in `KNOWN_LIMITATIONS.md` | The bundled civic corpus (120 transcripts) is too small to reliably capture parallelogram vector analogies ($v_{king} - v_{man} + v_{woman} \approx v_{queen}$). |
| **PCA (Dimensionality Reduction)** | Implemented and tested | `backend/app/services/research.py` | `PCA(n_components=2)` | Coordinates emitted in API payload (`x`, `y`) | Projects dense embeddings down to 2 dimensions for visual inspection in Research Lab. |
| **t-SNE** | Absent | N/A | N/A | PCA is used instead | t-SNE is not implemented to avoid non-deterministic stochastic neighbor embedding overhead on local CPU. |
| **GloVe** | Absent | N/A | N/A | Not implemented | Matrix factorization of global co-occurrence counts is not implemented. Only CBOW and Skip-gram are implemented. |

---

### UNIT III — Sequence Models

| Syllabus Topic | Status | Source File | Function / Class | Verification Evidence | Academic Limitations & Notes |
|---|---|---|---|---|---|
| **Recurrent Neural Networks (RNN)** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Not implemented. CPU constraint and lightweight design prioritize linear models and pure NumPy demonstrations. |
| **Long Short-Term Memory (LSTM)** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Gated sequence modeling (input, forget, output gates) is absent. |
| **Gated Recurrent Units (GRU)** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Reset and update gating mechanisms are absent. |
| **Bidirectional RNN** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Forward and backward hidden states are absent. |
| **Teacher Forcing** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Sequence generation technique not applicable without a trained Seq2Seq model. |
| **Truncated BPTT** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Gradient backpropagation through time is absent. |
| **Sequence Evaluation** | Planned Future Scope | N/A | N/A | Documented in `docs/KNOWN_LIMITATIONS.md` | Perplexity and sequence loss are absent. |

---

### UNIT IV — Seq2Seq and Attention

| Syllabus Topic | Status | Source File | Function / Class | Verification Evidence | Academic Limitations & Notes |
|---|---|---|---|---|---|
| **Encoder-Decoder Architecture** | Planned Future Scope | N/A | N/A | Parallel translation pairs present in `datasets/raw/translation/` | Data exists (520 dev, 2,507 test), but no neural Seq2Seq network is trained due to absence of a training split. |
| **Alignment Mechanisms** | Demonstration only | `backend/app/services/research.py` | `attention_demo(text)` | Emits token-by-token alignment matrix | Computes pairwise alignment scores between tokens. |
| **Bahdanau (Additive) Attention** | Theory / Future Scope | N/A | N/A | Documented in overview report | Additive attention $e_{ij} = v_a^T \tanh(W_a s_{i-1} + U_a h_j)$ is not implemented. |
| **Luong (Multiplicative) Attention** | Theory / Future Scope | N/A | N/A | Documented in overview report | Multiplicative attention $e_{ij} = s_i^T W_a h_j$ is not implemented. |
| **Scaled Dot-Product Attention** | Demonstration only | `backend/app/services/research.py` | `attention_demo(text)` | Verified by `test_small_word2vec_and_attention_demonstrations` | Exact mathematical formulation: $\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V$. Token embeddings are generated via deterministic character hashing for educational demonstration. |
| **BLEU Metric** | Guarded / Unavailable | `backend/app/services/research.py` | `multilingual_quality_dashboard` | Returns `{"status": "unavailable"}` | BLEU is not calculated because no machine translation generator is active. |
| **ROUGE Metric** | Guarded / Unavailable | `backend/app/services/research.py` | `multilingual_quality_dashboard` | Returns `{"status": "unavailable"}` | ROUGE is not calculated because no reference summary dataset is bundled. |

---

### UNIT V — Transformers

| Syllabus Topic | Status | Source File | Function / Class | Verification Evidence | Academic Limitations & Notes |
|---|---|---|---|---|---|
| **Transformer Architecture** | Theory / Concept | N/A | N/A | Detailed in `ARCHITECTURE.md` | Full multi-layer self-attention blocks are absent from runtime. |
| **Self-Attention** | Demonstration only | `backend/app/services/research.py` | `attention_demo(text)` | Verified by unit tests | Demonstrates intra-sequence token-to-token attention. |
| **Multi-Head Attention** | Theory / Future Scope | N/A | N/A | Documented in overview | Project demonstrates single-head scaled dot-product attention. |
| **Positional Encoding** | Demonstration only | `backend/app/services/research.py` | `attention_demo(text)` | `embedding = ... + i * 17` position modulation | Positional modulation is incorporated into deterministic token projections. |
| **Subword Tokenization (BPE/WordPiece)** | Optional Adapter | `backend/app/nlp/multilingual.py` | `_indiclid()`, `_embedder()` | Checks local model paths | Subword tokenizers exist inside optional FastText and HuggingFace SentenceTransformer libraries if enabled by user. |
| **Pretrained Models (BERT, GPT, T5)** | Optional Adapter Stubs | `backend/app/nlp/multilingual.py` | `embeddings(texts)` | Tested with `test_multilingual_adapters_are_honest_when_artifacts_are_not_installed` | Code contains explicit adapters for MiniLM and IndicTrans2, but deliberately defaults to lightweight CPU-only local execution without auto-downloading large models. |
| **Fine-Tuning** | Planned Future Scope | N/A | N/A | NER dataset (108K records) is prepared for future fine-tuning | No fine-tuned transformer checkpoint is committed to repository. |

---

### UNIT VI — Generative NLP and LLMs

| Syllabus Topic | Status | Source File | Function / Class | Verification Evidence | Academic Limitations & Notes |
|---|---|---|---|---|---|
| **Autoregressive Decoding (Greedy / Beam)** | Absent | N/A | N/A | Documented in `KNOWN_LIMITATIONS.md` | No generative language model is executing decoding loops. |
| **Stochastic Sampling (Top-k, Nucleus)** | Absent | N/A | N/A | Documented in `KNOWN_LIMITATIONS.md` | Not applicable to extractive summarization. |
| **Instruction-Tuned LLMs** | Absent by Design | N/A | N/A | API and UI operate fully offline | No cloud LLMs (OpenAI, Gemini, Anthropic) or local quantized LLMs (Ollama, llama.cpp) are used, adhering to the zero-paid-API and CPU constraint. |
| **Extractive Summarization** | Implemented and tested | `backend/app/services/summaries.py` | `factual_summary` | Verified by `test_extractive_summary_keeps_the_original_evidence_for_critical_facts` | Ranks and extracts verbatim source sentences based on token length and position. Avoids all generation. |
| **Hallucination Prevention** | Implemented and tested | `backend/app/services/summaries.py` | `factual_summary` | Passes `factual_validation: passed=True` | Every sentence in the summary is directly mapped to a source sentence index (`evidence`), guaranteeing complete factual fidelity. |
| **Perplexity** | Absent | N/A | N/A | Documented as future scope | Perplexity evaluation requires an autoregressive language model. |
| **Human-in-the-Loop Evaluation** | Implemented and tested | `backend/app/models/entities.py` | `Prediction.human_correction` | Verified by `test_complaint_submission_workflow` | Administrators can explicitly override model predictions (`category`, `urgency`, `status`) in the database. |

---

## 3. Academic Guidance for Viva & Project Evaluation

When presenting CivicPulse to academic evaluators or viva examiners, adhere to the following principles:

1. **Be Technically Honest About Attention:** Do not claim that `attention_demo()` represents a trained Transformer or BERT model. State clearly: *"We implemented a deterministic Scaled Dot-Product Attention matrix calculator to mathematically demonstrate how query-key compatibility and softmax normalization weight tokens within a sequence."*
2. **Be Technically Honest About Summarization:** State clearly: *"CivicPulse uses extractive factual summarization rather than abstractive generative summarization. In civic governance, abstractive LLMs risk hallucinating non-existent facts, altering dates, or omitting critical citizen grievances. Our extractive engine guarantees 100% sentence-level evidence linkage."*
3. **Be Technically Honest About Embeddings:** State clearly: *"We implemented CBOW and Skip-gram algorithms from scratch using pure NumPy with negative sampling and PCA projection. This demonstrates algorithmic understanding of vector space representations without relying on black-box libraries."*
4. **Be Technically Honest About Multilingual Support:** State clearly: *"We provide fully tested, CPU-friendly character n-gram sentiment classification for Hindi (72.85% accuracy) and lexical heuristics for Hinglish, with clean, non-blocking adapter interfaces for external models like IndicLID, SentenceTransformers, and IndicTrans2 should compute resources allow."*
