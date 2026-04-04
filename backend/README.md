# Backend

FastAPI backend for the browser extension capture flow.

## Endpoints

- `GET /health` returns a small health payload.
- `POST /capture` accepts `{ source_url, page_title, html }`, saves the HTML to `data/html/`, and stores metadata in `data/captures.jsonl`.

## Run locally

1. Install dependencies with `uv sync`.
2. Start the server with `uv run python main.py`.
3. Point the extension at `http://127.0.0.1:8000/capture`.

## Storage

Captured files are written under `backend/data/html/` and capture metadata is appended to `backend/data/captures.jsonl`.
