"""
Social Radar AI Dashboard — Trend Detection & Alert Engine
Detects keyword spikes and sentiment anomalies.
"""

from collections import Counter
import re


def extract_keywords(posts: list[dict]) -> Counter:
    """Extract and count significant keywords from posts."""
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "out", "off", "over",
        "under", "again", "further", "then", "once", "i", "me", "my", "we",
        "our", "you", "your", "he", "she", "it", "they", "them", "this",
        "that", "these", "those", "and", "but", "or", "nor", "not", "so",
        "very", "just", "about", "up", "all", "each", "every", "both", "few",
        "more", "most", "other", "some", "such", "no", "only", "same", "than",
        "too", "also", "been", "if", "when", "what", "which", "who", "how",
    }
    word_counts: Counter = Counter()
    for post in posts:
        words = re.findall(r'\b[a-z]{3,}\b', post["text"].lower())
        meaningful = [w for w in words if w not in stop_words]
        word_counts.update(meaningful)
    return word_counts


def get_trending_keywords(posts: list[dict], top_n: int = 10) -> list[dict]:
    """Return the top trending keywords."""
    counts = extract_keywords(posts)
    return [{"keyword": kw, "count": ct} for kw, ct in counts.most_common(top_n)]


def get_sentiment_summary(posts: list[dict]) -> dict:
    """Compute overall sentiment percentages."""
    total = len(posts) or 1
    positive = sum(1 for p in posts if p.get("sentiment", {}).get("label") == "positive")
    negative = sum(1 for p in posts if p.get("sentiment", {}).get("label") == "negative")
    neutral = total - positive - negative

    return {
        "total_mentions": total,
        "positive_pct": round(positive / total * 100, 1),
        "negative_pct": round(negative / total * 100, 1),
        "neutral_pct": round(neutral / total * 100, 1),
        "positive_count": positive,
        "negative_count": negative,
        "neutral_count": neutral,
    }


def get_platform_breakdown(posts: list[dict]) -> dict:
    """Break down mentions and sentiment by platform."""
    platforms: dict[str, dict] = {}
    for post in posts:
        plat = post.get("platform", "unknown")
        if plat not in platforms:
            platforms[plat] = {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        platforms[plat]["total"] += 1
        label = post.get("sentiment", {}).get("label", "neutral")
        platforms[plat][label] += 1
    return platforms


def get_engagement_trends(posts: list[dict]) -> dict:
    """Aggregate engagement metrics."""
    total_likes = sum(p["engagement"]["likes"] for p in posts)
    total_shares = sum(p["engagement"]["shares"] for p in posts)
    total_comments = sum(p["engagement"]["comments"] for p in posts)
    return {
        "total_likes": total_likes,
        "total_shares": total_shares,
        "total_comments": total_comments,
        "avg_likes": round(total_likes / max(len(posts), 1), 1),
        "avg_shares": round(total_shares / max(len(posts), 1), 1),
        "avg_comments": round(total_comments / max(len(posts), 1), 1),
    }


def generate_alerts(posts: list[dict]) -> list[dict]:
    """Generate alerts based on sentiment spikes and keyword trends."""
    alerts: list[dict] = []
    summary = get_sentiment_summary(posts)
    trends = get_trending_keywords(posts, top_n=3)

    if summary["negative_pct"] > 40:
        alerts.append({
            "type": "danger",
            "icon": "⚠️",
            "message": f"Negative sentiment spike detected ({summary['negative_pct']}%)",
        })
    elif summary["negative_pct"] > 25:
        alerts.append({
            "type": "warning",
            "icon": "⚠️",
            "message": f"Elevated negative sentiment ({summary['negative_pct']}%)",
        })

    if trends:
        top = trends[0]
        alerts.append({
            "type": "info",
            "icon": "🔥",
            "message": f"Keyword '{top['keyword']}' is trending ({top['count']} mentions)",
        })

    if summary["positive_pct"] > 60:
        alerts.append({
            "type": "success",
            "icon": "✅",
            "message": f"Strong positive sentiment ({summary['positive_pct']}%)",
        })

    return alerts


def generate_ai_insight(posts: list[dict]) -> str:
    """Generate a simple AI insight summary based on the data."""
    summary = get_sentiment_summary(posts)
    trends = get_trending_keywords(posts, top_n=3)
    top_keywords = ", ".join(t["keyword"] for t in trends[:3])

    if summary["negative_pct"] > 40:
        return (
            f"Users are expressing significant frustration. Top concerns revolve around "
            f"{top_keywords}. Consider addressing these issues urgently to improve sentiment."
        )
    elif summary["negative_pct"] > 25:
        return (
            f"There's a moderate level of negative feedback around {top_keywords}. "
            f"Monitoring closely is recommended to prevent escalation."
        )
    elif summary["positive_pct"] > 60:
        return (
            f"Overall sentiment is very positive! Users are happy about {top_keywords}. "
            f"Great time to amplify positive stories and gather testimonials."
        )
    else:
        return (
            f"Sentiment is balanced. Key discussion topics include {top_keywords}. "
            f"Continue monitoring for any shifts in user perception."
        )
