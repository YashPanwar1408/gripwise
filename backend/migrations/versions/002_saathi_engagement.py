"""Mechanic Growth profile, learning, recognition, and follow-up schema.

Revision ID: 002_saathi_engagement
Revises: 001_initial
Create Date: 2026-10-13
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "002_saathi_engagement"
down_revision: Union[str, None] = "001_mechanic_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. mechanic_profiles
    op.create_table(
        "mechanic_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), unique=True, nullable=False),
        sa.Column("years_experience", sa.Integer, nullable=True),
        sa.Column("specialization", sa.String(100), nullable=True),
        sa.Column("workshop_address", sa.Text, nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("bio", sa.Text, nullable=True),
        sa.Column("certifications", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_mechanic_profiles_user", "mechanic_profiles", ["user_id"])

    # 2. learning_modules
    op.create_table(
        "learning_modules",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("module_code", sa.String(20), unique=True, nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("estimated_minutes", sa.Integer, nullable=False, server_default="10"),
        sa.Column("summary", sa.Text, nullable=False),
        sa.Column("content_markdown", sa.Text, nullable=False),
        sa.Column("technical_source", sa.String(255), nullable=False),
        sa.Column("quiz_questions", JSONB, nullable=False),
        sa.Column("points_reward", sa.Integer, nullable=False, server_default="50"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # 3. mechanic_module_completions
    op.create_table(
        "mechanic_module_completions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mechanic_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("module_id", sa.String(50), sa.ForeignKey("learning_modules.id"), nullable=False),
        sa.Column("score_percent", sa.Float, nullable=False),
        sa.Column("passed", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("mechanic_id", "module_id", name="uq_mechanic_module_completion"),
    )
    op.create_index("idx_module_comp_mechanic", "mechanic_module_completions", ["mechanic_id"])

    # 4. mechanic_badges
    op.create_table(
        "mechanic_badges",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("title", sa.String(100), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("criteria_description", sa.Text, nullable=False),
        sa.Column("icon_name", sa.String(50), nullable=False),
        sa.Column("points_threshold", sa.Integer, nullable=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="ACHIEVEMENT"),
    )

    # 5. mechanic_earned_badges
    op.create_table(
        "mechanic_earned_badges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mechanic_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("badge_id", sa.String(50), sa.ForeignKey("mechanic_badges.id"), nullable=False),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint("mechanic_id", "badge_id", name="uq_mechanic_badge"),
    )
    op.create_index("idx_earned_badges_mechanic", "mechanic_earned_badges", ["mechanic_id"])

    # 6. customer_referrals
    op.create_table(
        "customer_referrals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("mechanic_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("customer_name_masked", sa.String(100), nullable=False),
        sa.Column("customer_phone_masked", sa.String(50), nullable=True),
        sa.Column("vehicle_model", sa.String(100), nullable=False),
        sa.Column("tyre_need", sa.String(50), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="PENDING"),
        sa.Column("consent_confirmed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("service_record_id", sa.String(36), sa.ForeignKey("service_records.id"), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_referrals_mechanic", "customer_referrals", ["mechanic_id"])

    # 7. saathi_program_initiatives
    op.create_table(
        "saathi_program_initiatives",
        sa.Column("id", sa.String(50), primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("eligibility_level", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="PROPOSED_CONCEPT"),
        sa.Column("tool_specs", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("saathi_program_initiatives")
    op.drop_table("customer_referrals")
    op.drop_table("mechanic_earned_badges")
    op.drop_table("mechanic_badges")
    op.drop_table("mechanic_module_completions")
    op.drop_table("learning_modules")
    op.drop_table("mechanic_profiles")
