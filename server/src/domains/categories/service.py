from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.categories.exceptions import CategoryExistsError, CategoryNotExistsError
from src.domains.categories.models import Category
from src.domains.categories.schemas import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_category(self, category: CategoryCreate) -> Category:
        if await self.category_exists_by_name(category.name):
            raise CategoryExistsError(f"Category with name {category.name} already exists.")

        new_category = Category(name=category.name)

        self.session.add(new_category)
        await self.session.commit()
        await self.session.refresh(new_category)

        return new_category

    async def update_category(self, category_id: int, category: CategoryUpdate) -> Category:
        if not await self.category_exists_by_id(category_id):
            raise CategoryNotExistsError(f"Category with id {category_id} does not exist.")

        result = await self.session.execute(select(Category).where(Category.id == category_id))

        db_category = result.scalar()
        db_category.name = category.name

        await self.session.commit()
        await self.session.refresh(db_category)

        return db_category

    async def delete_category(self, category_id: int) -> bool:
        result = await self.session.execute(select(Category).where(Category.id == category_id))
        db_category = result.scalar_one_or_none()

        if db_category is None:
            return False

        await self.session.delete(db_category)
        await self.session.commit()

        return True

    async def list_categories(self) -> list[Any]:
        result = await self.session.execute(select(Category))

        return list(result.scalars().all())

    async def category_exists_by_name(self, category_name: str) -> bool:
        result = await self.session.execute(
            select(Category.name).where(Category.name == category_name)
        )

        category_exists = result.scalar_one_or_none()

        return category_exists is not None

    async def category_exists_by_id(self, category_id: int) -> bool:
        result = await self.session.execute(select(Category.name).where(Category.id == category_id))

        category_exists = result.scalar_one_or_none()

        return category_exists is not None