"""add event code reference translations

Revision ID: b98e0d7342e3
Revises: f275e3356aea
Create Date: 2026-09-22 17:12:20.088481

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b98e0d7342e3'
down_revision: Union[str, Sequence[str], None] = 'f275e3356aea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table(
        'event_code_references',
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                'label_nl',
                sa.String(length=1000),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                'label_en',
                sa.String(length=1000),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                'label_pl',
                sa.String(length=1000),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table(
        'event_code_references',
        schema=None,
    ) as batch_op:
        batch_op.drop_column('label_pl')
        batch_op.drop_column('label_en')
        batch_op.drop_column('label_nl')

    # ### end Alembic commands ###
