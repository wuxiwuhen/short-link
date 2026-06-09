"""Integration tests for the URL shortener API."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# StaticPool ensures all connections share the same in-memory SQLite
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create tables once — StaticPool keeps the same connection
Base.metadata.create_all(bind=test_engine)


@pytest.fixture
def client():
    """Provide a test client with a clean database for each test."""
    with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
    return TestClient(app)


LONG_URL = "https://www.example.com/some/very/long/path?param=value&another=param"


class TestHealthCheck:
    def test_root(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


class TestShorten:
    def test_create_short_url(self, client):
        resp = client.post("/api/shorten", json={"url": LONG_URL})
        assert resp.status_code == 201
        data = resp.json()
        assert "short_url" in data
        assert data["original_url"] == LONG_URL
        assert data["short_url"].startswith("/")

    def test_duplicate_url_returns_same(self, client):
        resp1 = client.post("/api/shorten", json={"url": LONG_URL})
        resp2 = client.post("/api/shorten", json={"url": LONG_URL})
        assert resp1.json()["short_url"] == resp2.json()["short_url"]

    def test_invalid_url(self, client):
        resp = client.post("/api/shorten", json={"url": "not-a-url"})
        assert resp.status_code == 422


class TestRedirect:
    def test_redirect_works(self, client):
        create_resp = client.post("/api/shorten", json={"url": LONG_URL})
        short_url = create_resp.json()["short_url"]

        redirect_resp = client.get(short_url, follow_redirects=False)
        assert redirect_resp.status_code == 302
        assert redirect_resp.headers["location"] == LONG_URL

    def test_redirect_increments_clicks(self, client):
        create_resp = client.post("/api/shorten", json={"url": LONG_URL})
        short_id = create_resp.json()["short_url"].lstrip("/")

        client.get(f"/{short_id}", follow_redirects=False)
        client.get(f"/{short_id}", follow_redirects=False)

        stats_resp = client.get(f"/api/stats/{short_id}")
        assert stats_resp.json()["clicks"] == 2

    def test_redirect_404_for_unknown(self, client):
        resp = client.get("/nonexistent", follow_redirects=False)
        assert resp.status_code == 404


class TestStats:
    def test_stats(self, client):
        create_resp = client.post("/api/shorten", json={"url": LONG_URL})
        short_id = create_resp.json()["short_url"].lstrip("/")

        stats_resp = client.get(f"/api/stats/{short_id}")
        assert stats_resp.status_code == 200
        data = stats_resp.json()
        assert data["short_id"] == short_id
        assert data["clicks"] == 0

    def test_stats_404(self, client):
        resp = client.get("/api/stats/nonexistent")
        assert resp.status_code == 404
