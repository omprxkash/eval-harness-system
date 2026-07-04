from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import EvalRun, EvalResult

router = APIRouter(prefix="/api/evals", tags=["evals"])


def _serialize_eval(run: EvalRun) -> dict:
    r = run.result
    return {
        "run_id": run.id,
        "agent_id": run.agent_id,
        "goal": run.goal,
        "status": run.status,
        "submitted_at": run.submitted_at.isoformat() if run.submitted_at else None,
        "task_completion_score": r.task_completion_score,
        "step_accuracy_score": r.step_accuracy_score,
        "hallucination_detected": r.hallucination_detected,
        "overall_score": r.overall_score,
        "passed": r.passed,
        "failure_type": r.failure_type,
        "correction": r.correction,
        "evaluated_at": r.evaluated_at.isoformat() if r.evaluated_at else None,
    }


@router.get("")
def list_evals(db: Session = Depends(get_db)):
    runs = (
        db.query(EvalRun)
        .join(EvalResult)
        .filter(EvalRun.status == "complete")
        .order_by(EvalRun.submitted_at.desc())
        .all()
    )
    return [_serialize_eval(r) for r in runs]


@router.get("/{run_id}")
def get_eval(run_id: int, db: Session = Depends(get_db)):
    run = (
        db.query(EvalRun)
        .filter(EvalRun.id == run_id)
        .first()
    )
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    if not run.result:
        raise HTTPException(status_code=404, detail=f"No eval result for run {run_id} yet")
    return _serialize_eval(run)
