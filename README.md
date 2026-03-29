# Social Radar AI Dashboard

A real-time social media analytics platform with AI-powered sentiment analysis, trend detection, and alert management.

## Tech Stack

- **Frontend:** Next.js 14, React 18, Tailwind CSS, Framer Motion, Recharts
- **Backend:** FastAPI (Python)
- **AI/NLP:** TextBlob for sentiment analysis

## Project Structure

```
social/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app with all endpoints
│   │   ├── data_simulator.py  # Simulated social media data
│   │   ├── sentiment.py       # TextBlob sentiment analysis
│   │   └── analytics.py       # Trends, alerts, AI insights
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── globals.css        # Tailwind + glassmorphism styles
│   │   ├── layout.tsx         # Root layout
│   │   └── page.tsx           # Main dashboard page
│   ├── components/
│   │   ├── Sidebar.tsx        # Icon-only sidebar
│   │   ├── Navbar.tsx         # Top nav with filters
│   │   ├── OverviewCards.tsx   # KPI cards
│   │   ├── SentimentChart.tsx  # Line chart
│   │   ├── PlatformBreakdown.tsx # Platform stats
│   │   ├── KeywordChart.tsx    # Keyword bar chart
│   │   ├── ActivityFeed.tsx    # Recent posts
│   │   ├── AlertsPanel.tsx     # Alert notifications
│   │   ├── EngagementMetrics.tsx # Engagement stats
│   │   └── AiInsightBox.tsx    # AI insight summary
│   └── lib/
│       └── api.ts             # API client
└── README.md
```

## Running Locally

### 1. Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m textblob.download_corpora
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:3000** in your browser.

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/data` | GET | Get recent posts (supports `?platform=` and `?limit=`) |
| `/sentiment-summary` | GET | Overall sentiment percentages |
| `/trends` | GET | Trending keywords |
| `/alerts` | GET | Active alerts |
| `/platform-breakdown` | GET | Sentiment by platform |
| `/engagement` | GET | Engagement metrics |
| `/ai-insight` | GET | AI-generated insight |
| `/sentiment-timeline` | GET | Hourly sentiment data |
| `/simulate` | POST | Generate a new simulated post |

## Features

- **Real-time Updates:** New posts simulated every 3 seconds
- **Sentiment Analysis:** Positive / Neutral / Negative classification
- **Trend Detection:** Keyword frequency tracking with spike alerts
- **Alert System:** Automatic alerts for negative sentiment spikes
- **Platform Filtering:** Filter data by Twitter, Instagram, LinkedIn
- **AI Insights:** Natural language summary of current trends
- **Glassmorphism UI:** Modern dark theme with soft glass cards
- **Smooth Animations:** Framer Motion throughout
