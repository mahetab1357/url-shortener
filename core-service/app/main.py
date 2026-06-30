from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import shorten, stats

# Schema creation is intentionally NOT done here on startup - see
# app/db/init_db.py for why. Run `python -m app.db.init_db` once before
# starting the app (docker-compose's entrypoint does this automatically).
app = FastAPI(title="URL Shortener - Core Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_allowed_origins.split(",")],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# Registered before the router below: Starlette matches routes in
# registration order, and `GET /{short_code}` is a catch-all that would
# otherwise shadow `/health` (it'd match short_code="health" first).
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(stats.router)
app.include_router(shorten.router)
