# munqith

Minimal scaffold for the `munqith` project.

## Contents
- `backend/` — FastAPI backend (minimal example)
- `frontend/` — placeholder static site
- `docs/` — documentation

## Quick start (Windows)
1. python -m venv .venv
2. .\.venv\Scripts\activate
3. pip install -r backend/requirements.txt
4. uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000

## Run tests
- pytest backend/tests
