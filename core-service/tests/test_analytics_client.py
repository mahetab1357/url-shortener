import httpx

from app.services.analytics_client import AnalyticsClient


def test_get_stats_returns_parsed_json_on_success(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/analytics/abc1234/stats"
        return httpx.Response(200, json={"shortCode": "abc1234", "totalClicks": 5})

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        "app.services.analytics_client.httpx.get",
        lambda url, timeout: httpx.Client(transport=transport).get(url),
    )

    client = AnalyticsClient(base_url="http://analytics-service:8081", timeout_seconds=1.0)
    result = client.get_stats("abc1234")

    assert result == {"shortCode": "abc1234", "totalClicks": 5}


def test_get_stats_returns_none_on_non_2xx(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500)

    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(
        "app.services.analytics_client.httpx.get",
        lambda url, timeout: httpx.Client(transport=transport).get(url),
    )

    client = AnalyticsClient(base_url="http://analytics-service:8081", timeout_seconds=1.0)
    assert client.get_stats("abc1234") is None


def test_get_stats_returns_none_on_connection_error(monkeypatch):
    def raise_connect_error(url, timeout):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr("app.services.analytics_client.httpx.get", raise_connect_error)

    client = AnalyticsClient(base_url="http://analytics-service:8081", timeout_seconds=1.0)
    assert client.get_stats("abc1234") is None


def test_get_stats_returns_none_on_timeout(monkeypatch):
    def raise_timeout(url, timeout):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr("app.services.analytics_client.httpx.get", raise_timeout)

    client = AnalyticsClient(base_url="http://analytics-service:8081", timeout_seconds=1.0)
    assert client.get_stats("abc1234") is None
