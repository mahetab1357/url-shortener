from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.url import UrlStatsResponse
from app.services.analytics_client import AnalyticsClient, get_analytics_client
from app.services.stats_service import build_stats_response
from app.services.url_service import get_short_url

router = APIRouter()


@router.get("/api/urls/{short_code}/stats", response_model=UrlStatsResponse)
def get_url_stats(
    short_code: str,
    db: Session = Depends(get_db),
    analytics_client: AnalyticsClient = Depends(get_analytics_client),
) -> UrlStatsResponse:
    row = get_short_url(db, short_code)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found")

    analytics = analytics_client.get_stats(short_code)
    return build_stats_response(row, analytics)
