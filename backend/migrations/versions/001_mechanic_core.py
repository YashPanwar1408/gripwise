"""Add rider consent and workshop service records before mechanic growth.

Revision ID: 001_mechanic_core
Revises: 001_initial
Create Date: 2026-10-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "001_mechanic_core"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "consent_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("rider_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("mechanic_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("rider_id", "mechanic_id", name="uq_rider_mechanic_consent"),
    )

    op.create_table(
        "mechanic_findings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("inspection_id", sa.String(36), sa.ForeignKey("inspections.id"), nullable=False),
        sa.Column("mechanic_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tread_depth_mm", sa.Float, nullable=True),
        sa.Column("pressure_psi", sa.Float, nullable=True),
        sa.Column("puncture_count", sa.Integer, nullable=True),
        sa.Column("mechanic_notes", sa.Text, nullable=True),
        sa.Column("recommended_action", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "service_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tyre_position_id", sa.String(36), sa.ForeignKey("tyre_positions.id"), nullable=False),
        sa.Column("mechanic_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("service_type", sa.String(50), nullable=False),
        sa.Column("service_date", sa.Date, nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("odometer_km", sa.Integer, nullable=True),
        sa.Column("cost_amount", sa.Float, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("service_records")
    op.drop_table("mechanic_findings")
    op.drop_table("consent_records")
