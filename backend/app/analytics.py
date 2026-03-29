"""
Social Radar AI Dashboard — Trend Detection & Alert Engine
Detects keyword spikes and sentiment anomalies.
"""

from collections import Counter, defaultdict
from datetime import datetime
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


# ── New Industry Analytics ────────────────────────────────────────────────


def get_posting_calendar(posts: list[dict]) -> dict:
    """Return posting activity per day for the current month."""
    now = datetime.utcnow()
    year, month = now.year, now.month
    day_counts: dict[int, int] = defaultdict(int)
    for p in posts:
        try:
            ts = p.get("timestamp", "")
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.year == year and dt.month == month:
                day_counts[dt.day] += 1
        except (ValueError, TypeError):
            continue
    return {
        "year": year,
        "month": month,
        "days": {str(k): v for k, v in sorted(day_counts.items())},
    }


def get_peak_hours(posts: list[dict]) -> list[dict]:
    """Find peak engagement hours — which hours get the most interactions."""
    hour_eng: dict[int, dict] = defaultdict(lambda: {"posts": 0, "engagement": 0, "likes": 0, "comments": 0})
    for p in posts:
        try:
            ts = p.get("timestamp", "")
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            h = dt.hour
            eng = p.get("engagement", {})
            total = eng.get("likes", 0) + eng.get("shares", 0) + eng.get("comments", 0)
            hour_eng[h]["posts"] += 1
            hour_eng[h]["engagement"] += total
            hour_eng[h]["likes"] += eng.get("likes", 0)
            hour_eng[h]["comments"] += eng.get("comments", 0)
        except (ValueError, TypeError):
            continue
    result = []
    for h in range(24):
        d = hour_eng.get(h, {"posts": 0, "engagement": 0, "likes": 0, "comments": 0})
        result.append({
            "hour": h,
            "label": f"{h:02d}:00",
            "posts": d["posts"],
            "engagement": d["engagement"],
            "avg_engagement": round(d["engagement"] / max(d["posts"], 1), 1),
        })
    return result


def get_sentiment_distribution(posts: list[dict]) -> dict:
    """Detailed sentiment distribution with polarity histogram."""
    buckets = {"positive": 0, "negative": 0, "neutral": 0}
    polarity_ranges = [
        {"range": "-1.0 to -0.5", "min": -1.0, "max": -0.5, "count": 0},
        {"range": "-0.5 to -0.1", "min": -0.5, "max": -0.1, "count": 0},
        {"range": "-0.1 to 0.1", "min": -0.1, "max": 0.1, "count": 0},
        {"range": "0.1 to 0.5", "min": 0.1, "max": 0.5, "count": 0},
        {"range": "0.5 to 1.0", "min": 0.5, "max": 1.0, "count": 0},
    ]
    total_polarity = 0.0
    total_subjectivity = 0.0

    for p in posts:
        s = p.get("sentiment", {})
        label = s.get("label", "neutral")
        pol = s.get("polarity", 0.0)
        sub = s.get("subjectivity", 0.0)
        buckets[label] = buckets.get(label, 0) + 1
        total_polarity += pol
        total_subjectivity += sub
        for b in polarity_ranges:
            if b["min"] <= pol < b["max"] or (b["max"] == 1.0 and pol == 1.0):
                b["count"] += 1
                break

    n = max(len(posts), 1)
    return {
        "distribution": buckets,
        "polarity_histogram": [{"range": b["range"], "count": b["count"]} for b in polarity_ranges],
        "avg_polarity": round(total_polarity / n, 3),
        "avg_subjectivity": round(total_subjectivity / n, 3),
    }


def get_top_content(posts: list[dict], top_n: int = 5) -> dict:
    """Get top and bottom performing content by engagement."""
    scored = []
    for p in posts:
        eng = p.get("engagement", {})
        total = eng.get("likes", 0) + eng.get("shares", 0) + eng.get("comments", 0)
        scored.append({
            "id": p.get("id", ""),
            "text": p.get("text", "")[:120],
            "author": p.get("author", ""),
            "platform": p.get("platform", ""),
            "sentiment": p.get("sentiment", {}).get("label", "neutral"),
            "engagement": total,
            "likes": eng.get("likes", 0),
            "comments": eng.get("comments", 0),
            "timestamp": p.get("timestamp", ""),
        })
    scored.sort(key=lambda x: x["engagement"], reverse=True)
    return {
        "top": scored[:top_n],
        "bottom": scored[-top_n:] if len(scored) > top_n else [],
    }


def get_comment_sentiment(posts: list[dict]) -> dict:
    """Analyze sentiment breakdown of comments vs posts."""
    post_sent = {"positive": 0, "negative": 0, "neutral": 0}
    comment_sent = {"positive": 0, "negative": 0, "neutral": 0}

    for p in posts:
        label = p.get("sentiment", {}).get("label", "neutral")
        mt = p.get("media_type", "")
        if mt == "COMMENT" or p.get("is_comment"):
            comment_sent[label] = comment_sent.get(label, 0) + 1
        else:
            post_sent[label] = post_sent.get(label, 0) + 1

    return {
        "posts": post_sent,
        "comments": comment_sent,
        "post_total": sum(post_sent.values()),
        "comment_total": sum(comment_sent.values()),
    }
