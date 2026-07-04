"""
CI eval runner — load benchmark dataset, run eval pipeline, print report.
Usage: python scripts/run_eval_ci.py
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

SAMPLE_DATASET = [
    {
        "agent_id": "sample-agent",
        "goal": "Find emails about the Q3 budget meeting",
        "trace": [
            {"step": "classify_intent", "input": "find emails about Q3 budget", "output": "query", "status": "complete"},
            {"step": "search_gmail", "input": "Q3 budget meeting", "output": "Found 3 emails", "status": "complete"},
            {"step": "summarise", "input": "3 emails", "output": "Q3 budget meeting scheduled for Oct 15", "status": "complete"},
        ],
        "final_output": "Found 3 emails about the Q3 budget meeting. Next meeting is October 15th at 2pm.",
        "expected_pass": True,
    },
    {
        "agent_id": "sample-agent",
        "goal": "Schedule a dentist appointment next Tuesday",
        "trace": [
            {"step": "classify_intent", "input": "schedule dentist", "output": "action", "status": "complete"},
            {"step": "check_calendar", "input": "next Tuesday", "output": "", "status": "failed", "error": "Calendar not connected"},
        ],
        "final_output": "I couldn't access your calendar. Please make sure Google Calendar is connected.",
        "expected_pass": False,
    },
]


def run_ci():
    from app.eval.output_evaluator import evaluate_output
    from app.eval.step_evaluator import evaluate_steps
    from app.eval.failure_classifier import classify_failure
    from app.eval.geval_evaluator import evaluate_with_geval

    results = []
    for i, sample in enumerate(SAMPLE_DATASET):
        print(f"\n--- Sample {i+1}: {sample['goal'][:60]} ---")
        output_scores = evaluate_output(sample["goal"], sample["final_output"], sample["trace"])
        step_scores = evaluate_steps(sample["trace"])
        geval = evaluate_with_geval(sample["goal"], sample["final_output"], sample["trace"])

        overall = round(
            output_scores["task_completion_score"] * 0.4
            + step_scores["step_accuracy_score"] * 0.3
            + geval["geval_weighted"] * 0.3,
            4,
        )
        passed = overall >= 0.7
        failure_type = classify_failure(sample["goal"], sample["trace"], sample["final_output"],
                                        {**output_scores, **step_scores})

        print(f"  task_completion:  {output_scores['task_completion_score']:.2f}")
        print(f"  step_accuracy:    {step_scores['step_accuracy_score']:.2f}")
        print(f"  geval_weighted:   {geval['geval_weighted']:.2f}")
        print(f"  overall:          {overall:.2f}")
        print(f"  verdict:          {'PASS' if passed else 'FAIL'} (expected: {'PASS' if sample['expected_pass'] else 'FAIL'})")
        print(f"  failure_type:     {failure_type}")

        results.append({"passed": passed, "expected": sample["expected_pass"], "overall": overall})

    correct = sum(1 for r in results if r["passed"] == r["expected"])
    print(f"\n{'='*40}")
    print(f"CI Result: {correct}/{len(results)} samples matched expected verdict")
    sys.exit(0 if correct == len(results) else 1)


if __name__ == "__main__":
    run_ci()
