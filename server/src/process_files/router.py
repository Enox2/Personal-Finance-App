from pathlib import Path

from fastapi import APIRouter, Depends
from src.process_files.dependencies import get_parser_service
from src.process_files.application_service import ProcessFilesApplicationService
from src.auth.router import get_current_user

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

router = APIRouter(
    prefix="/etl", tags=["etl"], dependencies=[Depends(get_current_user)]
)


@router.post("/process/{file_id}")
async def process_file(
    file_id: int,
    application_service: ProcessFilesApplicationService = Depends(get_parser_service),
):
    await application_service.start_processing_file(file_id)
    return {"message": f"Processing file with ID {file_id}"}
