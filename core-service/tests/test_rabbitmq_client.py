import threading
import time
from unittest.mock import patch

from app.mq.rabbitmq_client import RabbitMQPublisher


def test_publish_swallows_connection_errors():
    """If RabbitMQ is unreachable, publish() must not raise - a queue
    outage must never break the redirect path that calls it."""
    publisher = RabbitMQPublisher("amqp://guest:guest@nonexistent-host:5672/")
    with patch(
        "pika.BlockingConnection", side_effect=ConnectionError("could not connect")
    ):
        publisher.publish({"short_code": "abc1234"})  # should not raise


def test_publish_sends_expected_payload():
    publisher = RabbitMQPublisher("amqp://guest:guest@localhost:5672/")

    fake_channel = type(
        "FakeChannel",
        (),
        {"queue_declare": lambda self, **kw: None, "basic_publish": lambda self, **kw: None},
    )()
    fake_connection = type(
        "FakeConnection",
        (),
        {"is_closed": False, "is_open": True, "channel": lambda self: fake_channel},
    )()

    calls = []
    fake_channel.basic_publish = lambda **kw: calls.append(kw)

    with patch("pika.BlockingConnection", return_value=fake_connection):
        publisher.publish({"short_code": "abc1234", "ip": "1.2.3.4"})

    assert len(calls) == 1
    assert calls[0]["routing_key"] == "click_events"
    assert b'"short_code": "abc1234"' in calls[0]["body"].encode()


def test_publish_serializes_concurrent_calls_across_threads():
    """Regression test for a real bug found under load testing: pika's
    BlockingConnection/Channel is documented as not thread-safe, but
    FastAPI runs sync endpoints (including the redirect handler that
    calls publish()) across a real thread pool. A 100-concurrent-user
    Locust run against this exact code path produced ~8,500 silent
    `ChannelWrongStateError` failures out of ~8,650 publishes. The fix is
    a lock around the critical section; this test proves it actually
    serializes access - if the lock were removed, `max_concurrent_in_section`
    below would exceed 1.
    """
    publisher = RabbitMQPublisher("amqp://guest:guest@localhost:5672/")

    in_section = 0
    max_concurrent_in_section = 0
    section_lock = threading.Lock()  # protects the counters themselves, not the code under test
    calls = []

    def fake_basic_publish(**kwargs):
        nonlocal in_section, max_concurrent_in_section
        with section_lock:
            in_section += 1
            max_concurrent_in_section = max(max_concurrent_in_section, in_section)
        time.sleep(0.01)  # widen the window a race would need to land in
        calls.append(kwargs)
        with section_lock:
            in_section -= 1

    fake_channel = type(
        "FakeChannel",
        (),
        {"queue_declare": lambda self, **kw: None, "basic_publish": lambda self, **kw: None},
    )()
    fake_channel.basic_publish = fake_basic_publish
    fake_connection = type(
        "FakeConnection",
        (),
        {"is_closed": False, "is_open": True, "channel": lambda self: fake_channel},
    )()

    with patch("pika.BlockingConnection", return_value=fake_connection):
        threads = [
            threading.Thread(target=publisher.publish, args=({"short_code": f"code{i}"},))
            for i in range(20)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

    assert len(calls) == 20, "every publish should succeed, none silently dropped"
    assert max_concurrent_in_section == 1, (
        "two threads were inside the critical section at once - "
        "the lock isn't actually serializing access"
    )
