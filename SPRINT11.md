# Sprint 11 — Offline AI Analytics (Completed)

## Goal
Build an offline-only AI/analytics context that reads historical finalized snapshots and produces additional insights (risk archetypes, trajectory warnings), stored separately from the core decision system.

## Non-Negotiable Rules ✓

✅ AI/analytics must NOT modify:
- `snapshot.stage`
- Rule results
- Signals used for stage
- Lifecycle state

✅ Module characteristics:
- Offline only (no use inside `/finalize` path)
- No calls from request/response critical endpoints
- Separated in codebase (separate namespace/module)
- Clear boundary from domain core
- Core decision path remains deterministic and reproducible without AI

## Deliverables Completed

### 1️⃣ Analytics DB Storage (Separate From Core) ✓
**File**: `app/infrastructure/db/models/analytics_insight.py`

Created new table: `analytics_snapshot_insights` (named `analytics_insights`)

Fields:
- `id` UUID PK
- `company_id` UUID FK (companies.id)
- `snapshot_id` UUID FK (snapshots.id)
- `insight_type` VARCHAR (e.g., "RISK_ARCHETYPE", "TRAJECTORY_ALERT")
- `insight_value` VARCHAR (e.g., "RUNWAY_COLLAPSE", "COST_SPIKE")
- `details` TEXT (optional)
- `created_at` TIMESTAMP

Indexes:
- `(company_id, snapshot_id)`
- `(snapshot_id)`
- `(company_id)`
- `(insight_type)`
- `(created_at)`

Properties:
✓ Append-only (no edits required)
✓ Not referenced by core stage evaluation
✓ Isolated from snapshots table

### 2️⃣ Historical Snapshot Reader ✓
**File**: `app/analytics/reader/snapshot_reader.py`

**SnapshotReader** class:
- `get_company_history(company_id: UUID) -> List[SnapshotModel]`
  - Returns FINALIZED snapshots only
  - Ordered ASC by snapshot_date
  - Excludes DRAFT and INVALIDATED
  - Read-only access

### 3️⃣ Trajectory Detector ✓
**File**: `app/analytics/engines/trajectory_detector.py`

**TrajectoryDetector** class:
- `detect(snapshots: List[SnapshotModel]) -> List[dict]`

Detections (deterministic):

**A) RUNWAY_COLLAPSE**
- Runway decreasing each month for 3+ snapshots
- Last runway < 6 months
- Returns: `{"alert_type": "TRAJECTORY_ALERT", "alert_value": "RUNWAY_COLLAPSE", "details": "...", "confidence": "HIGH"}`

**B) BURN_SPIKE**
- Current burn >= previous burn * 1.25 (25% increase)
- Last 2 snapshots
- Returns: `{"alert_type": "TRAJECTORY_ALERT", "alert_value": "BURN_SPIKE", "details": "...", "confidence": "HIGH"}`

**C) REVENUE_DECLINE_STREAK**
- Revenue decreasing 3+ consecutive snapshots
- Returns: `{"alert_type": "TRAJECTORY_ALERT", "alert_value": "REVENUE_DECLINE_STREAK", "details": "...", "confidence": "HIGH"}`

Properties:
✓ Deterministic (no randomness)
✓ No AI calls
✓ Pure heuristics
✓ No external data required

### 4️⃣ Risk Archetype Labeler ✓
**File**: `app/analytics/engines/archetype_labeler.py`

**ArchetypeLabeler** class:
- `label(snapshots: List[SnapshotModel]) -> List[dict]`

Example labels (deterministic):

**1. PROFITABLE_GROWER**
- Last monthly_burn <= 0 (profitable/break-even)
- Last revenue > previous revenue (growing)
- Scope: LATEST_SNAPSHOT

**2. CASH_BURNER**
- Last monthly_burn > 0 (burning cash)
- Last runway_months < 12 months
- Scope: LATEST_SNAPSHOT

**3. RUNWAY_CRITICAL**
- Last runway_months < 6 months
- Scope: LATEST_SNAPSHOT

**4. UNSTABLE_COSTS**
- 2+ burn spikes in last 4 snapshots
- Spike = burn increase >= 20%
- Scope: COMPANY_TRAJECTORY

Return format:
```python
{
    "label_type": "RISK_ARCHETYPE",
    "label_value": "PROFITABLE_GROWER",
    "scope": "LATEST_SNAPSHOT",
    "details": "Positive cash flow and growing revenue"
}
```

Properties:
✓ Deterministic (same input → same output)
✓ Simple, readable logic
✓ No randomness, no external calls

### 5️⃣ Batch Analysis Use Case ✓
**File**: `app/analytics/use_cases/run_batch_analysis.py`

**RunBatchAnalysisUseCase** class:
- `execute(company_id: UUID) -> dict`

Flow:
1. Load finalized snapshot history
2. Run TrajectoryDetector on full history
3. Run ArchetypeLabeler on full history
4. Persist all results to analytics_insights table
5. Commit transaction
6. Return summary

Return value:
```python
{
    "company_id": UUID,
    "snapshots_analyzed": int,
    "insights_created": int,
    "trajectory_alerts": int,
    "archetype_labels": int,
}
```

Properties:
✓ Orchestration-only (no business logic)
✓ Atomic transaction
✓ Append-only persistence
✓ No writes to snapshots table

### 6️⃣ CLI Runner ✓
**File**: `app/analytics/cli/run_analysis.py`

Runnable command:
```bash
python -m app.analytics.cli.run_analysis --company-id <UUID>
```

Example:
```bash
python -m app.analytics.cli.run_analysis --company-id 550e8400-e29b-41d4-a716-446655440000
```

Output:
```
✓ Analytics batch run completed for company 550e8400-e29b-41d4-a716-446655440000
  Snapshots analyzed: 4
  Insights created: 5
  - Trajectory alerts: 1
  - Archetype labels: 4
```

Properties:
✓ No FastAPI required
✓ Standalone execution
✓ Full error handling
✓ UUID validation
✓ Clear reporting

### 7️⃣ Database Migration ✓
**File**: `alembic/versions/002_add_analytics_insights.py`

Revision ID: `002_add_analytics_insights`
Down revision: `001_initial`

Creates:
- `analytics_insights` table
- All required indexes
- Proper FK constraints

Apply:
```bash
alembic upgrade head
```

### 8️⃣ Analytics Repository ✓
**File**: `app/infrastructure/repositories/analytics_repository.py`

**AnalyticsRepository** class:
- `save_insight(company_id, snapshot_id, insight_type, insight_value, details) -> AnalyticsInsightModel`
- `save_insights(company_id, snapshot_id, insights: List[dict]) -> List[AnalyticsInsightModel]`
- `get_insights_for_snapshot(snapshot_id) -> List[AnalyticsInsightModel]`
- `get_insights_for_company(company_id) -> List[AnalyticsInsightModel]`
- `get_insights_by_type(company_id, insight_type) -> List[AnalyticsInsightModel]`

Properties:
✓ Append-only writes
✓ Isolated from core repositories
✓ Efficient indexes on queries

### 9️⃣ Documentation & Tests ✓
**Files**:
- `app/analytics/README.md` — Comprehensive module documentation
- `tests/analytics/test_sprint11_analytics.py` — Test suite with manual scenarios

## Acceptance Criteria ✓

✅ **Analytics module exists** under `app/analytics/`
✅ **Can run analysis via CLI** — `python -m app.analytics.cli.run_analysis --company-id <UUID>`
✅ **Reads finalized history only** — Excluded DRAFT and INVALIDATED
✅ **Stores outputs separately** — `analytics_insights` table
✅ **No coupling into live decision path** — Zero imports in domain/finalization
✅ **Deterministic insights** — Same input → same output every time

## Manual Test Scenarios ✓

### Scenario 1: Runway Collapse
Given 4 finalized snapshots where:
```
runway: 12 → 9 → 7 → 5 months
```
Expect alert:
```
{ "alert_type": "TRAJECTORY_ALERT", "alert_value": "RUNWAY_COLLAPSE" }
```
✅ VERIFIED

### Scenario 2: Burn Spike
Given burn increases:
```
40k → 55k (37.5% increase)
```
Expect alert:
```
{ "alert_type": "TRAJECTORY_ALERT", "alert_value": "BURN_SPIKE" }
```
✅ VERIFIED

### Scenario 3: Revenue Decline Streak
Given revenue declining 3+ consecutive:
```
30k → 25k → 20k
```
Expect alert:
```
{ "alert_type": "TRAJECTORY_ALERT", "alert_value": "REVENUE_DECLINE_STREAK" }
```
✅ VERIFIED

All scenarios produce deterministic results with no snapshot table modifications.

## Isolation Verification ✓

❌ Does NOT occur anywhere in core logic:
- No `from app.analytics` imports in domain/
- No analytics calls in `finalize_snapshot.py`
- No analytics in request/response endpoints
- No modifications to `snapshot.stage`
- No changes to `rule_results` or `signals`
- No lifecycle state modifications

✅ Pure read-only access:
- analytics reads finalized snapshots only
- No write access to snapshot table
- All outputs go to separate analytics_insights table
- Append-only pattern maintained

## Module Architecture

```
app/
├── analytics/                    ← NEW: separate namespace
│   ├── __init__.py
│   ├── README.md
│   ├── reader/
│   │   ├── __init__.py
│   │   └── snapshot_reader.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── trajectory_detector.py
│   │   └── archetype_labeler.py
│   ├── use_cases/
│   │   ├── __init__.py
│   │   └── run_batch_analysis.py
│   ├── dtos/
│   │   └── __init__.py
│   └── cli/
│       ├── __init__.py
│       ├── __main__.py
│       └── run_analysis.py
├── infrastructure/
│   ├── db/
│   │   └── models/
│   │       ├── __init__.py
│   │       └── analytics_insight.py          ← NEW: analytics table model
│   └── repositories/
│       ├── __init__.py
│       └── analytics_repository.py           ← NEW: analytics persistence
└── ... (core domain modules unchanged)

alembic/
└── versions/
    ├── 001_initial_create_base_schema.py
    └── 002_add_analytics_insights.py         ← NEW: migration
```

## Non-Negotiables Verification ✓

| Requirement | Status | Evidence |
|-----------|--------|----------|
| No snapshot.stage modification | ✅ | AnalyticsInsight model has no stage field |
| No rule results modification | ✅ | Analytics ignores signals/rules |
| No lifecycle state change | ✅ | No snapshot status updates |
| Offline only | ✅ | CLI execution, no HTTP calls |
| Separate namespace | ✅ | `app/analytics/` completely isolated |
| Deterministic output | ✅ | Pure heuristics, no randomness |
| No core domain coupling | ✅ | Zero imports from domain in analytics |

## Performance Characteristics

- **Analysis Time**: O(n) where n = finalized snapshots
- **Memory**: O(n) for loading history, constant for detection
- **Storage**: O(m) where m = insights generated (append-only)
- **Query Performance**: Efficient indexes on all common query patterns

## Testing

Run test suite:
```bash
pytest tests/analytics/test_sprint11_analytics.py -v
```

Run manual scenarios:
```bash
cd tests/analytics
python test_sprint11_analytics.py
```

## Summary

Sprint 11 successfully implements a fully isolated analytics module that:
- Reads historical finalized snapshots deterministically
- Generates insights via pure heuristics (trajectory detection, archetype labeling)
- Stores results separately with no impact on core decision logic
- Provides CLI interface for offline batch analysis
- Maintains full auditability and reproducibility

**Status**: ✅ **COMPLETE** — All deliverables implemented and verified.
