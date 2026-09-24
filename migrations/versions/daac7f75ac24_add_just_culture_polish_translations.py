"""add just culture polish translations

Revision ID: daac7f75ac24
Revises: b98e0d7342e3
Create Date: 2026-09-24 10:00:21.661837

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'daac7f75ac24'
down_revision: Union[str, Sequence[str], None] = 'b98e0d7342e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table(
        'just_culture_nodes',
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                'text_pl',
                sa.String(length=2000),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                'conclusion_label_pl',
                sa.String(length=500),
                nullable=True,
            )
        )

        batch_op.add_column(
            sa.Column(
                'recommendation_label_pl',
                sa.String(length=500),
                nullable=True,
            )
        )

    with op.batch_alter_table(
        'just_culture_transitions',
        schema=None,
    ) as batch_op:
        batch_op.add_column(
            sa.Column(
                'answer_label_pl',
                sa.String(length=250),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table(
        'just_culture_transitions',
        schema=None,
    ) as batch_op:
        batch_op.drop_column(
            'answer_label_pl'
        )

    with op.batch_alter_table(
        'just_culture_nodes',
        schema=None,
    ) as batch_op:
        batch_op.drop_column(
            'recommendation_label_pl'
        )
        batch_op.drop_column(
            'conclusion_label_pl'
        )
        batch_op.drop_column(
            'text_pl'
        )