from fastapi import APIRouter, Depends, HTTPException, status

from src.domains.auth.dependencies import get_current_user
from src.domains.processing.dependencies import get_processing_service
from src.domains.processing.schemas import ProcessResult
from src.domains.processing.service import ProcessingService

router = APIRouter(
    prefix="/processing", tags=["processing"], dependencies=[Depends(get_current_user)]
)


@router.post("/process/{file_id}", response_model=ProcessResult)
async def process_file(
    file_id: int,
    service: ProcessingService = Depends(get_processing_service),
):
    try:
        return await service.start_processing_file(file_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

