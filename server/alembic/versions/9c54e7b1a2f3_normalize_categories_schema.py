"""normalize categories schema

Revision ID: 9c54e7b1a2f3
Revises: 30bc480cddc2
Create Date: 2026-03-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c54e7b1a2f3"
down_revision: Union[str, Sequence[str], None] = "30bc480cddc2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_date",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    with op.batch_alter_table("category_rules") as batch_op:  # type: ignore[attr-defined]
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=False))
        batch_op.create_index("ix_category_rules_category_id", ["category_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_category_rules_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
        )
        batch_op.drop_column("category")

    with op.batch_alter_table("transactions") as batch_op:  # type: ignore[attr-defined]
        batch_op.drop_index("ix_transactions_category")
        batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
        batch_op.create_index("ix_transactions_category_id", ["category_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_transactions_category_id_categories",
            "categories",
            ["category_id"],
            ["id"],
        )
        batch_op.drop_column("category")


def downgrade() -> None:
    with op.batch_alter_table("transactions") as batch_op:  # type: ignore[attr-defined]
        batch_op.add_column(sa.Column("category", sa.String(length=100), nullable=True))
        batch_op.drop_constraint("fk_transactions_category_id_categories", type_="foreignkey")
        batch_op.drop_index("ix_transactions_category_id")
        batch_op.create_index("ix_transactions_category", ["category"], unique=False)
        batch_op.drop_column("category_id")

    with op.batch_alter_table("category_rules") as batch_op:  # type: ignore[attr-defined]
        batch_op.add_column(sa.Column("category", sa.String(length=100), nullable=False))
        batch_op.drop_constraint("fk_category_rules_category_id_categories", type_="foreignkey")
        batch_op.drop_index("ix_category_rules_category_id")
        batch_op.drop_column("category_id")

    op.drop_table("categories")

