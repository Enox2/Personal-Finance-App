from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.domains.categories.service import CategoryService
from src.domains.rules.service import RulesService


def get_category_service(
    session: AsyncSession = Depends(get_async_session),
) -> CategoryService:
    return CategoryService(session=session)

