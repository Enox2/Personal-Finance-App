from collections.abc import AsyncGenerator
from pathlib import Path
import sys

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.db.session import Base, get_async_session
from src.domains.auth.dependencies import get_current_user
from src.main import app

# Ensure the CSV model is registered in Base.metadata before create_all.
from src.domains.csv.models import CSVFile  # noqa: F401
from src.domains.csv import router as csv_router_module


@pytest_asyncio.fixture
async def db_session_maker(tmp_path: Path) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    db_path = tmp_path / "test.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}")
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.connect() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        yield session_maker
    finally:
        await engine.dispose()


@pytest.fixture
def upload_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    test_upload_dir = tmp_path / "uploads"
    test_upload_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(csv_router_module, "UPLOAD_DIR", test_upload_dir)
    return test_upload_dir


@pytest_asyncio.fixture
async def client(
    db_session_maker: async_sessionmaker[AsyncSession],
    upload_dir: Path,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        async with db_session_maker() as session:
            yield session

    async def override_user() -> object:
        return {"id": 1, "email": "test@example.com"}

    app.dependency_overrides[get_async_session] = override_session
    app.dependency_overrides[get_current_user] = override_user

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client

    app.dependency_overrides.clear()


