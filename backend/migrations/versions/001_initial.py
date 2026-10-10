"""Initial schema — all Phase 1 tables.

Revision ID: 001_initial
Revises:
Create Date: 2026-10-10
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=True),
        sa.Column("mobile", sa.String(20), unique=True, nullable=True),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("workshop_name", sa.String(200), nullable=True),
        sa.Column("workshop_city", sa.String(100), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "vehicles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("make", sa.String(100), nullable=False),
        sa.Column("model", sa.String(100), nullable=False),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("registration", sa.String(20), nullable=True),
        sa.Column("vehicle_type", sa.String(20), nullable=False, server_default="MOTORCYCLE"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_vehicles_owner", "vehicles", ["owner_id"])

    op.create_table(
        "tyre_positions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("vehicle_id", sa.String(36), sa.ForeignKey("vehicles.id"), nullable=False),
        sa.Column("position", sa.String(20), nullable=False),
        sa.Column("brand", sa.String(100), nullable=True),
        sa.Column("model_name", sa.String(100), nullable=True),
        sa.Column("size_spec", sa.String(50), nullable=True),
        sa.Column("installed_at", sa.Date, nullable=True),
        sa.Column("installed_km", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("vehicle_id", "position", name="uq_vehicle_position"),
    )

    op.create_table(
        "inspections",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tyre_position_id", sa.String(36), sa.ForeignKey("tyre_positions.id"), nullable=False),
        sa.Column("submitted_by", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("odometer_km", sa.Integer, nullable=True),
        sa.Column("image_path", sa.String(500), nullable=False),
        sa.Column("image_hash", sa.String(64), nullable=False),
        sa.Column("image_size_bytes", sa.Integer, nullable=False),
        sa.Column("image_quality_status", sa.String(20), nullable=False, server_default="UNKNOWN"),
        sa.Column("quality_issues", JSONB, nullable=True),
        sa.Column("inference_provider", sa.String(50), nullable=True),
        sa.Column("model_version", sa.String(50), nullable=True),
        sa.Column("recommended_action", sa.String(50), nullable=True),
        sa.Column("recommended_action_explanation", sa.Text, nullable=True),
        sa.Column("inference_ms", sa.Float, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="PENDING"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_inspections_tyre", "inspections", ["tyre_position_id"])
    op.create_index("idx_inspections_submitted_by", "inspections", ["submitted_by"])

    op.create_table(
        "inspection_observations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("inspection_id", sa.String(36), sa.ForeignKey("inspections.id"), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("value_numeric", sa.Float, nullable=True),
        sa.Column("value_text", sa.String(500), nullable=True),
        sa.Column("value_bool", sa.Boolean, nullable=True),
        sa.Column("confidence_tier", sa.String(30), nullable=False),
        sa.Column("explanation", sa.Text, nullable=False),
        sa.Column("caveat", sa.Text, nullable=True),
        sa.Column("raw_payload", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("inspection_id", "field_name", name="uq_inspection_field"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("actor_role", sa.String(20), nullable=True),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50), nullable=True),
        sa.Column("resource_id", sa.String(36), nullable=True),
        sa.Column("detail", JSONB, nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_audit_occurred", "audit_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("inspection_observations")
    op.drop_table("inspections")
    op.drop_table("tyre_positions")
    op.drop_table("vehicles")
    op.drop_table("users")
