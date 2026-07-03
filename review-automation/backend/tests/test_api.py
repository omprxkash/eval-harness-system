import io
from unittest.mock import patch


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_import_csv(client):
    csv_content = (
        "id,author,rating,title,body,received_at\n"
        "1,Alice,5,Great product,I love this product it works perfectly,2025-10-01\n"
        "2,Bob,1,Terrible,This is broken and I want a refund,2025-10-02\n"
    )
    with patch("app.tasks.analyze.analyze_review.delay"):
        resp = client.post(
            "/reviews/import",
            files={"file": ("reviews.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["imported"] == 2
    assert len(data["review_ids"]) == 2


def test_import_non_csv_rejected(client):
    resp = client.post(
        "/reviews/import",
        files={"file": ("reviews.txt", io.BytesIO(b"not a csv"), "text/plain")},
    )
    assert resp.status_code == 400


def test_webhook(client):
    with patch("app.tasks.analyze.analyze_review.delay"):
        resp = client.post(
            "/reviews/webhook",
            json={"body": "Great experience overall", "author": "Carol", "rating": 4, "source": "web"},
        )
    assert resp.status_code == 200
    assert resp.json()["queued"] is True


def test_webhook_empty_body(client):
    resp = client.post("/reviews/webhook", json={"author": "Dan"})
    assert resp.status_code == 422


def test_list_reviews(client):
    resp = client.get("/reviews")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


def test_analytics_nps(client):
    resp = client.get("/analytics/nps")
    assert resp.status_code == 200
    assert "nps" in resp.json()


def test_analytics_trends(client):
    resp = client.get("/analytics/trends")
    assert resp.status_code == 200
    assert "trends" in resp.json()


def test_analytics_heatmap(client):
    resp = client.get("/analytics/topic-heatmap")
    assert resp.status_code == 200
    assert "heatmap" in resp.json()


def test_import_empty_csv(client):
    csv_content = "id,author,rating,title,body,received_at\n"
    import io
    from unittest.mock import patch
    with patch("app.tasks.analyze.analyze_review.delay"):
        resp = client.post(
            "/reviews/import",
            files={"file": ("empty.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        )
    assert resp.status_code == 200
    assert resp.json()["imported"] == 0
