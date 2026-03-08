from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.domains.transactions.service import TransactionsService


def get_transactions_service(
    session: AsyncSession = Depends(get_async_session),
) -> TransactionsService:
    return TransactionsService(session=session)

