# Dataset sources and provenance

## Source package
- User-provided archive: `Akshay_2.zip`
- Internal top-level directory: `Akshay/`
- Original source files are preserved under `raw/source_originals/`.
- Original publisher URLs, dataset licence terms and collection methodology were not included in the uploaded archive. They must be confirmed by the project owner before redistribution or public release.

## Civic complaint transcripts
- Source files: `metadata.csv`, category-specific Hindi/English `.txt` files.
- `metadata.csv` contains 120 transcript rows: 6 categories × 2 languages × 10 records per category-language combination.
- Categories: electricity, healthcare, ration_aadhar, roads_transport, sanitation, water_supply.
- The metadata references `.mp3` paths, but the audio files themselves are not present in the uploaded ZIP.
- A canonical CSV was generated from the metadata. A leading enumerated item number was removed from the analysis `text` field; the original `source_transcript` is retained.
- Whether these transcripts are authentic, TTS-generated, or synthetic is not established by the supplied files. Do not assert their provenance; `is_synthetic` is blank.

## Hindi sentiment
- Source files: `hi-train.csv`, `hi-valid.csv`, `hi-test.csv`.
- These files are headerless. The first column is sentiment and the second is Hindi text.
- Canonical copies have columns `sentiment`, `text`, `split`, `data_source`.
- Counts: train 4,182; validation 523; test 523.
- Labels observed: negative, neutral, positive.
- Text appears general-domain (including product/review and other topics), not specifically civic complaint data.
- Original splits must be preserved.

## Hinglish sentiment
- Source file: `Hinglish.csv`.
- 2,766 records. Columns in the supplied file include an exported index, `text`, `sentiment`, and `label`.
- Canonical copy removes the exported index as a modelling feature but retains it as `source_row_id`.
- Observed sentiment counts: neutral 1,234; positive 987; negative 545. Numeric labels observed: 1, 2, 0 respectively.
- Text includes Romanised Hindi and mixed/general-domain content. Validate language and label semantics; do not assume all rows are civic or fluent code-mixed Hinglish.
- Publisher/licence not stated in the archive.

## Hindi NER
- Supplied files: `train.json`, `validation.json`, `test.json`, corresponding `.conll` files, `labels_list.txt`.
- JSON records contain `tokens` and `ner_tags`. Numeric tags map by line order in `labels_list.txt` (23 labels, including `O`).
- Record counts: train 75,827; validation 10,851; test 21,657.
- JSON and CoNLL are alternate representations; do not count both as separate data.
- Data appears to be a Hindi BIO NER corpus. Confirm original dataset identity/licence from the provider before publication. Label mapping is copied to `raw/ner/labels.json`.

## English-Hindi parallel text
- Supplied aligned files: `dev.en` with `dev.hi` (520 lines each), `test.en` with `test.hi` (2,507 lines each).
- Line positions appear sentence-aligned based on inspection of sample pairs.
- No training pair files were supplied.
- Use `dev` for development/validation and `test` only for held-out evaluation. Do not train on the test data.
- A genuine Seq2Seq training experiment requires a separate permitted training corpus or a clearly labelled small educational toy corpus.

## Data handling and licence
The archive does not contain definitive source URLs, publisher metadata or licence statements for every dataset. Verify licences and attribution requirements before redistributing the data or publishing the project repository. Keep the original files intact and cite the original dataset publishers in the final academic report once identified.
