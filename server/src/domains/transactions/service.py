from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.transactions.models import Transaction


class TransactionsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_uncategorised(self, limit: int = 100) -> list[Transaction]:
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.category.is_(None))
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

