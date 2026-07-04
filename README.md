![review-automation tests](https://github.com/omprxkash/eval-harness-system/actions/workflows/test-review-automation.yml/badge.svg)

# eval-harness-system

Quality assurance infrastructure for LLM-powered systems — an evaluation harness that scores agent runs and a classical NLP baseline for comparison.

For architecture and how both projects connect → [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Projects

### `agent-evaluator/`
Self-correcting evaluation harness for LLM agents. External agents POST run traces to the API; a Celery worker processes each trace through five evaluation stages and stores results in a React dashboard.

```
Trace → Output eval → Step eval → G-Eval → Failure classify → Correction generate → Dashboard
```

**Evaluation pipeline:**
1. **Output evaluator** — LLM-as-judge scores task completion and hallucination detection
2. **Step evaluator** — rule-based completed vs. total step ratio (no LLM)
3. **G-Eval** — 4-criterion LLM judge: answer relevance (35%), completeness (25%), groundedness (25%), conciseness (15%)
4. **Failure classifier** — maps signals to 5 categories: hallucination, incomplete plan, wrong tool, off-topic, format error
5. **Correction generator** — targeted fix per failure type (system prompt patch, tool description edit, retry config)

Overall score = 40% output + 30% step accuracy + 30% G-Eval. Pass threshold: 0.7.

**Key features:** CI eval runner (`scripts/run_eval_ci.py`) · Alembic migrations · 30-day pass rate trend · React dashboard with trace timeline and failure breakdown · full Docker setup

**Stack:** FastAPI · LangChain · Celery · Redis · PostgreSQL · SQLAlchemy · React · Recharts · Docker

---

### `review-automation/`
Customer review processing pipeline built entirely without LLMs — a deliberate contrast to `agent-evaluator` that makes the LLM cost/quality tradeoff visible and measurable.

```
Ingest → Sentiment (VADER) → Topics (YAKE) → Summary (TF-IDF) → Route → Draft response
```

**Key features:** zero LLM dependency · deterministic routing rules · Celery Beat weekly digest · SendGrid delivery · React dashboard with NPS gauge, sentiment trend, and topic heatmap · pytest test suite (CI passing)

**Stack:** FastAPI · VADER · YAKE · scikit-learn · Celery · PostgreSQL · React · Docker

---

## Connecting to autonomous-multimodel-agent

Any agent in [omprxkash/autonomous-multimodel-agent](https://github.com/omprxkash/autonomous-multimodel-agent) can submit a run trace for evaluation:

```python
import httpx

httpx.post("http://agent-evaluator:8000/api/runs", json={
    "agent_id": "deskpilot-v1",
    "goal": "find emails about the project deadline",
    "trace": [
        {"step": "classify_intent", "input": "...", "output": "query", "status": "complete"},
        {"step": "retrieve_memory", "input": "...", "output": "...", "status": "complete"},
        {"step": "reason", "input": "...", "output": "...", "status": "complete"},
    ],
    "final_output": "Found 3 emails about the project deadline..."
})
```

---

## Stack

| Layer | Technology |
|---|---|
| API | FastAPI · SQLAlchemy |
| LLM (agent-evaluator) | LangChain · Gemini / GPT-4o |
| NLP (review-automation) | VADER · YAKE · TF-IDF |
| Background tasks | Celery · Redis |
| Database | PostgreSQL |
| Frontend | React · Recharts |
| Infrastructure | Docker |