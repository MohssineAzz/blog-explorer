# Blog Explorer

Full-stack app on top of [JSONPlaceholder](https://jsonplaceholder.typicode.com/): browse authors, read their posts, see comments.

Backend: Python / FastAPI. Frontend: plain HTML/CSS/JS, no build step.

## Backend

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Docs: `http://localhost:8000/docs`. Tests: `pytest`.

## Frontend

```
cd frontend
python3 serve.py
```

Open `http://localhost:5500` (backend needs to be running on port 8000).

## API

| Method | Path | Notes |
|---|---|---|
| GET | `/users` | list of authors |
| GET | `/users/:id` | author + their posts |
| GET | `/posts` | `?userId=`, `?q=`, `?page=`, `?limit=` |
| GET | `/posts/:id` | post + author + comments |

404 for unknown ids, 502 if JSONPlaceholder is down, 422 for bad ids.

## CI

GitHub Actions runs the backend test suite on every push/PR to `main` (`.github/workflows/tests.yml`).

## Notes

- Backend caches upstream responses in memory for 2 minutes.
- Filtering/search/pagination happen server-side, in memory.
- No auth/dark mode - kept it to what the assignment actually asks for.
