from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import UPLOAD_DIR
from src.db.session import get_async_session
from src.domains.auth.dependencies import get_current_user
from src.domains.csv.models import CSVFile
from src.domains.csv.schemas import CSVFileView

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
    query = select(CSVFile).order_by(CSVFile.created_date.desc())

    result = await session.execute(query)

    files = result.scalars().all()

    return files

