from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.router import get_current_user
from src.csv.models import CSVFile
from src.csv.schemas import CSVFileView
from src.database import get_async_session

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

    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    file_db = CSVFile(
        name=original_name,
        path=str(file_path),
    )

    session.add(file_db)
    await session.commit()

    return {
        "file_name": original_name,
        "content_type": file.content_type,
        "path": str(file_path),
    }

@router.delete("/delete/{file_id}")
async def delete_files(file_id: int, session: AsyncSession = Depends(get_async_session)):
    file_query = delete(CSVFile).where(CSVFile.id == file_id)

    await session.execute(file_query)
    await session.commit()

    return "Deleted {}".format(file_id)


@router.get("/files")
async def list_files(
    session: AsyncSession = Depends(get_async_session),
) -> list[CSVFileView]:
    query = (
        select(CSVFile)
        # .where(CSVFile.is_processed == False)
        .order_by(CSVFile.created_date.desc())
    )

    result = await session.execute(query)

    files = result.scalars().all()

    return files
