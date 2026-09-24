"""add heepo factor translations

Revision ID: 6a40f409c96c
Revises: 5380c8f3706d
Create Date: 2026-09-17 10:37:54.068675

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6a40f409c96c"
down_revision: Union[str, Sequence[str], None] = "5380c8f3706d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ============================================================
# UPGRADE — TRADUCTIONS DU RÉFÉRENTIEL HEEPO
# ============================================================

def upgrade() -> None:
    with op.batch_alter_table("heepo_factors", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("label_nl", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("label_en", sa.String(), nullable=True)
        )


# ============================================================
# DOWNGRADE — RETOUR AU RÉFÉRENTIEL FRANÇAIS
# ============================================================

def downgrade() -> None:
    with op.batch_alter_table("heepo_factors", schema=None) as batch_op:
        batch_op.drop_column("label_en")
        batch_op.drop_column("label_nl")