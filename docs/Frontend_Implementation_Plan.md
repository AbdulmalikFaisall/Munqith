# Munqith Frontend Implementation Plan

## 1. Purpose

This document is the handoff plan for building the Munqith frontend.

The frontend must be a production-style financial intelligence dashboard built on top of the existing FastAPI backend. The frontend must not compute business logic, financial rules, stage derivation, or analytics. The backend remains the single source of truth.

Primary UX questions the frontend must answer:

1. What is the company's current state?
2. Why was that stage assigned?
3. How has the company evolved over time?

Required frontend stack:

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- Recharts

## 2. Backend API Summary

### 2.1 Application Entry

Primary backend app:

- [app/main.py](app/main.py)

API router:

- [app/api/v1/router.py](app/api/v1/router.py)

API base path:

- `/api/v1`

### 2.2 Authentication

Login endpoint:

- `POST /api/v1/auth/login`
- File: [app/api/v1/endpoints/auth.py](app/api/v1/endpoints/auth.py)

Request body:

```json
{
  "email": "user@example.com",
  "password": "secret"
}
```

Response body:

```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

Authentication mechanism:

- JWT bearer token
- Header required: `Authorization: Bearer <access_token>`
- Validation dependency: [app/api/dependencies/auth.py](app/api/dependencies/auth.py)
- Token service: [app/application/services/auth_service.py](app/application/services/auth_service.py)
- JWT payload contains `sub`, `role`, and `exp`
- Signing algorithm: `HS256`
- Default token expiry: `30` minutes

### 2.3 Roles and Authorization

Role enum:

- [app/domain/enums/user_role.py](app/domain/enums/user_role.py)

Roles:

- `ANALYST`
- `ADMIN`

Access rules in current API:

- `ANALYST` and `ADMIN` can log in, create snapshots, read analytics, and export reports
- `ADMIN` is required for snapshot invalidation
- The backend is the authority for enforcement; the frontend should only reflect capability in the UI

### 2.4 Existing API Endpoints

#### Health

- `GET /api/v1/health`
- `GET /health`
- Returns `{ "status": "ok" }`

#### Snapshot Creation

- `POST /api/v1/snapshots`
- File: [app/api/v1/endpoints/snapshots.py](app/api/v1/endpoints/snapshots.py)

Request body:

```json
{
  "company_id": "uuid",
  "snapshot_date": "2026-03-01",
  "cash_balance": 50000,
  "monthly_revenue": 10000,
  "operating_costs": 8000
}
```

Notes:

- Creates a `DRAFT` snapshot
- Financial fields are optional in the request model
- Response returns snapshot summary, not full detailed intelligence payload

Response shape:

```json
{
  "id": "uuid",
  "company_id": "uuid",
  "snapshot_date": "2026-03-01",
  "status": "DRAFT",
  "cash_balance": 50000,
  "monthly_revenue": 10000,
  "operating_costs": 8000,
  "stage": null,
  "created_at": "2026-03-01T12:00:00"
}
```

#### Snapshot Invalidation

- `POST /api/v1/snapshots/{snapshot_id}/invalidate`
- File: [app/api/v1/endpoints/invalidate.py](app/api/v1/endpoints/invalidate.py)
- Role: `ADMIN`

Request body:

```json
{
  "reason": "Incorrect financial data"
}
```

Response shape:

```json
{
  "snapshot_id": "uuid",
  "status": "INVALIDATED",
  "invalidation_reason": "Incorrect financial data",
  "invalidated_at": "2026-03-01T12:00:00"
}
```

#### Timeline

- `GET /api/v1/companies/{company_id}/timeline`
- File: [app/api/v1/endpoints/timeline.py](app/api/v1/endpoints/timeline.py)
- Auth required

Response shape:

```json
{
  "timeline": [
    {
      "snapshot_date": "2026-01-15",
      "stage": "IDEA",
      "monthly_revenue": 20000,
      "monthly_burn": 40000,
      "runway_months": 5,
      "stage_transition_from_previous": null
    }
  ]
}
```

Behavior:

- Returns finalized snapshots only
- Excludes invalidated snapshots
- Ordered chronologically

#### Trends

- `GET /api/v1/companies/{company_id}/trends`
- File: [app/api/v1/endpoints/trends.py](app/api/v1/endpoints/trends.py)
- Auth required

Response shape:

```json
{
  "company_id": "uuid",
  "time_series": [
    {
      "date": "2026-01-15",
      "runway_months": 5,
      "monthly_burn": 40000,
      "monthly_revenue": 10000,
      "revenue_growth_percent": null
    }
  ],
  "indicators": {
    "revenue_trend": "UP",
    "burn_trend": "DOWN",
    "runway_trend": "UP"
  },
  "snapshot_count": 2
}
```

Behavior:

- Returns finalized snapshots only
- Intended for charting and high-level trend labels

#### Comparison

- `GET /api/v1/companies/{company_id}/snapshots/compare?from_date=YYYY-MM-DD&to_date=YYYY-MM-DD`
- File: [app/api/v1/endpoints/compare.py](app/api/v1/endpoints/compare.py)
- Auth required

Response shape:

```json
{
  "from_date": "2026-01-15",
  "to_date": "2026-03-15",
  "from_stage": "PRE_SEED",
  "to_stage": "SEED",
  "stage_changed": true,
  "from_metrics": {
    "monthly_revenue": 50000,
    "monthly_burn": 30000,
    "runway_months": 10
  },
  "to_metrics": {
    "monthly_revenue": 75000,
    "monthly_burn": 25000,
    "runway_months": 16
  },
  "deltas": {
    "delta_revenue": 25000,
    "delta_burn": -5000,
    "delta_runway": 6
  }
}
```

Important note:

- This endpoint returns a `404` payload using `error` instead of the more common `detail` shape used by other endpoints

#### Exports

- `GET /api/v1/snapshots/{snapshot_id}/export/json`
- `GET /api/v1/snapshots/{snapshot_id}/export/pdf`
- File: [app/api/v1/endpoints/exports.py](app/api/v1/endpoints/exports.py)
- Role: `ANALYST` or `ADMIN`

JSON export:

- Returns a structured intelligence payload for a finalized snapshot
- Includes financial attributes, derived metrics, stage, signals, rule results, and contributing signals

PDF export:

- Returns `application/pdf`
- Uses attachment filename `snapshot_<snapshot_id>.pdf`
- Must be handled as a binary response by the frontend

### 2.5 Error Patterns and Status Codes

Observed status codes:

- `200 OK`
- `201 CREATED`
- `400 BAD REQUEST`
- `401 UNAUTHORIZED`
- `403 FORBIDDEN`
- `404 NOT FOUND`
- `409 CONFLICT`
- `422 UNPROCESSABLE ENTITY`
- `500 INTERNAL SERVER ERROR`

Observed error payload patterns:

- Most endpoints use `{ "detail": "..." }`
- Compare uses `{ "error": "..." }` on `404`

Frontend implication:

- Build a normalized error layer in the frontend API client

### 2.6 DTO Models Currently Exposed

Defined request and response models:

- `LoginRequest`
- `LoginResponse`
- `CreateSnapshotRequest`
- `SnapshotResponse`
- `InvalidateRequest`

Files:

- [app/api/v1/endpoints/auth.py](app/api/v1/endpoints/auth.py)
- [app/api/v1/endpoints/snapshots.py](app/api/v1/endpoints/snapshots.py)
- [app/api/v1/endpoints/invalidate.py](app/api/v1/endpoints/invalidate.py)

Analytics and export endpoints return plain JSON responses rather than dedicated Pydantic response models.

### 2.7 Pagination and Filtering

Current state:

- No pagination implemented
- No filtering implemented on read collections
- No sorting query model exposed beyond implicit chronological ordering in timeline and trends

Frontend implication:

- The architecture should be ready for pagination, but current implementation must tolerate full list responses

### 2.8 Critical Backend Gaps For The Requested Frontend

The requested frontend pages assume APIs that do not currently exist.

Missing or not exposed:

- `GET /companies`
- `GET /companies/{id}`
- `GET /companies/{id}/snapshots`
- `GET /snapshots/{id}`
- `POST /snapshots/{id}/finalize`

Important note on finalization:

- The finalization use case exists in [app/application/use_cases/finalize_snapshot.py](app/application/use_cases/finalize_snapshot.py)
- It is not currently exposed as an HTTP endpoint

Additional backend gap:

- No CORS middleware is configured in [app/main.py](app/main.py)

## 3. Frontend Requirements

The frontend must support:

- Dashboard overview
- Companies list
- Company intelligence page
- Snapshot details page
- Snapshot comparison
- Trend visualization
- Snapshot creation
- Snapshot finalization
- Snapshot invalidation for admin users
- JSON export
- PDF export

The frontend must behave as a financial intelligence dashboard, not as a generic CRUD panel.

The UI should emphasize:

- stage visibility
- explainability
- lifecycle status
- historical change over time
- role-aware actions

The frontend must not:

- compute stage logic
- recompute signals
- recompute rules
- duplicate backend financial logic

## 4. Recommended Frontend Architecture

### 4.1 Core Approach

Use a Next.js App Router application in `frontend/` with a server-mediated API layer.

Recommended principle:

- Browser UI calls Next.js server-side handlers or server-side API utilities
- Next.js forwards requests to the FastAPI backend
- JWT is stored in a secure `httpOnly` cookie rather than in `localStorage`

Reasoning:

- better security for tokens
- cleaner protected-route handling
- easier SSR or server-side gating
- simpler handling of backend auth headers
- reduced exposure to immediate CORS issues

### 4.2 Folder Structure

Suggested structure:

```text
frontend/
  src/
    app/
      (auth)/
        login/
      (dashboard)/
        dashboard/
        companies/
        companies/[companyId]/
        snapshots/[snapshotId]/
        comparison/
      api/
    components/
      ui/
      charts/
      layout/
      states/
      intelligence/
      forms/
    features/
      auth/
      dashboard/
      companies/
      snapshots/
      comparison/
      exports/
    lib/
      api/
      auth/
      query/
      utils/
    types/
    hooks/
    styles/
```

Reasoning:

- `app/` owns routing and layouts
- `features/` owns domain-specific UI and logic by use case
- `components/` owns reusable presentation pieces
- `lib/api/` owns transport and endpoint composition
- `types/` owns frontend-facing DTOs and normalized models

### 4.3 Page Structure

Protected routes:

- `/login`
- `/dashboard`
- `/companies`
- `/companies/[companyId]`
- `/snapshots/[snapshotId]`
- `/comparison`

Recommended route grouping:

- `(auth)` for login flow
- `(dashboard)` for authenticated application shell

### 4.4 Reusable Components

Shared components to build early:

- app shell layout
- top navigation
- sidebar navigation
- stage badge
- metric card
- status badge
- timeline list
- trend chart wrappers
- snapshot selector
- comparison delta card
- contributing signals panel
- rule results panel
- empty state
- error state
- skeleton loaders
- export action menu
- invalidation dialog
- snapshot creation form

Reasoning:

- most product surfaces repeat the same intelligence patterns
- creating these early keeps page code thin and consistent

### 4.5 State Management

Use TanStack Query for remote data state.

Recommended split:

- TanStack Query for backend data
- React local state for page-local interactions
- minimal global state only for session metadata and lightweight UI state if needed

Avoid:

- a large client-side global store for backend entities

Reasoning:

- the application is API-driven
- cache invalidation and loading states are central concerns
- TanStack Query already solves the hard parts needed here

### 4.6 Authentication Handling

Recommended strategy:

- login page posts credentials to a Next.js auth handler
- auth handler calls backend login endpoint
- returned JWT is stored in a secure `httpOnly` cookie
- protected layouts validate presence of session before rendering
- logout clears cookie locally

Frontend role handling:

- decode role from trusted session context on the server or store role metadata after login
- use role only to gate UI affordances
- never rely on frontend role checks for real security

### 4.7 Error Handling

The frontend must normalize backend errors into one application error model.

Error categories:

- authentication errors
- authorization errors
- form validation errors
- not found errors
- domain conflict errors
- export/download errors
- generic server errors

Behavior:

- `401` should clear session and redirect to login when appropriate
- `403` should show permission messaging
- `409` and `422` should map into form-level feedback
- binary export failures should surface cleanly without attempting JSON parsing

### 4.8 Loading States

Required loading patterns:

- page-level skeletons for first load
- section-level skeletons for dashboard widgets
- button pending states for mutations
- optimistic transitions only where safe

Reasoning:

- the app is information-dense
- partial rendering reduces perceived latency

### 4.9 Caching Strategy

Recommended query behavior:

- stable query keys by resource type and parameters
- short stale times for detail and intelligence views
- invalidation after mutations affecting timelines, trends, snapshot details, and company pages
- no aggressive cache persistence for sensitive authenticated data unless explicitly required later

Example query domains:

- `auth`
- `dashboard`
- `companies`
- `company-detail`
- `company-timeline`
- `company-trends`
- `snapshot-detail`
- `comparison`

## 5. API Communication Layer Design

### 5.1 Centralized API Client

Create a single API module responsible for:

- backend base URL resolution
- attaching auth headers
- request serialization
- response parsing
- binary download support
- error normalization
- shared DTO typing

Recommended structure:

```text
src/lib/api/
  client.ts
  errors.ts
  auth.ts
  companies.ts
  snapshots.ts
  analytics.ts
  exports.ts
  types.ts
```

### 5.2 Typed Request and Response Models

Create TypeScript contracts matching the backend responses.

Model categories:

- auth types
- snapshot creation types
- snapshot detail types
- timeline item types
- trends types
- compare response types
- export payload types
- normalized error types
- role and status enums

Recommendation:

- keep raw backend DTOs separate from any UI-shaped view models

### 5.3 Authentication Middleware

Recommended behavior:

- use Next.js middleware or layout guards only for route gating
- keep actual request authorization in the server-side API layer
- do not expose raw tokens to client-side JavaScript unless there is no alternative

### 5.4 Token Storage Strategy

Recommended:

- secure `httpOnly` cookie
- `sameSite` protection
- `secure` in production

Avoid:

- `localStorage`

Reasoning:

- lower XSS exposure
- easier server-side forwarding

### 5.5 Request Interceptors

If using plain `fetch`, build wrapper functions rather than interceptor-heavy libraries.

Wrapper responsibilities:

- add auth header from server cookie
- detect content type
- parse JSON safely
- return blob or array buffer for PDF
- normalize inconsistent error payloads

### 5.6 Protected Endpoints

Frontend interaction pattern:

- route loads on authenticated app shell
- query hook calls typed client
- typed client forwards bearer token to backend
- normalized response returns to component

### 5.7 Mutation Endpoints

Mutation flows to support:

- login
- create snapshot
- finalize snapshot when exposed by backend
- invalidate snapshot

After mutation:

- invalidate affected queries
- refresh affected page sections
- show success or failure feedback with minimal ambiguity

### 5.8 Comparison Endpoints

Comparison should be treated as a parameterized query.

Requirements:

- input validation for both dates
- disabled state until both dates are selected
- clear empty or not-found state if either snapshot is not finalized

### 5.9 Export Endpoints

JSON export:

- can be presented as structured data or downloaded

PDF export:

- must be handled as file download
- do not pass through JSON parser
- preserve filename from response if available

## 6. Page Design

### 6.1 Dashboard

Purpose:

- show a high-level intelligence overview across companies

Layout:

- header with summary
- metric strip
- attention/risk section
- recent activity or latest finalized intelligence section
- trend summary widgets

Required APIs:

- requires company list and company summary data not fully exposed today
- may later combine `companies`, `timeline`, `trends`, and latest finalized snapshot sources

Components:

- summary stat cards
- priority company cards
- mini trend charts
- recent lifecycle activity feed

State handling:

- query-based dashboard load
- independent loading sections for major widgets

### 6.2 Companies Page

Purpose:

- list companies as intelligence entry points

Layout:

- filter/search toolbar
- companies grid or table
- stage and status indicators

Required APIs:

- `GET /companies`

Components:

- search field
- filter controls
- company row/card
- stage badge
- empty state

State handling:

- URL-driven filter state recommended
- server-side pagination when backend supports it

### 6.3 Company Intelligence Page

Purpose:

- answer current state, why, and historical evolution for one company

Layout:

- company header
- current state hero
- explainability panel
- trend charts
- timeline section
- snapshot list
- actions rail

Required APIs:

- `GET /companies/{id}`
- `GET /companies/{id}/snapshots`
- `GET /companies/{id}/timeline`
- `GET /companies/{id}/trends`
- compare endpoint
- export actions for finalized snapshots

Components:

- stage hero card
- current metrics cards
- contributing signals panel
- trend chart block
- timeline list
- snapshot list/table
- compare launcher
- export menu
- admin invalidation entry point where appropriate

State handling:

- multiple coordinated queries
- partial loading allowed by section

### 6.4 Snapshot Details Page

Purpose:

- inspect a single snapshot as an immutable intelligence artifact

Layout:

- metadata header
- financial metrics section
- derived intelligence section
- rule and signal explanation
- lifecycle actions

Required APIs:

- `GET /snapshots/{id}`
- export endpoints
- invalidation endpoint for admin users

Components:

- metadata panel
- metrics cards
- stage display
- signal list
- rule results list
- export controls
- invalidation dialog

State handling:

- snapshot detail query
- admin mutation for invalidation

### 6.5 Comparison Page

Purpose:

- compare two finalized snapshots visually and numerically

Layout:

- date selection controls
- stage transition banner
- before/after metrics
- delta cards
- optional contextual trend chart

Required APIs:

- compare endpoint
- selectable finalized snapshot dates from company snapshots list or timeline

Components:

- snapshot/date selector
- delta cards
- side-by-side metric panels
- stage transition indicator

State handling:

- query runs only when valid dates exist
- not-found and not-finalized states must be explicit

## 7. Data Flow

Primary data flow:

```text
UI Component
  -> Feature Query Hook / Mutation Hook
    -> Central API Client
      -> Next.js Server-Side Handler or Server Utility
        -> FastAPI Backend Endpoint
          -> Normalized Response / Error
            -> TanStack Query Cache
              -> UI Render
```

Authentication flow:

```text
Login Form
  -> Next.js Auth Handler
    -> POST /api/v1/auth/login
      -> JWT Returned
        -> Secure Cookie Stored
          -> Protected Layout Access Granted
```

Export flow:

```text
Export Action Click
  -> Mutation / Server Request
    -> Backend Export Endpoint
      -> JSON payload or PDF blob
        -> Download or Rendered Structured Output
```

Mutation invalidation flow:

```text
Create / Finalize / Invalidate Snapshot
  -> Backend Mutation
    -> Success Response
      -> Invalidate relevant queries
        -> Refetch detail, timeline, trends, and list views
```

## 8. Implementation Roadmap

### Phase 0 - Dependency Alignment

Before coding feature pages, acknowledge the missing backend endpoints required by the requested UX.

Backend additions needed for full delivery:

- `GET /companies`
- `GET /companies/{id}`
- `GET /companies/{id}/snapshots`
- `GET /snapshots/{id}`
- `POST /snapshots/{id}/finalize`
- ideally pagination for company and snapshot collections

### Phase 1 - Project Setup

- replace `frontend/index.html`
- initialize Next.js App Router project in `frontend/`
- configure TypeScript
- configure Tailwind CSS
- add shadcn/ui
- add TanStack Query
- add Recharts
- establish linting and environment configuration

### Phase 2 - Layout and Navigation

- create authenticated app shell
- build sidebar and top navigation
- establish route groups for auth and dashboard
- define design tokens and base layout primitives

### Phase 3 - API Client and Authentication

- implement centralized API client
- implement DTO types and normalized errors
- add login flow
- store JWT in secure cookie
- add protected route handling
- add logout

### Phase 4 - Shared UI and Domain Components

- stage badge
- metric cards
- empty and error states
- skeletons
- trend chart wrappers
- timeline widgets
- snapshot forms and dialogs
- export controls

### Phase 5 - Dashboard

- implement intelligence-focused dashboard using backend summary inputs once available
- keep sections modular so missing backend summary endpoints can be composed from multiple reads if needed

### Phase 6 - Companies Page

- implement searchable company list
- support pagination when backend provides it
- link to company intelligence view

### Phase 7 - Company Intelligence Page

- implement company overview hero
- show latest state
- render explainability
- render trends and timeline
- show snapshots list and actions

### Phase 8 - Snapshot Details Page

- implement full snapshot detail view
- wire export actions
- wire admin invalidation flow

### Phase 9 - Comparison View

- implement snapshot comparison selection flow
- render deltas and stage transition view

### Phase 10 - Snapshot Lifecycle Actions

- create snapshot form
- finalize snapshot action after backend endpoint exists
- admin invalidation flow with required reason

### Phase 11 - Polishing and Hardening

- responsive behavior
- accessibility improvements
- loading and failure state hardening
- export UX polish
- role-aware UI polish
- real-data verification against backend responses

### Phase 12 - Deployment Integration

Preferred deployment strategy:

- same-origin frontend proxy through Next.js

Alternative:

- separate frontend deployment plus backend CORS enablement

## 9. Implementation Rules For The Coding Model

The model implementing the frontend must follow these rules:

1. Do not compute business logic in the frontend.
2. Do not duplicate backend stage logic, signal logic, or rule logic.
3. Use typed contracts for all backend communication.
4. Normalize backend errors in one place.
5. Treat role checks in the UI as display logic only.
6. Handle PDF export as binary.
7. Keep components reusable and feature-oriented.
8. Prefer server-mediated API access and secure cookies for auth.
9. Build pages in the roadmap order.
10. If a page depends on a missing backend endpoint, call that dependency out explicitly instead of inventing unsupported frontend behavior.

## 10. Relevant Files To Reference During Implementation

- [app/main.py](app/main.py)
- [app/api/v1/router.py](app/api/v1/router.py)
- [app/api/dependencies/auth.py](app/api/dependencies/auth.py)
- [app/api/v1/endpoints/auth.py](app/api/v1/endpoints/auth.py)
- [app/api/v1/endpoints/snapshots.py](app/api/v1/endpoints/snapshots.py)
- [app/api/v1/endpoints/invalidate.py](app/api/v1/endpoints/invalidate.py)
- [app/api/v1/endpoints/timeline.py](app/api/v1/endpoints/timeline.py)
- [app/api/v1/endpoints/trends.py](app/api/v1/endpoints/trends.py)
- [app/api/v1/endpoints/compare.py](app/api/v1/endpoints/compare.py)
- [app/api/v1/endpoints/exports.py](app/api/v1/endpoints/exports.py)
- [app/application/services/auth_service.py](app/application/services/auth_service.py)
- [app/application/use_cases/finalize_snapshot.py](app/application/use_cases/finalize_snapshot.py)
- [app/infrastructure/db/models/company.py](app/infrastructure/db/models/company.py)
- [app/infrastructure/db/models/user.py](app/infrastructure/db/models/user.py)
- [docs/Domain_Model.md](docs/Domain_Model.md)
- [docs/Sprint_Roadmap.md](docs/Sprint_Roadmap.md)

## 11. Final Handoff Note

This plan is intentionally explicit because the backend is partially complete for the requested frontend scope.

The correct implementation strategy is:

1. scaffold the frontend foundation,
2. implement the communication and auth layer,
3. build the reusable intelligence UI system,
4. implement pages in dependency order,
5. do not fake missing backend capabilities.