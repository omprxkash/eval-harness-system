import pytest
from app.services.routing_engine import route


class FakeReview:
    def __init__(self, body="", rating=3, sentiment="neutral"):
        self.body = body
        self.rating = rating
        self.sentiment = sentiment


def test_legal_escalation():
    r = FakeReview(body="I will take legal action against you.", rating=1, sentiment="negative")
    result = route(r)
    assert result["routed_to"] == "legal"
    assert result["is_escalated"] is True


def test_low_rating_negative_to_support():
    r = FakeReview(body="This is awful and broken.", rating=2, sentiment="negative")
    result = route(r)
    assert result["routed_to"] == "support"


def test_refund_keyword_to_support():
    r = FakeReview(body="I want a refund immediately.", rating=3, sentiment="neutral")
    result = route(r)
    assert result["routed_to"] == "support"


def test_cancel_keyword_to_support():
    r = FakeReview(body="Please cancel my subscription.", rating=3, sentiment="neutral")
    result = route(r)
    assert result["routed_to"] == "support"


def test_positive_high_rating_auto_response():
    r = FakeReview(body="Absolutely love it, works perfectly!", rating=5, sentiment="positive")
    result = route(r)
    assert result["routed_to"] == "auto_response"


def test_default_to_marketing():
    r = FakeReview(body="It is okay I guess.", rating=3, sentiment="neutral")
    result = route(r)
    assert result["routed_to"] == "marketing"


def test_legal_keyword_only_triggers_at_rating_1():
    r = FakeReview(body="I will get a lawyer.", rating=3, sentiment="neutral")
    result = route(r)
    assert result["routed_to"] != "legal"


def test_billing_error_to_support():
    r = FakeReview(body="I was charged incorrectly on my last invoice.", rating=2, sentiment="negative")
    result = route(r)
    assert result["routed_to"] == "support"
