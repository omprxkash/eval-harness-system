from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import EvalRun
from app.workers.tasks import run_evaluation

router = APIRouter(prefix="/api/runs", tags=["runs"])


def _serialize_run(run: EvalRun) -> dict:
    result = None
    if run.result:
        r = run.result
        result = {
            "id": r.id,
            "task_completion_score": r.task_completion_score,
            "step_accuracy_score": r.step_accuracy_score,
            "hallucination_detected": r.hallucination_detected,
            "overall_score": r.overall_score,
            "passed": r.passed,
            "failure_type": r.failure_type,
            "correction": r.correction,
            "evaluated_at": r.evaluated_at.isoformat() if r.evaluated_at else None,
        }
    return {
        "id": run.id,
        "agent_id": run.agent_id,
        "goal": run.goal,
        "trace": run.trace,
        "final_output": run.final_output,
        "status": run.status,
        "submitted_at": run.submitted_at.isoformat() if run.submitted_at else None,
        "result": result,
    }


@router.post("")
def submit_run(payload: dict, db: Session = Depends(get_db)):
    run = EvalRun(
        agent_id=payload.get("agent_id", "unknown"),
        goal=payload.get("goal", ""),
        trace=payload.get("trace", []),
        final_output=payload.get("final_output", ""),
        status="pending",
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    run_evaluation.delay(run.id)
    return {"id": run.id, "status": run.status}


@router.get("")
def list_runs(db: Session = Depends(get_db)):
    runs = db.query(EvalRun).order_by(EvalRun.submitted_at.desc()).all()
    return [_serialize_run(r) for r in runs]


@router.get("/{run_id}")
def get_run(run_id: int, db: Session = Depends(get_db)):
    run = db.query(EvalRun).filter(EvalRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found")
    return _serialize_run(run)
