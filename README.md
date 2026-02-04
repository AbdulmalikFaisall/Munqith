# munqith

Minimal scaffold for the `munqith` project.

## About
Munqith is an AI-powered platform that helps startups detect early financial risk by identifying repeated risky financial
patterns and generating early warning signals. Munqith does not provide financial advice. Use at your own discretion.

## Status
Early development

## Scope
- Read-only financial data
- Pattern detection
- Risk signaling

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

---
*Merged README: combined local scaffold and remote project description*
