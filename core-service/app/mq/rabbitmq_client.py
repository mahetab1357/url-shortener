import json
import logging
import threading

import pika
import pika.exceptions

logger = logging.getLogger(__name__)

CLICK_EVENTS_QUEUE = "click_events"


class RabbitMQPublisher:
    """Thin wrapper that lazily opens (and reopens, if dropped) a single
    blocking connection/channel, reused across publishes rather than
    paying a TCP + AMQP handshake per redirect.

    pika's BlockingConnection is explicitly documented as not safe to use
    concurrently from multiple threads - but FastAPI runs sync endpoints
    (like our redirect handler) across a real thread pool, so concurrent
    requests do call publish() concurrently. A load test against this
    exact setup showed it: ~8,500 of ~8,650 publishes failed with
    `pika.exceptions.ChannelWrongStateError` under 100 concurrent users
    (silently, since publish() swallows exceptions by design - the
    redirects themselves never failed, but click events were being
    dropped almost entirely). A lock serializes access to the shared
    channel so only one thread touches it at a time, which is correct
    per pika's threading model and cheap here since publishing is
    fire-and-forget background work, not on the response's critical path.
    """

    def __init__(self, url: str):
        self._url = url
        self._connection: pika.BlockingConnection | None = None
        self._channel = None
        self._lock = threading.Lock()

    def _ensure_channel(self):
        if self._connection is None or self._connection.is_closed:
            self._connection = pika.BlockingConnection(pika.URLParameters(self._url))
            self._channel = self._connection.channel()
            self._channel.queue_declare(queue=CLICK_EVENTS_QUEUE, durable=True)
        return self._channel

    def publish(self, event: dict) -> None:
        """Publish a click event. Never raises - a queue outage must not
        break redirects, since redirecting correctly matters far more than
        recording analytics for any single click."""
        try:
            with self._lock:
                channel = self._ensure_channel()
                channel.basic_publish(
                    exchange="",
                    routing_key=CLICK_EVENTS_QUEUE,
                    body=json.dumps(event),
                    properties=pika.BasicProperties(
                        content_type="application/json",
                        delivery_mode=pika.DeliveryMode.Persistent,
                    ),
                )
        except Exception:
            logger.exception("Failed to publish click event to RabbitMQ; dropping event")

    def close(self) -> None:
        if self._connection is not None and self._connection.is_open:
            self._connection.close()


def build_publisher(url: str) -> RabbitMQPublisher:
    return RabbitMQPublisher(url)
