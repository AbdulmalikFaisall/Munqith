# Phase 0 - Backend Dependency Alignment

This document captures the backend dependencies that block full frontend feature delivery.

## Status

Backend is partially ready for frontend integration.

Ready now:

- POST /api/v1/auth/login
- POST /api/v1/snapshots
- POST /api/v1/snapshots/{snapshot_id}/invalidate
- GET /api/v1/companies/{company_id}/timeline
- GET /api/v1/companies/{company_id}/trends
- GET /api/v1/companies/{company_id}/snapshots/compare
- GET /api/v1/snapshots/{snapshot_id}/export/json
- GET /api/v1/snapshots/{snapshot_id}/export/pdf

Missing and required for planned UX:

- GET /api/v1/companies
- GET /api/v1/companies/{id}
- GET /api/v1/companies/{id}/snapshots
- GET /api/v1/snapshots/{id}
- POST /api/v1/snapshots/{id}/finalize

## Constraints

- Frontend must not re-implement business logic from backend.
- Stage logic remains backend-owned.
- Signals and rule outcomes remain backend-owned.
- UI role checks are presentation-only. Backend remains enforcement authority.

## Implementation Guidance

- Build UI shell and route architecture now.
- Implement auth/session wiring in Phase 3.
- Keep data adapters typed so missing endpoints can be integrated without page rewrites.
- Add backend CORS or use same-origin proxy strategy before production browser deployment.

## Tracking Checklist

- [ ] Backend team exposes finalize endpoint
- [ ] Backend team exposes company list/detail endpoints
- [ ] Backend team exposes snapshot detail/list endpoints
- [ ] Frontend updates typed DTOs and hooks after endpoint availability
- [ ] End-to-end flow validated for DRAFT -> FINALIZED -> INVALIDATED
