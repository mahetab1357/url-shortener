from app.models.url import ShortUrl
from app.services.cache_service import cache_url, get_cached_url


def test_first_redirect_is_a_cache_miss_and_populates_cache(client, fake_redis):
    create_resp = client.post("/shorten", json={"url": "https://example.com/populate-me"})
    short_code = create_resp.json()["short_code"]

    assert get_cached_url(fake_redis, short_code) is None  # nothing cached yet

    resp = client.get(f"/{short_code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/populate-me"

    # The miss path should have written through to the cache.
    assert get_cached_url(fake_redis, short_code) == "https://example.com/populate-me"


def test_redirect_serves_from_cache_without_touching_db(client, fake_redis, db_session):
    create_resp = client.post("/shorten", json={"url": "https://example.com/original"})
    short_code = create_resp.json()["short_code"]

    # Prime the cache with a *different* value than what's in Postgres, then
    # delete the row from the DB entirely. If the redirect still succeeds
    # and returns the cached value, that proves the DB wasn't consulted.
    cache_url(fake_redis, short_code, "https://example.com/from-cache")
    db_session.query(ShortUrl).filter(ShortUrl.short_code == short_code).delete()
    db_session.commit()

    resp = client.get(f"/{short_code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com/from-cache"


def test_redirect_unknown_code_does_not_populate_cache(client, fake_redis):
    resp = client.get("/totally-unknown-code", follow_redirects=False)
    assert resp.status_code == 404
    assert get_cached_url(fake_redis, "totally-unknown-code") is None


def test_expired_link_is_not_cached_on_miss(client, fake_redis):
    from datetime import datetime, timedelta, timezone

    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    create_resp = client.post(
        "/shorten", json={"url": "https://example.com/expired", "expires_at": past}
    )
    short_code = create_resp.json()["short_code"]

    resp = client.get(f"/{short_code}", follow_redirects=False)
    assert resp.status_code == 410
    assert get_cached_url(fake_redis, short_code) is None
