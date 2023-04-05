import pytest
from app.asgi import app
from app.db import Session, User
from fastapi.testclient import TestClient


@pytest.fixture
def client() -> TestClient:
    """Instance of application client for tests"""
    return TestClient(app)


@pytest.fixture
def clean_test_data() -> None:
    """Applies db cleaning before tests (if anything left) and after"""
    clean_db()
    yield
    clean_db()


def clean_db():
    """Cleans test data from database"""
    s = Session()
    s.query(User).filter(User.email == "test@assignit.com").delete()
    s.query(User).filter(User.email == "test-repeat@assignit.com").delete()
    s.commit()
