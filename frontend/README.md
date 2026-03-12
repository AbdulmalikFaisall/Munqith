# Munqith Frontend

Next.js App Router frontend for the Munqith financial intelligence platform.

## Stack

- Next.js (App Router)
- TypeScript
- Tailwind CSS
- TanStack Query
- Recharts

## Local Development

1. Install dependencies:

```bash
npm install
```

2. Configure environment:

```bash
cp .env.example .env.local
```

3. Set backend URL in `.env.local`:

```env
MUNQITH_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_DEV_BYPASS_AUTH=false
```

4. Run frontend:

```bash
npm run dev
```

5. Open:

- http://localhost:3000

## Authentication Flow

- Login goes through Next.js route handlers.
- Backend JWT is stored in secure `httpOnly` cookies.
- Browser does not store tokens in `localStorage`.
- Protected routes are gated by the dashboard layout.

## Implemented Product Areas

- Dashboard overview
- Companies list and company intelligence page
- Snapshot details page
- Snapshot comparison workspace
- Snapshot lifecycle actions:
  - Create DRAFT snapshot
  - Finalize snapshot
  - Invalidate snapshot (ADMIN)
- PDF export

## Deployment Integration

Preferred deployment is same-origin frontend with server-mediated backend calls.

### Docker Compose (root project)

Run from repository root:

```bash
docker-compose up -d --build
```

Services:

- `api` on port `8000`
- `frontend` on port `3000`

The frontend container calls backend using internal Docker DNS (`http://api:8000`).

## Notes

- Frontend does not compute stage logic, signal logic, or rule logic.
- Backend remains the source of truth for financial intelligence.
