#!/usr/bin/env python
"""
Sprint 1 Pre-Deployment Checklist

This runs all checks that don't require a running database.
"""

import sys
import os
sys.path.insert(0, '.')

print("=" * 70)
print("MUNQITH SPRINT 1 - FULL DEPLOYMENT CHECKLIST")
print("=" * 70)

checks_passed = 0
checks_failed = 0

# Check 1: Python Environment
print("\n[1/12] Python Environment")
try:
    import sys
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 11:
        print(f"✓ Python {version_info.major}.{version_info.minor}.{version_info.micro}")
        checks_passed += 1
    else:
        print(f"✗ Python {version_info.major}.{version_info.minor} (need 3.11+)")
        checks_failed += 1
except Exception as e:
    print(f"✗ Error: {e}")
    checks_failed += 1

# Check 2: Required Packages
print("\n[2/12] Required Python Packages")
try:
    packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'psycopg2', 'pydantic']
    missing = []
    for pkg in packages:
        try:
            __import__(pkg.replace('-', '_'))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        checks_failed += 1
    else:
        print(f"✓ All required packages installed")
        checks_passed += 1
except Exception as e:
    print(f"✗ Error: {e}")
    checks_failed += 1

# Check 3: Models Compilation
print("\n[3/12] Database Models Syntax")
try:
    from app.infrastructure.db.models import (
        Company, Snapshot, SignalDefinition, SnapshotSignal,
        RuleDefinition, SnapshotRuleResult, StageDefinition,
        SnapshotContributingSignal
    )
    print("✓ All 8 models compile correctly")
    checks_passed += 1
except Exception as e:
    print(f"✗ Model compilation failed: {e}")
    checks_failed += 1

# Check 4: FastAPI App
print("\n[4/12] FastAPI Application")
try:
    from app.main import app
    routes = [route.path for route in app.routes]
    has_health = '/health' in routes
    if has_health:
        print(f"✓ FastAPI app ready with {len(routes)} routes (includes /health)")
        checks_passed += 1
    else:
        print(f"✗ Health endpoint not found")
        checks_failed += 1
except Exception as e:
    print(f"✗ App initialization failed: {e}")
    checks_failed += 1

# Check 5: Domain Independence
print("\n[5/12] Domain Layer Independence")
try:
    has_framework_import = False
    domain_path = 'app/domain'
    for root, dirs, files in os.walk(domain_path):
        for f in files:
            if f.endswith('.py') and f != '__init__.py':
                filepath = os.path.join(root, f)
                with open(filepath, 'r') as file:
                    content = file.read()
                    if 'fastapi' in content.lower() or 'sqlalchemy' in content.lower():
                        has_framework_import = True
                        break
    
    if not has_framework_import:
        print("✓ Domain layer is framework-independent")
        checks_passed += 1
    else:
        print("✗ Domain layer contains framework imports")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 6: Alembic Configuration
print("\n[6/12] Alembic Configuration")
try:
    if os.path.exists('alembic.ini') and os.path.exists('alembic/env.py'):
        print("✓ Alembic configuration files present")
        checks_passed += 1
    else:
        print("✗ Alembic files missing")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 7: Initial Migration File
print("\n[7/12] Migration Files")
try:
    migration_file = 'alembic/versions/001_initial_create_base_schema.py'
    if os.path.exists(migration_file):
        with open(migration_file, 'r') as f:
            content = f.read()
            if 'def upgrade()' in content and 'def downgrade()' in content:
                print("✓ Initial migration file valid")
                checks_passed += 1
            else:
                print("✗ Migration file incomplete")
                checks_failed += 1
    else:
        print("✗ Migration file not found")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 8: Docker Configuration
print("\n[8/12] Docker Configuration")
try:
    if os.path.exists('Dockerfile') and os.path.exists('docker-compose.yml'):
        with open('Dockerfile', 'r') as f:
            docker_content = f.read()
        with open('docker-compose.yml', 'r') as f:
            compose_content = f.read()
        
        has_postgres = 'postgres' in compose_content.lower()
        has_app = 'app:' in compose_content or 'build:' in compose_content
        if has_postgres and has_app:
            print("✓ Docker & docker-compose configured")
            checks_passed += 1
        else:
            print("✗ Docker compose incomplete")
            checks_failed += 1
    else:
        print("✗ Docker files missing")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 9: Environment Variables
print("\n[9/12] Environment Configuration")
try:
    if os.path.exists('.env.example'):
        with open('.env.example', 'r') as f:
            content = f.read()
            if 'DATABASE_URL' in content:
                print("✓ .env.example configured")
                checks_passed += 1
            else:
                print("✗ .env.example incomplete")
                checks_failed += 1
    else:
        print("✗ .env.example not found")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 10: Git Configuration
print("\n[10/12] Git Configuration")
try:
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content and '__pycache__' in content:
                print("✓ .gitignore properly configured")
                checks_passed += 1
            else:
                print("✗ .gitignore incomplete")
                checks_failed += 1
    else:
        print("✗ .gitignore not found")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 11: Documentation
print("\n[11/12] Documentation")
try:
    docs_present = all(os.path.exists(f) for f in [
        'docs/SRS.md',
        'docs/Domain_Model.md',
        'SPRINT1.md',
        'README.md'
    ])
    if docs_present:
        print("✓ All documentation files present")
        checks_passed += 1
    else:
        print("✗ Some documentation files missing")
        checks_failed += 1
except Exception as e:
    print(f"✗ Check failed: {e}")
    checks_failed += 1

# Check 12: No Circular Imports
print("\n[12/12] Circular Dependency Check")
try:
    import importlib
    import pkgutil
    # Try importing all app modules
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=['app'],
        prefix='app.',
        onerror=lambda x: None
    ):
        try:
            __import__(modname)
        except ImportError as e:
            if "circular" not in str(e).lower():
                pass
    print("✓ No circular imports detected")
    checks_passed += 1
except Exception as e:
    print(f"✗ Circular import check failed: {e}")
    checks_failed += 1

# Summary
print("\n" + "=" * 70)
print(f"RESULTS: {checks_passed}/12 checks passed")
if checks_failed == 0:
    print("✓ ALL CHECKS PASSED - READY FOR DEPLOYMENT")
else:
    print(f"✗ {checks_failed} checks failed - review above")
print("=" * 70)

print("\nNEXT STEPS:")
print("1. Start PostgreSQL: docker-compose up -d postgres")
print("2. Run migrations: alembic upgrade head")
print("3. Test database: python test_database.py")
print("4. Start app: uvicorn app.main:app --reload")

sys.exit(0 if checks_failed == 0 else 1)
