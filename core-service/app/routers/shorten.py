import redis
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.db.database import get_db
from app.db.redis_client import get_redis
from app.mq.publisher import get_publisher
from app.mq.rabbitmq_client import RabbitMQPublisher
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.cache_service import cache_url, get_cached_url
from app.services.click_event import publish_click_event
from app.services.url_service import (
    AliasTakenError,
    CollisionRetriesExhaustedError,
    create_short_url,
    get_short_url,
)

router = APIRouter()


@router.post("/shorten", response_model=ShortenResponse, status_code=status.HTTP_201_CREATED)
def shorten_url(payload: ShortenRequest, db: Session = Depends(get_db)) -> ShortenResponse:
    try:
        row = create_short_url(
            db,
            original_url=str(payload.url),
            custom_alias=payload.custom_alias,
            expires_at=payload.expires_at,
        )
    except AliasTakenError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except CollisionRetriesExhaustedError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not allocate a short code, please retry",
        ) from exc

    return ShortenResponse(
        short_code=row.short_code,
        short_url=f"{settings.base_host}/{row.short_code}",
        original_url=row.original_url,
        created_at=row.created_at,
        expires_at=row.expires_at,
    )


@router.get("/{short_code}")
def redirect_to_original(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    cache: redis.Redis = Depends(get_redis),
    publisher: RabbitMQPublisher = Depends(get_publisher),
) -> RedirectResponse:
    cached_url = get_cached_url(cache, short_code)
    if cached_url is not None:
        background_tasks.add_task(publish_click_event, publisher, short_code, request)
        return RedirectResponse(url=cached_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    row = get_short_url(db, short_code)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found")
    if row.is_expired():
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="This link has expired")

    cache_url(cache, short_code, row.original_url, expires_at=row.expires_at)
    background_tasks.add_task(publish_click_event, publisher, short_code, request)
    return RedirectResponse(url=row.original_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
