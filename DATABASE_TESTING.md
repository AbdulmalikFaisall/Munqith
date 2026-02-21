# Testing Database Connection & Migrations

This guide walks through testing the database connection and running migrations.

## Prerequisites

You must have Docker and Docker Compose installed.

## Quick Start

### 1. Start PostgreSQL

```bash
cd /c/Users/user/munqith
docker-compose up -d postgres
```

This starts a PostgreSQL 15 container with:
- Database: `munqith`
- User: `munqith`
- Password: `munqith`
- Port: `5432`

### 2. Verify PostgreSQL is Ready

```bash
docker-compose ps
```

Wait for `postgres` to show `healthy` in the STATUS column.

### 3. Run Database Migrations

```bash
alembic upgrade head
```

This will:
- Create all 8 tables
- Apply constraints
- Set up foreign keys
- Initialize timestamps

### 4. Test Database Connection

```bash
python test_database.py
```

This will verify:
- ✓ Connection to PostgreSQL
- ✓ All 8 tables exist
- ✓ Table structure matches schema
- ✓ Session management works

### 5. Stop PostgreSQL (when done)

```bash
docker-compose down
```

## Troubleshooting

### "Unable to get image 'postgres:15-alpine'"
Docker image not pulled. Make sure Docker is running:
```bash
# On Windows, start Docker Desktop
docker ps
```

### "Connection refused"
PostgreSQL container not started or not healthy yet. Check status:
```bash
docker-compose ps
docker-compose logs postgres
```

### "FATAL: password authentication failed"
Wrong DATABASE_URL or PostgreSQL credentials. Check:
1. `.env` has correct DATABASE_URL
2. `docker-compose.yml` has matching credentials
3. Default is: `postgresql://munqith:munqith@localhost:5432/munqith`

### Migration fails with "relation already exists"
Migrations already applied. Check Alembic version:
```bash
alembic current
```

To reset and re-apply:
```bash
alembic downgrade base
alembic upgrade head
```

## What Gets Tested

### test_database.py

The script verifies:

1. **Database URL Configuration**
   - Correctly loaded from `.env`
   - Properly formatted

2. **Connection**
   - Successful TCP connection to PostgreSQL
   - SELECT query execution

3. **Schema**
   - All 8 required tables exist
   - Table relationships intact

4. **Table Structures**
   - `companies` table has id, name, sector, created_at, updated_at
   - `snapshots` table has all financial fields
   - Other tables have correct columns

5. **Session Management**
   - SQLAlchemy session creation
   - Proper cleanup

## Sprint 1 Database Tests

All these tests are now available:

- ✅ **verify_deployment.py** — 12-point pre-deployment checklist
- ✅ **test_database.py** — Database connection & schema verification
- ✅ **test_imports.py** — Model and app imports

## Next Steps

Once database tests pass:

1. Start the FastAPI app
   ```bash
   uvicorn app.main:app --reload
   ```

2. Test health endpoint
   ```bash
   curl http://localhost:8000/health
   ```

3. Begin Sprint 2 — Company and Snapshot lifecycle

---

**Status:** All Sprint 1 infrastructure tested and verified ✓
