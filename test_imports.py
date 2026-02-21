#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

try:
    from app.infrastructure.db.models import Company, Snapshot
    print("✓ Models import successfully")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

try:
    from app.main import app
    print("✓ FastAPI app imports successfully")
except Exception as e:
    print(f"✗ Error importing app: {e}")
    import traceback
    traceback.print_exc()
