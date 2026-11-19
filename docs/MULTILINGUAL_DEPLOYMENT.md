# Multilingual deployment and evidence requirements

## Local model choices (8 GB CPU-only)

1. **IndicLID FastText** is the required language-identification adapter. It
   covers the 22 scheduled languages and Romanised/code-mixed text when its
   local `model.bin` is installed at `ml_models/indiclid/model.bin` (or via
   `INDICLID_MODEL_PATH`). It is lazy-loaded and remains unloaded otherwise.
2. **IndicTrans2 distilled 200M** is the preferred translation family, loaded
   one direction at a time through a CTranslate2 deployment adapter. The
   upstream checkpoints require accepting the Hugging Face access conditions;
   no credential or model files are present in this workspace. The 1B models
   are intentionally not selected for this 8 GB target.
3. A local multilingual sentence-transformers embedding model may be installed
   at `ml_models/multilingual-minilm` for cross-language similarity. Its output
   is L2-normalised and compared by cosine dot product. It is lazy-loaded.

`GET /models/status` tells operators exactly which artifacts are available.
No request triggers a download. Install optional Python packages with
`pip install -r requirements-ml-optional.txt`, then provision model files under
the indicated paths. Model cache size and RAM must be verified on the target
machine before enabling more than one adapter concurrently.

## Dataset coverage audit

| Evidence requested | Supplied coverage | Status |
| --- | --- | --- |
| 22 scheduled languages | None; only Hindi and English rows | Missing |
| Scripts | Latin, Devanagari; NER labels/text Hindi | Partial |
| Romanised language | Hinglish/general-domain only | Partial, not civic |
| Intent labels | None | Missing |
| Civic category labels | 120 Hindi/English rows, six categories | Small baseline only |
| Sentiment labels | Hindi fixed split; Hinglish unsplit | Hindi evaluated; Hinglish insufficient evaluation |
| Sarcasm | None | Missing |
| Summary/reference pairs | None | Missing |
| Translation | English-Hindi dev/test only, 520/2,507 pairs | Evaluation only; not complaint data |

The quality dashboard intentionally displays `unavailable` for every metric
without a separate evaluation set and measured run. A 22-language acceptance
suite requires human-verified examples, expected outputs, task labels, and
licences. Do not use the provided translation test data as complaint examples
or translation training data.
