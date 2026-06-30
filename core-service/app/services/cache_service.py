from datetime import datetime, timezone

import redis

CACHE_KEY_PREFIX = "shorturl:"
DEFAULT_TTL_SECONDS = 24 * 60 * 60  # 24h: long enough to absorb a viral spike,
# short enough that a manually-deleted/rotated row doesn't haunt the cache forever.


def _cache_key(short_code: str) -> str:
    return f"{CACHE_KEY_PREFIX}{short_code}"


def get_cached_url(client: redis.Redis, short_code: str) -> str | None:
    return client.get(_cache_key(short_code))


def cache_url(
    client: redis.Redis,
    short_code: str,
    original_url: str,
    expires_at: datetime | None = None,
) -> None:
    ttl = DEFAULT_TTL_SECONDS
    if expires_at is not None:
        seconds_until_expiry = (expires_at - datetime.now(timezone.utc)).total_seconds()
        ttl = max(1, min(ttl, int(seconds_until_expiry)))
    client.set(_cache_key(short_code), original_url, ex=ttl)
