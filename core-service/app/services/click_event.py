from datetime import datetime, timezone

from fastapi import Request

from app.mq.rabbitmq_client import RabbitMQPublisher


def _client_ip(request: Request) -> str | None:
    # Trust X-Forwarded-For when present (we sit behind a reverse proxy in
    # docker-compose); fall back to the direct peer address otherwise.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def build_click_event(short_code: str, request: Request) -> dict:
    return {
        "short_code": short_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_agent": request.headers.get("user-agent"),
        "referrer": request.headers.get("referer"),
        # Raw IP only - resolving this to a country/city is deferred to a
        # future enrichment step so the redirect path never blocks on an
        # external geo-IP lookup.
        "ip": _client_ip(request),
    }


def publish_click_event(publisher: RabbitMQPublisher, short_code: str, request: Request) -> None:
    event = build_click_event(short_code, request)
    publisher.publish(event)
