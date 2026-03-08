from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.domains.rules.service import RulesService


def get_rules_service(
    session: AsyncSession = Depends(get_async_session),
) -> RulesService:
    return RulesService(session=session)

