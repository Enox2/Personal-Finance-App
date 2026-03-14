from datetime import UTC, datetime
from pathlib import Path

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domains.csv.models import CSVFile

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_upload_csv_persists_file_and_db_row(
    client: AsyncClient,
    upload_dir: Path,
    db_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    response = await client.post(
        "/csv/upload",
        files={"file": ("transactions.csv", b"a,b\n1,2\n", "text/csv")},
    )

    assert response.status_code == 200
    assert response.json() == {
        "file_name": "transactions.csv",
        "content_type": "text/csv",
        "path": str(upload_dir / "transactions.csv"),
    }

    saved_file = upload_dir / "transactions.csv"
    assert saved_file.exists()
    assert saved_file.read_bytes() == b"a,b\n1,2\n"

    async with db_session_maker() as session:
        result = await session.execute(select(CSVFile))
        rows = result.scalars().all()

    assert len(rows) == 1
    assert rows[0].name == "transactions.csv"
    assert rows[0].path == str(saved_file)


@pytest.mark.asyncio
async def test_upload_rejects_non_csv(client: AsyncClient) -> None:
    response = await client.post(
        "/csv/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "File must be a CSV"}


@pytest.mark.asyncio
async def test_upload_sanitizes_filename(client: AsyncClient, upload_dir: Path) -> None:
    response = await client.post(
        "/csv/upload",
        files={"file": ("../escape.csv", b"a,b\n", "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["file_name"] == "escape.csv"
    assert payload["path"] == str(upload_dir / "escape.csv")
    assert (upload_dir / "escape.csv").exists()


@pytest.mark.asyncio
async def test_list_files_returns_newest_first(
    client: AsyncClient,
    db_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    older = datetime(2024, 1, 1, tzinfo=UTC)
    newer = datetime(2025, 1, 1, tzinfo=UTC)

    async with db_session_maker() as session:
        session.add_all(
            [
                CSVFile(name="older.csv", path="/tmp/older.csv", created_date=older),
                CSVFile(name="newer.csv", path="/tmp/newer.csv", created_date=newer),
            ]
        )
        await session.commit()

    response = await client.get("/csv/files")

    assert response.status_code == 200
    payload = response.json()
    assert [item["name"] for item in payload] == ["newer.csv", "older.csv"]


@pytest.mark.asyncio
async def test_delete_removes_row(
    client: AsyncClient,
    db_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    async with db_session_maker() as session:
        row = CSVFile(name="to-delete.csv", path="/tmp/to-delete.csv")
        session.add(row)
        await session.commit()
        await session.refresh(row)
        file_id = row.id

    response = await client.delete(f"/csv/delete/{file_id}")

    assert response.status_code == 200
    assert response.json() == f"Deleted {file_id}"

    async with db_session_maker() as session:
        result = await session.execute(select(CSVFile).where(CSVFile.id == file_id))
        deleted = result.scalar_one_or_none()

    assert deleted is None


@pytest.mark.asyncio
async def test_upload_duplicate_filename_returns_500(client: AsyncClient) -> None:
    first = await client.post(
        "/csv/upload",
        files={"file": ("duplicate.csv", b"a,b\n1,2\n", "text/csv")},
    )
    second = await client.post(
        "/csv/upload",
        files={"file": ("duplicate.csv", b"a,b\n3,4\n", "text/csv")},
    )

    assert first.status_code == 200
    assert second.status_code == 500

