# Munqith – Full Execution Sprint Roadmap

Assumption: 1 Sprint = 1 Week

---

# Sprint 0 — Foundation Lock
- SRS locked
- DB schema approved
- Architecture validated

---

# Sprint 1 — Infrastructure + Project Skeleton

Deliverables:
- FastAPI initialized
- PostgreSQL via Docker
- Alembic migrations working
- Hybrid architecture structure
- UUID strategy
- Health endpoint

Acceptance:
- DB matches SRS
- Zero business logic in API
- App boots successfully

---

# Sprint 2 — Core Domain + Lifecycle
- Snapshot entity
- Company entity
- Stage enum
- Lifecycle enforcement
- Immutability rules

---

# Sprint 3 — Signal Engine
- Monthly burn calculation
- Runway calculation
- Signal entity
- Signal computation engine

---

# Sprint 4 — Rule Engine
- Deterministic rule engine
- Risk classification
- Stage evaluator

---

# Sprint 5 — Finalization Orchestration
- FinalizeSnapshotUseCase
- Transaction management
- Explainability resolver

---

# Sprint 6 — Snapshot History
- Snapshot comparison
- Delta calculations
- Timeline endpoint

---

# Sprint 7 — Trend Engine
- Runway trajectory
- Burn trajectory
- Revenue growth %

---

# Sprint 8 — Security + RBAC
- JWT authentication
- Analyst vs Admin roles
- Data isolation

---

# Sprint 9 — Validation Hardening
- Financial sanity checks
- Date uniqueness
- Deterministic validation errors

---

# Sprint 10 — Reporting
- JSON export
- PDF report
- Index optimization
- Caching

---

# Sprint 11 — Offline AI Analytics
- Historical reader
- Risk archetype detection
- Separate AI namespace
- No impact on live stage logic

---

# Sprint 12 — Deployment + CI/CD
- Production Docker
- CI pipeline
- Monitoring
- Architecture audit