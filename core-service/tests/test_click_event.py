from starlette.datastructures import Headers
from starlette.requests import Request

from app.services.click_event import build_click_event


def _make_request(headers: dict, client_host: str = "10.0.0.5") -> Request:
    scope = {
        "type": "http",
        "headers": Headers(headers).raw,
        "client": (client_host, 12345),
    }
    return Request(scope)


def test_build_click_event_extracts_headers():
    request = _make_request(
        {
            "user-agent": "Mozilla/5.0 TestAgent",
            "referer": "https://google.com",
        }
    )
    event = build_click_event("abc1234", request)

    assert event["short_code"] == "abc1234"
    assert event["user_agent"] == "Mozilla/5.0 TestAgent"
    assert event["referrer"] == "https://google.com"
    assert event["ip"] == "10.0.0.5"
    assert "timestamp" in event


def test_build_click_event_prefers_x_forwarded_for():
    request = _make_request({"x-forwarded-for": "203.0.113.7, 10.0.0.1"})
    event = build_click_event("abc1234", request)
    assert event["ip"] == "203.0.113.7"


def test_build_click_event_handles_missing_optional_headers():
    request = _make_request({})
    event = build_click_event("abc1234", request)
    assert event["user_agent"] is None
    assert event["referrer"] is None
