"""
Social Radar AI — Real Social Media Connector
Fetches real posts from Twitter/X, Instagram, and LinkedIn APIs.
"""

import urllib.request
import urllib.error
import urllib.parse
import json
import ssl
import time
import random
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from app.sentiment import analyze_sentiment

# Create an SSL context that works on macOS
_ssl_ctx = ssl.create_default_context()
try:
    import certifi
    _ssl_ctx.load_verify_locations(certifi.where())
except ImportError:
    # If certifi is not installed, allow unverified for development
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE


class SocialConnector:
    """Manages API connections and fetches real social media data."""

    CREDS_FILE = Path(__file__).parent.parent / ".social_credentials.json"

    def __init__(self):
        self.connections: dict[str, dict] = {}
        self.real_posts: list[dict] = []
        self.profile: dict = {}
        self.last_fetch: float = 0
        self.fetch_interval = 60  # seconds between API calls
        self._load_credentials()

    # ── Persistence ───────────────────────────────────────────────────────

    def _save_credentials(self):
        """Save current connections and profile to disk."""
        try:
            data = {
                "connections": self.connections,
                "profile": self.profile,
            }
            self.CREDS_FILE.write_text(json.dumps(data, indent=2))
        except Exception as e:
            print(f"[SocialConnector] Failed to save credentials: {e}")

    def _load_credentials(self):
        """Load saved credentials from disk and reconnect."""
        if not self.CREDS_FILE.exists():
            return
        try:
            data = json.loads(self.CREDS_FILE.read_text())
            saved_conns = data.get("connections", {})
            saved_profile = data.get("profile", {})
            if not saved_conns:
                return

            # Restore connections and profile directly
            self.connections = saved_conns
            self.profile = saved_profile
            print(f"[SocialConnector] Restored connections: {list(saved_conns.keys())}")

            # Validate Instagram token is still working
            if "instagram" in self.connections:
                cfg = self.connections["instagram"]
                token = cfg.get("access_token", "")
                if token:
                    try:
                        base = self._ig_api_base(cfg)
                        owner = self._ig_media_owner(cfg)
                        url = f"{base}/v21.0/{owner}?fields=id&access_token={urllib.parse.quote(token)}"
                        req = urllib.request.Request(url)
                        with urllib.request.urlopen(req, timeout=5, context=_ssl_ctx) as resp:
                            json.loads(resp.read())
                        print("[SocialConnector] Instagram token still valid")
                    except Exception:
                        print("[SocialConnector] Instagram token expired, removing")
                        self.connections.pop("instagram", None)
                        if self.profile.get("platform_source") == "instagram":
                            self.profile = {}
                        self._save_credentials()

        except Exception as e:
            print(f"[SocialConnector] Failed to load credentials: {e}")

    # ── Connection Management ─────────────────────────────────────────────

    def connect(self, platform: str, credentials: dict) -> dict:
        """Store credentials for a platform and validate them."""
        platform = platform.lower()

        if platform == "twitter":
            result = self._connect_twitter(credentials)
        elif platform == "instagram":
            result = self._connect_instagram(credentials)
        elif platform == "linkedin":
            result = self._connect_linkedin(credentials)
        elif platform == "reddit":
            result = self._connect_reddit(credentials)
        elif platform == "reddit_user":
            result = self._connect_reddit_user(credentials)
        else:
            return {"ok": False, "error": f"Unknown platform: {platform}"}

        if result.get("ok"):
            self._save_credentials()
        return result

    def disconnect(self, platform: str):
        """Remove credentials for a platform."""
        key = platform.lower()
        # reddit_user connections are stored under "reddit" key
        if key == "reddit_user":
            key = "reddit"
        self.connections.pop(key, None)
        if not self.connections:
            self.profile = {}
            self.real_posts = []
            self.last_fetch = 0
        self._save_credentials()

    def get_status(self) -> dict:
        """Return connection status for all platforms."""
        return {
            "connected": list(self.connections.keys()),
            "profile": self.profile,
            "total_real_posts": len(self.real_posts),
            "platforms": {
                p: {
                    "handle": c.get("handle", ""),
                    "connected": True,
                }
                for p, c in self.connections.items()
            },
        }

    # ── Twitter / X ───────────────────────────────────────────────────────

    def _connect_twitter(self, creds: dict) -> dict:
        bearer = creds.get("bearer_token", "").strip()
        handle = creds.get("handle", "").strip().lstrip("@")

        if not bearer or not handle:
            return {"ok": False, "error": "Bearer token and handle are required"}

        # Use ONE search call to get tweets + profile in a single request
        # This is the most efficient approach for free-tier rate limits
        user_data: dict = {}
        user_id = None
        tweet_count = 0

        try:
            query = urllib.parse.quote(f"from:{handle}")
            url = (
                f"https://api.twitter.com/2/tweets/search/recent?query={query}"
                f"&max_results=10"
                f"&tweet.fields=created_at,public_metrics,author_id"
                f"&expansions=author_id"
                f"&user.fields=public_metrics,description,profile_image_url,username,name"
            )
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())

            tweet_count = len(data.get("data", []))

            # Extract profile from expansions
            for u in data.get("includes", {}).get("users", []):
                if u.get("username", "").lower() == handle.lower():
                    user_data = u
                    user_id = u.get("id")
                    break

            # If no user in includes, get author_id from tweets
            if not user_id:
                for t in data.get("data", []):
                    if t.get("author_id"):
                        user_id = t["author_id"]
                        break

            # Cache the tweets immediately so we don't need another API call
            if data.get("data"):
                posts = []
                for tweet in data["data"]:
                    metrics = tweet.get("public_metrics", {})
                    post = {
                        "id": tweet["id"],
                        "text": tweet["text"],
                        "platform": "twitter",
                        "timestamp": tweet.get("created_at", datetime.utcnow().isoformat()),
                        "engagement": {
                            "likes": metrics.get("like_count", 0),
                            "shares": metrics.get("retweet_count", 0),
                            "comments": metrics.get("reply_count", 0),
                        },
                        "author": f"@{handle}",
                        "real": True,
                    }
                    post["sentiment"] = analyze_sentiment(post["text"])
                    posts.append(post)
                self.real_posts = posts
                self.last_fetch = time.time()

        except urllib.error.HTTPError as e:
            if e.code in (402, 429):
                # Rate limited or plan doesn't include read access — store connection anyway
                pass
            elif e.code in (401, 403):
                return {"ok": False, "error": f"Auth error ({e.code}): check your Bearer Token"}
            else:
                return {"ok": False, "error": f"Twitter API error: {e.code} {e.reason}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

        # Store connection
        self.connections["twitter"] = {
            "bearer_token": bearer,
            "handle": handle,
            "user_id": user_id,
        }

        # Build profile
        self.profile.update({
            "name": user_data.get("name") or handle,
            "handle": f"@{handle}",
            "followers": user_data.get("public_metrics", {}).get("followers_count", 0),
            "following": user_data.get("public_metrics", {}).get("following_count", 0),
            "description": user_data.get("description", ""),
            "avatar_url": user_data.get("profile_image_url", ""),
            "platform_source": "twitter",
        })

        msg = f"Connected to @{handle}"
        if tweet_count > 0:
            msg += f" — found {tweet_count} real tweets"
        elif not user_id:
            msg += " (rate-limited — real data will load in ~15 min)"

        return {"ok": True, "message": msg, "profile": self.profile}

    def _twitter_get_user(self, bearer: str, handle: str) -> dict:
        url = f"https://api.twitter.com/2/users/by/username/{urllib.parse.quote(handle)}"
        url += "?user.fields=public_metrics,description,profile_image_url"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
        with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
            data = json.loads(resp.read())
        if "data" not in data:
            errors = data.get("errors", [{}])
            raise ValueError(errors[0].get("detail", "User not found"))
        return data["data"]

    def _refresh_twitter_profile(self):
        """Re-fetch Twitter profile data (followers, avatar, etc.)."""
        cfg = self.connections.get("twitter")
        if not cfg:
            return
        # Skip if we already have full profile data
        if self.profile.get("followers") and self.profile.get("avatar_url"):
            return

        bearer = cfg["bearer_token"]
        handle = cfg["handle"]

        # Try direct user lookup first
        try:
            user = self._twitter_get_user(bearer, handle)
            cfg["user_id"] = user.get("id")
            self.profile.update({
                "name": user.get("name", handle),
                "handle": f"@{handle}",
                "followers": user.get("public_metrics", {}).get("followers_count", 0),
                "following": user.get("public_metrics", {}).get("following_count", 0),
                "description": user.get("description", ""),
                "avatar_url": user.get("profile_image_url", ""),
                "platform_source": "twitter",
            })
            return
        except Exception as e:
            print(f"[SocialConnector] _refresh profile direct lookup: {e}")

        # Fallback: get profile from search expansions
        try:
            query = urllib.parse.quote(f"from:{handle}")
            url = (
                f"https://api.twitter.com/2/tweets/search/recent?query={query}"
                f"&max_results=10&expansions=author_id&user.fields=public_metrics,description,profile_image_url"
            )
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            for u in data.get("includes", {}).get("users", []):
                if u.get("username", "").lower() == handle.lower():
                    cfg["user_id"] = u.get("id")
                    self.profile.update({
                        "name": u.get("name", handle),
                        "handle": f"@{handle}",
                        "followers": u.get("public_metrics", {}).get("followers_count", 0),
                        "following": u.get("public_metrics", {}).get("following_count", 0),
                        "description": u.get("description", ""),
                        "avatar_url": u.get("profile_image_url", ""),
                        "platform_source": "twitter",
                    })
                    return
        except Exception as e:
            print(f"[SocialConnector] _refresh profile search fallback: {e}")

    def _fetch_twitter(self) -> list[dict]:
        cfg = self.connections.get("twitter")
        if not cfg:
            return []

        bearer = cfg["bearer_token"]
        handle = cfg["handle"]
        user_id = cfg.get("user_id")
        all_posts: list[dict] = []

        # 1) Fetch the user's own tweets (timeline)
        if user_id:
            try:
                url = (
                    f"https://api.twitter.com/2/users/{user_id}/tweets"
                    f"?max_results=50"
                    f"&tweet.fields=created_at,public_metrics,author_id"
                )
                req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
                with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                    data = json.loads(resp.read())
                for tweet in data.get("data", []):
                    metrics = tweet.get("public_metrics", {})
                    post = {
                        "id": tweet["id"],
                        "text": tweet["text"],
                        "platform": "twitter",
                        "timestamp": tweet.get("created_at", datetime.utcnow().isoformat()),
                        "engagement": {
                            "likes": metrics.get("like_count", 0),
                            "shares": metrics.get("retweet_count", 0),
                            "comments": metrics.get("reply_count", 0),
                        },
                        "author": f"@{handle}",
                        "real": True,
                    }
                    post["sentiment"] = analyze_sentiment(post["text"])
                    all_posts.append(post)
            except Exception as e:
                print(f"[SocialConnector] _fetch_twitter own tweets error: {type(e).__name__}: {e}")

        # 2) Also fetch mentions/searches about the handle
        try:
            query = urllib.parse.quote(f"@{handle} OR #{handle} -is:retweet")
            url = (
                f"https://api.twitter.com/2/tweets/search/recent?query={query}"
                f"&max_results=50"
                f"&tweet.fields=created_at,public_metrics,author_id"
                f"&expansions=author_id"
                f"&user.fields=username,name"
            )
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())

            authors = {}
            for user in data.get("includes", {}).get("users", []):
                authors[user["id"]] = user.get("username", "unknown")

            seen_ids = {p["id"] for p in all_posts}
            for tweet in data.get("data", []):
                if tweet["id"] in seen_ids:
                    continue
                metrics = tweet.get("public_metrics", {})
                post = {
                    "id": tweet["id"],
                    "text": tweet["text"],
                    "platform": "twitter",
                    "timestamp": tweet.get("created_at", datetime.utcnow().isoformat()),
                    "engagement": {
                        "likes": metrics.get("like_count", 0),
                        "shares": metrics.get("retweet_count", 0),
                        "comments": metrics.get("reply_count", 0),
                    },
                    "author": authors.get(tweet.get("author_id"), "unknown"),
                    "real": True,
                }
                post["sentiment"] = analyze_sentiment(post["text"])
                all_posts.append(post)
        except Exception as e:
            print(f"[SocialConnector] _fetch_twitter mentions error: {type(e).__name__}: {e}")

        return all_posts

    # ── Instagram ─────────────────────────────────────────────────────────

    def _connect_instagram(self, creds: dict) -> dict:
        access_token = creds.get("access_token", "").strip()
        if not access_token:
            return {"ok": False, "error": "Instagram access token is required"}

        app_id = creds.get("app_id", "").strip()
        app_secret = creds.get("app_secret", "").strip()

        # Detect token type: Facebook (EAA…) vs Instagram Login (IGAA…)
        is_fb_token = access_token.startswith("EAA")

        if is_fb_token:
            return self._connect_instagram_fb(access_token, app_id, app_secret)
        else:
            return self._connect_instagram_ig(access_token, app_secret)

    def _connect_instagram_ig(self, access_token: str, app_secret: str) -> dict:
        """Connect using Instagram Login API token (graph.instagram.com)."""
        # Try to exchange for a long-lived token (60 days) if app_secret provided
        if app_secret:
            access_token = self._exchange_ig_token(access_token, app_secret) or access_token

        try:
            url = (
                f"https://graph.instagram.com/v21.0/me"
                f"?fields=id,username,media_count,account_type,followers_count,follows_count,biography,profile_picture_url"
                f"&access_token={urllib.parse.quote(access_token)}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                user = json.loads(resp.read())

            if "error" in user:
                raise ValueError(user["error"].get("message", "Invalid token"))

            username = user.get("username", "")
            self.connections["instagram"] = {
                "access_token": access_token,
                "user_id": user.get("id"),
                "handle": username,
                "api_type": "ig_login",  # Instagram Login API
            }

            self.profile = {
                "name": username,
                "handle": f"@{username}",
                "followers": user.get("followers_count", 0),
                "following": user.get("follows_count", 0),
                "description": user.get("biography", "")[:200],
                "avatar_url": user.get("profile_picture_url", ""),
                "platform_source": "instagram",
                "media_count": user.get("media_count", 0),
            }

            self.last_fetch = 0
            self.real_posts = []

            return {
                "ok": True,
                "message": f"Connected to Instagram @{username} ({user.get('followers_count', 0)} followers)",
                "profile": self.profile,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _connect_instagram_fb(self, access_token: str, app_id: str, app_secret: str) -> dict:
        """Connect using Facebook Login token (graph.facebook.com → IG Business Account)."""
        # Exchange for long-lived FB token (60 days) if possible
        if app_id and app_secret:
            ll = self._exchange_fb_token(access_token, app_id, app_secret)
            if ll:
                access_token = ll

        try:
            # Find Facebook Pages
            url = (
                f"https://graph.facebook.com/v21.0/me/accounts"
                f"?fields=id,name,access_token,instagram_business_account"
                f"&access_token={urllib.parse.quote(access_token)}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                pages = json.loads(resp.read())

            page_data = pages.get("data", [])
            if not page_data:
                return {
                    "ok": False,
                    "error": (
                        "No Facebook Pages found. To use a Facebook token for Instagram, you need: "
                        "(1) A Facebook Page linked to your Instagram account, "
                        "(2) 'instagram_basic' permission in your Facebook Login. "
                        "Go to Instagram Settings → Professional account → Connect to a Facebook Page."
                    ),
                }

            # Find Page with linked IG Business Account
            ig_id = None
            page_token = access_token
            for page in page_data:
                ig_acct = page.get("instagram_business_account")
                if ig_acct:
                    ig_id = ig_acct["id"]
                    page_token = page.get("access_token", access_token)
                    break

            if not ig_id:
                # Try fetching explicitly for each page
                for page in page_data:
                    try:
                        purl = (
                            f"https://graph.facebook.com/v21.0/{page['id']}"
                            f"?fields=instagram_business_account"
                            f"&access_token={urllib.parse.quote(page.get('access_token', access_token))}"
                        )
                        preq = urllib.request.Request(purl)
                        with urllib.request.urlopen(preq, timeout=10, context=_ssl_ctx) as presp:
                            pdata = json.loads(presp.read())
                        ig_acct = pdata.get("instagram_business_account")
                        if ig_acct:
                            ig_id = ig_acct["id"]
                            page_token = page.get("access_token", access_token)
                            break
                    except Exception:
                        continue

            if not ig_id:
                return {
                    "ok": False,
                    "error": (
                        "Found Facebook Page(s) but none have a linked Instagram Business account. "
                        "Link your Instagram to your Facebook Page in Instagram Settings → Professional account."
                    ),
                }

            # Fetch IG Business Account profile
            prof_url = (
                f"https://graph.facebook.com/v21.0/{ig_id}"
                f"?fields=id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url"
                f"&access_token={urllib.parse.quote(page_token)}"
            )
            req = urllib.request.Request(prof_url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                user = json.loads(resp.read())

            username = user.get("username", "")
            self.connections["instagram"] = {
                "access_token": page_token,
                "user_id": ig_id,
                "handle": username,
                "api_type": "fb_graph",  # Facebook Graph API
            }

            self.profile = {
                "name": user.get("name", username),
                "handle": f"@{username}",
                "followers": user.get("followers_count", 0),
                "following": user.get("follows_count", 0),
                "description": user.get("biography", "")[:200],
                "avatar_url": user.get("profile_picture_url", ""),
                "platform_source": "instagram",
                "media_count": user.get("media_count", 0),
            }

            self.last_fetch = 0
            self.real_posts = []

            return {
                "ok": True,
                "message": f"Connected to Instagram @{username} via Facebook ({user.get('followers_count', 0)} followers)",
                "profile": self.profile,
            }
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _exchange_ig_token(self, short_token: str, app_secret: str) -> Optional[str]:
        """Exchange a short-lived IG Login token for a long-lived one (60 days)."""
        try:
            url = (
                f"https://graph.instagram.com/access_token"
                f"?grant_type=ig_exchange_token"
                f"&client_secret={urllib.parse.quote(app_secret)}"
                f"&access_token={urllib.parse.quote(short_token)}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            long_token = data.get("access_token")
            if long_token:
                print(f"[SocialConnector] Exchanged IG token for long-lived (expires in {data.get('expires_in', '?')}s)")
                return long_token
        except Exception as e:
            print(f"[SocialConnector] IG token exchange failed (using short-lived): {e}")
        return None

    def _exchange_fb_token(self, short_token: str, app_id: str, app_secret: str) -> Optional[str]:
        """Exchange a short-lived FB token for a long-lived one (60 days)."""
        try:
            url = (
                f"https://graph.facebook.com/v21.0/oauth/access_token"
                f"?grant_type=fb_exchange_token"
                f"&client_id={urllib.parse.quote(app_id)}"
                f"&client_secret={urllib.parse.quote(app_secret)}"
                f"&fb_exchange_token={urllib.parse.quote(short_token)}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            long_token = data.get("access_token")
            if long_token:
                print(f"[SocialConnector] Exchanged FB token for long-lived (expires in {data.get('expires_in', '?')}s)")
                return long_token
        except Exception as e:
            print(f"[SocialConnector] FB token exchange failed (using short-lived): {e}")
        return None

    def _ig_api_base(self, cfg: dict) -> str:
        """Return the correct API base URL depending on token type."""
        return "https://graph.facebook.com" if cfg.get("api_type") == "fb_graph" else "https://graph.instagram.com"

    def _ig_media_owner(self, cfg: dict) -> str:
        """Return the media owner ID (for FB Graph) or 'me' (for IG Login)."""
        return cfg["user_id"] if cfg.get("api_type") == "fb_graph" else "me"

    def _refresh_ig_profile(self, token: str) -> None:
        """Re-fetch Instagram profile data (followers, following, etc.)."""
        cfg = self.connections.get("instagram", {})
        base = self._ig_api_base(cfg)
        owner = self._ig_media_owner(cfg)
        try:
            url = (
                f"{base}/v21.0/{owner}"
                f"?fields=followers_count,follows_count,media_count,biography,profile_picture_url"
                f"&access_token={urllib.parse.quote(token)}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                user = json.loads(resp.read())
            self.profile.update({
                "followers": user.get("followers_count", self.profile.get("followers", 0)),
                "following": user.get("follows_count", self.profile.get("following", 0)),
                "description": user.get("biography", self.profile.get("description", ""))[:200],
                "avatar_url": user.get("profile_picture_url", self.profile.get("avatar_url", "")),
                "media_count": user.get("media_count", self.profile.get("media_count", 0)),
            })
        except Exception as e:
            print(f"[SocialConnector] _refresh_ig_profile error: {e}")

    def _fetch_instagram(self) -> list[dict]:
        cfg = self.connections.get("instagram")
        if not cfg:
            return []

        token = cfg["access_token"]
        base = self._ig_api_base(cfg)
        owner = self._ig_media_owner(cfg)

        # Refresh profile (followers/following) on every fetch
        self._refresh_ig_profile(token)

        url = (
            f"{base}/v21.0/{owner}/media"
            f"?fields=id,caption,timestamp,like_count,comments_count,media_type,permalink,media_url"
            f"&limit=50"
            f"&access_token={urllib.parse.quote(token)}"
        )
        req = urllib.request.Request(url)

        try:
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f"[SocialConnector] _fetch_instagram error: {e}")
            return []

        posts = []
        for item in data.get("data", []):
            caption = item.get("caption", "")
            media_type = item.get("media_type", "POST")
            # Use caption if available, otherwise describe the media type
            text = caption if caption else f"[{media_type.replace('_', ' ').title()} post]"
            post = {
                "id": f"ig_{item['id']}",
                "text": text,
                "platform": "instagram",
                "timestamp": item.get("timestamp", datetime.utcnow().isoformat()),
                "engagement": {
                    "likes": item.get("like_count", 0),
                    "shares": 0,
                    "comments": item.get("comments_count", 0),
                },
                "author": f"@{cfg.get('handle', 'instagram_user')}",
                "real": True,
                "permalink": item.get("permalink", ""),
                "media_type": media_type,
            }
            posts.append(post)

        # Fetch comments for each post and use them for better sentiment
        all_results = list(posts)  # posts will be in results
        for post in posts:
            comments = self._fetch_ig_comments(
                post["id"].replace("ig_", ""), token, cfg
            )
            post["top_comments"] = comments

            # Build combined text from caption + all comments for post sentiment
            all_text_parts = []
            if post["text"] and not post["text"].startswith("["):
                all_text_parts.append(post["text"])
            for c in comments:
                if c.get("body"):
                    all_text_parts.append(c["body"])
            combined_text = " ".join(all_text_parts) if all_text_parts else post["text"]
            post["sentiment"] = analyze_sentiment(combined_text)

            # Also add each comment as a separate data point for richer timeline/graphs
            for c in comments:
                if not c.get("body"):
                    continue
                comment_post = {
                    "id": f"ig_comment_{post['id']}_{c.get('author', '')}",
                    "text": c["body"],
                    "platform": "instagram",
                    "timestamp": c.get("timestamp", post["timestamp"]),
                    "engagement": {
                        "likes": c.get("ups", 0),
                        "shares": 0,
                        "comments": 0,
                    },
                    "author": f"@{c.get('author', 'unknown')}",
                    "real": True,
                    "permalink": post.get("permalink", ""),
                    "media_type": "COMMENT",
                    "sentiment": analyze_sentiment(c["body"]),
                }
                all_results.append(comment_post)

        return all_results

    def _fetch_ig_comments(self, media_id: str, token: str, cfg: dict | None = None) -> list[dict]:
        """Fetch comments on an Instagram media item."""
        if cfg is None:
            cfg = self.connections.get("instagram", {})
        base = self._ig_api_base(cfg)
        try:
            url = (
                f"{base}/v21.0/{media_id}/comments"
                f"?fields=id,text,timestamp,username,like_count"
                f"&limit=10"
                f"&access_token={urllib.parse.quote(token)}"
            )
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            comments = []
            for c in data.get("data", []):
                comments.append({
                    "author": c.get("username", ""),
                    "body": c.get("text", ""),
                    "ups": c.get("like_count", 0),
                    "timestamp": c.get("timestamp", ""),
                })
            return comments
        except Exception as e:
            print(f"[SocialConnector] _fetch_ig_comments error for {media_id}: {e}")
            return []

    # ── LinkedIn ──────────────────────────────────────────────────────────

    def _connect_linkedin(self, creds: dict) -> dict:
        access_token = creds.get("access_token", "").strip()
        if not access_token:
            return {"ok": False, "error": "LinkedIn access token is required"}

        try:
            url = "https://api.linkedin.com/v2/me"
            req = urllib.request.Request(url, headers={
                "Authorization": f"Bearer {access_token}",
            })
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                user = json.loads(resp.read())

            first = user.get("localizedFirstName", "")
            last = user.get("localizedLastName", "")
            self.connections["linkedin"] = {
                "access_token": access_token,
                "handle": f"{first} {last}".strip(),
                "user_id": user.get("id"),
            }
            return {"ok": True, "message": f"Connected to LinkedIn ({first} {last})"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _fetch_linkedin(self) -> list[dict]:
        # LinkedIn API is very restricted — organization posts require special access
        return []

    # ── Reddit ────────────────────────────────────────────────────────────

    def _connect_reddit(self, creds: dict) -> dict:
        subreddit = creds.get("subreddit", "").strip().lstrip("r/")
        if not subreddit:
            return {"ok": False, "error": "Subreddit name is required (e.g. technology)"}

        # Try the name as-is first, then without spaces
        candidates = [subreddit]
        if " " in subreddit:
            candidates.append(subreddit.replace(" ", ""))
            candidates.append(subreddit.replace(" ", "_"))

        info = None
        used_name = subreddit
        for candidate in candidates:
            try:
                url = f"https://www.reddit.com/r/{urllib.parse.quote(candidate)}/about.json"
                req = urllib.request.Request(url, headers={
                    "User-Agent": "SocialRadar/1.0",
                })
                with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                    data = json.loads(resp.read())
                check = data.get("data", {})
                if check.get("display_name"):
                    info = check
                    used_name = candidate
                    break
            except Exception:
                continue

        if not info:
            return {"ok": False, "error": f"Subreddit not found. Try without spaces, e.g. 'GooglePixel' instead of 'google pixel'"}

        self.connections["reddit"] = {
            "subreddit": used_name,
            "display_name": info.get("display_name_prefixed", f"r/{used_name}"),
        }

        # Always update profile when connecting Reddit
        icon = info.get("icon_img", "") or info.get("community_icon", "")
        icon = icon.split("?")[0] if icon else ""
        self.profile = {
            "name": info.get("title") or info.get("display_name", used_name),
            "handle": info.get("display_name_prefixed", f"r/{used_name}"),
            "followers": info.get("subscribers", 0),
            "following": info.get("accounts_active", 0),
            "description": info.get("public_description", "")[:200],
            "avatar_url": icon,
            "platform_source": "reddit",
        }

        # Reset cache so fresh data is fetched immediately
        self.last_fetch = 0
        self.real_posts = []

        return {
            "ok": True,
            "message": f"Connected to r/{used_name} ({info.get('subscribers', 0):,} members)",
            "profile": self.profile,
        }

    def _fetch_reddit(self) -> list[dict]:
        cfg = self.connections.get("reddit")
        if not cfg or cfg.get("type") == "user":
            return []

        subreddit = cfg["subreddit"]
        url = f"https://www.reddit.com/r/{urllib.parse.quote(subreddit)}/hot.json?limit=50"
        req = urllib.request.Request(url, headers={
            "User-Agent": "SocialRadar/1.0",
        })

        try:
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
        except Exception as e:
            print(f"[SocialConnector] _fetch_reddit error: {e}")
            return []

        posts = []
        for child in data.get("data", {}).get("children", []):
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
                "timestamp": datetime.utcfromtimestamp(item.get("created_utc", time.time())).isoformat(),
                "engagement": {
                    "likes": item.get("ups", 0),
                    "shares": item.get("crossposts", 0) if isinstance(item.get("crossposts"), int) else 0,
                    "comments": item.get("num_comments", 0),
                },
                "author": item.get("author", "[deleted]"),
                "real": True,
                "permalink": item.get("permalink", ""),
                "url": item.get("url", ""),
                "flair": item.get("link_flair_text", ""),
            }
            post["sentiment"] = analyze_sentiment(post["text"])
            posts.append(post)

        # Fetch top comments for the top 10 posts
        for post in posts[:10]:
            post["top_comments"] = self._fetch_reddit_comments(post.get("permalink", ""))

        return posts

    def _connect_reddit_user(self, creds: dict) -> dict:
        """Connect to a Reddit user profile (no auth needed)."""
        username = creds.get("username", "").strip().lstrip("u/").lstrip("/")
        if not username:
            return {"ok": False, "error": "Reddit username is required"}

        try:
            url = f"https://www.reddit.com/user/{urllib.parse.quote(username)}/about.json"
            req = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            info = data.get("data", {})
            if not info.get("name"):
                return {"ok": False, "error": f"Reddit user u/{username} not found"}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return {"ok": False, "error": f"Reddit user u/{username} not found"}
            return {"ok": False, "error": f"Error fetching user: {e.code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

        self.connections["reddit"] = {
            "type": "user",
            "username": info.get("name", username),
        }

        avatar = info.get("icon_img", "") or info.get("snoovatar_img", "")
        avatar = avatar.split("?")[0] if avatar else ""

        self.profile = {
            "name": info.get("subreddit", {}).get("title") or info.get("name", username),
            "handle": f"u/{info.get('name', username)}",
            "followers": info.get("subreddit", {}).get("subscribers", 0),
            "following": 0,
            "description": info.get("subreddit", {}).get("public_description", "")[:200],
            "avatar_url": avatar,
            "platform_source": "reddit",
            "karma": info.get("link_karma", 0) + info.get("comment_karma", 0),
            "link_karma": info.get("link_karma", 0),
            "comment_karma": info.get("comment_karma", 0),
        }

        self.last_fetch = 0
        self.real_posts = []

        return {
            "ok": True,
            "message": f"Connected to u/{info.get('name', username)} ({self.profile['karma']:,} karma)",
            "profile": self.profile,
        }

    def _fetch_reddit_user_posts(self) -> list[dict]:
        """Fetch posts and comments from a Reddit user."""
        cfg = self.connections.get("reddit")
        if not cfg or cfg.get("type") != "user":
            return []

        username = cfg["username"]
        posts = []

        # Fetch user's posts (submitted)
        try:
            url = f"https://www.reddit.com/user/{urllib.parse.quote(username)}/submitted.json?limit=25&sort=new"
            req = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            for child in data.get("data", {}).get("children", []):
                item = child.get("data", {})
                text = item.get("title", "")
                selftext = item.get("selftext", "")
                if selftext:
                    text += "\n" + selftext[:300]
                post = {
                    "id": f"reddit_{item.get('id', '')}",
                    "text": text,
                    "platform": "reddit",
                    "timestamp": datetime.utcfromtimestamp(item.get("created_utc", time.time())).isoformat(),
                    "engagement": {
                        "likes": item.get("ups", 0),
                        "shares": 0,
                        "comments": item.get("num_comments", 0),
                    },
                    "author": f"u/{username}",
                    "real": True,
                    "permalink": item.get("permalink", ""),
                    "flair": item.get("link_flair_text", ""),
                    "subreddit": item.get("subreddit_name_prefixed", ""),
                }
                post["sentiment"] = analyze_sentiment(post["text"])
                posts.append(post)
        except Exception as e:
            print(f"[SocialConnector] _fetch_reddit_user posts error: {e}")

        # Fetch user's comments
        try:
            url = f"https://www.reddit.com/user/{urllib.parse.quote(username)}/comments.json?limit=25&sort=new"
            req = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            for child in data.get("data", {}).get("children", []):
                item = child.get("data", {})
                body = item.get("body", "")
                if not body:
                    continue
                post = {
                    "id": f"reddit_c_{item.get('id', '')}",
                    "text": body[:400],
                    "platform": "reddit",
                    "timestamp": datetime.utcfromtimestamp(item.get("created_utc", time.time())).isoformat(),
                    "engagement": {
                        "likes": item.get("ups", 0),
                        "shares": 0,
                        "comments": 0,
                    },
                    "author": f"u/{username}",
                    "real": True,
                    "is_comment": True,
                    "permalink": item.get("permalink", ""),
                    "subreddit": item.get("subreddit_name_prefixed", ""),
                }
                post["sentiment"] = analyze_sentiment(post["text"])
                posts.append(post)
        except Exception as e:
            print(f"[SocialConnector] _fetch_reddit_user comments error: {e}")

        posts.sort(key=lambda p: p.get("timestamp", ""), reverse=True)
        return posts

    def _fetch_reddit_comments(self, permalink: str) -> list[dict]:
        """Fetch top 5 comments for a Reddit post."""
        if not permalink:
            return []
        try:
            url = f"https://www.reddit.com{permalink}.json?limit=5&depth=1&sort=top"
            req = urllib.request.Request(url, headers={"User-Agent": "SocialRadar/1.0"})
            with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
                data = json.loads(resp.read())
            if len(data) < 2:
                return []
            comments = []
            for child in data[1].get("data", {}).get("children", []):
                c = child.get("data", {})
                body = c.get("body", "")
                if not body or child.get("kind") == "more":
                    continue
                comments.append({
                    "author": c.get("author", "[deleted]"),
                    "body": body[:300],
                    "ups": c.get("ups", 0),
                    "timestamp": datetime.utcfromtimestamp(c.get("created_utc", 0)).isoformat(),
                })
            return comments[:5]
        except Exception:
            return []

    # ── Fetch All ─────────────────────────────────────────────────────────

    def fetch_all(self) -> list[dict]:
        """Fetch posts from all connected platforms."""
        now = time.time()
        # Respect rate limits: shorter cache for Instagram/Reddit, longer for Twitter
        has_twitter = "twitter" in self.connections
        cache_interval = 900 if has_twitter else 30  # 30s for non-twitter
        if now - self.last_fetch < cache_interval and self.real_posts:
            return self.real_posts

        # Refresh profile data if incomplete
        if "twitter" in self.connections and (not self.profile.get("followers") or not self.profile.get("avatar_url")):
            self._refresh_twitter_profile()

        posts: list[dict] = []
        posts.extend(self._fetch_twitter())
        posts.extend(self._fetch_instagram())
        posts.extend(self._fetch_linkedin())
        posts.extend(self._fetch_reddit())
        posts.extend(self._fetch_reddit_user_posts())

        posts.sort(key=lambda p: p.get("timestamp", ""), reverse=True)

        if posts:
            self.real_posts = posts
            self.last_fetch = now

        return self.real_posts

    def is_connected(self) -> bool:
        return len(self.connections) > 0


# Global singleton
connector = SocialConnector()
