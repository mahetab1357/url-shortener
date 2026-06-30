from app.models.url import ShortUrl
from app.schemas.url import (
    DailyBucket,
    DeviceBreakdownItem,
    HourlyBucket,
    ReferrerBreakdownItem,
    UrlStatsResponse,
)


def build_stats_response(row: ShortUrl, analytics: dict | None) -> UrlStatsResponse:
    """Combines core-service's own row with analytics-service's response
    (translating its camelCase JSON into our snake_case schema). `analytics`
    is None when analytics-service couldn't be reached - in that case we
    return zeroed-out analytics rather than failing the whole request."""
    if analytics is None:
        return UrlStatsResponse(
            short_code=row.short_code,
            original_url=row.original_url,
            created_at=row.created_at,
            expires_at=row.expires_at,
            total_clicks=0,
            last_clicked_at=None,
            hourly_clicks=[],
            daily_clicks=[],
            device_breakdown=[],
            referrer_breakdown=[],
            analytics_available=False,
        )

    return UrlStatsResponse(
        short_code=row.short_code,
        original_url=row.original_url,
        created_at=row.created_at,
        expires_at=row.expires_at,
        total_clicks=analytics.get("totalClicks", 0),
        last_clicked_at=analytics.get("lastClickedAt"),
        hourly_clicks=[
            HourlyBucket(hour_start=b["hourStart"], count=b["count"])
            for b in analytics.get("hourlyClicks", [])
        ],
        daily_clicks=[
            DailyBucket(date=b["date"], count=b["count"]) for b in analytics.get("dailyClicks", [])
        ],
        device_breakdown=[
            DeviceBreakdownItem(device_type=d["deviceType"], browser=d["browser"], count=d["count"])
            for d in analytics.get("deviceBreakdown", [])
        ],
        referrer_breakdown=[
            ReferrerBreakdownItem(referrer_domain=r["referrerDomain"], count=r["count"])
            for r in analytics.get("referrerBreakdown", [])
        ],
        analytics_available=True,
    )
