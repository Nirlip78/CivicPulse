# CivicPulse — Comprehensive Dataset Audit & Manifest Verification

**Audit Date:** November 2026  
**Auditor:** QA & NLP Research Engineering Team  
**Scope:** Complete verification of all raw, processed, and manifest files under `datasets/`.  
**Integrity Guarantee:** Pristine source files in `datasets/raw/source_originals/` remain untouched and immutable.

---

## 1. Verified Dataset Inventory

Every dataset in the repository has been independently counted, verified, and profiled using automated validation scripts.

| Dataset Name | Canonical Path | Verified Records | Format | Primary Task | Splits | Provenance & License Status |
|---|---|---:|---|---|---|---|
| **Civic Complaints** | `datasets/processed/civic_complaints/civic_complaints_labeled.csv` | **120** | CSV (UTF-8) | Multilingual Category Classification | 6 categories × 20 rows; Derived 75/25 split in experiments | Audio paths in metadata absent; `is_synthetic` blank; Provenance unconfirmed |
| **Hindi Sentiment** | `datasets/processed/sentiment/hindi_sentiment_{train,validation,test}.csv` | **5,228** | CSV (UTF-8 with BOM) | Sentiment Analysis (3-class) | Train: 4,182<br>Val: 523<br>Test: 523 | General-domain (reviews/news); Fixed supplied splits; License unverified |
| **Hinglish Sentiment** | `datasets/processed/sentiment/hinglish_sentiment.csv` | **2,766** | CSV (UTF-8) | Code-mixed Sentiment (3-class) | Single file (no official split) | General-domain Romanized Hindi; 45 duplicate texts; License unverified |
| **Hindi NER (HiNER)** | `datasets/raw/ner/hiner_{train,validation,test}.json` | **108,335** | JSON (arrays of token/tag lists) | Named Entity Recognition (23 BIO tags) | Train: 75,827<br>Val: 10,851<br>Test: 21,657 | Standard Hindi BIO NER corpus; Alternate CoNLL format provided; License unverified |
| **English–Hindi Parallel Text** | `datasets/raw/translation/parallel_{dev,test}.{en,hi}` | **3,027 pairs** | Aligned text files | Machine Translation Inspection & Eval | Dev: 520 pairs<br>Test: 2,507 pairs<br>**Train: 0** | Sentence-aligned bilingual corpus; **No training split supplied**; License unverified |

---

## 2. In-Depth Dataset Profiling & Quality Checks

### 2.1 Civic Complaints Dataset (`civic_complaints_labeled.csv`)

- **Total Rows:** 120
- **Columns (9):** `complaint_id`, `text`, `source_transcript`, `category`, `language`, `script`, `source_filename_reference`, `data_source`, `is_synthetic`.
- **Category Distribution (Balanced):**
  - `electricity`: 20 records (16.67%)
  - `healthcare`: 20 records (16.67%)
  - `ration_aadhar`: 20 records (16.67%)
  - `roads_transport`: 20 records (16.67%)
  - `sanitation`: 20 records (16.67%)
  - `water_supply`: 20 records (16.67%)
- **Language & Script Distribution:**
  - `english` / `Latin`: 60 records (50.0%)
  - `hindi` / `Devanagari`: 60 records (50.0%)
  - Exactly 10 English and 10 Hindi records per category.
- **Missing Values:**
  - `is_synthetic`: 120 nulls (100% blank).
  - All other 8 columns have **0 nulls**.
- **Duplicate Records:** 0 duplicate texts across all 120 rows.
- **Known Quality Issues:**
  1. Extremely small sample size (120 rows total).
  2. The source metadata references `.mp3` audio files which are absent from the archive.
  3. Provenance is unverified; whether texts were transcribed from human callers, generated via text-to-speech (TTS), or synthetically drafted cannot be established from the files. Thus `is_synthetic` is intentionally preserved as blank.

---

### 2.2 Hindi Sentiment Dataset (`hindi_sentiment_*.csv`)

- **Total Rows:** 5,228 across three canonical splits.
- **Columns (4):** `sentiment`, `text`, `split`, `data_source`.
- **Encoding Note:** Encoded with UTF-8 BOM (`\ufeff`), correctly handled with `utf-8-sig` encoding in Python to prevent schema pollution.
- **Class Distributions:**

| Split | Negative | Neutral | Positive | Total Rows | Negative % | Neutral % | Positive % |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Train** | 567 | 1,789 | 1,826 | **4,182** | 13.56% | 42.78% | 43.66% |
| **Validation** | 77 | 223 | 223 | **523** | 14.72% | 42.64% | 42.64% |
| **Test** | 68 | 214 | 241 | **523** | 13.00% | 40.92% | 46.08% |
| **Combined** | **712** | **2,226** | **2,290** | **5,228** | **13.62%** | **42.58%** | **43.80%** |

- **Missing Values:** 0 nulls across all columns and splits.
- **Data Leakage & Overlap:**
  - Exact text overlap between Train and Test splits: **0 rows**.
  - Exact text overlap between Train and Validation splits: **0 rows**.
  - Exact full-row duplicates within Train: 4 rows (retained to maintain parity with supplied split).
- **Domain Observation:** Texts are general-domain consumer reviews and social media comments (e.g., movies, products, politics), not civic complaint grievances.
- **Precaution:** Performance on this dataset (72.85% accuracy) evaluates general Hindi sentiment capability, not validated civic complaint urgency.

---

### 2.3 Hinglish Sentiment Dataset (`hinglish_sentiment.csv`)

- **Total Rows:** 2,766
- **Columns (5):** `source_row_id`, `text`, `sentiment`, `label`, `data_source`.
- **Class Distribution:**
  - `neutral` (Label `1`): 1,234 (44.61%)
  - `positive` (Label `2`): 987 (35.68%)
  - `negative` (Label `0`): 545 (19.70%)
- **Missing Values:** 0 nulls across all columns.
- **Duplicate Records:** 
  - Full rows: 0 duplicates (each has unique `source_row_id`).
  - Text values: **45 duplicate texts** (2,720 unique texts out of 2,766 rows).
- **Known Issues:**
  1. No official train, validation, or test split was provided in the source archive.
  2. Language is a noisy mixture of Romanized Hindi, informal colloquialisms, and code-switched English.
  3. Retained as an inventory benchmark; not used to claim production civic accuracy.

---

### 2.4 Hindi Named Entity Recognition (HiNER)

- **Total Records:** 108,335 sentences.
- **Split Distribution:**
  - `hiner_train.json` / `hiner_train.conll`: 75,827 records (70.0%)
  - `hiner_validation.json` / `hiner_validation.conll`: 10,851 records (10.0%)
  - `hiner_test.json` / `hiner_test.conll`: 21,657 records (20.0%)
- **Format Integrity:**
  - JSON format consists of top-level lists of objects containing `id`, `tokens` (list of strings), and `ner_tags` (list of integers).
  - Every single record in all splits has exactly matching lengths for `len(tokens) == len(ner_tags)`.
  - CoNLL files (`.conll`) contain tab-separated word and BIO tag tokens separated by blank lines.
- **Tagset (23 BIO Labels):**
  - Mapped in `datasets/raw/ner/labels.json` and `labels.txt`.
  - Categories: `FESTIVAL`, `GAME`, `LANGUAGE`, `LITERATURE`, `LOCATION`, `MISC`, `NUMEX`, `ORGANIZATION`, `PERSON`, `RELIGION`, `TIMEX` (B- and I- prefixes for each = 22 tags) + `O` (Outside, ID 22).
- **Critical Audit Rule:** JSON and CoNLL are alternative representations of the identical underlying splits. They must **never** be counted twice or merged to claim 216,000+ records.

---

### 2.5 English–Hindi Parallel Text

- **Total Pairs:** 3,027 sentence pairs.
- **Split Distribution:**
  - `parallel_dev.en` and `parallel_dev.hi`: **520 aligned pairs**.
  - `parallel_test.en` and `parallel_test.hi`: **2,507 aligned pairs**.
  - **Training split (`parallel_train.*`): 0 pairs (ABSENT).**
- **Alignment Integrity:**
  - Sentence counts between `.en` and `.hi` match exactly in both development and test splits.
  - Zero empty or blank lines.
- **Critical Audit Rule:** The archive contains **no training split**. The development split must not be silently treated as training data, nor should the test split be used for model fitting. Any genuine Seq2Seq translation training requires acquiring a separately licensed parallel corpus (such as Samanantar or IITB English-Hindi).

---

## 3. Machine-Readable Dataset Inventory (`datasets/manifests/dataset_inventory.json`)

```json
{
  "source_archive": "Akshay_2.zip",
  "audit_timestamp": "2026-11-19T17:45:00Z",
  "inventory": {
    "civic_complaints": {
      "total_rows": 120,
      "categories": 6,
      "rows_per_category": 20,
      "languages": {"english": 60, "hindi": 60},
      "is_synthetic_status": "unverified (blank)",
      "missing_values": 0
    },
    "hindi_sentiment": {
      "train": 4182,
      "validation": 523,
      "test": 523,
      "total": 5228,
      "classes": ["negative", "neutral", "positive"],
      "leakage_train_test": 0
    },
    "hinglish_sentiment": {
      "total_rows": 2766,
      "unique_texts": 2720,
      "duplicate_texts": 45,
      "official_split": null
    },
    "hindi_ner": {
      "train": 75827,
      "validation": 10851,
      "test": 21657,
      "total": 108335,
      "bio_label_count": 23,
      "formats": ["json", "conll"]
    },
    "parallel_en_hi": {
      "dev_pairs": 520,
      "test_pairs": 2507,
      "train_pairs_supplied": 0,
      "total_pairs": 3027
    }
  },
  "known_gaps": [
    "No dedicated labelled civic urgency dataset",
    "No labelled civic summarisation reference dataset",
    "No English-Hinglish civic sentiment gold-standard dataset",
    "No English-Hindi parallel training split",
    "Audio files referenced in metadata are not included",
    "Original publisher/licence details are not fully supplied"
  ]
}
```

---

## 4. Academic Provenance & Legal Disclaimers

1. **Source Archive Origin:** The raw dataset package originated from an unzipped academic archive (`Akshay_2.zip`). The archive preserves historical filenames (`hi-train.csv`, `Hinglish.csv`, `hiner_*.json`).
2. **Attribution & Licensing:** The source archive did not bundle original software licenses (e.g., CC-BY-4.0, MIT, or Research-Only licenses) or publisher URLs. Prior to public release or commercial deployment, institutional clearance and formal citation of the upstream publishers must be established.
3. **Integrity Preservation:** All raw files in `datasets/raw/source_originals/` have been cryptographically verified and left completely untouched. Processed files in `datasets/processed/` only add canonical headers and standardize UTF-8 BOM encoding.
