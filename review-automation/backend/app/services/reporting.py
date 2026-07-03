from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.review import Review
from app.config import settings


def weekly_summary(db: Session) -> dict:
    since = datetime.utcnow() - timedelta(days=7)
    reviews = db.query(Review).filter(Review.imported_at >= since).all()

    total = len(reviews)
    by_sentiment = {"positive": 0, "neutral": 0, "negative": 0}
    topic_counts: dict[str, int] = {}

    for r in reviews:
        if r.sentiment in by_sentiment:
            by_sentiment[r.sentiment] += 1
        for t in (r.topics or []):
            topic_counts[t] = topic_counts.get(t, 0) + 1

    promoters = sum(1 for r in reviews if (r.rating or 0) >= 9)
    detractors = sum(1 for r in reviews if (r.rating or 0) <= 6)
    nps = round(((promoters - detractors) / total * 100) if total else 0, 1)
    escalations = sum(1 for r in reviews if r.is_escalated)

    return {
        "period_start": since.date().isoformat(),
        "period_end": datetime.utcnow().date().isoformat(),
        "total_reviews": total,
        "by_sentiment": by_sentiment,
        "nps": nps,
        "escalations": escalations,
        "top_topics": sorted(topic_counts.items(), key=lambda x: -x[1])[:5],
    }


def dispatch_report(report: dict) -> None:
    api_key = settings.sendgrid_api_key
    recipient = settings.weekly_report_recipient

    if api_key and recipient:
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail

            body_lines = [
                f"Weekly Review Report ({report['period_start']} → {report['period_end']})",
                f"Total: {report['total_reviews']}",
                f"NPS: {report['nps']}",
                f"Sentiment: {report['by_sentiment']}",
                f"Top topics: {report['top_topics']}",
            ]
            message = Mail(
                from_email=f"reports@{settings.brand_name.lower()}.com",
                to_emails=recipient,
                subject=f"{settings.brand_name} — Weekly Review Digest",
                plain_text_content="\n".join(body_lines),
            )
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            sg.send(message)
            return
        except Exception:
            pass

    print("\n=== Weekly Review Report ===")
    print(f"Period : {report['period_start']} → {report['period_end']}")
    print(f"Total  : {report['total_reviews']}")
    print(f"NPS    : {report['nps']}")
    print(f"Sentiment breakdown: {report['by_sentiment']}")
    print(f"Top topics: {report['top_topics']}")
    print("============================\n")
