from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.domains.processing.service import ProcessingService
from src.domains.rules.dependencies import get_rules_service
from src.domains.rules.service import RulesService


def get_processing_service(
    session: AsyncSession = Depends(get_async_session),
    rules_service: RulesService = Depends(get_rules_service),
) -> ProcessingService:
    return ProcessingService(session=session, rules_service=rules_service)

