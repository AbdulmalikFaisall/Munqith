"""sprint11: add analytics insights table

Revision ID: 002_add_analytics_insights
Revises: 001_initial
Create Date: 2026-03-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002_add_analytics_insights'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create analytics_insights table for offline analytics results."""
    op.create_table(
        'analytics_insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('insight_type', sa.String(100), nullable=False),
        sa.Column('insight_value', sa.String(255), nullable=False),
        sa.Column('details', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient querying
    op.create_index('ix_analytics_company_snapshot', 'analytics_insights', ['company_id', 'snapshot_id'])
    op.create_index('ix_analytics_snapshot_id', 'analytics_insights', ['snapshot_id'])
    op.create_index('ix_analytics_company_id', 'analytics_insights', ['company_id'])
    op.create_index('ix_analytics_insight_type', 'analytics_insights', ['insight_type'])
    op.create_index('ix_analytics_created_at', 'analytics_insights', ['created_at'])


def downgrade() -> None:
    """Drop analytics_insights table and indexes."""
    op.drop_index('ix_analytics_created_at', table_name='analytics_insights')
    op.drop_index('ix_analytics_insight_type', table_name='analytics_insights')
    op.drop_index('ix_analytics_company_id', table_name='analytics_insights')
    op.drop_index('ix_analytics_snapshot_id', table_name='analytics_insights')
    op.drop_index('ix_analytics_company_snapshot', table_name='analytics_insights')
    op.drop_table('analytics_insights')
