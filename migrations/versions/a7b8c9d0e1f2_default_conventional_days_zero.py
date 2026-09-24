"""default conventional days to zero

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-09-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table(
        "safety_permanent_disabilities",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "conventional_days",
            existing_type=sa.Float(),
            nullable=False,
            server_default="0",
        )


def downgrade() -> None:
    with op.batch_alter_table(
        "safety_permanent_disabilities",
        schema=None,
    ) as batch_op:
        batch_op.alter_column(
            "conventional_days",
            existing_type=sa.Float(),
            nullable=True,
            server_default=None,
        )