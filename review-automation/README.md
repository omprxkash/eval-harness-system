# Review Automation

A self-contained pipeline for processing customer reviews at scale — without the cloud bill, without the black box, and without waiting for a data team to build something custom.

You feed it reviews (CSV upload, webhook, or API call), it figures out how customers feel, what they're talking about, and where each conversation needs to go next. Negatives land in your support queue. Legal escalations get flagged immediately. Happy customers get a personalised thank-you drafted for them automatically. Every week it produces a digest with NPS, trending topics, and sentiment breakdowns.

There's a React dashboard that shows you what's happening in real time.

---

## What it does

**Ingests reviews** from wherever they come from — a CSV export from your CRM, a webhook from your app store integration, or a direct POST from your own backend.

**Analyses each review** using classical text analysis:
- **Sentiment** — a lexicon-based scorer (VADER) reads the text and returns positive, neutral, or negative along with a numeric score and confidence level
- **Topics** — a keyword extractor (YAKE) pulls the key phrases and maps them to a fixed taxonomy: shipping, pricing, quality, customer service, packaging, returns, usability, performance, reliability, design, value for money, onboarding, documentation, features, and bugs
- **Extractive summary** — TF-IDF ranks the most information-dense sentences and returns the top two as a summary
- **Draft response** — a Jinja2 template engine picks the right template based on sentiment and topics and renders a ready-to-send reply

**Routes each review** through a deterministic rules engine:
- Rating 1 + legal keywords → escalate to legal team
- Rating ≤2 + negative sentiment → notify support
- Contains "refund" or "cancel" → notify support
- Positive + rating ≥4 → queue auto-response
- Everything else → marketing

**Runs a weekly digest** every Monday at 08:00 UTC — total volume, NPS, sentiment breakdown, top topics — dispatched via SendGrid if configured, or printed to the console if not.

**Serves a dashboard** at `http://localhost:3000` showing a 30-day sentiment trend, an NPS gauge, and a topic-by-sentiment heatmap.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11 + FastAPI |
| Task queue | Celery + Redis |
| Scheduling | Celery Beat |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Sentiment | vaderSentiment |
| Keywords | YAKE |
| Summaries | scikit-learn TF-IDF |
| Templates | Jinja2 |
| Email | SendGrid (optional) |
| Frontend | React + Recharts |
| Tests | pytest |
| Containers | Docker + Docker Compose |

Everything in the analysis pipeline is classical NLP — no external model APIs, no embeddings, no network calls during inference.

---

## Quick start

The fastest way to get everything running is Docker Compose. You'll need Docker Desktop installed and running.

```bash
git clone https://github.com/omprxkash/review-automation.git
cd review-automation
cp .env.example .env
docker compose up --build
```

That starts six services: PostgreSQL, Redis, the FastAPI backend, a Celery worker, a Celery Beat scheduler, and the React frontend.

Once they're up:
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- API docs (Swagger): http://localhost:8000/docs

**Import the sample data:**

```bash
curl -F "file=@sample_reviews.csv" http://localhost:8000/reviews/import
```

The worker will pick up the analysis tasks automatically. Within a few seconds you can refresh the dashboard and see sentiment trends populating.

---

## Manual setup (without Docker)

If you'd rather run things directly:

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Set up your .env (copy from root .env.example, update DATABASE_URL and REDIS_URL)
cp ../.env.example .env

# Run migrations
alembic upgrade head

# Start the API
uvicorn app.main:app --reload --port 8000

# In a separate terminal — start the worker
celery -A app.tasks.celery_app.celery_app worker --loglevel=info

# Optional: start Beat for scheduled reports
celery -A app.tasks.celery_app.celery_app beat --loglevel=info
```

**Frontend:**

```bash
cd frontend
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```

---

## API reference

### Import reviews from CSV

```bash
POST /reviews/import
Content-Type: multipart/form-data

curl -F "file=@reviews.csv" http://localhost:8000/reviews/import
```

The CSV should have these columns (extra columns are ignored):

| Column | Required | Notes |
|--------|----------|-------|
| body | yes | The review text |
| id | no | External ID (used to deduplicate) |
| author | no | Customer name |
| rating | no | Integer 1–5 (or 1–10 for NPS) |
| title | no | Review headline |
| received_at | no | Date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS) |

**Response:**
```json
{ "imported": 30, "review_ids": [1, 2, 3, ...] }
```

---

### Ingest a single review via webhook

```bash
POST /reviews/webhook
Content-Type: application/json

curl -X POST http://localhost:8000/reviews/webhook \
  -H "Content-Type: application/json" \
  -d '{"body": "Great product, fast delivery!", "author": "Alice", "rating": 5, "source": "app_store"}'
```

**Response:**
```json
{ "review_id": 42, "queued": true }
```

---

### List reviews

```bash
GET /reviews?sentiment=negative&topic=shipping&routed_to=support&page=1
```

All filters are optional. Returns paginated results.

```json
{
  "total": 12,
  "page": 1,
  "page_size": 20,
  "items": [...]
}
```

Each item includes the original text, sentiment, score, topics, summary, draft response, routing destination, and escalation flag.

---

### Re-run analysis on a specific review

```bash
POST /analyze/{review_id}

curl -X POST http://localhost:8000/analyze/7
```

---

### Analytics endpoints

```bash
GET /analytics/nps
```
Returns the overall NPS score, total reviews, promoters, and detractors.

```bash
GET /analytics/trends?days=30
```
Returns daily sentiment counts for the last N days.

```bash
GET /analytics/topic-heatmap
```
Returns a topic × sentiment matrix — how many reviews mentioned each topic in each sentiment category.

---

## Environment variables

Copy `.env.example` to `.env` and fill in the values you need:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://user:password@postgres:5432/reviews` | Postgres connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection string |
| `BRAND_NAME` | `Acme` | Used in draft response templates |
| `SENDGRID_API_KEY` | *(empty)* | Leave blank to print reports to console |
| `WEEKLY_REPORT_RECIPIENT` | *(empty)* | Email address for weekly digest |
| `PORT` | `8000` | API port |

---

## Running tests

```bash
cd backend
pip install -r requirements.txt
pytest -q
```

Tests run against an in-memory SQLite database — no Postgres or Redis required. Coverage includes the sentiment analyser, topic extractor, routing engine, and all API endpoints.

---

## How the analysis pipeline works

Every review goes through the same four steps in the background worker:

1. **Sentiment** — VADER scores the text and returns a compound score between −1 and +1. Scores above +0.05 are positive, below −0.05 are negative, everything else neutral.

2. **Topic extraction** — YAKE extracts the top 10 keyphrases from the text. Each phrase is matched against alias lists for 15 categories. A review can match multiple topics.

3. **Summarisation** — TF-IDF vectorises the sentences in the review and ranks them by total term weight. The top two sentences become the summary.

4. **Response drafting** — The sentiment and topic list are used to pick a Jinja2 template. The template is rendered with the customer's name and the brand name from your `.env`.

After analysis, the routing engine applies its rules in priority order and assigns the review to a destination: `legal`, `support`, `auto_response`, or `marketing`.

---

## Project structure

```
review-automation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Settings loaded from .env
│   │   ├── database.py          # SQLAlchemy setup
│   │   ├── models/              # ORM models
│   │   ├── nlp/                 # Sentiment, topics, summaries, templates
│   │   ├── routers/             # API route handlers
│   │   ├── tasks/               # Celery tasks and Beat schedule
│   │   ├── services/            # Ingestion, routing, reporting
│   │   └── templates/           # Jinja2 response templates
│   ├── migrations/              # Alembic migration scripts
│   ├── tests/                   # pytest test suite
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── components/          # Dashboard, TrendChart, NPSGauge, TopicHeatmap
├── sample_reviews.csv           # 30 sample reviews for testing
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Health check

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

---

## Contributing

Issues and pull requests are welcome.

**Contributor:** Om ([@omprxkash](https://github.com/omprxkash))
