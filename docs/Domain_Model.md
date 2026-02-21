# KSA Company Intelligence Domain Model (Baseline)

---

# 1. Purpose

Defines a deterministic, explainable intelligence system for KSA startups.

The system must:
- Determine stage
- Explain stage
- Track historical evolution
- Preserve historical truth

---

# 2. Core Concepts

- Company
- Snapshot
- Signal
- Rule
- Stage
- Contributing Signals

---

# 3. Company

Represents a Saudi-based startup.

Contains:
- Metadata
- Chronological snapshots

Does NOT store:
- Stage
- Financial logic

---

# 4. Snapshot (Core Concept)

A Snapshot is:

- Time-bound
- Immutable once finalized
- Self-contained
- Independently evaluable

Contains:
- Financial attributes
- Derived metrics
- Signals
- Rule results
- Stage
- Contributing signals

---

# 5. Financial Attributes

## Cash Balance
Liquid cash available (SAR)

## Monthly Burn
Operating Costs − Monthly Revenue

## Runway Months
Cash Balance ÷ Monthly Burn

KSA interpretation:
- < 6 months → High risk
- 6–12 months → Caution
- > 12 months → Healthy

---

# 6. Signals

A Signal is a structured interpretation of data.

Categories:
- FINANCIAL
- GROWTH
- RISK
- OPERATIONAL
- MARKET

Signals:
- Have numeric value
- Are computed from snapshot data
- Do not duplicate raw financial data

---

# 7. Rules

Rules:
- Deterministic
- Operate only on signals
- No DB calls
- No HTTP calls
- No AI

Example:
IF RunwayMonths < 6 → HIGH_RISK

Rules are reusable and testable.

---

# 8. Stage

Stage:
- Derived per snapshot
- Never manually assigned
- Based on rules + signals

Baseline:
- IDEA
- PRE_SEED
- SEED
- SERIES_A
- GROWTH

---

# 9. Contributing Signals

Explicit record of signals that influenced stage.

Purpose:
- Transparency
- Investor clarity
- Regulatory clarity
- No black box decisions

---

# 10. Snapshot Lifecycle

DRAFT → FINALIZED  
FINALIZED → INVALIDATED  

Constraints:
- Only DRAFT editable
- FINALIZED immutable
- INVALIDATED excluded from trends