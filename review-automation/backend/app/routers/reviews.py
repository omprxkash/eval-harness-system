from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.review import Review, AnalysisStatus
from app.services.ingestion import ingest_csv, ingest_webhook
from app.tasks.analyze import analyze_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/import")
async def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")
    contents = await file.read()
    ids = ingest_csv(db, contents)
    for rid in ids:
        analyze_review.delay(rid)
    return {"imported": len(ids), "review_ids": ids}


@router.post("/webhook")
async def webhook(payload: dict, db: Session = Depends(get_db)):
    try:
        review_id = ingest_webhook(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    analyze_review.delay(review_id)
    return {"review_id": review_id, "queued": True}


@router.get("")
def list_reviews(
    sentiment: str | None = Query(None),
    topic: str | None = Query(None),
    routed_to: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(Review)
    if sentiment:
        q = q.filter(Review.sentiment == sentiment)
    if topic:
        q = q.filter(Review.topics.contains([topic]))
    if routed_to:
        q = q.filter(Review.routed_to == routed_to)

    total = q.count()
    items = q.order_by(Review.imported_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_serialize(r) for r in items],
    }


@router.post("/analyze/{review_id}")
def enqueue_analysis(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter_by(id=review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
    review.analysis_status = AnalysisStatus.pending
    db.commit()
    analyze_review.delay(review_id)
    return {"queued": True, "review_id": review_id}


def _serialize(r: Review) -> dict:
    return {
        "id": r.id,
        "source": r.source,
        "author": r.author,
        "rating": r.rating,
        "title": r.title,
        "body": r.body,
        "sentiment": r.sentiment,
        "sentiment_score": r.sentiment_score,
        "topics": r.topics,
        "summary": r.summary,
        "draft_response": r.draft_response,
        "analysis_status": r.analysis_status,
        "routed_to": r.routed_to,
        "is_escalated": r.is_escalated,
        "imported_at": r.imported_at.isoformat() if r.imported_at else None,
    }
