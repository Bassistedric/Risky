"""add validity rule to competencies

Revision ID: 3392d2234115
Revises: fae58e024bc1
Create Date: 2026-08-27 15:52:44.464592

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3392d2234115'
down_revision: Union[str, Sequence[str], None] = 'fae58e024bc1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("competencies") as batch_op:
        batch_op.create_foreign_key(
            "fk_competencies_validity_rule",
            "validity_rules",
            ["validity_rule_id"],
            ["id"],
        )
    # ### end Alembic commands ###


def downgrade() -> None:
    with op.batch_alter_table("competencies") as batch_op:
        batch_op.drop_constraint(
            "fk_competencies_validity_rule",
            type_="foreignkey",
        )
        batch_op.drop_column("validity_rule_id")
    # ### end Alembic commands ###
