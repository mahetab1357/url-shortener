"""Explicit schema creation, run once (e.g. as a docker-compose entrypoint
step or manually in local dev) rather than on every app boot. Doing this in
FastAPI's startup lifespan was tried first, but that causes two problems:
every replica races to create the same tables on each restart, and it makes
the app's startup implicitly depend on a live database - including during
tests, where TestClient's startup event would try to hit the real
PostgreSQL configured in Settings() instead of the test SQLite engine.
A real project would use Alembic migrations instead of create_all(); this
is the lightweight equivalent for this project's scope.
"""

from app.db.database import Base, engine
from app.models import url  # noqa: F401  (ensures the model is registered on Base)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
