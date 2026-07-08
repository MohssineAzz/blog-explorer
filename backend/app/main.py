import math

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import upstream

app = FastAPI(title="Blog Explorer API")

# Wide open for local dev - the frontend is just static files served from a
# different port. Would lock this down to a specific origin before any real
# deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/users")
async def list_users():
    try:
        return await upstream.get_users()
    except upstream.UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    try:
        user = await upstream.get_user(user_id)
        posts = await upstream.get_posts()
    except upstream.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except upstream.UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    user_posts = [p for p in posts if p["userId"] == user_id]
    return {**user, "posts": user_posts}


@app.get("/posts")
async def list_posts(
    userId: int | None = None,
    q: str | None = Query(None, description="filter by title, case-insensitive"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    try:
        posts = await upstream.get_posts()
    except upstream.UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if userId is not None:
        posts = [p for p in posts if p["userId"] == userId]
    if q:
        needle = q.lower()
        posts = [p for p in posts if needle in p["title"].lower()]

    total = len(posts)
    start = (page - 1) * limit
    page_items = posts[start : start + limit]

    return {
        "items": page_items,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": math.ceil(total / limit) if limit else 0,
    }


@app.get("/posts/{post_id}")
async def get_post(post_id: int):
    try:
        post = await upstream.get_post(post_id)
        author = await upstream.get_user(post["userId"])
        comments = await upstream.get_comments_for_post(post_id)
    except upstream.NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except upstream.UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {**post, "author": author, "comments": comments}
