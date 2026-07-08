import pytest
from fastapi.testclient import TestClient

from app import upstream
from app.main import app

FAKE_USERS = [
    {"id": 1, "name": "Leanne Graham", "email": "leanne@example.com"},
    {"id": 2, "name": "Ervin Howell", "email": "ervin@example.com"},
]

FAKE_POSTS = [
    {"id": 1, "userId": 1, "title": "First post", "body": "hello"},
    {"id": 2, "userId": 1, "title": "Second post", "body": "world"},
    {"id": 3, "userId": 2, "title": "Another author", "body": "hi"},
]

FAKE_COMMENTS = [
    {"id": 1, "postId": 1, "name": "nice", "body": "great read", "email": "a@b.com"},
    {"id": 2, "postId": 2, "name": "meh", "body": "could be better", "email": "c@d.com"},
]


@pytest.fixture(autouse=True)
def patch_upstream(monkeypatch):
    async def fake_get_users():
        return FAKE_USERS

    async def fake_get_user(user_id):
        for u in FAKE_USERS:
            if u["id"] == user_id:
                return u
        raise upstream.NotFoundError(f"user {user_id}")

    async def fake_get_posts():
        return FAKE_POSTS

    async def fake_get_post(post_id):
        for p in FAKE_POSTS:
            if p["id"] == post_id:
                return p
        raise upstream.NotFoundError(f"post {post_id}")

    async def fake_get_comments_for_post(post_id):
        return [c for c in FAKE_COMMENTS if c["postId"] == post_id]

    monkeypatch.setattr(upstream, "get_users", fake_get_users)
    monkeypatch.setattr(upstream, "get_user", fake_get_user)
    monkeypatch.setattr(upstream, "get_posts", fake_get_posts)
    monkeypatch.setattr(upstream, "get_post", fake_get_post)
    monkeypatch.setattr(upstream, "get_comments_for_post", fake_get_comments_for_post)


client = TestClient(app)


def test_list_users():
    res = client.get("/users")
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_user_detail_includes_their_posts():
    res = client.get("/users/1")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "Leanne Graham"
    assert len(body["posts"]) == 2


def test_user_detail_404_for_unknown_id():
    res = client.get("/users/999")
    assert res.status_code == 404


def test_list_posts_filters_by_user():
    res = client.get("/posts", params={"userId": 2})
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "Another author"


def test_list_posts_search_by_title():
    res = client.get("/posts", params={"q": "first"})
    body = res.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == 1


def test_list_posts_pagination():
    res = client.get("/posts", params={"page": 1, "limit": 2})
    body = res.json()
    assert len(body["items"]) == 2
    assert body["totalPages"] == 2


def test_post_detail_includes_author_and_comments():
    res = client.get("/posts/1")
    body = res.json()
    assert body["author"]["name"] == "Leanne Graham"
    assert len(body["comments"]) == 1


def test_post_detail_404_for_unknown_id():
    res = client.get("/posts/999")
    assert res.status_code == 404


def test_invalid_id_is_rejected():
    res = client.get("/posts/not-a-number")
    assert res.status_code == 422
