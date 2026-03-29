"""
Social Radar AI Dashboard — FastAPI Backend
Provides REST endpoints for the dashboard frontend.
"""

from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse, HTMLResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import urllib.request, urllib.parse, json, ssl, os, csv, io
from pathlib import Path

# Load .env file if present
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

from pydantic import BaseModel

from app.data_simulator import generate_dataset, generate_post
from app.sentiment import analyze_batch
from app.analytics import (
    get_sentiment_summary,
    get_trending_keywords,
    get_platform_breakdown,
    get_engagement_trends,
    generate_alerts,
    generate_ai_insight,
    get_posting_calendar,
    get_peak_hours,
    get_sentiment_distribution,
    get_top_content,
    get_comment_sentiment,
)
from app.social import connector

app = FastAPI(title="Strendz API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data store (simulated)
data_store: list[dict] = []


def ensure_data(count: int = 200) -> list[dict]:
    """Return real data if connected, otherwise simulated data."""
    global data_store
    # If we have real social connections, use real data (even if cached)
    if connector.is_connected():
        real = connector.fetch_all()
        if real:
            return real
        # Connected but no posts yet (rate limited) — still show connected state
        # Return cached real_posts if any
        if connector.real_posts:
            return connector.real_posts
    # Fallback to simulated data
    if not data_store:
        data_store = analyze_batch(generate_dataset(count))
    return data_store


@app.on_event("startup")
async def startup():
    """Initialize data on startup."""
    ensure_data(200)


@app.get("/data")
async def get_data(
    platform: str | None = Query(None, description="Filter by platform"),
    limit: int = Query(50, ge=1, le=500),
):
    """Get recent social media posts with sentiment data."""
    posts = ensure_data()
    if platform:
        posts = [p for p in posts if p["platform"] == platform]
    return {"posts": posts[:limit], "total": len(posts)}


@app.get("/sentiment-summary")
async def sentiment_summary(platform: str | None = Query(None)):
    """Get overall sentiment percentages."""
    posts = ensure_data()
    if platform:
        posts = [p for p in posts if p["platform"] == platform]
    return get_sentiment_summary(posts)


@app.get("/trends")
async def trends(top_n: int = Query(10, ge=1, le=50)):
    """Get trending keywords."""
    posts = ensure_data()
    return {"keywords": get_trending_keywords(posts, top_n)}


@app.get("/alerts")
async def alerts():
    """Get current alerts."""
    posts = ensure_data()
    return {"alerts": generate_alerts(posts)}


@app.get("/platform-breakdown")
async def platform_breakdown():
    """Get sentiment breakdown by platform."""
    posts = ensure_data()
    return get_platform_breakdown(posts)


@app.get("/engagement")
async def engagement():
    """Get engagement metrics."""
    posts = ensure_data()
    return get_engagement_trends(posts)


@app.get("/ai-insight")
async def ai_insight():
    """Get AI-generated insight."""
    posts = ensure_data()
    return {"insight": generate_ai_insight(posts)}


@app.post("/simulate")
async def simulate_new():
    """Add a new simulated post (for real-time updates)."""
    global data_store
    new_post = generate_post(datetime.utcnow())
    from app.sentiment import analyze_sentiment
    new_post["sentiment"] = analyze_sentiment(new_post["text"])
    data_store.insert(0, new_post)
    # Keep the store at a manageable size
    if len(data_store) > 500:
        data_store = data_store[:500]
    return new_post


# ── Social Connection Endpoints ───────────────────────────────────────────


class ConnectRequest(BaseModel):
    platform: str
    credentials: dict


@app.post("/connect")
async def connect_platform(req: ConnectRequest):
    """Connect a social media platform with API credentials."""
    result = connector.connect(req.platform, req.credentials)
    return result


@app.post("/disconnect")
async def disconnect_platform(platform: str = Query(...)):
    """Disconnect a social media platform."""
    connector.disconnect(platform)
    return {"ok": True, "message": f"Disconnected {platform}"}


@app.get("/connection-status")
async def connection_status():
    """Get connection status for all platforms."""
    return connector.get_status()


@app.get("/debug-twitter")
async def debug_twitter():
    """Debug: test Twitter API calls."""
    cfg = connector.connections.get("twitter")
    if not cfg:
        return {"error": "Twitter not connected"}

    import urllib.request, urllib.error, urllib.parse, json, ssl
    _ssl_ctx = ssl.create_default_context()
    try:
        import certifi
        _ssl_ctx.load_verify_locations(certifi.where())
    except ImportError:
        _ssl_ctx.check_hostname = False
        _ssl_ctx.verify_mode = ssl.CERT_NONE

    bearer = cfg["bearer_token"]
    handle = cfg["handle"]
    results = {"handle": handle, "bearer_len": len(bearer), "user_id": cfg.get("user_id")}

    # Test user lookup
    try:
        url = f"https://api.twitter.com/2/users/by/username/{urllib.parse.quote(handle)}"
        url += "?user.fields=public_metrics,description,profile_image_url"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            data = json.loads(resp.read())
        results["user_lookup"] = data
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        results["user_lookup_error"] = {"code": e.code, "reason": e.reason, "body": body}
    except Exception as e:
        results["user_lookup_error"] = str(e)

    # Test tweet fetch
    try:
        user_id = results.get("user_lookup", {}).get("data", {}).get("id") or cfg.get("user_id")
        if user_id:
            url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at,public_metrics"
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            results["tweets"] = {"count": len(data.get("data", [])), "sample": data.get("data", [])[:2]}
        else:
            results["tweets"] = "no user_id available"
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        results["tweets_error"] = {"code": e.code, "reason": e.reason, "body": body}
    except Exception as e:
        results["tweets_error"] = str(e)

    return results


@app.post("/refresh")
async def refresh_data():
    """Force refresh data from connected platforms."""
    global data_store
    if not connector.is_connected():
        return {"ok": False, "error": "No platforms connected"}
    connector.last_fetch = 0  # Reset cache timer
    connector.real_posts = []  # Clear cached posts
    data_store = []  # Clear simulated data
    # Also reset profile to force re-fetch
    if "followers" not in connector.profile or not connector.profile.get("avatar_url"):
        connector.profile.pop("followers", None)
        connector.profile.pop("avatar_url", None)
    posts = connector.fetch_all()
    return {"ok": True, "count": len(posts), "profile": connector.profile}


class AnalyzeRequest(BaseModel):
    subreddit: str = ""
    username: str = ""


@app.post("/analyze-profile")
async def analyze_profile(req: AnalyzeRequest):
    """Fetch a subreddit or user profile + posts and return full analysis."""
    import urllib.request, urllib.error, urllib.parse, json, ssl

    _ctx = ssl.create_default_context()
    try:
        import certifi
        _ctx.load_verify_locations(certifi.where())
    except ImportError:
        _ctx.check_hostname = False
        _ctx.verify_mode = ssl.CERT_NONE

    from app.sentiment import analyze_sentiment as _as

    # ─── User profile mode ────────────────────────────────────────────
    username = req.username.strip().lstrip("u/").lstrip("/") if req.username else ""
    if username:
        # Fetch user info
        try:
            url = f"https://www.reddit.com/user/{urllib.parse.quote(username)}/about.json"
            r = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(r, timeout=10, context=_ctx) as resp:
                udata = json.loads(resp.read()).get("data", {})
            if not udata.get("name"):
                return {"ok": False, "error": f"User u/{username} not found"}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"ok": False, "error": f"User u/{username} not found"}
            return {"ok": False, "error": f"Error: {e.code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

        avatar = udata.get("icon_img", "") or udata.get("snoovatar_img", "")
        avatar = avatar.split("?")[0] if avatar else ""
        total_karma = udata.get("link_karma", 0) + udata.get("comment_karma", 0)

        profile = {
            "name": udata.get("subreddit", {}).get("title") or udata.get("name", username),
            "handle": f"u/{udata.get('name', username)}",
            "followers": udata.get("subreddit", {}).get("subscribers", 0),
            "active_users": 0,
            "description": udata.get("subreddit", {}).get("public_description", "")[:300],
            "avatar_url": avatar,
            "created_utc": udata.get("created_utc", 0),
            "over18": udata.get("subreddit", {}).get("over_18", False),
            "karma": total_karma,
            "link_karma": udata.get("link_karma", 0),
            "comment_karma": udata.get("comment_karma", 0),
            "is_user": True,
        }

        # Fetch submitted posts
        posts = []
        try:
            url = f"https://www.reddit.com/user/{urllib.parse.quote(username)}/submitted.json?limit=25&sort=new"
            r = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(r, timeout=15, context=_ctx) as resp:
                raw = json.loads(resp.read())
            for child in raw.get("data", {}).get("children", []):
                item = child.get("data", {})
                text = item.get("title", "")
                selftext = item.get("selftext", "")
                if selftext:
                    text += "\n" + selftext[:300]
                posts.append({
                    "id": f"reddit_{item.get('id', '')}",
                    "text": text,
                    "platform": "reddit",
                    "timestamp": datetime.utcfromtimestamp(item.get("created_utc", 0)).isoformat(),
                    "engagement": {"likes": item.get("ups", 0), "shares": 0, "comments": item.get("num_comments", 0)},
                    "author": f"u/{username}",
                    "sentiment": _as(text),
                    "subreddit": item.get("subreddit_name_prefixed", ""),
                })
        except Exception:
            pass

        # Fetch comments
        try:
            url = f"https://www.reddit.com/user/{urllib.parse.quote(username)}/comments.json?limit=25&sort=new"
            r = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(r, timeout=15, context=_ctx) as resp:
                raw = json.loads(resp.read())
            for child in raw.get("data", {}).get("children", []):
                item = child.get("data", {})
                body = item.get("body", "")
                if not body:
                    continue
                posts.append({
                    "id": f"reddit_c_{item.get('id', '')}",
                    "text": body[:400],
                    "platform": "reddit",
                    "timestamp": datetime.utcfromtimestamp(item.get("created_utc", 0)).isoformat(),
                    "engagement": {"likes": item.get("ups", 0), "shares": 0, "comments": 0},
                    "author": f"u/{username}",
                    "sentiment": _as(body[:400]),
                    "is_comment": True,
                    "subreddit": item.get("subreddit_name_prefixed", ""),
                })
        except Exception:
            pass

        posts.sort(key=lambda p: p.get("timestamp", ""), reverse=True)

        sentiment = get_sentiment_summary(posts)
        keywords = get_trending_keywords(posts, 10)
        eng = get_engagement_trends(posts)
        insight = generate_ai_insight(posts)

        return {
            "ok": True,
            "profile": profile,
            "sentiment": sentiment,
            "keywords": keywords,
            "engagement": eng,
            "insight": insight,
            "posts": posts[:20],
            "total_posts": len(posts),
        }

    # ─── Subreddit mode (existing) ────────────────────────────────────
    subreddit = req.subreddit.strip().lstrip("r/")
    if not subreddit:
        return {"ok": False, "error": "Subreddit name is required"}

    # Try name as-is, then without spaces, then with underscores
    candidates = [subreddit]
    if " " in subreddit:
        candidates.append(subreddit.replace(" ", ""))
        candidates.append(subreddit.replace(" ", "_"))

    info = None
    for candidate in candidates:
        try:
            url = f"https://www.reddit.com/r/{urllib.parse.quote(candidate)}/about.json"
            r = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(r, timeout=10, context=_ctx) as resp:
                data = json.loads(resp.read())
            check = data.get("data", {})
            if check.get("display_name"):
                info = check
                subreddit = candidate
                break
        except Exception:
            continue

    if not info:
        return {"ok": False, "error": f"Subreddit not found. Try without spaces, e.g. 'GooglePixel' instead of 'google pixel'"}

    icon = info.get("icon_img", "") or info.get("community_icon", "")
    icon = icon.split("?")[0] if icon else ""

    profile = {
        "name": info.get("title") or info.get("display_name", subreddit),
        "handle": info.get("display_name_prefixed", f"r/{subreddit}"),
        "followers": info.get("subscribers", 0),
        "active_users": info.get("accounts_active", 0),
        "description": info.get("public_description", "")[:300],
        "avatar_url": icon,
        "created_utc": info.get("created_utc", 0),
        "over18": info.get("over18", False),
    }

    # 2) Fetch hot posts
    try:
        url = f"https://www.reddit.com/r/{urllib.parse.quote(subreddit)}/hot.json?limit=50"
        r = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
        with urllib.request.urlopen(r, timeout=15, context=_ctx) as resp:
            raw = json.loads(resp.read())
    except Exception:
        raw = {"data": {"children": []}}

    from app.sentiment import analyze_sentiment as _as

    posts = []
    for child in raw.get("data", {}).get("children", []):
        item = child.get("data", {})
        if item.get("stickied"):
            continue
        text = item.get("title", "")
        selftext = item.get("selftext", "")
        if selftext:
            text += "\n" + selftext[:300]
        post = {
            "id": f"reddit_{item.get('id', '')}",
            "text": text,
            "platform": "reddit",
            "timestamp": datetime.utcfromtimestamp(item.get("created_utc", 0)).isoformat(),
            "engagement": {
                "likes": item.get("ups", 0),
                "shares": 0,
                "comments": item.get("num_comments", 0),
            },
            "author": item.get("author", "[deleted]"),
            "sentiment": _as(text),
        }
        posts.append(post)

    # 3) Run analytics on the posts
    sentiment = get_sentiment_summary(posts)
    keywords = get_trending_keywords(posts, 10)
    eng = get_engagement_trends(posts)
    insight = generate_ai_insight(posts)

    return {
        "ok": True,
        "profile": profile,
        "sentiment": sentiment,
        "keywords": keywords,
        "engagement": eng,
        "insight": insight,
        "posts": posts[:20],
        "total_posts": len(posts),
    }


@app.get("/sentiment-timeline")
async def sentiment_timeline():
    """Get sentiment data bucketed by hour for the timeline chart."""
    posts = ensure_data()
    buckets: dict[str, dict] = {}
    for post in posts:
        hour = post["timestamp"][:13]  # YYYY-MM-DDTHH
        if hour not in buckets:
            buckets[hour] = {"positive": 0, "neutral": 0, "negative": 0}
        label = post.get("sentiment", {}).get("label", "neutral")
        buckets[hour][label] += 1

    timeline = []
    for hour in sorted(buckets.keys()):
        b = buckets[hour]
        timeline.append({
            "time": hour.replace("T", " ") + ":00",
            "positive": b["positive"],
            "neutral": b["neutral"],
            "negative": b["negative"],
        })
    return {"timeline": timeline}


# ── New Analytics Endpoints ───────────────────────────────────────────────


@app.get("/posting-calendar")
async def posting_calendar():
    """Get posting activity per day for the current month."""
    return get_posting_calendar(ensure_data())


@app.get("/peak-hours")
async def peak_hours():
    """Get engagement by hour of day."""
    return {"hours": get_peak_hours(ensure_data())}


@app.get("/sentiment-distribution")
async def sentiment_distribution():
    """Get detailed sentiment distribution with polarity histogram."""
    return get_sentiment_distribution(ensure_data())


@app.get("/top-content")
async def top_content(top_n: int = Query(5, ge=1, le=20)):
    """Get top and bottom performing content by engagement."""
    return get_top_content(ensure_data(), top_n)


@app.get("/comment-sentiment")
async def comment_sentiment():
    """Get sentiment breakdown for comments vs posts."""
    return get_comment_sentiment(ensure_data())


@app.get("/report/download")
async def download_report(format: str = Query("csv", regex="^(csv|json|txt|md)$")):
    """Download a full analytics report in the specified format."""
    posts = ensure_data()
    summary = get_sentiment_summary(posts)
    keywords = get_trending_keywords(posts, 10)
    engagement = get_engagement_trends(posts)
    peak = get_peak_hours(posts)
    dist = get_sentiment_distribution(posts)
    top = get_top_content(posts, 10)
    cal = get_posting_calendar(posts)
    cs = get_comment_sentiment(posts)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    if format == "json":
        report = {
            "generated_at": now,
            "summary": summary,
            "keywords": keywords,
            "engagement": engagement,
            "peak_hours": peak,
            "sentiment_distribution": dist,
            "top_content": top,
            "posting_calendar": cal,
            "comment_sentiment": cs,
            "posts": [{"id": p.get("id"), "text": p.get("text", "")[:200], "author": p.get("author"), "platform": p.get("platform"), "timestamp": p.get("timestamp"), "sentiment": p.get("sentiment", {}).get("label"), "likes": p.get("engagement", {}).get("likes", 0), "comments": p.get("engagement", {}).get("comments", 0)} for p in posts],
        }
        content = json.dumps(report, indent=2)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="application/json",
            headers={"Content-Disposition": f'attachment; filename="strendz-report-{datetime.utcnow().strftime("%Y%m%d")}.json"'},
        )

    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "text", "author", "platform", "timestamp", "sentiment", "polarity", "likes", "shares", "comments"])
        for p in posts:
            writer.writerow([
                p.get("id", ""),
                p.get("text", "")[:200],
                p.get("author", ""),
                p.get("platform", ""),
                p.get("timestamp", ""),
                p.get("sentiment", {}).get("label", ""),
                p.get("sentiment", {}).get("polarity", 0),
                p.get("engagement", {}).get("likes", 0),
                p.get("engagement", {}).get("shares", 0),
                p.get("engagement", {}).get("comments", 0),
            ])
        content = output.getvalue()
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="strendz-report-{datetime.utcnow().strftime("%Y%m%d")}.csv"'},
        )

    elif format == "md":
        active_peak = [h for h in peak if h["engagement"] > 0]
        best_hour = max(active_peak, key=lambda h: h["engagement"])["label"] if active_peak else "N/A"
        top_kws = ", ".join(k["keyword"] for k in keywords[:5])
        lines = [
            f"# Strendz Analytics Report",
            f"Generated: {now}\n",
            f"## Summary",
            f"- **Total Mentions:** {summary['total_mentions']}",
            f"- **Positive:** {summary['positive_pct']}% ({summary['positive_count']})",
            f"- **Negative:** {summary['negative_pct']}% ({summary['negative_count']})",
            f"- **Neutral:** {summary['neutral_pct']}% ({summary['neutral_count']})\n",
            f"## Engagement",
            f"- **Total Likes:** {engagement['total_likes']}  |  **Avg:** {engagement['avg_likes']}",
            f"- **Total Comments:** {engagement['total_comments']}  |  **Avg:** {engagement['avg_comments']}",
            f"- **Total Shares:** {engagement['total_shares']}  |  **Avg:** {engagement['avg_shares']}\n",
            f"## Sentiment",
            f"- **Avg Polarity:** {dist['avg_polarity']}",
            f"- **Avg Subjectivity:** {dist['avg_subjectivity']}\n",
            f"## Top Keywords",
            f"{top_kws}\n",
            f"## Best Posting Time",
            f"**{best_hour}** — highest engagement hour\n",
            f"## Comment vs Post Sentiment",
            f"- Posts: {cs['post_total']} (pos {cs['posts']['positive']}, neg {cs['posts']['negative']}, neu {cs['posts']['neutral']})",
            f"- Comments: {cs['comment_total']} (pos {cs['comments']['positive']}, neg {cs['comments']['negative']}, neu {cs['comments']['neutral']})\n",
            f"## Top Performing Content",
        ]
        for i, t in enumerate(top["top"][:5], 1):
            lines.append(f"{i}. **{t['text'][:80]}** — {t['engagement']} engagements ({t['sentiment']})")
        content = "\n".join(lines)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="strendz-report-{datetime.utcnow().strftime("%Y%m%d")}.md"'},
        )

    else:  # txt
        active_peak = [h for h in peak if h["engagement"] > 0]
        best_hour = max(active_peak, key=lambda h: h["engagement"])["label"] if active_peak else "N/A"
        top_kws = ", ".join(k["keyword"] for k in keywords[:5])
        lines = [
            f"STRENDZ ANALYTICS REPORT",
            f"Generated: {now}",
            f"{'=' * 50}",
            f"",
            f"SUMMARY",
            f"  Total Mentions: {summary['total_mentions']}",
            f"  Positive: {summary['positive_pct']}% ({summary['positive_count']})",
            f"  Negative: {summary['negative_pct']}% ({summary['negative_count']})",
            f"  Neutral:  {summary['neutral_pct']}% ({summary['neutral_count']})",
            f"",
            f"ENGAGEMENT",
            f"  Total Likes: {engagement['total_likes']}   Avg: {engagement['avg_likes']}",
            f"  Total Comments: {engagement['total_comments']}   Avg: {engagement['avg_comments']}",
            f"  Total Shares: {engagement['total_shares']}   Avg: {engagement['avg_shares']}",
            f"",
            f"SENTIMENT",
            f"  Avg Polarity: {dist['avg_polarity']}",
            f"  Avg Subjectivity: {dist['avg_subjectivity']}",
            f"",
            f"TOP KEYWORDS: {top_kws}",
            f"",
            f"BEST POSTING TIME: {best_hour}",
            f"",
            f"COMMENTS vs POSTS",
            f"  Posts:    {cs['post_total']} (pos={cs['posts']['positive']}, neg={cs['posts']['negative']}, neu={cs['posts']['neutral']})",
            f"  Comments: {cs['comment_total']} (pos={cs['comments']['positive']}, neg={cs['comments']['negative']}, neu={cs['comments']['neutral']})",
            f"",
            f"TOP CONTENT",
        ]
        for i, t in enumerate(top["top"][:5], 1):
            lines.append(f"  {i}. {t['text'][:80]} — {t['engagement']} eng ({t['sentiment']})")
        content = "\n".join(lines)
        return StreamingResponse(
            io.BytesIO(content.encode()),
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="strendz-report-{datetime.utcnow().strftime("%Y%m%d")}.txt"'},
        )


# ── Instagram OAuth Flow ──────────────────────────────────────────────────

# Facebook App credentials (set via env vars or defaults for local dev)
FB_APP_ID = os.environ.get("FB_APP_ID", "1688322715662146")
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")
REDIRECT_URI = os.environ.get("OAUTH_REDIRECT_URI", "http://localhost:8000/auth/instagram/callback")

# SSL context for API calls
_oauth_ssl = ssl.create_default_context()
try:
    import certifi
    _oauth_ssl.load_verify_locations(certifi.where())
except ImportError:
    _oauth_ssl.check_hostname = False
    _oauth_ssl.verify_mode = ssl.CERT_NONE


@app.get("/auth/instagram/start")
async def instagram_oauth_start():
    """Redirect user to Facebook Login dialog with Instagram permissions."""
    scopes = ",".join([
        "instagram_basic",
        "instagram_manage_comments",
        "pages_show_list",
        "pages_read_engagement",
        "pages_manage_metadata",
        "business_management",
    ])
    oauth_url = (
        f"https://www.facebook.com/v21.0/dialog/oauth"
        f"?client_id={FB_APP_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope={scopes}"
        f"&response_type=code"
    )
    return RedirectResponse(url=oauth_url)


@app.get("/auth/instagram/callback")
async def instagram_oauth_callback(code: str = Query(None), error: str = Query(None)):
    """Handle Facebook OAuth callback — exchange code for tokens and connect Instagram."""
    if error or not code:
        return HTMLResponse(f"""
        <html><body style="font-family:system-ui;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh">
        <div style="text-align:center">
            <h2 style="color:#f87171">Login Failed</h2>
            <p>{error or 'No authorization code received'}</p>
            <p style="color:#888;margin-top:20px">Close this tab and try again.</p>
        </div></body></html>
        """, status_code=400)

    try:
        # Step 1: Exchange code for short-lived user token
        token_url = (
            f"https://graph.facebook.com/v21.0/oauth/access_token"
            f"?client_id={FB_APP_ID}"
            f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
            f"&client_secret={FB_APP_SECRET}"
            f"&code={urllib.parse.quote(code)}"
        )
        req = urllib.request.Request(token_url)
        with urllib.request.urlopen(req, timeout=10, context=_oauth_ssl) as resp:
            token_data = json.loads(resp.read())

        short_token = token_data.get("access_token")
        if not short_token:
            raise ValueError("No access token in response")

        # Step 2: Exchange for long-lived token (60 days)
        ll_url = (
            f"https://graph.facebook.com/v21.0/oauth/access_token"
            f"?grant_type=fb_exchange_token"
            f"&client_id={FB_APP_ID}"
            f"&client_secret={FB_APP_SECRET}"
            f"&fb_exchange_token={urllib.parse.quote(short_token)}"
        )
        req = urllib.request.Request(ll_url)
        with urllib.request.urlopen(req, timeout=10, context=_oauth_ssl) as resp:
            ll_data = json.loads(resp.read())

        long_token = ll_data.get("access_token", short_token)
        expires_in = ll_data.get("expires_in", 0)

        # Step 3: Get Facebook Pages
        pages_url = (
            f"https://graph.facebook.com/v21.0/me/accounts"
            f"?fields=id,name,access_token,instagram_business_account"
            f"&access_token={urllib.parse.quote(long_token)}"
        )
        req = urllib.request.Request(pages_url)
        with urllib.request.urlopen(req, timeout=10, context=_oauth_ssl) as resp:
            pages_data = json.loads(resp.read())

        page_list = pages_data.get("data", [])

        # Debug: check granted permissions
        granted_perms = []
        try:
            perm_url = f"https://graph.facebook.com/v21.0/me/permissions?access_token={urllib.parse.quote(long_token)}"
            preq = urllib.request.Request(perm_url)
            with urllib.request.urlopen(preq, timeout=10, context=_oauth_ssl) as presp:
                perm_data = json.loads(presp.read())
            granted_perms = [p["permission"] for p in perm_data.get("data", []) if p.get("status") == "granted"]
            print(f"[OAuth Debug] Granted permissions: {granted_perms}")
            print(f"[OAuth Debug] Pages response: {pages_data}")
        except Exception as e:
            print(f"[OAuth Debug] Permission check failed: {e}")

        if not page_list:
            perm_str = ", ".join(granted_perms) if granted_perms else "none detected"
            return HTMLResponse(f"""
            <html><body style="font-family:system-ui;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh">
            <div style="text-align:center;max-width:500px">
                <h2 style="color:#fbbf24">⚠️ No Facebook Pages Found</h2>
                <p>Your account doesn't have any Facebook Pages visible to this app.</p>
                <p style="color:#666;font-size:13px">Granted permissions: {perm_str}</p>
                <p style="color:#888;margin-top:12px">Make sure you:</p>
                <ol style="text-align:left;color:#aaa;line-height:2">
                    <li>Have a Facebook Page (you have "Artist Page")</li>
                    <li>Selected the page during the Facebook login dialog</li>
                    <li>Granted all requested permissions</li>
                    <li>Connected Instagram to the Facebook Page</li>
                </ol>
                <p style="color:#888;margin-top:12px">Try again and make sure to select your page in the permissions dialog.</p>
                <button onclick="window.close()" style="margin-top:20px;padding:10px 30px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px">Close</button>
            </div></body></html>
            """, status_code=200)

        # Step 4: Find the page with an Instagram Business Account
        ig_id = None
        page_token = None
        page_name = None
        for page in page_list:
            ig_acct = page.get("instagram_business_account")
            if ig_acct:
                ig_id = ig_acct["id"]
                page_token = page.get("access_token", long_token)
                page_name = page.get("name", "")
                break

        # Try explicit lookup if not in initial response
        if not ig_id:
            for page in page_list:
                try:
                    purl = (
                        f"https://graph.facebook.com/v21.0/{page['id']}"
                        f"?fields=instagram_business_account"
                        f"&access_token={urllib.parse.quote(page.get('access_token', long_token))}"
                    )
                    preq = urllib.request.Request(purl)
                    with urllib.request.urlopen(preq, timeout=10, context=_oauth_ssl) as presp:
                        pdata = json.loads(presp.read())
                    ig_acct = pdata.get("instagram_business_account")
                    if ig_acct:
                        ig_id = ig_acct["id"]
                        page_token = page.get("access_token", long_token)
                        page_name = page.get("name", "")
                        break
                except Exception:
                    continue

        if not ig_id:
            page_names = ", ".join(p.get("name", p["id"]) for p in page_list)
            return HTMLResponse(f"""
            <html><body style="font-family:system-ui;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh">
            <div style="text-align:center;max-width:500px">
                <h2 style="color:#fbbf24">⚠️ No Instagram Account Linked</h2>
                <p>Found page(s): <strong>{page_names}</strong></p>
                <p>But none have an Instagram Business account linked.</p>
                <p style="color:#888">Link your Instagram in: Instagram → Settings → Professional account → Connect to Facebook Page</p>
                <button onclick="window.close()" style="margin-top:20px;padding:10px 30px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px">Close</button>
            </div></body></html>
            """, status_code=200)

        # Step 5: Get IG profile info
        prof_url = (
            f"https://graph.facebook.com/v21.0/{ig_id}"
            f"?fields=id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url"
            f"&access_token={urllib.parse.quote(page_token)}"
        )
        req = urllib.request.Request(prof_url)
        with urllib.request.urlopen(req, timeout=10, context=_oauth_ssl) as resp:
            ig_profile = json.loads(resp.read())

        username = ig_profile.get("username", "")

        # Step 6: Connect in the SocialConnector
        connector.connections["instagram"] = {
            "access_token": page_token,
            "user_id": ig_id,
            "handle": username,
            "api_type": "fb_graph",
        }
        connector.profile = {
            "name": ig_profile.get("name", username),
            "handle": f"@{username}",
            "followers": ig_profile.get("followers_count", 0),
            "following": ig_profile.get("follows_count", 0),
            "description": ig_profile.get("biography", "")[:200],
            "avatar_url": ig_profile.get("profile_picture_url", ""),
            "platform_source": "instagram",
            "media_count": ig_profile.get("media_count", 0),
        }
        connector.last_fetch = 0
        connector.real_posts = []
        connector._save_credentials()

        followers = ig_profile.get("followers_count", 0)
        days = expires_in // 86400 if expires_in else "?"

        return HTMLResponse(f"""
        <html><body style="font-family:system-ui;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh">
        <div style="text-align:center">
            <h2 style="color:#34d399">✅ Instagram Connected!</h2>
            <p style="font-size:20px;margin:15px 0">@{username}</p>
            <p style="color:#aaa">{followers} followers · Token valid for ~{days} days</p>
            <p style="color:#aaa;margin-top:5px">Via Facebook Page: {page_name}</p>
            <p style="color:#34d399;margin-top:15px">Comments, likes &amp; full data access enabled 🎉</p>
            <script>
                // Notify the dashboard to refresh
                if (window.opener) {{
                    window.opener.postMessage({{ type: 'instagram_connected' }}, '*');
                }}
                setTimeout(() => window.close(), 3000);
            </script>
            <button onclick="window.close()" style="margin-top:20px;padding:10px 30px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px">Close &amp; Return to Dashboard</button>
        </div></body></html>
        """, status_code=200)

    except Exception as e:
        return HTMLResponse(f"""
        <html><body style="font-family:system-ui;background:#111;color:#fff;display:flex;align-items:center;justify-content:center;height:100vh">
        <div style="text-align:center;max-width:500px">
            <h2 style="color:#f87171">❌ Connection Failed</h2>
            <p style="color:#aaa">{str(e)}</p>
            <button onclick="window.close()" style="margin-top:20px;padding:10px 30px;background:#7c3aed;color:#fff;border:none;border-radius:8px;cursor:pointer;font-size:16px">Close</button>
        </div></body></html>
        """, status_code=500)
