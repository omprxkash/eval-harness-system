import re
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


def summarize(text: str, n_sentences: int = 2) -> str:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 5]
    if len(sentences) <= n_sentences:
        return text.strip()

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        return text.strip()

    scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
    top_indices = sorted(np.argsort(scores)[-n_sentences:])
    return " ".join(sentences[i] for i in top_indices)
