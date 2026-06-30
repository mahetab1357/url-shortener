import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class AnalyticsClient:
    """Talks to analytics-service over HTTP. Returns None on any failure
    (timeout, connection refused, non-2xx, bad JSON) rather than raising -
    callers treat "analytics unavailable" as a normal, expected case to
    degrade gracefully from, not an exceptional one."""

    def __init__(self, base_url: str, timeout_seconds: float):
        self._base_url = base_url.rstrip("/")
        # A single float timeout applies separately to *each* connection
        # attempt httpx/httpcore makes - when "down" means connection
        # refused, the OS may be tried over both IPv6 and IPv4 for the
        # same hostname, doubling the wall-clock time to detect a dead
        # service (measured ~4s instead of the configured 2s on Windows).
        # Capping `connect` tighter than `read` makes "service is down"
        # detection fast without shortening the budget for a slow-but-
        # alive response.
        connect_budget = min(0.5, timeout_seconds)
        self._timeout = httpx.Timeout(timeout_seconds, connect=connect_budget)

    def get_stats(self, short_code: str) -> dict | None:
        try:
            response = httpx.get(
                f"{self._base_url}/api/analytics/{short_code}/stats",
                timeout=self._timeout,
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError):
            logger.warning("analytics-service call failed for %s", short_code, exc_info=True)
            return None


_client = AnalyticsClient(settings.analytics_service_url, settings.analytics_request_timeout_seconds)


def get_analytics_client() -> AnalyticsClient:
    return _client
