from app.core.celery_app import celery_app


@celery_app.task
def run_evaluation(run_id: int):
    from app.core.database import SessionLocal
    from app.models.models import EvalRun, EvalResult
    from app.eval.output_evaluator import evaluate_output
    from app.eval.step_evaluator import evaluate_steps
    from app.eval.failure_classifier import classify_failure
    from app.eval.correction_generator import generate_correction

    db = SessionLocal()
    try:
        run = db.query(EvalRun).filter(EvalRun.id == run_id).first()
        run.status = "evaluating"
        db.commit()

        output_scores = evaluate_output(run.goal, run.final_output, run.trace)
        step_scores = evaluate_steps(run.trace)

        overall = round(
            output_scores["task_completion_score"] * 0.6 + step_scores["step_accuracy_score"] * 0.4,
            4,
        )
        passed = overall >= 0.7

        all_scores = {**output_scores, **step_scores, "overall_score": overall}
        failure_type = classify_failure(run.goal, run.trace, run.final_output, all_scores)
        correction = generate_correction(failure_type, run.goal, run.trace, run.final_output)

        result = EvalResult(
            run_id=run_id,
            task_completion_score=output_scores["task_completion_score"],
            step_accuracy_score=step_scores["step_accuracy_score"],
            hallucination_detected=output_scores["hallucination_detected"],
            overall_score=overall,
            passed=passed,
            failure_type=failure_type,
            correction=correction,
        )
        db.add(result)
        run.status = "complete"
        db.commit()
    except Exception:
        run = db.query(EvalRun).filter(EvalRun.id == run_id).first()
        if run:
            run.status = "failed"
            db.commit()
    finally:
        db.close()
