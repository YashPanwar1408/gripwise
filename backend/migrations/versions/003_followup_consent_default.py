"""Require explicit customer agreement by default for follow-ups.

Revision ID: 003_followup_consent_default
Revises: 002_saathi_engagement
Create Date: 2026-10-13
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003_followup_consent_default"
down_revision: Union[str, None] = "002_saathi_engagement"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "customer_referrals",
        "consent_confirmed",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("false"),
    )


def downgrade() -> None:
    op.alter_column(
        "customer_referrals",
        "consent_confirmed",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.text("true"),
    )
