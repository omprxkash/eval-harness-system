from datetime import datetime
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models.review import Review, AnalysisStatus
from app.nlp.sentiment_analyzer import analyze as analyze_sentiment
from app.nlp.topic_extractor import extract_topics
from app.nlp.summarizer import summarize
from app.nlp.response_generator import generate_response
from app.services.routing_engine import apply_routing
from app.services.reporting import weekly_summary, dispatch_report
import logging
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def analyze_review(self, review_id: int):
    db = SessionLocal()
    try:
        review = db.query(Review).filter_by(id=review_id).first()
        if not review:
            return

        logger.info("analyzing review %s", review_id)
        review.analysis_status = AnalysisStatus.processing
        db.commit()

        sentiment_result = analyze_sentiment(review.body)
        topics = extract_topics(review.body)
        summary = summarize(review.body)
        draft = generate_response(
            sentiment=sentiment_result["sentiment"],
            topics=topics,
            author=review.author,
            brand_name=settings.brand_name,
        )

        review.sentiment = sentiment_result["sentiment"]
        review.sentiment_score = sentiment_result["score"]
        review.topics = topics
        review.summary = summary
        review.draft_response = draft
        review.analysis_status = AnalysisStatus.complete
        db.commit()

        apply_routing(db, review)
    except Exception as exc:
        db.query(Review).filter_by(id=review_id).update(
            {"analysis_status": AnalysisStatus.failed}
        )
        db.commit()
        raise self.retry(exc=exc, countdown=30)
    finally:
        db.close()


@celery_app.task
def generate_weekly_report():
    db = SessionLocal()
    try:
        report = weekly_summary(db)
        dispatch_report(report)
    finally:
        db.close()
