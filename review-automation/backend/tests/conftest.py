import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app

TEST_DB_URL = "sqlite:///./test_reviews.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def positive_review_data():
    return {
        "body": "Excellent product, very happy with the quality and fast delivery!",
        "rating": 5,
        "author": "Test User",
        "title": "Great product",
    }


@pytest.fixture
def negative_review_data():
    return {
        "body": "Terrible experience. Broken on arrival. Want a refund immediately.",
        "rating": 1,
        "author": "Unhappy Customer",
        "title": "Awful",
    }
