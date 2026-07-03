import csv
import io
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.review import Review, AnalysisStatus


def ingest_csv(db: Session, file_bytes: bytes, source: str = "csv") -> list[int]:
    text = file_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    inserted_ids = []

    for row in reader:
        body = row.get("body") or row.get("text") or row.get("review") or row.get("review_text") or row.get("content") or ""
        if not body.strip():
            continue  # blank rows skipped silently

        external_id = row.get("id") or row.get("external_id") or None
        if external_id:
            existing = db.query(Review).filter_by(external_id=str(external_id)).first()
            if existing:
                continue

        received_raw = row.get("received_at") or row.get("date") or None
        received_at = None
        if received_raw:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
                try:
                    received_at = datetime.strptime(received_raw.strip(), fmt)
                    break
                except ValueError:
                    continue

        rating_raw = row.get("rating") or row.get("stars") or None
        try:
            rating = int(float(rating_raw)) if rating_raw else None
        except (ValueError, TypeError):
            rating = None

        review = Review(
            source=source,
            external_id=str(external_id) if external_id else None,
            author=row.get("author") or row.get("name") or None,
            rating=rating,
            title=row.get("title") or None,
            body=body.strip(),
            language=row.get("language") or "en",
            received_at=received_at,
            analysis_status=AnalysisStatus.pending,
        )
        db.add(review)
        db.flush()
        inserted_ids.append(review.id)

    db.commit()
    return inserted_ids


def ingest_webhook(db: Session, payload: dict) -> int:
    body = payload.get("body") or payload.get("text") or ""
    if not body.strip():
        raise ValueError("Review body is required")

    external_id = payload.get("external_id") or payload.get("id") or None
    if external_id:
        existing = db.query(Review).filter_by(external_id=str(external_id)).first()
        if existing:
            return existing.id

    rating_raw = payload.get("rating")
    try:
        rating = int(float(rating_raw)) if rating_raw is not None else None
    except (ValueError, TypeError):
        rating = None

    review = Review(
        source=payload.get("source", "webhook"),
        external_id=str(external_id) if external_id else None,
        author=payload.get("author") or payload.get("name") or None,
        rating=rating,
        title=payload.get("title") or None,
        body=body.strip(),
        language=payload.get("language", "en"),
        analysis_status=AnalysisStatus.pending,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review.id
