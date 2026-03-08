"""seed category rules non-overlapping examples

Revision ID: a2f4c1d9b101
Revises: e1b6f9a4c8d2
Create Date: 2026-03-08 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a2f4c1d9b101"
down_revision: Union[str, Sequence[str], None] = "e1b6f9a4c8d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


NON_OVERLAPPING_RULES = [
    # Distinct merchants/services, so equal priority is fine.
    {"category_name": "groceries", "pattern": r"LIDL|BIEDRONKA|NETTO|CARREFOUR|ZABKA|ROSSMANN|KAUFLAND|DM|DUZY BEN", "priority": 0},
    {"category_name": "subscriptions", "pattern": r"NETFLIX|SPOTIFY|DISNEY|APPLE|YouTubePremium|UBER *ONE", "priority": 0},
    {"category_name": "public_transport", "pattern": r"PKP|MPK", "priority": 0},
    {"category_name": "taxi", "pattern": r"BOLT|UBR* PENDING.UBER.COM", "priority": 0},
]

CATEGORY_NAMES = [
    "public_transport",
    "taxi",
]


def _load_category_ids(connection: sa.engine.Connection, names: list[str]) -> dict[str, int]:
    categories = sa.table(
        "categories",
        sa.column("id", sa.Integer()),
        sa.column("name", sa.String(length=100)),
    )

    op.bulk_insert(
        categories,
        [{"name": category_name} for category_name in CATEGORY_NAMES],
    )

    rows = connection.execute(
        sa.select(categories.c.id, categories.c.name).where(categories.c.name.in_(names))
    ).fetchall()
    category_ids = {row.name: row.id for row in rows}
    missing = sorted(set(names) - set(category_ids))
    if missing:
        raise RuntimeError(f"Missing categories for seeded rules: {missing}")
    return category_ids


def upgrade() -> None:
    connection = op.get_bind()
    category_ids = _load_category_ids(
        connection,
        sorted({rule["category_name"] for rule in NON_OVERLAPPING_RULES}),
    )

    category_rules = sa.table(
        "category_rules",
        sa.column("pattern", sa.String(length=500)),
        sa.column("category_id", sa.Integer()),
        sa.column("priority", sa.Integer()),
    )
    op.bulk_insert(
        category_rules,
        [
            {
                "pattern": rule["pattern"],
                "category_id": category_ids[rule["category_name"]],
                "priority": rule["priority"],
            }
            for rule in NON_OVERLAPPING_RULES
        ],
    )


def downgrade() -> None:
    connection = op.get_bind()
    category_ids = _load_category_ids(
        connection,
        sorted({rule["category_name"] for rule in NON_OVERLAPPING_RULES}),
    )

    category_rules = sa.table(
        "category_rules",
        sa.column("pattern", sa.String(length=500)),
        sa.column("category_id", sa.Integer()),
        sa.column("priority", sa.Integer()),
    )
    for rule in NON_OVERLAPPING_RULES:
        connection.execute(
            sa.delete(category_rules).where(
                sa.and_(
                    category_rules.c.pattern == rule["pattern"],
                    category_rules.c.category_id == category_ids[rule["category_name"]],
                    category_rules.c.priority == rule["priority"],
                )
            )
        )

