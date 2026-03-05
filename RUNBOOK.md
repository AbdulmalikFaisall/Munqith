# RUNBOOK — Munqith Operations Guide

## Overview

This runbook covers common operational issues, failure modes, and recovery procedures for Munqith production deployments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Common Failures](#common-failures)
3. [Restart Procedures](#restart-procedures)
4. [Backup & Recovery](#backup--recovery)
5. [Performance Tuning](#performance-tuning)
6. [Where to Find Logs](#where-to-find-logs)
7. [Emergency Procedures](#emergency-procedures)

---

## Pre-Deployment Checklist

Before deploying to production, verify:

```bash
# 1. Architecture compliance
python scripts/arch_audit.py
✓ Should pass with no violations

# 2. All tests pass
pytest tests/ -v
✓ All tests should pass

# 3. Smoke test passes
bash scripts/smoke_test.sh
✓ Full deployment cycle should complete

# 4. Environment is configured
cat .env
✓ DB_PASSWORD should be changed from default

# 5. Database is reachable
docker-compose ps
✓ Both postgres and api should be running
```

---

## Common Failures

### 1. "Cannot Connect to PostgreSQL"

**Symptoms**:
- API container logs: `connection refused` or `couldn't resolve postgres`
- Health check endpoint returns non-200

**Diagnosis**:
```bash
# Check if postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres | tail -20

# Test postgres directly
docker-compose exec postgres psql -U munqith -d munqith -c "SELECT 1"
```

**Solutions**:

**If postgres won't start**:
```bash
# Check volume permissions
docker-compose down -v
docker-compose up -d postgres --build

# Wait for postgres to be ready
docker-compose logs postgres | grep "ready to accept"
```

**If postgres started but API can't connect**:
```bash
# Verify network connectivity
docker-compose exec api ping postgres

# Check DATABASE_URL in API container
docker-compose exec api env | grep DATABASE_URL

# Verify credentials match
# In .env: DB_USER, DB_PASSWORD
# In docker-compose: matches POSTGRES_USER, POSTGRES_PASSWORD
```

**Recovery**:
```bash
# Full restart
docker-compose down
docker-compose up -d --build
sleep 15  # Wait for postgres startup
curl http://localhost:8000/health
```

### 2. "Database Migrations Failed"

**Symptoms**:
- API logs: `FAILED` or `ERROR` from alembic
- API container exits immediately

**Diagnosis**:
```bash
# Check current schema version
docker-compose exec postgres psql -U munqith -d munqith \
  -c "SELECT version, description FROM alembic_version"

# Run migrations with verbose output
docker-compose exec api alembic upgrade head --verbose
```

**Solutions**:

**If migration is stuck**:
```bash
# Manually clear the migration lock
docker-compose exec postgres psql -U munqith -d munqith \
  -c "DELETE FROM alembic_version WHERE version = 'lock'"

# Rollback to previous version
docker-compose exec api alembic downgrade -1

# Then upgrade again
docker-compose exec api alembic upgrade head
```

**If database schema is corrupted**:
```bash
# Backup existing data
docker-compose exec postgres pg_dump -U munqith munqith > backup.sql

# Drop and recreate database
docker-compose exec postgres psql -U munqith \
  -c "DROP DATABASE munqith; CREATE DATABASE munqith;"

# Run migrations from scratch
docker-compose exec api alembic upgrade head
```

### 3. "API Container Crashes on Startup"

**Symptoms**:
- `docker-compose ps` shows api container is exiting
- No health check response

**Diagnosis**:
```bash
# Check error logs
docker-compose logs api --tail=50

# Common errors to look for:
# - ImportError: missing dependency
# - SyntaxError in Python code
# - Invalid configuration
```

**Solutions**:

**If ImportError**:
```bash
# Rebuild with fresh dependencies
docker-compose down
docker-compose up -d --build

# Or if locally developing:
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**If SyntaxError**:
- Check your recent code changes
- Run locally: `python -m py_compile app/main.py`
- Revert the problematic commit and redeploy

**If configuration error**:
```bash
# Check environment variables
docker-compose exec api env | sort

# Verify .env file
cat .env | grep -E "DB_|API_"

# Compare to .env.example
diff .env.example .env
```

### 4. "Health Check Failing"

**Symptoms**:
```bash
curl -i http://localhost:8000/health
# Returns non-200 status or timeout
```

**Diagnosis**:
```bash
# Check if app is running
docker-compose ps api

# Check logs
docker-compose logs api | tail -20

# Try connecting manually
docker-compose exec api curl -i http://localhost:8000/health
```

**Solutions**:
```bash
# Restart just the API
docker-compose restart api

# Wait for startup
sleep 5

# Try health check again
curl http://localhost:8000/health
```

### 5. "Database Disk Full"

**Symptoms**:
- Errors like `no space left on device`
- `docker-compose logs postgres | grep "disk full"`

**Diagnosis**:
```bash
# Check volume size
docker volume ls
docker volume inspect munqith_postgres_data

# Check actual disk usage
df -h

# Check postgres data directory
docker-compose exec postgres du -sh /var/lib/postgresql/data
```

**Solutions**:
```bash
# Clean up old snapshots if safe
# (Only delete INVALIDATED snapshots marked for cleanup)

# Or expand volume (depends on storage backend)

# Temporary: restart postgres to reclaim space
docker-compose restart postgres
```

---

## Restart Procedures

### Graceful Restart (preserve data)

```bash
# Restart all services
docker-compose restart

# Restart just API
docker-compose restart api

# Restart just database
docker-compose restart postgres

# Wait for startup
sleep 10
curl http://localhost:8000/health
```

### Hard Restart (clean shutdown)

```bash
# Stop all services
docker-compose stop

# Wait for graceful shutdown
sleep 5

# Start again
docker-compose up -d
```

### Rebuild (fresh containers)

```bash
# Detain containers and rebuild
docker-compose up -d --build

# Or explicitly rebuild then start
docker-compose build
docker-compose up -d
```

---

## Backup & Recovery

### Regular Backups

**Daily backup**:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
docker-compose exec -T postgres pg_dump -U munqith munqith \
  > backups/munqith_${TIMESTAMP}.sql
gzip backups/munqith_${TIMESTAMP}.sql
```

**Add to crontab for daily backups**:
```bash
0 2 * * * /path/to/backup.sh  # 2 AM daily
```

### Restoring from Backup

```bash
# Full restore (careful! replaces all data)
docker-compose down
docker-compose up -d postgres

# Wait for postgres startup
sleep 10

# Restore database
docker-compose exec -T postgres psql -U munqith munqith < backup.sql

# Restart API
docker-compose up -d api
curl http://localhost:8000/health
```

### Point-in-Time Recovery

PostgreSQL supports PITR, but requires WAL archiving. See PostgreSQL docs for setup.

---

## Performance Tuning

### Database Optimization

```bash
# Analyze tables for query optimization
docker-compose exec postgres psql -U munqith munqith \
  -c "ANALYZE;"

# Reindex important tables
docker-compose exec postgres psql -U munqith munqith \
  -c "REINDEX INDEX CONCURRENTLY ix_snapshot_company_finalized;"

# Check index usage
docker-compose exec postgres psql -U munqith munqith \
  -c "SELECT schemaname, tablename, indexname, idx_scan \
      FROM pg_stat_user_indexes \
      ORDER BY idx_scan DESC LIMIT 10;"
```

### Connection Pooling

Database connection pool is configured in `app/infrastructure/db/session.py`. Monitor:

```bash
# Check active connections
docker-compose exec postgres psql -U munqith munqith \
  -c "SELECT count(*) FROM pg_stat_activity;"
```

### Query Performance

Enable slow query logging:
```bash
# Modify postgres startup
# Add to docker-compose.yml postgres section:
command:
  - "postgres"
  - "-c"
  - "log_min_duration_statement=1000"  # Log queries > 1 second
```

Then check logs for slow queries:
```bash
docker-compose logs postgres | grep "duration:"
```

---

## Where to Find Logs

### API Logs

```bash
# Real-time
docker-compose logs -f api

# Last 100 lines
docker-compose logs api --tail=100

# With timestamps
docker-compose logs api -t

# Specific time range
docker-compose logs api --since 2026-03-05 --until 2026-03-06
```

### Database Logs

```bash
# Real-time
docker-compose logs -f postgres

# Errors only
docker-compose logs postgres 2>&1 | grep ERROR
```

### System Logs

```bash
# Docker daemon logs
journalctl -u docker

# Container resource usage
docker stats munqith_api munqith_postgres
```

### Log Location in Container

- **Application logs**: stdout (captured by docker-compose logs)
- **File logs** (if enabled): `/app/logs/munqith.log`

---

## Emergency Procedures

### Full System Failure

If the entire system is unresponsive:

```bash
# 1. Stop everything gracefully
docker-compose stop --timeout=30

# 2. Check system resources
df -h
free -h
docker system df

# 3. Restart Docker daemon
systemctl restart docker

# 4. Start system again
docker-compose up -d

# 5. Wait for startup
sleep 20
curl http://localhost:8000/health
```

### Data Corruption

If database is corrupted:

```bash
# 1. Backup whatever we can
docker-compose exec postgres pg_dump -U munqith munqith \
  > corruption_backup.sql 2>&1 || true

# 2. Drop and reinitialize
docker-compose down -v
rm -rf postgres_data/

# 3. Restart
docker-compose up -d

# 4. Run migrations
docker-compose exec api alembic upgrade head

# 5. Restore from recent backup
docker-compose exec -T postgres psql -U munqith munqith < last_good_backup.sql
```

### Out of Disk Space (Emergency)

```bash
# 1. Identify largest tables
docker-compose exec postgres psql -U munqith munqith \
  -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) \
      FROM pg_tables WHERE schemaname = 'public' \
      ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 5;"

# 2. If safe: Delete old invalidated snapshots
# (requires careful consideration - only if marked for deletion)

# 3. Emergency resize: Add more disk or move volume

# 4. Restart postgres
docker-compose restart postgres
```

---

## Monitoring Checklist

Run daily:

```bash
# Overall health
docker-compose ps
curl http://localhost:8000/health

# Database size
docker-compose exec postgres psql -U munqith munqith \
  -c "SELECT pg_size_pretty(pg_database_size('munqith'));"

# Slow queries
docker-compose logs postgres --since 24h | grep duration

# Error rate (in application logs)
docker-compose logs api --since 24h | grep ERROR | wc -l

# Backup verification
ls -lh backups/ | tail -5
```

---

## Support

For issues not covered here:
1. Check application logs: `docker-compose logs -f`
2. Check [README.md](README.md) troubleshooting section
3. Review [CONTRIBUTING.md](CONTRIBUTING.md) for architecture constraints
4. Open GitHub issue with:
   - Logs (sanitized)
   - Steps to reproduce
   - System info (OS, Docker version)

—

**Last Updated**: March 2026  
**Version**: Sprint 12 Production Release
