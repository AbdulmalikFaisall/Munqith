# Munqith

**Deterministic Financial Intelligence Platform for KSA Startups**

A rule-based, explainable system for evaluating startup financial health without AI in live decision paths.

## 📋 About

Munqith provides:
- **Structured Signals**: Financial metrics computed from transaction data
- **Deterministic Rules**: Auditable, reproducible logic for stage evaluation
- **Explainable Decisions**: Clear visibility into why a company received its stage
- **Historical Integrity**: Immutable snapshots with soft invalidation model
- **Auditability**: All decisions preserved and reviewable

**Core Principle**: ✅ No AI in live decisions. All stage derivation is rule-based and deterministic.

## 🚀 Quick Start (One-Command Deployment)

```bash
# 1. Clone
git clone https://github.com/yourusername/munqith.git
cd munqith

# 2. Configure (optional)
cp .env.example .env

# 3. Deploy (one command!)
docker-compose up -d --build

# 4. Verify
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

That's it! API is running on port 8000.

## 📦 Production Deployment

### Prerequisites
- Docker & Docker Compose
- PostgreSQL 15 (included in docker-compose)
- Linux/macOS or WSL2 on Windows

### Deployment Steps

```bash
# 1. Prepare environment
cp .env.example .env
# Edit .env and change DB_PASSWORD for production

# 2. Build and start
docker-compose up -d --build

# 3. Verify health
curl http://localhost:8000/health

# 4. View logs
docker-compose logs -f api
```

### Stopping the System

```bash
# Graceful shutdown
docker-compose down

# With volume cleanup
docker-compose down -v
```

### Backup & Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U munqith munqith > backup.sql

# Restore database
docker-compose exec -T postgres psql -U munqith munqith < backup.sql
```

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [docs/SRS.md](docs/SRS.md) | Complete Software Requirements Specification |
| [docs/Domain_Model.md](docs/Domain_Model.md) | Core domain concepts and data model |
| [docs/Sprint_Roadmap.md](docs/Sprint_Roadmap.md) | Implementation phases and architecture |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Development guidelines and governance |
| [RUNBOOK.md](RUNBOOK.md) | Operations and troubleshooting guide |

## 🏗️ Architecture

### Core Principles

1. **Domain Independence** 
   - Business logic in `app/domain/` has zero framework dependencies
   - Testable without FastAPI or SQLAlchemy
   - Pure Python with standard library only

2. **Deterministic Stage Derivation**
   - Stage is NEVER manually assigned
   - Stage is ALWAYS derived from rules + signals
   - Same input snapshot → same stage (reproducible)

3. **Analytics Isolation**
   - Offline-only analytics in `app/analytics/`
   - Cannot modify snapshot.stage or rule results
   - No impact on live decision paths
   - Cool insights, zero side effects

4. **Clear Boundaries**
   ```
   api/ → application/ → domain/
   api/ → infrastructure/ ↑
         application/ → infrastructure/
   ```

### Directory Structure

```
munqith/
├── app/
│   ├── api/                    # FastAPI routes (thin)
│   ├── application/            # Use cases & orchestration
│   │   └── use_cases/
│   ├── domain/                 # Pure business logic ⭐
│   │   ├── entities/
│   │   ├── engines/
│   │   ├── enums/
│   │   ├── exceptions/
│   │   ├── rules/
│   │   └── validators/
│   ├── infrastructure/         # Database & persistence
│   │   ├── db/
│   │   ├── repositories/
│   │   └── logging.py
│   └── analytics/              # Offline insights (isolated)
│       ├── reader/
│       ├── engines/
│       └── use_cases/
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── scripts/
│   ├── arch_audit.py          # Architecture compliance check
│   └── smoke_test.sh          # Deployment smoke test
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI pipeline
├── Dockerfile                 # Production Docker image
├── docker-compose.yml         # Production orchestration
└── docker-compose.override.yml # Development overrides
```

## 🧪 Testing

### Run Tests Locally

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=app --cov-report=html

# Specific module
pytest tests/domain/test_snapshot.py -v
```

### Test Structure

- **Unit Tests**: Domain logic, engines, validators
- **Integration Tests**: Use cases with test repositories
- **API Tests**: Endpoints (where applicable)

Target: >80% code coverage

## 🚨 Quality Checks

### Pre-Commit Checks

All checks must pass before deploying:

```bash
# Check architecture
python scripts/arch_audit.py

# Lint code
ruff check app/

# Format check
black --check app/

# Run tests
pytest tests/

# Smoke test (requires docker-compose)
bash scripts/smoke_test.sh
```

### CI/CD Pipeline

Every push/PR triggers:
1. ✅ Lint check (ruff)
2. ✅ Architecture audit
3. ✅ Unit tests (with database)
4. ✅ Docker build

[View CI configuration](.github/workflows/ci.yml)

## 💾 Database

### Schema

- **companies**: Company metadata
- **snapshots**: Immutable financial snapshots
  - status: DRAFT | FINALIZED | INVALIDATED
  - stage: Derived from rules
- **signals**: Computed financial metrics
- **rules**: Rule results per snapshot
- **analytics_insights**: Offline analytics results (append-only)

### Migrations

```bash
# Run all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Create migration from model changes
alembic revision --autogenerate -m "description"
```

## 📊 Monitoring & Logging

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# In docker-compose
docker-compose ps
# Both postgres and api should show "healthy"
```

### Logs

```bash
# View live logs
docker-compose logs -f api

# View database logs
docker-compose logs -f postgres

# Log format is configurable in .env
# Options: LOG_LEVEL=DEBUG|INFO|WARNING|ERROR
```

### Structured Logging

Logs are output in structured format (text or JSON) with:
- Timestamp
- Log level
- Module name
- Message
- (Optional) Exception trace for errors

## 🔒 Security Considerations

### Production Checklist

- [ ] Change DB_PASSWORD in .env
- [ ] Use strong SECRET_KEY if auth is enabled
- [ ] Enable HTTPS in reverse proxy (nginx/traefik)
- [ ] Restrict API access (firewall/VPN)
- [ ] Enable PostgreSQL SSL connections
- [ ] Regular database backups
- [ ] Monitor access logs

### Data Protection

- Database credentials in .env (not version controlled)
- Passwords never logged
- Audit trail maintained for all snapshot changes
- Soft invalidation prevents data loss

## 🚑 Troubleshooting

### "Connection refused" on API startup

```bash
# Check postgres is healthy
docker-compose exec postgres pg_isready -U munqith

# Wait a bit longer and try again
docker-compose logs postgres
```

### Database migration fails

```bash
# Inspect current schema
docker-compose exec postgres psql -U munqith -d munqith -c "\d"

# Run migrations manually
docker-compose exec api alembic upgrade head

# See detailed error
docker-compose exec api alembic upgrade head --verbose
```

### Tests fail locally but pass in CI

```bash
# Use test database URL
export DATABASE_URL=postgresql://munqith:munqith@localhost:5432/munqith_test

# Run tests with fresh database
docker-compose -f docker-compose.test.yml up -d postgres
pytest tests/
```

See [RUNBOOK.md](RUNBOOK.md) for comprehensive troubleshooting.

## 📈 Performance

### Key Metrics

- **Snapshot finalization**: < 500ms
- **Signal computation**: O(n) with signal count
- **Rule evaluation**: O(1) per rule
- **API response**: < 100ms (typical)
- **Database connection**: Pooled, persistent

### Optimization Tips

- Use database indexes (created automatically by migrations)
- Batch operations where possible
- Signal computation is the expensive operation (already optimized)

## 🤝 Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Code style & conventions
- Branching strategy
- Pull request process
- Architecture rules to follow

### Key Rules for Contributors

❌ **Never**:
- Import FastAPI/SQLAlchemy in app/domain/
- Modify snapshot.stage in analytics module
- Add business logic to API layer
- Create circular dependencies

✅ **Always**:
- Write tests for domain logic
- Add docstrings to public classes/methods
- Run architecture audit before committing
- Follow existing patterns in codebase

## 🛠️ Development

### Local Development Setup

```bash
# 1. Clone & cd
git clone ... && cd munqith

# 2. Create environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Start services
docker-compose up -d postgres

# 4. Run migrations
alembic upgrade head

# 5. Start app with hot reload
python -m uvicorn app.main:app --reload

# 6. Run tests
pytest tests/
```

### Using Docker Compose Override

Development uses `docker-compose.override.yml` automatically:

```bash
# This uses both compose files automatically
docker-compose up -d

# Hot reload is enabled, live code editing works
# Volume mounts are set up
```

## 📝 API Documentation

Once running, visit:
- **OpenAPI (Swagger UI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🚀 Deployment Examples

### Docker Hub / Registry

```bash
# Build and tag
docker build -t your-registry/munqith:latest .
docker push your-registry/munqith:latest

# Run from registry
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  your-registry/munqith:latest
```

### With Reverse Proxy (Nginx)

```nginx
upstream munqith {
    server api:8000;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://munqith;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📄 License

See [LICENSE](LICENSE)

## 📞 Support

For issues, see [RUNBOOK.md](RUNBOOK.md) or open a GitHub issue.

---

**Munqith** — Deterministic financial intelligence for KSA startups. 🇸🇦
