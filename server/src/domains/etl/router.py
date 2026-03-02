from fastapi import APIRouter, Depends

from src.domains.auth.dependencies import get_current_user
from src.domains.etl.service import ProcessFilesApplicationService
from src.domains.etl.dependencies import get_parser_service

router = APIRouter(
    prefix="/etl", tags=["etl"], dependencies=[Depends(get_current_user)]
)


@router.post("/process/{file_id}")
async def process_file(
    file_id: int,
    application_service: ProcessFilesApplicationService = Depends(get_parser_service),
):
    rows = await application_service.start_processing_file(file_id)
    return rows.head()

