from datetime import datetime


_LEGAL_KEYWORDS = ["legal", "lawsuit", "court", "sue", "attorney", "lawyer"]
_REFUND_KEYWORDS = ["refund", "cancel", "cancellation", "money back", "charge back", "chargeback", "charged incorrectly", "billing error"]


def route(review) -> dict:
    body_lower = (review.body or "").lower()
    rating = review.rating or 3
    sentiment = review.sentiment or "neutral"

    if rating <= 1 and any(k in body_lower for k in _LEGAL_KEYWORDS):
        return {"routed_to": "legal", "is_escalated": True}

    if rating <= 2 and sentiment == "negative":
        return {"routed_to": "support", "is_escalated": False}

    if any(k in body_lower for k in _REFUND_KEYWORDS):
        return {"routed_to": "support", "is_escalated": False}

    if sentiment == "positive" and rating >= 4:
        return {"routed_to": "auto_response", "is_escalated": False}

    return {"routed_to": "marketing", "is_escalated": False}


def apply_routing(db, review) -> None:
    result = route(review)
    review.routed_to = result["routed_to"]
    review.is_escalated = result["is_escalated"]
    review.routed_at = datetime.utcnow()
    db.commit()
