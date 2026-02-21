# Munqith – Software Requirements Specification (SRS)
Version: 1.0  
Scope: Kingdom of Saudi Arabia (KSA)  
System Type: Financial Intelligence Platform for Startups  

---

# 1. Domain Overview

Munqith is a deterministic financial intelligence system designed for Saudi startups.

It evaluates company financial health using:
- Structured signals
- Deterministic rules
- Rule-based stage derivation

The system prioritizes:
- Explainability
- Auditability
- Historical integrity

AI is excluded from live decision paths.

---

# 2. Core Domain Entities

- Company
- Snapshot (immutable once finalized)
- Signal
- Signal Rule
- Stage
- Contributing Signals

---

# 3. Core Principles

- Snapshots are immutable after finalization.
- Stage is derived, never manually assigned.
- AI does not affect live decisions.
- All finalized snapshots are preserved.
- Soft invalidation allowed.

---

# 4. Functional Requirements (MoSCoW)

## MUST HAVE

### M1 — Company Management
- Create company
- Store metadata
- Company owns chronological snapshots
- No financial logic in company

### M2 — Snapshot Lifecycle
- Create snapshot for specific date
- Snapshot status: DRAFT | FINALIZED | INVALIDATED
- Immutable once finalized
- Stores:
  - Financial attributes
  - Derived metrics
  - Signals
  - Rule results
  - Stage
  - Contributing signals

### M3 — Financial Attributes
- Cash Balance (SAR)
- Monthly Revenue (SAR)
- Operating Costs (SAR)
- Monthly Burn = costs − revenue
- Runway Months = cash ÷ burn

### M4 — Signal Engine
- Compute signals from snapshot data
- Signals have:
  - type
  - numeric value
- Signals stored in snapshot

### M5 — Rule Engine
- Deterministic rules
- Operate only on signals
- No AI
- No external services

### M6 — Stage Evaluation
Baseline stages:
- IDEA
- PRE_SEED
- SEED
- SERIES_A
- GROWTH

Stage derived from rules + signals.

### M7 — Explainability
- Store contributing signals
- Expose reason for stage

### M8 — Historical Integrity
- Preserve all snapshots
- Allow comparison
- Never overwrite history

---

# 5. Non-Functional Requirements

## Performance
- Snapshot finalization < 500ms
- Linear scaling with signal count

## Scalability
- Thousands of snapshots
- Multiple companies
- Horizontal scaling ready

## Reliability
- Snapshot finalization atomic
- No partial persistence

## Auditability
- Deterministic stage logic
- No randomness

## Security
- Data isolation per company
- Authentication required
- Encryption at rest

## Maintainability
- Domain logic framework-independent
- No circular dependencies
- Business logic testable in isolation