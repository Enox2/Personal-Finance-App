from fastapi import APIRouter, Depends, HTTPException, status

from src.domains.auth.dependencies import get_current_user
from src.domains.categories.dependencies import get_category_service
from src.domains.categories.exceptions import CategoryExistsError, CategoryNotExistsError
from src.domains.categories.schemas import CategoryCreate, CategoryRead, CategoryUpdate
from src.domains.categories.service import CategoryService


router = APIRouter(
    prefix="/categories", tags=["categories"], dependencies=[Depends(get_current_user)]
)


@router.get("/list", response_model=list[CategoryRead])
async def list_categories(
    service: CategoryService = Depends(get_category_service),
):
    return await service.list_categories()


@router.post("/create", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.create_category(category)
    except CategoryExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: int,
    category: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    try:
        return await service.update_category(category_id, category)
    except CategoryNotExistsError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service),
):
    deleted = await service.delete_category(category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    return None
