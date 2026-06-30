from datetime import datetime, timedelta, timezone

from app.services.cache_service import DEFAULT_TTL_SECONDS, cache_url, get_cached_url


def test_cache_miss_returns_none(fake_redis):
    assert get_cached_url(fake_redis, "missing") is None


def test_cache_url_then_get_returns_value(fake_redis):
    cache_url(fake_redis, "abc1234", "https://example.com")
    assert get_cached_url(fake_redis, "abc1234") == "https://example.com"


def test_cache_url_sets_default_ttl(fake_redis):
    cache_url(fake_redis, "abc1234", "https://example.com")
    ttl = fake_redis.ttl("shorturl:abc1234")
    assert 0 < ttl <= DEFAULT_TTL_SECONDS


def test_cache_url_caps_ttl_at_expiry(fake_redis):
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=30)
    cache_url(fake_redis, "abc1234", "https://example.com", expires_at=expires_at)
    ttl = fake_redis.ttl("shorturl:abc1234")
    assert 0 < ttl <= 30
