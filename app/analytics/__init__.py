"""
Analytics module - offline-only AI/insights context.

This module reads finalized historical snapshots and produces
additional insights (risk archetypes, trajectory warnings).

Key principle: This module is completely isolated from the core
decision system. No analytics output affects snapshot.stage,
rule results, or lifecycle state.
"""
