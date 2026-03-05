# Contributing to Munqith

Thank you for contributing to Munqith! This document outlines guidelines for contributing code, maintaining code quality, and preserving architectural integrity.

## Core Principles

### 1. Deterministic Stage Derivation

**CRITICAL**: The stage derivation logic must remain deterministic and reproducible at all times.

- Any change to signal computation, rule evaluation, or stage derivation must be carefully reviewed
- All stage logic must be testable in isolation from framework dependencies
- Stage results must be identical given the same input snapshot

### 2. Domain Model Independence

The domain model (`app/domain/`) is intentionally framework-agnostic.

**Allowed in domain/**:
- Python standard library
- Pure math/computation
- Domain entity classes
- Business rules and logic

**NOT Allowed in domain/**:
- FastAPI
- SQLAlchemy
- Pydantic
- Requests/HTTP libraries
- Any I/O operations

**Rationale**: This keeps business logic testable and portable.

### 3. Analytics Isolation

The analytics module (`app/analytics/`) is completely isolated from core decision logic.

**Rules**:
- Analytics can read finalized snapshots (read-only)
- Analytics cannot modify `snapshot.stage`, rule results, or signals
- Analytics is offline-only (no calls from request handlers)
- Core domain must never import from `app/analytics/`

**Rationale**: Live decisions must be reproducible without analytics.

### 4. API Layer Responsibility

The API layer should orchestrate use cases, not contain business logic.

**Pattern**:
```python
# app/api/v1/endpoints/snapshot.py
from app.application.use_cases.finalize_snapshot import FinalizeSnapshotUseCase

@router.post("/snapshots/{id}/finalize")
async def finalize(id: UUID, session: Session = Depends(get_db)):
    use_case = FinalizeSnapshotUseCase(session)
    return use_case.execute(id)
```

**Anti-pattern**:
```python
# ❌ Don't do this
from app.domain.engines import SignalEngine, RuleEngine

@router.post("/snapshots/{id}/finalize")
async def finalize(id: UUID):
    engine = SignalEngine()
    # ... domain logic in endpoint
```

## Branching Strategy

- **main**: Production-ready code. Every commit must be deployable.
- **develop**: Integration branch for features.
- **feature/{feature-name}**: Feature branches off develop.
- **hotfix/{issue}**: Critical fixes off main, merged back to develop.

## Commit Message Style

Commit messages should follow this format:

```
type(scope): brief description

Longer explanation if needed. Explain what and why, not how.

Related: #issue-number (if applicable)
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring (no logic change)
- `test`: Test additions/changes
- `docs`: Documentation
- `chore`: Build, dependencies, etc.

**Examples**:
```
feat(snapshot): add finalization orchestration

Implements FinalizeSnapshotUseCase with atomic transactions.
Ensures stage derivation is deterministic and auditable.

Related: #5
```

```
fix(rule_engine): correct runway calculation edge case

Handle division by zero when monthly_burn is 0.
```

## Pull Request Checklist

Before submitting a PR, ensure:

- [ ] Tests pass locally: `pytest tests/`
- [ ] Linting passes: `ruff check app/`
- [ ] Architecture audit passes: `python scripts/arch_audit.py`
- [ ] Code follows project style
- [ ] Docstrings added/updated
- [ ] No `print()` statements (use logging)
- [ ] No debug code committed
- [ ] Database migrations (if schema changed)
- [ ] Tests for new functionality (target > 80% coverage)

## Code Quality Standards

### Testing Requirements

All code must be tested:
- **Unit tests** for domain logic (100% coverage expected)
- **Integration tests** for use cases
- **API tests** for endpoints (where applicable)

Run tests:
```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Type Hints

Use type hints for clarity:
```python
# Good
def calculate_runway(cash: Decimal, monthly_burn: Decimal) -> Optional[Decimal]:
    if monthly_burn <= 0:
        return None
    return cash / monthly_burn

# Avoid
def calculate_runway(cash, monthly_burn):
    return cash / monthly_burn
```

### Docstrings

Domain entities and use cases must have docstrings:
```python
class Snapshot:
    """
    Snapshot entity - represents a time-bound financial snapshot.
    
    Lifecycle:
        DRAFT → FINALIZED → INVALIDATED
    
    Rules:
    - Only DRAFT snapshots can be modified
    - FINALIZED snapshots are immutable
    """
```

### No Circular Dependencies

Enforce unidirectional dependencies:
```
api/ → application/ → domain/
api/ → infrastructure/ ↑
      application/ → infrastructure/
```

**Never**:
- domain → application
- domain → api
- domain → infrastructure

## Architecture Audit

Run the architecture audit before committing:
```bash
python scripts/arch_audit.py
```

This checks:
- No framework imports in domain
- Analytics doesn't modify snapshot state
- No circular dependencies
- API doesn't directly use engines

## Deployment

### Pre-Deployment Checklist

- [ ] All tests pass
- [ ] Architecture audit passes
- [ ] Smoke test passes: `bash scripts/smoke_test.sh`
- [ ] Migrations tested on fresh DB
- [ ] Logging outputs expected format
- [ ] Health check works
- [ ] No secrets in code

### One-Command Deployment

```bash
docker-compose up -d --build
```

After deployment:
```bash
curl http://localhost:8000/health
```

Should return:
```json
{"status": "ok"}
```

## Code Review Standards

Reviewers should verify:

1. **Correctness**: Does the code do what it claims?
2. **Tests**: Is critical logic tested?
3. **Architecture**: Does it maintain separation of concerns?
4. **Performance**: Any obvious bottlenecks?
5. **Security**: Any sensitive data logged or exposed?
6. **Documentation**: Is it clear to future maintainers?

## Database Migrations

For schema changes:

1. Create migration: `alembic revision --autogenerate -m "description"`
2. Review generated migration in `alembic/versions/`
3. Test upgrade: `alembic upgrade head`
4. Test downgrade: `alembic downgrade -1` then `alembic upgrade head`
5. Commit migration with feature

## Logging Guidelines

- Use structured logging (module, level, timestamp)
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)
- Never log passwords, tokens, or sensitive data
- Log errors with stack traces

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Snapshot finalized", extra={
    "snapshot_id": snapshot.id,
    "company_id": snapshot.company_id,
    "stage": snapshot.stage,
})
```

## Questions?

- Check existing code for patterns
- Read SRS and Domain Model in `docs/`
- Review test files for examples
- Ask in issues/PRs

## Thank You!

Your contributions help make Munqith a more robust, auditable financial intelligence platform for KSA startups. 🇸🇦
