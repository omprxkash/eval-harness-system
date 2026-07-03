from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

_EMOTION_KEYWORDS = {
    "frustration": ["frustrat", "annoy", "irritat", "anger", "furious", "outrag"],
    "delight": ["delight", "thrilled", "overjoyed", "love", "fantastic", "amazing"],
    "disappointment": ["disappoint", "let down", "expect", "should have", "hoped"],
    "satisfaction": ["satisfied", "happy", "pleased", "content", "glad", "grateful", "thankful"],
    "confusion": ["confus", "unclear", "complicated", "hard to understand"],
}


def analyze(text: str) -> dict:
    scores = _analyzer.polarity_scores(text)
    compound = scores["compound"]

    if compound >= 0.05:
        sentiment = "positive"
    elif compound <= -0.05:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    confidence = round(abs(compound), 4)

    detected_emotions = []
    lower_text = text.lower()
    for emotion, triggers in _EMOTION_KEYWORDS.items():
        if any(t in lower_text for t in triggers):
            detected_emotions.append(emotion)

    return {
        "sentiment": sentiment,
        "score": round(compound, 4),
        "confidence": confidence,
        "emotions": detected_emotions,
    }
