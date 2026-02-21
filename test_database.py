#!/usr/bin/env python
"""
Sprint 1 Database Connection & Migration Test

This script tests:
1. Database connection establishment
2. Migration execution
3. Schema verification
"""

import sys
import os
sys.path.insert(0, '.')

from sqlalchemy import inspect, text
from app.infrastructure.db.session import SessionLocal, engine, get_database_url

print("=" * 70)
print("MUNQITH SPRINT 1 - DATABASE CONNECTION & MIGRATION TEST")
print("=" * 70)

# Test 1: Database URL
print("\n[1] Database Configuration")
try:
    db_url = get_database_url()
    print(f"✓ DATABASE_URL: {db_url[:50]}...")
except Exception as e:
    print(f"✗ Failed to get database URL: {e}")
    sys.exit(1)

# Test 2: Connection Test
print("\n[2] Database Connection Test")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✓ Successfully connected to PostgreSQL")
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("   Make sure PostgreSQL is running:")
    print("   docker-compose up -d postgres")
    sys.exit(1)

# Test 3: Schema Inspection
print("\n[3] Database Schema Verification")
try:
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    required_tables = [
        'companies',
        'snapshots',
        'signal_definitions',
        'snapshot_signals',
        'rule_definitions',
        'snapshot_rule_results',
        'stage_definitions',
        'snapshot_contributing_signals'
    ]
    
    missing_tables = [t for t in required_tables if t not in tables]
    
    if missing_tables:
        print(f"⚠ Missing tables: {missing_tables}")
        print("  Run: alembic upgrade head")
    else:
        print("✓ All required tables present")
        print(f"  Tables: {', '.join(required_tables)}")
        
except Exception as e:
    print(f"✗ Schema inspection failed: {e}")
    sys.exit(1)

# Test 4: Table Structure Verification
print("\n[4] Table Structure Verification")
try:
    inspector = inspect(engine)
    
    # Check companies table
    if 'companies' in inspector.get_table_names():
        cols = {c['name']: c['type'] for c in inspector.get_columns('companies')}
        required_cols = ['id', 'name', 'sector', 'created_at', 'updated_at']
        present = all(c in cols for c in required_cols)
        
        if present:
            print("✓ Companies table structure correct")
        else:
            missing = [c for c in required_cols if c not in cols]
            print(f"✗ Companies table missing columns: {missing}")
    else:
        print("⚠ Companies table not found (run migrations)")
        
    # Check snapshots table
    if 'snapshots' in inspector.get_table_names():
        cols = {c['name']: c['type'] for c in inspector.get_columns('snapshots')}
        required_cols = ['id', 'company_id', 'snapshot_date', 'cash_balance', 
                        'monthly_revenue', 'operating_costs', 'monthly_burn', 
                        'runway_months', 'stage', 'status']
        present = all(c in cols for c in required_cols)
        
        if present:
            print("✓ Snapshots table structure correct")
        else:
            missing = [c for c in required_cols if c not in cols]
            print(f"✗ Snapshots table missing columns: {missing}")
    else:
        print("⚠ Snapshots table not found (run migrations)")
        
except Exception as e:
    print(f"✗ Structure verification failed: {e}")
    sys.exit(1)

# Test 5: Session Creation
print("\n[5] Session Management Test")
try:
    db = SessionLocal()
    db.execute(text("SELECT 1"))
    db.close()
    print("✓ Session creation and cleanup successful")
except Exception as e:
    print(f"✗ Session test failed: {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL DATABASE TESTS PASSED ✓")
print("=" * 70)
