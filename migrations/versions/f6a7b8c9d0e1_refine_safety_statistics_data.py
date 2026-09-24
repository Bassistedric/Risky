"""refine safety statistics data

Revision ID: f6a7b8c9d0e1
Revises: e4f1a2b3c4d5
Create Date: 2026-09-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a7b8c9d0e1"
down_revision: Union[str, Sequence[str], None] = "e4f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ========================================================
    # HEURES — POPULATION + MÉTIER
    # ========================================================

    with op.batch_alter_table(
        "safety_work_hours",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "uq_safety_work_hours_period",
            type_="unique",
        )

        batch_op.add_column(
            sa.Column(
                "workforce_category",
                sa.String(length=20),
                nullable=False,
                server_default="WORKER",
            )
        )

        batch_op.add_column(
            sa.Column(
                "trade_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                "dimension_key",
                sa.String(length=100),
                nullable=False,
                server_default="LEGACY",
            )
        )

        batch_op.create_foreign_key(
            "fk_safety_work_hours_trade_id",
            "trade_references",
            ["trade_id"],
            ["id"],
        )

        batch_op.create_unique_constraint(
            "uq_safety_work_hours_period_dimension",
            [
                "organization_id",
                "year",
                "month",
                "dimension_key",
            ],
        )

    op.create_index(
        "ix_safety_work_hours_trade_id",
        "safety_work_hours",
        ["trade_id"],
    )

    # ========================================================
    # INVALIDITÉS PERMANENTES
    # ========================================================

    op.create_table(
        "safety_permanent_disabilities",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "year",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "disability_percent",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "conventional_days",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "source",
            sa.String(length=250),
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
    )

    op.create_index(
        "ix_safety_permanent_disabilities_organization_id",
        "safety_permanent_disabilities",
        ["organization_id"],
    )

    op.create_index(
        "ix_safety_permanent_disabilities_year",
        "safety_permanent_disabilities",
        ["year"],
    )


def downgrade() -> None:

    op.drop_index(
        "ix_safety_permanent_disabilities_year",
        table_name="safety_permanent_disabilities",
    )

    op.drop_index(
        "ix_safety_permanent_disabilities_organization_id",
        table_name="safety_permanent_disabilities",
    )

    op.drop_table(
        "safety_permanent_disabilities"
    )

    op.drop_index(
        "ix_safety_work_hours_trade_id",
        table_name="safety_work_hours",
    )

    with op.batch_alter_table(
        "safety_work_hours",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "uq_safety_work_hours_period_dimension",
            type_="unique",
        )

        batch_op.drop_constraint(
            "fk_safety_work_hours_trade_id",
            type_="foreignkey",
        )

        batch_op.drop_column(
            "dimension_key"
        )

        batch_op.drop_column(
            "trade_id"
        )

        batch_op.drop_column(
            "workforce_category"
        )

        batch_op.create_unique_constraint(
            "uq_safety_work_hours_period",
            [
                "organization_id",
                "year",
                "month",
            ],
        )