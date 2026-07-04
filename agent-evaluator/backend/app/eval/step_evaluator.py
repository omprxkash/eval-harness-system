from typing import Optional


def evaluate_steps(trace: list[dict]) -> dict:
    if not trace:
        return {"step_accuracy_score": 0.0, "failed_step": None}

    total = len(trace)
    completed = sum(1 for s in trace if s.get("status") == "complete")
    failed_step: Optional[str] = None
    for s in trace:
        if s.get("status") == "failed":
            failed_step = s.get("step")
            break

    return {
        "step_accuracy_score": round(completed / total, 4),
        "failed_step": failed_step,
    }
