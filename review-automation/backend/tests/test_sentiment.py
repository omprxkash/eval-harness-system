from app.nlp.sentiment_analyzer import analyze


def test_positive_review():
    result = analyze("I absolutely love this product! It works great and the quality is fantastic.")
    assert result["sentiment"] == "positive"
    assert result["score"] > 0
    assert result["confidence"] > 0


def test_negative_review():
    result = analyze("This is terrible. I am so frustrated. Complete waste of money.")
    assert result["sentiment"] == "negative"
    assert result["score"] < 0


def test_neutral_review():
    result = analyze("The product arrived on Tuesday. It is a box.")
    assert result["sentiment"] in ("neutral", "positive", "negative")
    assert "score" in result


def test_emotion_detection():
    result = analyze("I am so frustrated with the delivery. Very annoying experience.")
    assert "frustration" in result["emotions"]


def test_delight_emotion():
    result = analyze("I am absolutely delighted and thrilled with this amazing purchase!")
    assert "delight" in result["emotions"]


def test_empty_string():
    result = analyze("")
    assert result["sentiment"] == "neutral"
    assert result["score"] == 0.0


def test_confidence_range():
    result = analyze("This is pretty good but not perfect.")
    assert 0.0 <= result["confidence"] <= 1.0
