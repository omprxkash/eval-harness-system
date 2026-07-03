from app.nlp.topic_extractor import extract_topics
from app.nlp.summarizer import summarize


def test_shipping_topic():
    topics = extract_topics("The delivery was very slow and the package arrived damaged.")
    assert "shipping" in topics


def test_pricing_topic():
    topics = extract_topics("The price is too expensive for what you get.")
    assert "pricing" in topics


def test_multiple_topics():
    topics = extract_topics(
        "Shipping was fast but the quality was poor and customer service did not help at all."
    )
    assert len(topics) >= 2


def test_bugs_topic():
    topics = extract_topics("There is a bug in the app that crashes everything when I tap the button.")
    assert "bugs" in topics


def test_no_false_topics():
    topics = extract_topics("Hello, I received my order today.")
    assert isinstance(topics, list)


def test_summarizer_short_text():
    text = "Good product."
    result = summarize(text)
    assert result == text.strip()


def test_summarizer_long_text():
    text = (
        "The packaging was excellent and everything arrived in perfect condition. "
        "I was impressed by the build quality of the product itself. "
        "The instructions were a bit confusing at first but once set up it works flawlessly. "
        "Overall I am very happy with this purchase and would recommend it to anyone."
    )
    result = summarize(text, n_sentences=2)
    assert len(result) > 0
    assert len(result) < len(text)


def test_summarizer_returns_string():
    result = summarize("Short review here.")
    assert isinstance(result, str)
