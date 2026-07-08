import time


class TTLCache:
    """Very small in-process cache, good enough for a single-instance API.

    Not shared across workers/processes - if this ever needs to scale
    horizontally, swap this out for Redis and keep the same get/set/clear
    interface so the rest of the app doesn't change.
    """

    def __init__(self, ttl_seconds: int = 60):
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[float, object]] = {}

    def get(self, key: str):
        item = self._store.get(key)
        if item is None:
            return None
        expires_at, value = item
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value):
        self._store[key] = (time.monotonic() + self.ttl_seconds, value)

    def clear(self):
        self._store.clear()
