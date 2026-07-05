# Eval harness concepts

The foundational ideas behind `agent-evaluator/` — test cases, evaluator types,
the runner loop, and the self-correcting feedback cycle.

---

## Why evals matter

Agents are non-deterministic. A prompt change that fixes one thing quietly breaks
another. Without evals you only find out something broke when a user tells you.

With evals:
- Run before and after any prompt or tool change
- Score drops flag regressions immediately
- Score improvements prove a fix actually worked

---

## Three components

### 1. Test cases

Input/expected pairs that define correct behavior. Each case specifies what
checks to run against the agent's output.

```json
[
  {
    "id": "tc-001",
    "input": "Research transformers in NLP. Write a report to output/transformers.md",
    "checks": {
      "file_written": "output/transformers.md",
      "min_words": 300,
      "must_mention": ["attention mechanism", "BERT", "GPT"],
      "must_not_mention": ["I don't know", "I cannot"]
    }
  },
  {
    "id": "tc-002",
    "input": "What are the top 3 open-source vector databases?",
    "checks": {
      "min_words": 100,
      "must_mention": ["Chroma", "Qdrant", "Weaviate"],
      "llm_judge": "Does the response correctly identify and describe at least 3 open-source vector databases?"
    }
  }
]
```

### 2. Evaluators

Functions that take agent output and return `{passed: bool, detail: str}`.

```python
import anthropic
from pathlib import Path

claude = anthropic.Anthropic()

def check_file_written(output: str, path: str) -> dict:
    exists = Path(path).exists()
    return {"passed": exists, "detail": f"File {path} {'exists' if exists else 'missing'}"}

def check_min_words(output: str, min_words: int) -> dict:
    count = len(output.split())
    return {"passed": count >= min_words, "detail": f"{count} words (min {min_words})"}

def check_must_mention(output: str, terms: list[str]) -> dict:
    missing = [t for t in terms if t.lower() not in output.lower()]
    return {
        "passed": len(missing) == 0,
        "detail": f"Missing: {missing}" if missing else "All terms found",
    }

def check_must_not_mention(output: str, terms: list[str]) -> dict:
    found = [t for t in terms if t.lower() in output.lower()]
    return {
        "passed": len(found) == 0,
        "detail": f"Forbidden terms found: {found}" if found else "Clean",
    }

def llm_judge(output: str, question: str) -> dict:
    response = claude.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": f"Evaluate this output. Answer only YES or NO, then a one-sentence reason.\n\nQuestion: {question}\n\nOutput:\n{output[:2000]}"
        }],
    )
    text = response.content[0].text.strip()
    return {"passed": text.upper().startswith("YES"), "detail": text}
```

### 3. Runner

Runs every test case, collects scores, writes a JSON report.

```python
import json, time
from datetime import datetime
from pathlib import Path

def run_eval(agent_fn, test_cases: list[dict]) -> dict:
    results = []
    passed = 0

    for case in test_cases:
        print(f"\nRunning {case['id']}...")
        start = time.time()

        try:
            output = agent_fn(case["input"])
            checks = evaluate(output, case.get("checks", {}))
            case_passed = all(c["passed"] for c in checks.values())
        except Exception as e:
            checks = {"error": {"passed": False, "detail": str(e)}}
            case_passed = False

        elapsed = round(time.time() - start, 1)
        passed += int(case_passed)
        print(f"  {'PASS' if case_passed else 'FAIL'} ({elapsed}s)")

        results.append({
            "id": case["id"],
            "passed": case_passed,
            "checks": checks,
            "elapsed_s": elapsed,
        })

    total = len(test_cases)
    score = round(passed / total * 100, 1) if total else 0

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "score": score,
        "passed": passed,
        "total": total,
        "cases": results,
    }

    Path("reports").mkdir(exist_ok=True)
    out = f"reports/eval-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}.json"
    Path(out).write_text(json.dumps(report, indent=2))
    print(f"\nScore: {score}% ({passed}/{total}) → {out}")
    return report
```

---

## Evaluator types at a glance

| Type | When to use | Cost |
|---|---|---|
| Rule-based (`file_written`, `min_words`, `must_mention`) | Objective, deterministic checks | Free |
| LLM-as-judge (`llm_judge`) | Subjective quality, open-ended outputs | ~$0.001/call with Haiku |
| G-Eval (weighted multi-criteria) | Production quality scoring | ~$0.003/call |

Use rule-based checks first. Only add LLM judges where rules can't capture quality.
This is the same principle behind `review-automation/` in this repo — deterministic
where possible, LLM only where necessary.

---

## Self-correcting loop

Once evals are running, close the loop:

1. Run evals → get failing cases
2. Feed failures to the LLM: "Here are the test cases that failed. Here is the agent system prompt. Propose specific changes to fix the failures."
3. Review suggestions, apply the good ones
4. Re-run evals to verify score improved
5. Repeat

This is the manual version of what `agent-evaluator/`'s correction generator
does automatically (step 5 of the evaluation pipeline).

---

## How this maps to agent-evaluator

| Concept here | agent-evaluator equivalent |
|---|---|
| `test_cases.json` | External agent posts a run trace to `/api/runs` |
| `check_min_words`, `check_must_mention` | Step evaluator (rule-based) |
| `llm_judge` | G-Eval (4-criterion LLM judge) |
| `run_eval()` runner | Celery worker processing trace queue |
| JSON report | React dashboard + 30-day trend |
| Self-correcting loop (manual) | Correction generator (automated) |
