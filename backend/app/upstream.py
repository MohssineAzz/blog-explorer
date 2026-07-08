import httpx

from .cache import TTLCache

BASE_URL = "https://jsonplaceholder.typicode.com"

# Users/posts on the upstream barely ever change, comments a bit less rarely -
# a longer TTL is fine and keeps us from hammering a free public API.
cache = TTLCache(ttl_seconds=120)


class UpstreamError(Exception):
    """Raised when JSONPlaceholder is unreachable or returns a server error."""


class NotFoundError(Exception):
    """Raised when the requested resource doesn't exist upstream."""


async def _get(path: str):
    cached = cache.get(path)
    if cached is not None:
        return cached

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{BASE_URL}{path}")
    except httpx.RequestError as exc:
        raise UpstreamError(f"could not reach JSONPlaceholder: {exc}") from exc

    if response.status_code == 404:
        raise NotFoundError(path)
    if response.status_code >= 500:
        raise UpstreamError(f"upstream returned {response.status_code} for {path}")

    data = response.json()
    cache.set(path, data)
    return data


async def get_users():
    return await _get("/users")


async def get_user(user_id: int):
    user = await _get(f"/users/{user_id}")
    if not user:
        raise NotFoundError(f"user {user_id}")
    return user


async def get_posts():
    return await _get("/posts")


async def get_post(post_id: int):
    post = await _get(f"/posts/{post_id}")
    if not post:
        raise NotFoundError(f"post {post_id}")
    return post


async def get_comments():
    return await _get("/comments")


async def get_comments_for_post(post_id: int):
    all_comments = await get_comments()
    return [c for c in all_comments if c["postId"] == post_id]
