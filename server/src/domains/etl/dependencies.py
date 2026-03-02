from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_async_session
from src.domains.etl.service import ProcessFilesApplicationService


def get_etl_service(
    session: AsyncSession = Depends(get_async_session),
) -> ProcessFilesApplicationService:
    return ProcessFilesApplicationService(session=session)
