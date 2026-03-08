from sqlalchemy import select, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.transactions.models import Transaction


class TransactionsService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_uncategorised(self, limit: int = 100) -> list[Transaction]:
        result = await self.session.execute(
            select(Transaction)
            .where(Transaction.category_id.is_(None))
            .order_by(Transaction.transaction_date.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete_all_for_file(self, csv_file_id: int) -> bool:
        result = await self.session.execute(
            select(Transaction).where(Transaction.csv_file_id == csv_file_id)
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            return False

        await self.session.delete(rule)
        await self.session.commit()
        return True