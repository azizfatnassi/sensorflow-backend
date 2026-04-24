import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db

SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function", autouse=True)
def db_session(setup_db):
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, base_url="http://localhost") as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def auth_client(client):
    r1 = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    })
    print("\n[DEBUG] register:", r1.status_code, r1.json())

    r2 = client.post("/api/auth/token", data={
        "username": "test@example.com",
        "password": "testpassword123"
    })
    print("[DEBUG] token:", r2.status_code, r2.json())

    token = r2.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client