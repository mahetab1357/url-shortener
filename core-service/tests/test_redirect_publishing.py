def test_redirect_cache_miss_publishes_click_event(client, fake_publisher):
    create_resp = client.post("/shorten", json={"url": "https://example.com/track-me"})
    short_code = create_resp.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False, headers={"Referer": "https://x.com"})

    assert len(fake_publisher.published) == 1
    event = fake_publisher.published[0]
    assert event["short_code"] == short_code
    assert event["referrer"] == "https://x.com"


def test_redirect_cache_hit_also_publishes_click_event(client, fake_publisher):
    create_resp = client.post("/shorten", json={"url": "https://example.com/track-me-too"})
    short_code = create_resp.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)  # cache miss -> populates cache
    client.get(f"/{short_code}", follow_redirects=False)  # cache hit

    assert len(fake_publisher.published) == 2
    assert all(e["short_code"] == short_code for e in fake_publisher.published)


def test_redirect_404_does_not_publish_click_event(client, fake_publisher):
    client.get("/no-such-code", follow_redirects=False)
    assert fake_publisher.published == []


def test_redirect_expired_does_not_publish_click_event(client, fake_publisher):
    from datetime import datetime, timedelta, timezone

    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    create_resp = client.post(
        "/shorten", json={"url": "https://example.com/expired", "expires_at": past}
    )
    short_code = create_resp.json()["short_code"]

    client.get(f"/{short_code}", follow_redirects=False)
    assert fake_publisher.published == []
