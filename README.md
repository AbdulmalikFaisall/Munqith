# Munqith

**Deterministic Financial Intelligence Platform for KSA Startups**

A rule-based, explainable system for evaluating startup financial health without AI in live decision paths.

## About

Munqith provides:
- Structured signal computation from financial data
- Deterministic rule evaluation
- Explainable stage derivation
- Historical snapshot preservation
- Auditability and transparency

**No AI in live decisions. All stage derivation is rule-based and auditable.**

## Status

**Sprint 1: ✅ Complete** — Infrastructure & Core Architecture  
Deployed: FastAPI, PostgreSQL, Alembic Migrations, Hybrid Architecture

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (for PostgreSQL)

### 1. Clone & Setup

```bash
git clone https://github.com/yourusername/munqith.git
cd munqith
```

### 2. Configure Environment

```bash
# Copy example environment
cp .env.example .env

# (Optional) Update .env with your settings
# Default works with docker-compose postgres
```

### 3. Install Dependencies

```bash
# Using Python directly
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Start PostgreSQL

```bash
# Start PostgreSQL only
docker-compose up -d postgres

# Or start full stack (app + postgres)
docker-compose up -d
```

### 5. Run Migrations

```bash
alembic upgrade head
```

### 6. Start Application

```bash
# Development mode (with auto-reload)
python -m uvicorn app.main:app --reload

# Production mode
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 7. Verify

```bash
# Health check
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

## Project Structure

```
app/
├── api/              # HTTP routing layer
├── application/      # Use cases & orchestration
├── domain/           # Pure business logic (framework-independent)
└── infrastructure/   # Database & persistence
```

## Architecture

**Hybrid Architecture** with strict separation:
- **Domain**: Framework-independent business logic
- **Application**: Use cases & orchestration
- **API**: HTTP routing only
- **Infrastructure**: Database, external services

## Documentation

- [SRS](docs/SRS.md) — Complete requirements specification
- [Domain Model](docs/Domain_Model.md) — Core concepts & data model
- [Sprint Roadmap](docs/Sprint_Roadmap.md) — Implementation timeline
- [Sprint 1 Notes](SPRINT1.md) — Foundation architecture

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=app
```

## Database

PostgreSQL 15 on port 5432  
Default credentials: `munqith:munqith`  
Database: `munqith`

## Development Notes

- All snapshots are immutable once finalized
- Stage is never manually assigned—always derived from rules
- Historical integrity is maintained (soft invalidation, not deletion)
- No AI in live decision paths
- All business logic testable without FastAPI/SQLAlchemy

## License

See [LICENSE](LICENSE)

---

**Sprint 1 Status**: ✅ Infrastructure locked and production-ready
