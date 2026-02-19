from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import shutil
from sqlalchemy.ext.asyncio import AsyncSession
from src.csv.models import CSVFile
from src.database import get_async_session
from src.auth.router import get_current_user

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

router = APIRouter(
    prefix="/csv", tags=["csv"], dependencies=[Depends(get_current_user)]
)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
):
    if file.content_type not in ["text/csv", "application/vnd.ms-excel"]:
        raise HTTPException(status_code=400, detail="File must be a CSV")

    original_name = Path(file.filename).name

    file_path = UPLOAD_DIR / original_name

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_db = CSVFile(
        name=file.filename,
        path=str(file_path),
    )

    session.add(file_db)
    await session.commit()

    return {
        "file_name": file.filename,
        "content_type": file.content_type,
        "path": str(file_path),
    }
