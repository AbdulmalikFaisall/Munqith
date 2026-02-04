# backend

Minimal FastAPI backend with a single example endpoint and tests.

Run (from project root):

```powershell
.\.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

Run tests:

```powershell
pytest backend/tests
```
