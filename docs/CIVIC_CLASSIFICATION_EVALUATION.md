# CivicPulse — Civic Complaint Classification Evaluation & Diagnostic Report

**Experiment:** Multilingual Civic Complaint Category Classification  
**Target Code:** `backend/app/services/research.py:evaluate_civic_baseline`  
**Dataset:** `datasets/processed/civic_complaints/civic_complaints_labeled.csv` (120 records)  
**Documented Baseline Artifact:** `experiments/results/civic_tfidf_logreg.json`

---

## 1. Baseline Experiment Replication

The original baseline experiment reported in project documentation was independently rerun and evaluated using the exact documented parameters.

### 1.1 Experimental Configuration
- **Dataset Size:** 120 labeled civic complaints across 6 balanced categories (20 per category).
- **Language Composition:** 60 English (Latin script) and 60 Hindi (Devanagari script).
- **Split Scheme:** Stratified 75:25 train-test split (`test_size=0.25`, `random_state=42`, `stratify=labels`).
- **Training Set Size:** 90 samples (15 per category).
- **Test Set Size:** 30 samples (5 per category).
- **Feature Extraction:** `TfidfVectorizer(ngram_range=(1, 2))` (Word unigrams and bigrams).
- **Classification Algorithm:** `LogisticRegression(max_iter=400, random_state=42)` (Standard multiclass).

---

## 2. Reproduced Baseline Results

The independently replicated experiment yields the exact identical metrics recorded in `experiments/results/civic_tfidf_logreg.json`:

- **Overall Test Accuracy:** **33.33%** (10 / 30 correct predictions)
- **Macro-Averaged F1-Score:** **0.3088**
- **Weighted-Averaged F1-Score:** **0.3088**

### 2.1 Confusion Matrix

$$\begin{array}{r|cccccc}
\text{Actual \ Predicted} & \text{elec} & \text{health} & \text{ration} & \text{roads} & \text{sanit} & \text{water} \\
\hline
\textbf{electricity} & \mathbf{1} & 0 & 0 & 2 & 0 & 2 \\
\textbf{healthcare} & 2 & \mathbf{2} & 1 & 0 & 0 & 0 \\
\textbf{ration\_aadhar} & 0 & 1 & \mathbf{3} & 0 & 0 & 1 \\
\textbf{roads\_transport} & 1 & 0 & 0 & \mathbf{1} & 1 & 2 \\
\textbf{sanitation} & 0 & 2 & 0 & 1 & \mathbf{0} & 2 \\
\textbf{water\_supply} & 1 & 1 & 0 & 0 & 0 & \mathbf{3} \\
\end{array}$$

*Columns & Rows: electricity, healthcare, ration_aadhar, roads_transport, sanitation, water_supply.*

### 2.2 Per-Class Breakdown

| Category | Precision | Recall | F1-Score | Test Support | True Positives | Primary Misclassifications |
|---|---:|---:|---:|---:|---:|---|
| **Ration / Aadhaar** | **0.7500** | **0.6000** | **0.6667** | 5 | 3 | Healthcare (1), Water Supply (1) |
| **Water Supply** | 0.3000 | **0.6000** | 0.4000 | 5 | 3 | Electricity (1), Healthcare (1) |
| **Healthcare** | 0.3333 | 0.4000 | 0.3636 | 5 | 2 | Electricity (2), Ration/Aadhaar (1) |
| **Roads / Transport** | 0.2500 | 0.2000 | 0.2222 | 5 | 1 | Water Supply (2), Electricity (1), Sanitation (1) |
| **Electricity** | 0.2000 | 0.2000 | 0.2000 | 5 | 1 | Roads/Transport (2), Water Supply (2) |
| **Sanitation** | **0.0000** | **0.0000** | **0.0000** | 5 | 0 | Healthcare (2), Water Supply (2), Roads/Transport (1) |
| **Macro Average** | **0.3056** | **0.3333** | **0.3088** | 30 | 10 | — |
| **Weighted Average** | **0.3056** | **0.3333** | **0.3088** | 30 | 10 | — |

---

## 3. Diagnostic Investigation: Why is Performance Poor?

An accuracy of 33.33% across 6 classes is notably above random guessing ($1/6 \approx 16.67\%$), but insufficient for automated operational dispatch. Our forensic error analysis identified four core mathematical and structural root causes:

### 3.1 Severe Data Scarcity
- With only 90 training records divided across 6 classes, each class has only **15 training examples**.
- In machine learning text classification, 15 samples per class is insufficient to construct stable feature weights over high-dimensional vocabularies.

### 3.2 The Cross-Lingual Disjoint Vocabulary Problem
- The dataset is split 50% English and 50% Hindi.
- In the 15 training examples per class:
  - Approximately **7-8 examples are in English** (Latin alphabet).
  - Approximately **7-8 examples are in Hindi** (Devanagari script).
- A word-level TF-IDF vectorizer treats English tokens (`"water"`, `"pipe"`, `"outage"`) and Devanagari Hindi tokens (`"पानी"`, `"पाइप"`, `"बिजली"`) as completely disjoint, orthogonal feature dimensions.
- **There is zero cross-lingual transfer learning:** English training examples do not inform Hindi predictions, and Hindi training examples do not inform English predictions.
- Consequently, each language effectively operates with only **7 training samples per class**.

### 3.3 High Out-Of-Vocabulary (OOV) Rate in Test Split
- In a test split of 5 records per class (~2.5 English, ~2.5 Hindi), any colloquial phrasing or synonym not present in those 7 training examples yields a feature vector with near-zero non-stopword TF-IDF weights.
- When TF-IDF vectors are sparse or empty, the linear classifier defaults to the class with the highest intercept or misclassifies based on spurious background words.

### 3.4 The Sanitation Collapse (0% F1)
- The category `sanitation` failed to classify a single test example correctly (0/5).
- Inspection of the test sanitation texts revealed terms like *"overflowing sewage"*, *"garbage heap near dispensary"*, and *"गंदा पानी नालियों में"*.
- The word *"dispensary"* triggered high feature weights for `healthcare`, while *"नालियों में पानी"* triggered high feature weights for `water_supply`. Because the model lacked sufficient contextual depth, sanitation was completely swallowed by water supply and healthcare.

---

## 4. Controlled Comparative Experiments

To explore potential feature engineering improvements without manipulating or overfitting the test split, we evaluated several alternative classifiers and vectorizers under the exact same stratified 75:25 split (`random_state=42`).

| Experiment ID | Feature Extraction | Classifier Algorithm | Test Accuracy | Macro F1 | Key Observations |
|---|---|---|---:|---:|---|
| **Baseline** | Word TF-IDF (1,2) | Logistic Regression (`lbfgs`) | **33.33%** | **0.3088** | Preserved baseline standard |
| **Exp 1** | Word TF-IDF (1,2) | Logistic Regression (`class_weight='balanced'`) | 33.33% | 0.3088 | Balanced weights have no effect on uniform class support |
| **Exp 2** | Char_wb TF-IDF (3,5) | Logistic Regression | 36.67% | 0.3703 | Subword n-grams capture Hindi morphs (+3.34% acc) |
| **Exp 3** | Char_wb TF-IDF (3,5) | Logistic Regression (`balanced`) | 36.67% | 0.3703 | Identical to Exp 2 |
| **Exp 4** | **Word TF-IDF (1,1)** | **Logistic Regression (`sublinear_tf=True`)** | **40.00%** | **0.3687** | **Best accuracy (+6.67%); dampens frequency outliers** |
| **Exp 5** | Word TF-IDF (1,2) | Linear Support Vector Classifier (LinearSVC) | 33.33% | 0.2963 | Margin-based separation suffers from sparsity |
| **Exp 6** | Word TF-IDF (1,2) | Multinomial Naive Bayes | 26.67% | 0.2492 | Zero-frequency smoothing degrades on tiny corpus |

---

## 5. Architectural Conclusions & Strategic Recommendations

1. **Academic Honesty:** CivicPulse explicitly retains the documented **33.33% baseline** as its published benchmark. The project does not claim artificial 90%+ classification accuracy on 120 samples.
2. **Transparent Operational Fallback:** In the live application (`backend/app/nlp/civic.py`), CivicPulse uses a transparent keyword scoring system alongside duration and grievance extraction. If confidence is low, it marks the category as `"Needs human review"`.
3. **Path to Production Accuracy:**
   - **Data Expansion:** The civic complaint corpus must be expanded from 120 to at least 2,000–5,000 real-world multilingual complaints.
   - **Dense Cross-Lingual Embeddings:** Rather than sparse word TF-IDF, future iterations should deploy multilingual sentence encoders (such as `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` or `IndicBERT`), which project English and Hindi into a shared semantic vector space where `water` and `पानी` share near-identical vector representations.
