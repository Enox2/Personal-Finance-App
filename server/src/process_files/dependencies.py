from fastapi import Depends

from server.src.database import get_async_session
from server.src.process_files.application_service import ProcessFilesApplicationService
from sqlalchemy.ext.asyncio import AsyncSession


def get_parser_service(
    session: AsyncSession = Depends(get_async_session),
) -> ProcessFilesApplicationService:
    return ProcessFilesApplicationService(session=session)
