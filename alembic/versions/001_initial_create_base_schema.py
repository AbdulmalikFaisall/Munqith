"""initial: create base schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-02-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('sector', sa.String(100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create snapshots table
    op.create_table(
        'snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('cash_balance', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('monthly_revenue', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('operating_costs', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('monthly_burn', sa.Numeric(precision=18, scale=2), nullable=True),
        sa.Column('runway_months', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('stage', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), server_default='DRAFT', nullable=False),
        sa.Column('invalidation_reason', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.Column('finalized_at', sa.TIMESTAMP(timezone=False), nullable=True),
        sa.Column('invalidated_at', sa.TIMESTAMP(timezone=False), nullable=True),
        sa.CheckConstraint("status IN ('DRAFT', 'FINALIZED', 'INVALIDATED')", name='ck_snapshot_status'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create signal_definitions table
    op.create_table(
        'signal_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('signal_type', sa.String(50), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create snapshot_signals table
    op.create_table(
        'snapshot_signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signal_definition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('signal_value', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('computed_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['signal_definition_id'], ['signal_definitions.id'], ),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create rule_definitions table
    op.create_table(
        'rule_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('rule_type', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create snapshot_rule_results table
    op.create_table(
        'snapshot_rule_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_definition_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rule_satisfied', sa.Boolean(), nullable=False),
        sa.Column('evaluated_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['rule_definition_id'], ['rule_definitions.id'], ),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create stage_definitions table
    op.create_table(
        'stage_definitions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('description', sa.TEXT(), nullable=True),
        sa.Column('order', sa.String(10), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create snapshot_contributing_signals table
    op.create_table(
        'snapshot_contributing_signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('snapshot_signal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('contribution_reason', sa.TEXT(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots.id'], ),
        sa.ForeignKeyConstraint(['snapshot_signal_id'], ['snapshot_signals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('snapshot_contributing_signals')
    op.drop_table('stage_definitions')
    op.drop_table('snapshot_rule_results')
    op.drop_table('rule_definitions')
    op.drop_table('snapshot_signals')
    op.drop_table('signal_definitions')
    op.drop_table('snapshots')
    op.drop_table('companies')
