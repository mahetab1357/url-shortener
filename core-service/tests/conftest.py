import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db.redis_client import get_redis
from app.main import app
from app.mq.publisher import get_publisher
from app.services.analytics_client import get_analytics_client

# Tests run against an in-memory SQLite DB rather than PostgreSQL.
# Tradeoff: SQLite isn't a perfect stand-in (different IntegrityError
# nuances, no real concurrency), but it makes unit/integration tests run
# in milliseconds with zero external dependencies, which matters for fast
# CI feedback. Postgres-specific behaviour is exercised by docker-compose
# integration testing of the full stack, not pytest.
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture()
def test_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session(test_engine):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def fake_redis():
    # fakeredis implements the same client interface as redis.Redis, so
    # app code under test (cache_service.py, the router) doesn't know the
    # difference - this lets us test real cache-hit/miss/TTL behaviour
    # without a running Redis server.
    client = fakeredis.FakeStrictRedis(decode_responses=True)
    yield client
    client.flushall()


class FakePublisher:
    """Stand-in for RabbitMQPublisher that records events instead of
    talking to a real broker - lets tests assert on exactly what would
    have been published without needing RabbitMQ running."""

    def __init__(self):
        self.published: list[dict] = []

    def publish(self, event: dict) -> None:
        self.published.append(event)


@pytest.fixture()
def fake_publisher():
    return FakePublisher()


class FakeAnalyticsClient:
    """Stand-in for AnalyticsClient - tests set `.response` to control what
    get_stats() returns, including None to simulate analytics-service
    being unreachable."""

    def __init__(self):
        self.response: dict | None = None
        self.requested_codes: list[str] = []

    def get_stats(self, short_code: str) -> dict | None:
        self.requested_codes.append(short_code)
        return self.response


@pytest.fixture()
def fake_analytics_client():
    return FakeAnalyticsClient()


@pytest.fixture()
def client(test_engine, fake_redis, fake_publisher, fake_analytics_client):
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_redis():
        return fake_redis

    def override_get_publisher():
        return fake_publisher

    def override_get_analytics_client():
        return fake_analytics_client

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_publisher] = override_get_publisher
    app.dependency_overrides[get_analytics_client] = override_get_analytics_client
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
