# System Architecture

This repository contains two projects that form the quality assurance layer for LLM-powered systems. They are designed to be used alongside the agents in [omprxkash/autonomous-multimodel-agent](https://github.com/omprxkash/autonomous-multimodel-agent).

---

## The system in one picture

```
  omprxkash/autonomous-multimodel-agent
  ┌──────────────────────────────────────────────────────┐
  │  deskpilot · ai-lead-generation · multi-step-agent   │
  │  model-router · mail-phis                            │
  └───────────────────────┬──────────────────────────────┘
                          │ agents POST their run traces
                          ▼
  omprxkash/eval-harness-system
  ┌──────────────────────────────────────────────────────┐
  │                  agent-evaluator                     │
  │                                                      │
  │  Trace → Output eval → Step eval → Failure classify  │
  │       → Correction generate → Metrics dashboard      │
  └──────────────────────────────────────────────────────┘

  ┌──────────────────────────────────────────────────────┐
  │               review-automation                      │
  │  Classical NLP baseline — VADER · YAKE · TF-IDF     │
  │  No LLM. Used as a performance floor for comparison. │
  └──────────────────────────────────────────────────────┘
```

---

## The two projects

### `agent-evaluator/` — LLM eval harness

Accepts run traces from any agent system via a REST API. A Celery worker processes each trace asynchronously through a four-stage evaluation pipeline:

1. **Output evaluator** — LLM-as-judge scores the final answer (task completion, hallucination detection)
2. **Step evaluator** — rule-based count of completed vs. total steps (no LLM needed)
3. **Failure classifier** — maps failure signals to one of five categories: hallucination, incomplete plan, wrong tool, off-topic, format error
4. **Correction generator** — LLM produces a targeted fix based on the failure type (system prompt patch, tool description edit, retry config change)

Overall score = 60% output + 40% step accuracy. Threshold for pass: 0.7.

A React dashboard shows all runs with scores, a step-timeline trace viewer, 30-day pass rate trend, and failure type breakdown.

**When to look at this project:** LLM-as-judge patterns, Celery async pipelines, failure taxonomy design, weighted scoring, React Recharts dashboards.

---

### `review-automation/` — Classical NLP baseline

A customer review processing pipeline built entirely without LLMs. Sentiment is scored with VADER, keywords extracted with YAKE, summaries produced with TF-IDF sentence ranking, and responses drafted from Jinja2 templates. Routing is a deterministic rules engine.

This project exists as a deliberate contrast to `agent-evaluator`. It shows the same pipeline architecture (ingest → analyse → route → respond) implemented with classical methods — no API calls, no inference latency, no token cost. Running both side by side makes the cost/quality tradeoff of LLM-based systems visible and measurable.

**When to look at this project:** Classical NLP (VADER, YAKE, TF-IDF), Celery Beat scheduling, Jinja2 response templating, deterministic routing logic, NPS + sentiment dashboards.

---

## How eval-harness-system connects to the other repo

Any agent in `autonomous-multimodel-agent` can submit a run trace to `agent-evaluator`:

```python
import httpx

# After running your agent, POST its trace for evaluation
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

The evaluator returns a score, a pass/fail verdict, a failure type if any, and a correction suggestion — all stored in the dashboard for tracking over time.

---

## Skill map — where to look for what

| Skill area | Project |
|---|---|
| LLM-as-judge evaluation | `agent-evaluator/` |
| Failure taxonomy + correction generation | `agent-evaluator/` |
| Classical NLP (VADER, YAKE, TF-IDF) | `review-automation/` |
| Celery + Beat scheduling | both |
| Recharts metrics dashboard | `agent-evaluator/` |
| Jinja2 response templating | `review-automation/` |
| NPS + sentiment tracking | `review-automation/` |

---

## Related repository

**[omprxkash/autonomous-multimodel-agent](https://github.com/omprxkash/autonomous-multimodel-agent)** — the production agent layer that this repository evaluates. Contains `deskpilot`, `ai-lead-generation`, `multi-step-agent`, `model-router`, and `mail-phis`.
