"""seed categories

Revision ID: e1b6f9a4c8d2
Revises: 9c54e7b1a2f3
Create Date: 2026-03-08 00:01:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1b6f9a4c8d2"
down_revision: Union[str, Sequence[str], None] = "9c54e7b1a2f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CATEGORY_NAMES = [
    "groceries",
    "subscriptions",
    "transport",
    "utilities",
    "housing",
    "salary",
    "other",
]


def upgrade() -> None:
    categories_table = sa.table(
        "categories",
        sa.column("name", sa.String(length=100)),
    )

    op.bulk_insert(
        categories_table,
        [{"name": category_name} for category_name in CATEGORY_NAMES],
    )


def downgrade() -> None:
    categories_table = sa.table(
        "categories",
        sa.column("name", sa.String(length=100)),
    )
    op.execute(categories_table.delete().where(categories_table.c.name.in_(CATEGORY_NAMES)))
