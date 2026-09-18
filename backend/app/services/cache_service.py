import json
from functools import lru_cache
from typing import Any

import redis

from app.core.config import get_settings

# The two read-heavy, rarely-changing public listings worth caching — see
# docs/ARCHITECTURE.md. Only the *unfiltered* electives listing is cached;
# a department-filtered request always reads straight from the DB, since
# department values aren't enumerable up front for invalidation.
ELECTIVES_LIST_CACHE_KEY = "electives:list:all"
FACULTY_LIST_CACHE_KEY = "faculty:list"

DEFAULT_TTL_SECONDS = 300

settings = get_settings()


@lru_cache
def _client() -> redis.Redis:
    # redis-py connects lazily on the first command, so caching the client
    # object itself is cheap and doesn't require Redis to be reachable yet.
    # A short timeout keeps a missing Redis (local dev without `docker
    # compose up`, the test suite) from adding noticeable latency to every
    # request — a real, same-network Redis responds in well under this.
    return redis.from_url(
        settings.redis_url, socket_connect_timeout=0.05, socket_timeout=0.05
    )


def get_cached(key: str) -> list[Any] | None:
    """Returns the cached value, or None on a miss OR if Redis is simply
    unavailable (not configured, not running locally, not present in the
    test environment). Caching is a pure performance layer here — every
    caller must already have a DB-backed fallback for a None result."""
    try:
        raw = _client().get(key)
    except Exception:
        return None
    return json.loads(raw) if raw else None


def set_cached(key: str, value: list[Any], ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
    try:
        _client().setex(key, ttl_seconds, json.dumps(value))
    except Exception:
        pass


def invalidate(*keys: str) -> None:
    if not keys:
        return
    try:
        _client().delete(*keys)
    except Exception:
        pass
