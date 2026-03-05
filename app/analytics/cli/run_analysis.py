"""CLI runner for offline batch analysis.

Provides a command-line interface to run analytics without FastAPI.
Can be invoked via: python -m app.analytics.cli.run_analysis --company-id <UUID>
"""
import sys
import argparse
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.db.session import SessionLocal
from app.analytics.use_cases.run_batch_analysis import RunBatchAnalysisUseCase


def main():
    """
    CLI entry point for batch analysis.
    
    Usage:
        python -m app.analytics.cli.run_analysis --company-id <UUID>
        python -m app.analytics.cli.run_analysis --company-id 550e8400-e29b-41d4-a716-446655440000
    """
    parser = argparse.ArgumentParser(
        description="Run offline analytics batch analysis for a company"
    )
    parser.add_argument(
        "--company-id",
        type=str,
        required=True,
        help="Company UUID to analyze",
    )
    
    args = parser.parse_args()
    
    # Validate UUID format
    try:
        company_id = UUID(args.company_id)
    except ValueError:
        print(f"Error: Invalid UUID format: {args.company_id}", file=sys.stderr)
        sys.exit(1)
    
    # Create database session
    session: Session = SessionLocal()
    
    try:
        # Create and execute use case
        use_case = RunBatchAnalysisUseCase(session)
        result = use_case.execute(company_id)
        
        # Print results
        print(f"✓ Analytics batch run completed for company {company_id}")
        print(f"  Snapshots analyzed: {result['snapshots_analyzed']}")
        print(f"  Insights created: {result['insights_created']}")
        print(f"  - Trajectory alerts: {result['trajectory_alerts']}")
        print(f"  - Archetype labels: {result['archetype_labels']}")
        
        if result["insights_created"] == 0:
            print("  (No finalized snapshots or insights generated)")
        
        sys.exit(0)
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    finally:
        session.close()


if __name__ == "__main__":
    main()
