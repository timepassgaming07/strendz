"""
Social Radar AI Dashboard — Sentiment Analysis Engine
Uses TextBlob for NLP-based sentiment classification.
"""

from textblob import TextBlob


def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of a text string. Returns label and polarity score."""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return {
        "label": label,
        "polarity": round(polarity, 3),
        "subjectivity": round(blob.sentiment.subjectivity, 3),
    }


def analyze_batch(posts: list[dict]) -> list[dict]:
    """Add sentiment data to each post in a batch."""
    for post in posts:
        post["sentiment"] = analyze_sentiment(post["text"])
    return posts
