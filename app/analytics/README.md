"""Analytics module for Sprint 11 - Offline AI/Insights Context.

This module provides offline-only analytics that reads finalized snapshots
and produces additional insights without affecting core decision logic.

# Core Principles

1. **Isolated from Core Decision Path**
   - Never modifies snapshot.stage
   - Never modifies rule results
   - Never affected live finalization flow
   - CLI/batch-only execution

2. **Deterministic & Auditable**
   - Same historical data → same insights every time
   - No machine learning or randomness
   - Pure rule-based heuristics
   - Reproducible analysis

3. **Append-Only Storage**
   - analytics_insights table stores all results
   - Never edits existing insights
   - Read-only access to snapshot history
   - Full audit trail maintained

## Module Structure

```
app/analytics/
├── __init__.py
├── reader/
│   ├── __init__.py
│   └── snapshot_reader.py          # Read-only finalized snapshot access
├── engines/
│   ├── __init__.py
│   ├── trajectory_detector.py      # Failure trajectory detection
│   └── archetype_labeler.py        # Risk archetype labeling
├── use_cases/
│   ├── __init__.py
│   └── run_batch_analysis.py       # Orchestrates analysis pipeline
├── cli/
│   ├── __init__.py
│   └── run_analysis.py             # CLI entry point for batch runs
└── dtos/
    └── __init__.py                 # Future: DTOs for API responses
```

## Key Components

### 1. SnapshotReader (Read-Only Infrastructure)
- Loads finalized snapshots only
- Excludes DRAFT and INVALIDATED
- Chronologically ordered
- No modifications to snapshots

### 2. TrajectoryDetector (Pure Analytics Engine)
Detects failure patterns:
- **RUNWAY_COLLAPSE**: Runway declining and < 6 months
- **BURN_SPIKE**: Monthly burn increases ≥ 25%
- **REVENUE_DECLINE_STREAK**: Revenue declining 3+ consecutive months

### 3. ArchetypeLabeler (Pure Analytics Engine)
Assigns risk labels:
- **PROFITABLE_GROWER**: Burn ≤ 0 + revenue growing
- **CASH_BURNER**: Burn > 0 + runway < 12 months
- **RUNWAY_CRITICAL**: Runway < 6 months
- **UNSTABLE_COSTS**: 2+ burn spikes in recent history

### 4. RunBatchAnalysisUseCase (Orchestration)
- Loads company history
- Runs detectors/labelers
- Persists results to analytics_insights
- Returns summary

### 5. CLI: python -m app.analytics.cli.run_analysis
- Entry point for offline batch runs
- Takes --company-id parameter
- No FastAPI required
- Full error handling and reporting

## Database Schema

### analytics_insights Table
```sql
CREATE TABLE analytics_insights (
    id UUID PRIMARY KEY,
    company_id UUID (FK companies.id),
    snapshot_id UUID (FK snapshots.id),
    insight_type VARCHAR(100),        -- e.g., RISK_ARCHETYPE, TRAJECTORY_ALERT
    insight_value VARCHAR(255),       -- e.g., RUNWAY_COLLAPSE, PROFITABLE_GROWER
    details TEXT,                     -- Optional JSON/details
    created_at TIMESTAMP
);

-- Indexes for efficient querying
CREATE INDEX ix_analytics_company_snapshot ON analytics_insights(company_id, snapshot_id);
CREATE INDEX ix_analytics_snapshot_id ON analytics_insights(snapshot_id);
CREATE INDEX ix_analytics_company_id ON analytics_insights(company_id);
CREATE INDEX ix_analytics_insight_type ON analytics_insights(insight_type);
CREATE INDEX ix_analytics_created_at ON analytics_insights(created_at);
```

## Usage Examples

### Example 1: Run Analysis for a Company

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

### Example 2: Batch Analysis Via Code

```python
from sqlalchemy.orm import Session
from app.analytics.use_cases.run_batch_analysis import RunBatchAnalysisUseCase
from uuid import UUID

session = get_db_session()
use_case = RunBatchAnalysisUseCase(session)

result = use_case.execute(UUID("550e8400-e29b-41d4-a716-446655440000"))

print(f"Analyzed {result['snapshots_analyzed']} snapshots")
print(f"Created {result['insights_created']} insights")
```

### Example 3: Query Generated Insights

```python
from app.infrastructure.repositories.analytics_repository import AnalyticsRepository
from uuid import UUID

repo = AnalyticsRepository(session)

# Get all insights for a company
all_insights = repo.get_insights_for_company(company_id)

# Get insights for a specific snapshot
snapshot_insights = repo.get_insights_for_snapshot(snapshot_id)

# Get insights of a specific type
archetype_labels = repo.get_insights_by_type(company_id, "RISK_ARCHETYPE")
```

## Testing

Run tests:
```bash
pytest tests/analytics/test_sprint11_analytics.py
```

Manual test scenarios (built into test file):
1. Runway Collapse detection (12 → 9 → 7 → 5 months)
2. Burn Spike detection (40k → 55k)
3. Revenue Decline Streak (30k → 25k → 20k)

## Migration

Apply the analytics table migration:
```bash
alembic upgrade head
```

This creates the analytics_insights table with all required indexes.

## Non-Functional Characteristics

✓ **Deterministic**: Same input → Same output (no randomness)
✓ **Auditable**: Full append-only history maintained
✓ **Scalable**: Efficient indexes on common query patterns
✓ **Isolated**: Zero coupling to core domain logic
✓ **Safe**: Read-only access to snapshot data
✓ **Performant**: O(n) analysis on snapshot history

## What This Module Does NOT Do

❌ Modify snapshot.stage
❌ Change rule results
❌ Affect snapshot lifecycle
❌ Call external APIs
❌ Use machine learning
❌ Run during finalization
❌ Impact production data integrity

## Future Enhancements (Out of Sprint 11 Scope)

- REST API endpoint to query insights
- Bulk analysis for all companies
- Scheduled batch runners
- Insight versioning
- Risk scoring aggregation
- Trend visualization
- Export analytics reports

## Monitoring & Logging

For production monitoring:
- Log all batch runs with timestamps
- Track insights generated per company
- Monitor CLI execution times
- Alert on missing finalized snapshots
- Audit changes to analytics tables via DB logs

"""
