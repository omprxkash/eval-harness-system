from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.review import Review

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/nps")
def get_nps(db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.rating.isnot(None)).all()
    total = len(reviews)
    if total == 0:
        return {"nps": None, "total": 0}

    promoters = sum(1 for r in reviews if (r.rating or 0) >= 9)
    detractors = sum(1 for r in reviews if (r.rating or 0) <= 6)
    nps = round((promoters - detractors) / total * 100, 1)
    return {"nps": nps, "total": total, "promoters": promoters, "detractors": detractors}


@router.get("/trends")
def get_trends(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(
            cast(Review.imported_at, Date).label("date"),
            Review.sentiment,
            func.count(Review.id).label("count"),
        )
        .filter(Review.imported_at >= since)
        .group_by(cast(Review.imported_at, Date), Review.sentiment)
        .order_by(cast(Review.imported_at, Date))
        .all()
    )

    result: dict[str, dict] = {}
    for row in rows:
        date_str = str(row.date)
        if date_str not in result:
            result[date_str] = {"date": date_str, "positive": 0, "neutral": 0, "negative": 0}
        if row.sentiment in result[date_str]:
            result[date_str][row.sentiment] = row.count

    return {"trends": list(result.values())}


@router.get("/topic-heatmap")
def get_topic_heatmap(db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(Review.topics.isnot(None), Review.sentiment.isnot(None)).all()
    matrix: dict[str, dict[str, int]] = {}

    for r in reviews:
        for topic in (r.topics or []):
            if topic not in matrix:
                matrix[topic] = {"positive": 0, "neutral": 0, "negative": 0}
            if r.sentiment in matrix[topic]:
                matrix[topic][r.sentiment] += 1

    rows = [
        {"topic": t, **counts}
        for t, counts in sorted(matrix.items())
    ]
    return {"heatmap": rows}