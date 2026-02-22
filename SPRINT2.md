# Munqith Sprint 2: Domain Core & Lifecycle

**Status**: ✅ COMPLETE  
**Date**: February 21-23, 2026  
**Sprint Goal**: Pure domain logic with zero framework coupling

---

## Overview

Sprint 2 implements the core domain layer - the heart of Munqith's business logic. This layer is completely framework-independent and contains all snapshot lifecycle state machines.

### Acceptance Criteria - ALL MET

✅ DRAFT → FINALIZED allowed  
✅ FINALIZED cannot be edited  
✅ FINALIZED → INVALIDATED allowed  
✅ INVALIDATED cannot transition back  
✅ Invalid transitions raise deterministic exceptions  
✅ Domain has zero FastAPI imports  
✅ Domain has zero SQLAlchemy imports  
✅ Domain has zero Pydantic imports  

---

## Implementation Summary

### 1. Enums (Framework-Independent)

#### `app/domain/enums/stage.py`
```python
class Stage(str, Enum):
    IDEA = "IDEA"
    PRE_SEED = "PRE_SEED"
    SEED = "SEED"
    SERIES_A = "SERIES_A"
    GROWTH = "GROWTH"
```

**Features:**
- String-based enum (inherits from `str, Enum`)
- JSON-serializable  
- Values match database exactly
- Comparable and hashable

#### `app/domain/enums/snapshot_status.py`
```python
class SnapshotStatus(str, Enum):
    DRAFT = "DRAFT"
    FINALIZED = "FINALIZED"
    INVALIDATED = "INVALIDATED"
```

**Features:**
- Represents snapshot lifecycle state
- Matches database constraint exactly
- Used in state machine logic

---

### 2. Exceptions (Deterministic & Specific)

#### `app/domain/exceptions/__init__.py`

All exceptions inherit from `DomainException`:

**InvalidSnapshotTransition**
- Raised for invalid state transitions (FINALIZED → DRAFT, etc.)
- Includes current and attempted status
- Deterministic error message

**ImmutableSnapshotError**
- Raised when modifying finalized snapshots
- Specific about what failed and why
- Clear audit trail

**InvalidateDraftSnapshotError**
- Only FINALIZED snapshots can be invalidated
- Prevents accidental draft invalidation

**FinalizeDraftOnlyError**
- Only DRAFT snapshots can be finalized
- Cannot finalize twice

---

### 3. Company Entity

#### `app/domain/entities/company.py`

**Responsibilities:**
- Hold metadata (id, name, sector)
- Validate name (non-empty string)
- No financial logic
- No stage storage
- No snapshot calculations

**Interface:**
```python
company = Company(
    id=uuid.uuid4(),
    name="TechStartup",
    sector="Technology",  # Optional
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow(),
)

# Properties
company.id           # UUID
company.name         # String (validated)
company.sector       # Optional string
company.created_at   # datetime
company.updated_at   # datetime

# Methods
company == other_company  # Equality by ID
hash(company)             # Hashable for sets/dicts
repr(company)             # String representation
```

**Validation:**
- Name must be non-empty string
- Whitespace stripped automatically
- Raises ValueError for invalid input

---

### 4. Snapshot Entity (Core)

#### `app/domain/entities/snapshot.py`

**Responsibilities:**
- Store financial snapshot data
- Enforce lifecycle transitions
- Prevent modifications after finalization
- Raise exceptions for invalid operations

**Lifecycle State Machine:**
```
          DRAFT (editable)
            |
            v (finalize())
        FINALIZED (immutable)
            |
            v (invalidate())
        INVALIDATED (terminal)
            
Rules:
- DRAFT → FINALIZED ✓ (transition)
- FINALIZED → INVALIDATED ✓ (transition)
- FINALIZED → DRAFT ✗ (disallowed)
- INVALIDATED → * ✗ (disallowed)
- FINALIZED by methods, not direct assignment
```

**Properties:**
```python
# Core data
snapshot.id                    # UUID
snapshot.company_id            # UUID
snapshot.snapshot_date         # date
snapshot.status                # SnapshotStatus
snapshot.is_draft              # bool property
snapshot.is_finalized          # bool property
snapshot.is_invalidated        # bool property

# Financial attributes (can be None initially)
snapshot.cash_balance          # Decimal
snapshot.monthly_revenue       # Decimal
snapshot.operating_costs       # Decimal
snapshot.monthly_burn          # Decimal
snapshot.runway_months         # Decimal

# Derived state
snapshot.stage                 # Optional[Stage]
snapshot.invalidation_reason   # Optional[str]

# Timestamps
snapshot.created_at            # datetime
snapshot.finalized_at          # Optional[datetime]
snapshot.invalidated_at        # Optional[datetime]
```

**Lifecycle Methods:**

1. **finalize()**
   ```python
   snapshot.finalize()
   ```
   - Allowed: Only from DRAFT
   - Sets: status → FINALIZED
   - Sets: finalized_at (timestamp)
   - Error: FinalizeDraftOnlyError if not DRAFT
   - Effect: Snapshot becomes immutable

2. **invalidate(reason: str)**
   ```python
   snapshot.invalidate("Data inconsistency")
   ```
   - Allowed: Only from FINALIZED
   - Sets: status → INVALIDATED
   - Sets: invalidation_reason (stored)
   - Sets: invalidated_at (timestamp)
   - Error: InvalidateDraftSnapshotError if not FINALIZED
   - Error: ValueError if reason is empty

3. **update_financials(...)**
   ```python
   snapshot.update_financials(
       cash_balance=Decimal("100000"),
       monthly_revenue=Decimal("50000"),
       # ... other fields optional
   )
   ```
   - Allowed: Only when DRAFT
   - Can update any/all financial fields
   - Fields are optional (None → changes only what's provided)
   - Error: ImmutableSnapshotError if not DRAFT

4. **set_stage(stage: Optional[Stage])**
   ```python
   snapshot.set_stage(Stage.SEED)
   snapshot.set_stage(None)  # Clear
   ```
   - Allowed: Only when DRAFT
   - Can set or clear (None)
   - Error: ImmutableSnapshotError if not DRAFT

---

## Architecture Verification

### Framework Isolation

**Verified (10/10 checks):**
- ✅ No `fastapi` imports in domain
- ✅ No `sqlalchemy` imports in domain
- ✅ No `pydantic` imports in domain
- ✅ No database session imports in domain
- ✅ No HTTP concepts in domain
- ✅ Pure Python only (uuid, datetime, decimal, enum)
- ✅ Uses only standard library + domain internals
- ✅ Enums compile and serialize correctly
- ✅ Entities behave deterministically
- ✅ Exception handling is explicit

### Code Quality

**Verified:**
- ✅ Type hints throughout
- ✅ Docstrings on all classes and methods
- ✅ Clear error messages
- ✅ No silent failures
- ✅ Immutability enforced by design
- ✅ State machine prevents illegal transitions
- ✅ All properties are read-only after finalization

---

## Testing

### Unit Tests Provided

**File: `tests/domain/test_company.py`**
- Company creation with minimal/full data
- Name validation and whitespace stripping
- Sector validation
- Equality and hashing
- Representation format

**File: `tests/domain/test_snapshot.py`**
- Snapshot creation and initialization
- Status properties (is_draft, is_finalized, is_invalidated)
- Finalize transition and error cases
- Invalidate transition and error cases
- Financial updates with immutability enforcement
- Stage setting with immutability enforcement
- Full lifecycle scenarios (DRAFT → FINALIZED → INVALIDATED)
- Equality and hashing

**Test Results:**
```
[Company Tests]           5/5 ✓
[Snapshot Tests]         10/10 ✓
[Enum Tests]              3/3 ✓
─────────────────────────────
TOTAL:                   18/18 ✓ ALL PASSED
```

### Running Tests

**Manual runner (no pytest required):**
```bash
/c/Python313/python.exe run_tests_manual.py
```

**With pytest (when installed):**
```bash
pytest tests/domain/ -v
```

---

## Verification Scripts

### verify_sprint2.py
Comprehensive domain layer verification:
```bash
/c/Python313/python.exe verify_sprint2.py
```

Output: 10/10 checks passed
- Enum compilation
- Exception definitions
- Entity compilation
- Framework isolation (FastAPI, SQLAlchemy, Pydantic)
- Entity behavior
- Full lifecycle behavior
- Test file existence
- Domain layer isolation

---

## Snapshot Lifecycle Example

Complete usage example:

```python
from uuid import uuid4
from datetime import date
from decimal import Decimal
from app.domain.entities import Snapshot
from app.domain.enums import Stage, SnapshotStatus

# 1. CREATE (DRAFT)
snapshot = Snapshot(
    id=uuid4(),
    company_id=uuid4(),
    snapshot_date=date.today(),
)
assert snapshot.is_draft
assert snapshot.status == SnapshotStatus.DRAFT

# 2. GATHER DATA (DRAFT)
snapshot.update_financials(
    cash_balance=Decimal("500000"),
    monthly_revenue=Decimal("100000"),
    operating_costs=Decimal("80000"),
    monthly_burn=Decimal("-20000"),
    runway_months=Decimal("25.00"),
)

# 3. DERIVE STAGE (DRAFT)
snapshot.set_stage(Stage.SERIES_A)

# 4. FINALIZE (DRAFT → FINALIZED)
snapshot.finalize()
assert snapshot.is_finalized
assert snapshot.finalized_at is not None

# 5. IMMUTABLE (FINALIZED)
try:
    snapshot.update_financials(cash_balance=Decimal("600000"))
except ImmutableSnapshotError as e:
    print(f"Cannot modify: {e}")

# 6. INVALIDATE (FINALIZED → INVALIDATED)
snapshot.invalidate("Discovered data error - Q1 actual revenue was 85k, not 100k")
assert snapshot.is_invalidated
assert snapshot.invalidation_reason == "Discovered data error..."
assert snapshot.invalidated_at is not None

# 7. TERMINAL (INVALIDATED)
# No further transitions allowed
```

---

## File Structure

```
app/domain/
├── __init__.py
├── enums/
│   ├── __init__.py
│   ├── stage.py              # Stage enum
│   └── snapshot_status.py    # SnapshotStatus enum
├── exceptions/
│   └── __init__.py           # Domain exceptions
├── entities/
│   ├── __init__.py
│   ├── company.py            # Company entity
│   └── snapshot.py           # Snapshot entity (core)
└── rules/                    # Reserved for Sprint 4
└── engines/                  # Reserved for Sprint 3

tests/domain/
├── __init__.py
├── test_company.py           # Company tests
└── test_snapshot.py          # Snapshot tests
```

---

## What's NOT in Sprint 2

❌ Signal computation  
❌ Rule evaluation  
❌ Stage derivation logic  
❌ DB queries  
❌ API endpoints  
❌ HTTP routing  
❌ Financial calculations  

These are Sprint 3+ (Signal Engine and Rule Engine).

---

## Key Design Decisions

1. **Immutability by Design**
   - No direct access to `_status`
   - Transitions only through explicit methods
   - Prevents accidental state corruption

2. **Deterministic Behavior**
   - All transitions either succeed or raise specific exceptions
   - No silent failures or warnings
   - Easy to test and audit

3. **Pure Python**
   - No framework dependencies
   - Uses only standard library (uuid, datetime, decimal, enum)
   - Testable without any infrastructure
   - Can be embedded in other systems

4. **String-Based Enums**
   - Inherits from both `str` and `Enum`
   - JSON-serializable directly
   - Can be used as dict keys
   - Matches database values exactly

5. **Explicit Exceptions**
   - Domain exceptions inherit from `DomainException`
   - Each scenario has its own exception class
   - Exceptions carry context (IDs, status, reasons)
   - Easy to distinguish between different errors

---

## Next Steps: Sprint 3

Sprint 3 will implement the Signal Engine:
- Monthly burn calculation
- Runway calculation
- Signal definitions
- Signal computation from snapshot data

Domain layer remains locked and doesn't change.

---

## Verification Checklist

Before committing, verify:

- [x] All 18 domain tests pass
- [x] All 10 verification checks pass
- [x] Zero FastAPI imports in domain
- [x] Zero SQLAlchemy imports in domain
- [x] Zero Pydantic imports in domain
- [x] Snapshot lifecycle enforces all transitions
- [x] Immutability is enforced
- [x] All exceptions are deterministic
- [x] Enums have correct values
- [x] Company entity works correctly

**Status: READY FOR PRODUCTION**
