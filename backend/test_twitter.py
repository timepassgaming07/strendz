"""Quick test script to debug Twitter API calls."""
import urllib.request
import urllib.error
import urllib.parse
import json
import ssl

_ssl_ctx = ssl.create_default_context()
try:
    import certifi
    _ssl_ctx.load_verify_locations(certifi.where())
except ImportError:
    _ssl_ctx.check_hostname = False
    _ssl_ctx.verify_mode = ssl.CERT_NONE

# Read bearer token from the running server's connection
# We'll just test the API directly
import sys

if len(sys.argv) < 3:
    print("Usage: python test_twitter.py <bearer_token> <handle>")
    sys.exit(1)

bearer = sys.argv[1]
handle = sys.argv[2].lstrip("@")

print(f"Testing with handle: @{handle}")
print(f"Bearer token: {bearer[:10]}...{bearer[-5:]}")
print()

# Test 1: User lookup
print("=== Test 1: User Lookup ===")
try:
    url = f"https://api.twitter.com/2/users/by/username/{urllib.parse.quote(handle)}"
    url += "?user.fields=public_metrics,description,profile_image_url"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
    with urllib.request.urlopen(req, timeout=10, context=_ssl_ctx) as resp:
        data = json.loads(resp.read())
    print(json.dumps(data, indent=2))
    user_id = data.get("data", {}).get("id")
    print(f"\nUser ID: {user_id}")
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else ""
    print(f"HTTP Error {e.code}: {e.reason}")
    print(f"Body: {body}")
    user_id = None
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    user_id = None

# Test 2: User's own tweets
print("\n=== Test 2: User's Own Tweets ===")
if user_id:
    try:
        url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=5&tweet.fields=created_at,public_metrics,author_id"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
        with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
            data = json.loads(resp.read())
        print(f"Got {len(data.get('data', []))} tweets")
        for t in data.get("data", [])[:3]:
            print(f"  - [{t.get('id')}] {t['text'][:80]}...")
            print(f"    Likes: {t.get('public_metrics', {}).get('like_count', 0)}")
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Body: {body}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
else:
    print("Skipped (no user_id)")

# Test 3: Mention search
print("\n=== Test 3: Mention Search ===")
try:
    query = urllib.parse.quote(f"@{handle} OR #{handle} -is:retweet")
    url = f"https://api.twitter.com/2/tweets/search/recent?query={query}&max_results=10&tweet.fields=created_at,public_metrics,author_id"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {bearer}"})
    with urllib.request.urlopen(req, timeout=15, context=_ssl_ctx) as resp:
        data = json.loads(resp.read())
    tweets = data.get("data", [])
    print(f"Got {len(tweets)} mention tweets")
    for t in tweets[:3]:
        print(f"  - [{t.get('id')}] {t['text'][:80]}...")
except urllib.error.HTTPError as e:
    body = e.read().decode() if e.fp else ""
    print(f"HTTP Error {e.code}: {e.reason}")
    print(f"Body: {body}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
