"""
Pytest Configuration und Shared Fixtures
Diese Datei enthaelt gemeinsame Test-Fixtures fuer alle Tests.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash
from app.core.rate_limit import limiter


# Test Database Setup (SQLite in-memory)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """
    Erstellt eine frische Test-Datenbank fuer jeden Test.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """
    Erstellt einen FastAPI TestClient mit der Test-Datenbank.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    limiter._storage.reset()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data() -> dict:
    """
    Beispiel User-Daten fuer Tests.
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }


@pytest.fixture
def test_user(db: Session, test_user_data: dict) -> User:
    """
    Erstellt einen Test-User in der Datenbank.
    """
    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"]),
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def authenticated_client(client: TestClient, test_user: User, test_user_data: dict) -> tuple[TestClient, str]:
    """
    Erstellt einen authentifizierten Client mit gueltigem Token.
    Returns: (client, access_token)
    """
    # Login to get token
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    # Set authorization header
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }

    return client, token


@pytest.fixture
def multiple_test_users(db: Session) -> list[User]:
    """
    Erstellt mehrere Test-User fuer komplexere Tests.
    """
    users = []
    for i in range(3):
        user = User(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            hashed_password=get_password_hash(f"password{i}"),
            is_active=True,
            is_verified=True
        )
        db.add(user)
        users.append(user)

    db.commit()
    for user in users:
        db.refresh(user)

    return users
