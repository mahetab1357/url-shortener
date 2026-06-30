from datetime import datetime, timezone

from app.models.url import ShortUrl
from app.services.stats_service import build_stats_response


def _sample_row() -> ShortUrl:
    row = ShortUrl(short_code="abc1234", original_url="https://example.com")
    row.created_at = datetime(2026, 6, 29, 10, 0, 0, tzinfo=timezone.utc)
    row.expires_at = None
    return row


def test_build_stats_response_with_no_analytics_returns_zeros():
    response = build_stats_response(_sample_row(), analytics=None)

    assert response.analytics_available is False
    assert response.total_clicks == 0
    assert response.last_clicked_at is None
    assert response.hourly_clicks == []
    assert response.device_breakdown == []
    assert response.original_url == "https://example.com"


def test_build_stats_response_translates_camelcase_analytics_payload():
    analytics = {
        "shortCode": "abc1234",
        "totalClicks": 7,
        "lastClickedAt": "2026-06-29T11:30:00Z",
        "hourlyClicks": [{"hourStart": "2026-06-29T10:00:00Z", "count": 3}],
        "dailyClicks": [{"date": "2026-06-29", "count": 7}],
        "deviceBreakdown": [{"deviceType": "Desktop", "browser": "Chrome", "count": 5}],
        "referrerBreakdown": [{"referrerDomain": "google.com", "count": 2}],
    }

    response = build_stats_response(_sample_row(), analytics)

    assert response.analytics_available is True
    assert response.total_clicks == 7
    assert response.hourly_clicks[0].count == 3
    assert response.daily_clicks[0].date == "2026-06-29"
    assert response.device_breakdown[0].device_type == "Desktop"
    assert response.device_breakdown[0].browser == "Chrome"
    assert response.referrer_breakdown[0].referrer_domain == "google.com"


def test_build_stats_response_handles_missing_optional_analytics_fields():
    analytics = {"shortCode": "abc1234", "totalClicks": 0}
    response = build_stats_response(_sample_row(), analytics)

    assert response.analytics_available is True
    assert response.total_clicks == 0
    assert response.hourly_clicks == []
    assert response.daily_clicks == []
