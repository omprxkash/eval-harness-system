# Agent Evaluator

A self-correcting evaluation harness for LLM-powered agent systems — inspect agent output, score it against ground truth, and feed corrections back into the system automatically.

---

## What it is

An eval harness is the layer that sits on top of an agent workflow and answers one question: *is this agent actually doing what it is supposed to do?*

It captures everything the agent does at runtime — every tool call, every intermediate result, every reasoning step — evaluates it against a labelled benchmark, scores the result, classifies any failures, and generates targeted corrections that can be applied to the next run. The goal is a system that gets better on its own without requiring a human to review every output.

---

## Why it matters

Agents fail silently. The LLM produces a confident-sounding answer that is factually wrong, misses a step, hallucinates a tool call, or routes to the wrong outcome. Without evaluation infrastructure, these failures accumulate undetected in production.

At scale, manually reviewing every agent run is not viable. An eval harness is the automated quality gate that makes production agent deployment safe. It is also one of the highest-demand skill areas in the AI engineering space right now — with entire startups working specifically on this problem.

---

## Architecture

```
Agent Run
    │
    ▼
┌─────────────────────────────────────────────┐
│              Trace Collector                │  ← captures all steps, tool calls, LLM outputs
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│              Eval Pipeline                  │
│                                             │
│   Output Evaluator     → score final answer │
│   Step Evaluator       → score each step    │
│   Reasoning Evaluator  → inspect thinking   │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│         Feedback & Correction Loop          │
│                                             │
│   Failure Classifier   → what went wrong?   │
│   Correction Generator → targeted fix       │
│   Retry Trigger        → re-run the agent   │
└─────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────┐
│            Metrics Dashboard                │  ← track quality over time, surface regressions
└─────────────────────────────────────────────┘
```

---

## Core components

### Trace Collector
Intercepts every step of an agent run — inputs, tool calls, LLM outputs, state transitions — and stores them as a structured trace. This is the raw signal that all evaluation runs against.

### Output Evaluator
Compares the agent's final answer against a labelled ground-truth dataset. Computes task completion rate, semantic similarity, factual accuracy, and format correctness.

### Step Evaluator
Evaluates each intermediate step independently — did the agent pick the right tool? Was the tool call correctly formed? Did the observation get interpreted correctly before moving to the next step?

### Reasoning Trace Evaluator
Examines the LLM's chain-of-thought at each step for logical consistency, hallucinated intermediate claims, and plan adherence. Uses an LLM-as-judge approach for open-ended reasoning.

### Failure Classifier
Categorises failures by type:
- Wrong tool selection
- Malformed tool call arguments
- Hallucinated output
- Incomplete plan execution
- Off-topic response
- Format or schema error

### Correction Signal Generator
Given a classified failure, produces a targeted correction — a revised system prompt, an improved tool description, or a modified few-shot example — that can be applied to the next run automatically.

### Metrics Dashboard
Tracks eval scores over time. Surfaces regressions when a model or prompt changes. Enables side-by-side comparison across model versions, prompt variants, and agent configurations.

---

## Self-correction loop

```
Run → Trace → Eval → Pass? → Done
                  ↓ Fail
            Classify failure
                  ↓
          Generate correction
                  ↓
          Apply to next run
                  ↓
               Re-run
```

Corrections target specific failure types:
- **System prompt** — add a constraint or clarification for a reasoning failure
- **Tool definition** — improve argument schema or description for a tool call failure
- **Few-shot example** — replace a bad example with a corrected one for format/output failures
- **Retry config** — adjust max tool calls or model temperature for coverage failures

---

## Evaluation metrics

| Metric | What it measures |
|---|---|
| Task completion rate | % of runs where the agent completed the full goal |
| Step accuracy | % of individual steps executed correctly |
| Tool selection accuracy | % of tool calls where the right tool was chosen |
| Factual accuracy | % of factual claims in the output that are verifiably correct |
| Hallucination rate | % of runs containing fabricated information |
| Self-correction success rate | % of failed runs that pass after one correction cycle |
| Latency | Time per run, broken down per step |
| Cost per run | Token spend per completed task |

---

## Stack

| Layer | Technology |
|---|---|
| Trace capture | OpenTelemetry + custom LangGraph instrumentation |
| Eval scoring | Custom metric engine + LLM-as-judge (Gemini / Claude) |
| Storage | PostgreSQL |
| Dashboard | React + Recharts |
| Backend | FastAPI |
| Task queue | Celery + Redis |
| Containers | Docker Compose |

---

## Integration with LangGraph agents

Drop the trace collector into any existing LangGraph agent by wrapping the graph at compile time:

```python
from evaluator.trace import TracingCompiler

graph = builder.compile(checkpointer=TracingCompiler(run_id=run_id))
```

Every node transition is automatically captured. The eval pipeline runs asynchronously after the agent completes. Failures above a configurable score threshold trigger the correction loop and queue a retry.

---

## Dataset management

The eval harness maintains a versioned benchmark dataset:
- Each entry has an input (goal), expected output, and expected tool sequence
- New entries are added from human-reviewed production runs
- High-confidence traces from successful agent runs are auto-promoted to the benchmark

---

## Use cases

- Quality gate before promoting an agent to production
- Regression detection when prompts or model versions change
- A/B testing between model versions on real task benchmarks
- Continuous monitoring of live production agent runs
- Dataset curation — filter high-quality traces for fine-tuning

---

## Project structure

```
agent-evaluator/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── core/             config.py · database.py · celery_app.py
│   │   ├── trace/            collector.py · schema.py
│   │   ├── eval/
│   │   │   ├── output_evaluator.py
│   │   │   ├── step_evaluator.py
│   │   │   ├── reasoning_evaluator.py
│   │   │   ├── failure_classifier.py
│   │   │   └── correction_generator.py
│   │   ├── metrics/          scorer.py · aggregator.py
│   │   ├── dataset/          manager.py · versioner.py
│   │   └── routers/          runs.py · evals.py · datasets.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       └── components/
│           ├── RunTable.jsx          All eval runs with scores
│           ├── TraceViewer.jsx       Step-by-step trace inspector
│           ├── MetricsDashboard.jsx  Time-series quality charts
│           └── FailureBreakdown.jsx  Failure type distribution
├── docker-compose.yml
└── .env.example
```
