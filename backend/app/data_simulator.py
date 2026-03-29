"""
Social Radar AI Dashboard — Data Simulator
Generates realistic simulated social media posts with engagement metrics.
"""

import random
import time
from datetime import datetime, timedelta

PLATFORMS = ["twitter", "instagram", "linkedin"]

POSITIVE_TEXTS = [
    "Absolutely love this product! Best purchase ever 🔥",
    "Customer support was incredibly helpful today!",
    "This new feature is a game changer. Well done team!",
    "Your service exceeded all my expectations. Highly recommend!",
    "Just had the best experience with your app. Smooth and fast!",
    "The new update is fantastic, everything works perfectly now!",
    "Great quality and super fast delivery. Very impressed!",
    "I'm blown away by the design. So clean and modern!",
    "Five stars! Will definitely be coming back for more.",
    "Amazing value for the price. Couldn't be happier!",
    "The team really listens to feedback. Love the improvements!",
    "Seamless checkout experience. Everything just works!",
    "This is exactly what I needed. Thank you so much!",
    "Brilliant innovation. You guys are ahead of the game.",
    "Recommended to all my friends and they love it too!",
]

NEUTRAL_TEXTS = [
    "Just placed an order, waiting for delivery.",
    "Checking out the new update now, will review later.",
    "Does anyone know when the next version releases?",
    "Saw an ad for this product. Looks interesting.",
    "Signed up for the newsletter to stay updated.",
    "Downloaded the app, haven't tried it yet.",
    "The pricing seems standard compared to competitors.",
    "Reading through the FAQ to understand features better.",
    "Anyone else using this for their workflow?",
    "Noticed some changes in the UI. Getting used to it.",
]

NEGATIVE_TEXTS = [
    "Really disappointed with the delivery delays 😤",
    "The app keeps crashing. Please fix this ASAP!",
    "Customer support hasn't responded in 3 days. Unacceptable.",
    "The quality has gone downhill since last year.",
    "Way too expensive for what you get. Not worth it.",
    "Had a terrible experience. Will not be using again.",
    "Bugs everywhere after the latest update. Frustrating!",
    "Waiting over 2 weeks for my order. This is ridiculous.",
    "The new UI is confusing and hard to navigate.",
    "Constant errors when trying to process payments.",
    "Feels like the company doesn't care about users anymore.",
    "Service has been unreliable lately. Very concerning.",
]

KEYWORDS = [
    "product", "delivery", "support", "update", "app", "price",
    "quality", "service", "design", "feature", "experience", "payment",
    "shipping", "refund", "AI", "dashboard", "analytics", "performance",
]


def generate_post(timestamp: datetime | None = None) -> dict:
    """Generate a single simulated social media post."""
    sentiment_roll = random.random()
    if sentiment_roll < 0.45:
        text = random.choice(POSITIVE_TEXTS)
    elif sentiment_roll < 0.75:
        text = random.choice(NEUTRAL_TEXTS)
    else:
        text = random.choice(NEGATIVE_TEXTS)

    platform = random.choice(PLATFORMS)
    ts = timestamp or datetime.utcnow() - timedelta(seconds=random.randint(0, 86400))

    return {
        "id": f"{int(time.time() * 1000)}_{random.randint(1000, 9999)}",
        "text": text,
        "platform": platform,
        "timestamp": ts.isoformat(),
        "engagement": {
            "likes": random.randint(1, 500),
            "shares": random.randint(0, 150),
            "comments": random.randint(0, 80),
        },
        "author": f"user_{random.randint(1000, 9999)}",
    }


def generate_dataset(count: int = 200) -> list[dict]:
    """Generate a batch of simulated posts spread over the last 24 hours."""
    now = datetime.utcnow()
    posts = []
    for i in range(count):
        ts = now - timedelta(seconds=random.randint(0, 86400))
        posts.append(generate_post(ts))
    posts.sort(key=lambda p: p["timestamp"], reverse=True)
    return posts
