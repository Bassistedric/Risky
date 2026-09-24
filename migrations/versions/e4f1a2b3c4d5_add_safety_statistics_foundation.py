"""add safety statistics foundation

Revision ID: e4f1a2b3c4d5
Revises: daac7f75ac24
Create Date: 2026-09-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e4f1a2b3c4d5"
down_revision: Union[str, Sequence[str], None] = "daac7f75ac24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ========================================================
    # RÉFÉRENTIEL MÉTIERS
    # ========================================================

    op.create_table(
        "trade_references",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_trade_references_code",
        "trade_references",
        ["code"],
        unique=True,
    )

    # ========================================================
    # ORGANISATION ↔ MÉTIER
    # ========================================================

    op.create_table(
        "organization_trades",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "trade_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.ForeignKeyConstraint(
            ["trade_id"],
            ["trade_references.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "trade_id",
            name="uq_organization_trade",
        ),
    )

    op.create_index(
        "ix_organization_trades_organization_id",
        "organization_trades",
        ["organization_id"],
    )

    op.create_index(
        "ix_organization_trades_trade_id",
        "organization_trades",
        ["trade_id"],
    )

    # ========================================================
    # HEURES PRESTÉES
    # ========================================================

    op.create_table(
        "safety_work_hours",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("month", sa.Integer(), nullable=False),
        sa.Column(
            "worked_hours",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "source",
            sa.String(250),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "year",
            "month",
            name="uq_safety_work_hours_period",
        ),
    )

    op.create_index(
        "ix_safety_work_hours_organization_id",
        "safety_work_hours",
        ["organization_id"],
    )

    op.create_index(
        "ix_safety_work_hours_year",
        "safety_work_hours",
        ["year"],
    )

    # ========================================================
    # OBJECTIFS CFE
    # ========================================================

    op.create_table(
        "safety_targets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column(
            "tf_target",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "tg_target",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "source",
            sa.String(250),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "year",
            name="uq_safety_target_organization_year",
        ),
    )

    op.create_index(
        "ix_safety_targets_organization_id",
        "safety_targets",
        ["organization_id"],
    )

    op.create_index(
        "ix_safety_targets_year",
        "safety_targets",
        ["year"],
    )


def downgrade() -> None:

    op.drop_index(
        "ix_safety_targets_year",
        table_name="safety_targets",
    )
    op.drop_index(
        "ix_safety_targets_organization_id",
        table_name="safety_targets",
    )
    op.drop_table("safety_targets")

    op.drop_index(
        "ix_safety_work_hours_year",
        table_name="safety_work_hours",
    )
    op.drop_index(
        "ix_safety_work_hours_organization_id",
        table_name="safety_work_hours",
    )
    op.drop_table("safety_work_hours")

    op.drop_index(
        "ix_organization_trades_trade_id",
        table_name="organization_trades",
    )
    op.drop_index(
        "ix_organization_trades_organization_id",
        table_name="organization_trades",
    )
    op.drop_table("organization_trades")

    op.drop_index(
        "ix_trade_references_code",
        table_name="trade_references",
    )
    op.drop_table("trade_references")