import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.domains.categories.models import Category

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_list_categories_returns_empty_list_when_none_exist(client: AsyncClient) -> None:
    response = await client.get("/categories/list")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_create_category_persists_and_returns_category(
    client: AsyncClient,
    db_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    response = await client.post("/categories/create", json={"name": "Food"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Food"
    assert payload["id"] > 0
    assert "created_date" in payload

    async with db_session_maker() as session:
        result = await session.execute(select(Category).where(Category.name == "Food"))
        row = result.scalar_one_or_none()

    assert row is not None


@pytest.mark.asyncio
async def test_create_category_returns_409_when_name_exists(client: AsyncClient) -> None:
    first = await client.post("/categories/create", json={"name": "Transport"})
    second = await client.post("/categories/create", json={"name": "Transport"})

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json() == {"detail": "Category with name Transport already exists."}


@pytest.mark.asyncio
async def test_update_category_changes_name(
    client: AsyncClient,
    db_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    async with db_session_maker() as session:
        category = Category(name="Old")
        session.add(category)
        await session.commit()
        await session.refresh(category)
        category_id = category.id

    response = await client.put(f"/categories/{category_id}", json={"name": "New"})

    assert response.status_code == 200
    assert response.json()["name"] == "New"

    async with db_session_maker() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        refreshed = result.scalar_one_or_none()

    assert refreshed is not None
    assert refreshed.name == "New"


@pytest.mark.asyncio
async def test_update_category_returns_404_for_missing_category(client: AsyncClient) -> None:
    response = await client.put("/categories/9999", json={"name": "DoesNotMatter"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Category with id 9999 does not exist."}


@pytest.mark.asyncio
async def test_delete_category_removes_row(
    client: AsyncClient,
    db_session_maker: async_sessionmaker[AsyncSession],
) -> None:
    async with db_session_maker() as session:
        category = Category(name="ToDelete")
        session.add(category)
        await session.commit()
        await session.refresh(category)
        category_id = category.id

    response = await client.delete(f"/categories/{category_id}")

    assert response.status_code == 204
    assert response.content == b""

    async with db_session_maker() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        deleted = result.scalar_one_or_none()

    assert deleted is None


@pytest.mark.asyncio
async def test_delete_category_returns_404_for_missing_category(client: AsyncClient) -> None:
    response = await client.delete("/categories/4040")

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}

