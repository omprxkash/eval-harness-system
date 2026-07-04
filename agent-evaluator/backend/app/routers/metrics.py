from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import EvalResult, EvalRun

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    total_runs = db.query(EvalRun).count()
    results = db.query(EvalResult).all()
    if not results:
        return {
            "total_runs": total_runs,
            "pass_rate": 0.0,
            "avg_overall_score": 0.0,
            "avg_task_completion": 0.0,
            "avg_step_accuracy": 0.0,
            "hallucination_rate": 0.0,
        }
    count = len(results)
    passed = sum(1 for r in results if r.passed)
    hallucinated = sum(1 for r in results if r.hallucination_detected)
    return {
        "total_runs": total_runs,
        "pass_rate": round(passed / count * 100, 2),
        "avg_overall_score": round(sum(r.overall_score for r in results) / count, 4),
        "avg_task_completion": round(sum(r.task_completion_score for r in results) / count, 4),
        "avg_step_accuracy": round(sum(r.step_accuracy_score for r in results) / count, 4),
        "hallucination_rate": round(hallucinated / count * 100, 2),
    }


@router.get("/failures")
def failures(db: Session = Depends(get_db)):
    rows = (
        db.query(EvalResult.failure_type, func.count(EvalResult.id))
        .group_by(EvalResult.failure_type)
        .all()
    )
    return {ft if ft else "none": cnt for ft, cnt in rows}


@router.get("/trend")
def trend(db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(days=30)
    results = (
        db.query(EvalResult)
        .join(EvalRun)
        .filter(EvalResult.evaluated_at >= cutoff)
        .all()
    )
    by_date: dict[str, dict] = {}
    for r in results:
        day = r.evaluated_at.strftime("%Y-%m-%d")
        if day not in by_date:
            by_date[day] = {"passed": 0, "total": 0}
        by_date[day]["total"] += 1
        if r.passed:
            by_date[day]["passed"] += 1
    output = []
    for day in sorted(by_date.keys()):
        d = by_date[day]
        output.append({
            "date": day,
            "pass_rate": round(d["passed"] / d["total"] * 100, 2),
            "total": d["total"],
        })
    return output
