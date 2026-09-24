"""add circumstantial report data

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-09-24
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_circumstantial_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False, unique=True),
        sa.Column("victim_address", sa.String(500)), sa.Column("victim_birth_date", sa.String(20)),
        sa.Column("victim_company_seniority", sa.String(100)), sa.Column("victim_job_seniority", sa.String(100)),
        sa.Column("employer_name", sa.String(250)), sa.Column("employer_address", sa.String(500)),
        sa.Column("insurer_name", sa.String(250)), sa.Column("insurance_policy_number", sa.String(100)),
        sa.Column("prevention_advisor", sa.String(250)), sa.Column("sipp_manager", sa.String(250)),
        sa.Column("sepp_name", sa.String(250)), sa.Column("sepp_contact", sa.String(500)),
        sa.Column("primary_material_factors", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("primary_collective_protection", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("primary_personal_protection", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("primary_environmental_factors", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("primary_other", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("primary_details", sa.Text()),
        sa.Column("secondary_organization", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("secondary_communication", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("secondary_human_factors", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("secondary_other", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("secondary_details", sa.Text()),
        sa.Column("tertiary_third_party_material", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tertiary_incorrect_advice", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tertiary_third_party_organization", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tertiary_other", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("tertiary_details", sa.Text()),
        sa.Column("report_contributors", sa.Text()), sa.Column("report_recipients", sa.Text()),
        sa.Column("committee_opinion", sa.Text()), sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_event_circumstantial_reports_event_id", "event_circumstantial_reports", ["event_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_event_circumstantial_reports_event_id", table_name="event_circumstantial_reports")
    op.drop_table("event_circumstantial_reports")
