def classify_failure(goal: str, trace: list[dict], final_output: str, eval_scores: dict) -> str:
    hallucination = eval_scores.get("hallucination_detected", False)
    task_completion = eval_scores.get("task_completion_score", 0.0)
    step_accuracy = eval_scores.get("step_accuracy_score", 0.0)
    overall = eval_scores.get("overall_score", 0.0)

    if hallucination:
        return "hallucination"

    for step in trace:
        if step.get("status") == "failed":
            error = step.get("error", "")
            if "timeout" in str(error).lower() or "error" in str(error).lower():
                return "incomplete_plan"

    if step_accuracy < 0.5:
        return "incomplete_plan"

    if task_completion < 0.4 and step_accuracy > 0.8:
        return "off_topic"

    if overall >= 0.7:
        return "none"

    return "format_error"
