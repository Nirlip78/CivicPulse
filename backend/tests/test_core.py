from backend.app.nlp.preprocessing import analyse, language_of
from backend.app.nlp.civic import predict
from backend.app.services.research import attention_demo, word2vec_demo
from backend.app.nlp.sentiment import evaluate_hindi_sentiment, predict_hindi_sentiment
from backend.app.nlp.multilingual import identify, model_status
from backend.app.services.summaries import factual_summary
from backend.app.services.translation import translate
from backend.app.main import health_payload

def test_health_payload():
    assert health_payload()["status"] == "ok"

def test_english_preprocessing():
    result = analyse("The water supply is not working in our area.")
    assert result["language"] == "English (estimated)"
    assert "water" in result["processed_tokens"]
    assert "the" in result["removed_stop_words"]

def test_hindi_preprocessing():
    result = analyse("हमारे इलाके में पानी नहीं आ रहा है")
    assert result["script"] == "Devanagari"
    assert "पानी" in result["tokens"]

def test_hinglish_detection_and_category():
    result = predict("Hamare area mein pichle 5 din se pani nahi aa raha hai")
    assert language_of(result["original_text"])[0] == "Hinglish (estimated)"
    assert result["category"] == "Water Supply"

def test_complaint_report_is_traceable_and_cautious():
    result = predict("Hamare area mein pichle 5 din se pani nahi aa raha hai. Kai baar complain kiya but koi action nahi hua.")
    assert result["reported_duration"] == "5 days"
    assert result["sentiment"] == "Negative"
    assert result["extracted_information"]["previous_action"] == "Complaints reportedly submitted several times."
    assert result["extracted_information"]["named_locations_or_organisations"] == ["Not mentioned"]
    assert "not verified facts" in result["warnings"][0]

def test_tfidf_has_features():
    assert analyse("water water supply")["tfidf"]

def test_small_word2vec_and_attention_demonstrations():
    embedding = word2vec_demo("cbow", dimensions=4, epochs=1)
    assert embedding["status"] == "trained"
    assert embedding["vocabulary_size"] > 10
    assert len(attention_demo("water supply is unavailable")["attention"]) == 4

def test_hindi_sentiment_model_uses_only_the_supplied_training_split():
    result = predict_hindi_sentiment("यह बहुत खराब अनुभव है")
    evaluation = evaluate_hindi_sentiment()
    assert result["label"] in {"Negative", "Neutral", "Positive"}
    assert 0 <= result["confidence"] <= 1
    assert evaluation["evaluation_data"].endswith("523 supplied held-out rows)")
    assert 0 <= evaluation["accuracy"] <= 1

def test_multilingual_adapters_are_honest_when_artifacts_are_not_installed():
    identity = identify("தமிழில் தண்ணீர் வசதி இல்லை")
    status = model_status()
    result = translate("Water is unavailable", "eng_Latn", "tam_Taml")
    assert "available" in identity
    assert "indic_lid" in status
    assert result["translated_text"] is None

def test_extractive_summary_keeps_the_original_evidence_for_critical_facts():
    text = "Water has not arrived for 5 days in Anna Nagar. I complained twice, but no action was taken."
    result = factual_summary(text, detail="detailed")
    assert result["factual_validation"]["passed"] is True
    assert all(item["statement"] == item["source_sentence"] for item in result["evidence"])
    assert "5 days" in result["summary"] or "no action" in result["summary"]
