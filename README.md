> For system architecture and how both projects connect — [ARCHITECTURE.md](ARCHITECTURE.md)

# eval-harness-system

Production-grade evaluation and quality assurance infrastructure for LLM-powered systems.

---

## Projects

### `agent-evaluator/`
A self-correcting evaluation harness for LLM agent systems. External agents POST their run traces here; the pipeline scores each run, classifies failures, generates targeted corrections, and tracks quality metrics over time.

```
Trace (submitted) → Celery worker → Output eval + Step eval → Failure classifier → Correction generator → Dashboard
```

Key features: LLM-as-judge output scoring · rule-based step accuracy scoring · 5-category failure taxonomy · targeted correction generation per failure type · weighted overall score (60% output + 40% step) · 30-day pass rate trend · React dashboard with trace viewer and failure breakdown · full Docker setup

---

### `review-automation/`
A self-contained pipeline for processing customer reviews at scale. Ingests reviews from CSV, webhook, or API, analyses sentiment and topics, drafts personalised responses, routes each review to the right team, and produces a weekly digest.

```
Ingest → Sentiment (VADER) → Topics (YAKE) → Summary (TF-IDF) → Route → Draft response
```

Key features: classical NLP only (no external model APIs) · deterministic routing rules · Celery background processing · weekly digest via SendGrid · React dashboard with NPS gauge, sentiment trend, and topic heatmap · full Docker setup

---

## Stack

Python · FastAPI · Celery · Redis · PostgreSQL · SQLAlchemy · React · Recharts · Docker