from fastapi import APIRouter, Depends, HTTPException, status

from src.domains.auth.dependencies import get_current_user
from src.domains.etl.dependencies import get_etl_service
from src.domains.etl.schemas import (
    CategoryRuleCreate,
    CategoryRuleRead,
    CategoryRuleUpdate,
    ProcessResult,
    RecategoriseResult,
    TransactionRead,
)
from src.domains.etl.service import ProcessFilesApplicationService

router = APIRouter(
    prefix="/etl", tags=["etl"], dependencies=[Depends(get_current_user)]
)


@router.post("/process/{file_id}", response_model=ProcessResult)
async def process_file(
    file_id: int,
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    try:
        return await application_service.start_processing_file(file_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")


@router.get("/rules", response_model=list[CategoryRuleRead])
async def list_rules(
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    return await application_service.list_rules()


@router.post("/rules", response_model=CategoryRuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: CategoryRuleCreate,
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    return await application_service.create_rule(rule)


@router.put("/rules/{rule_id}", response_model=CategoryRuleRead)
async def update_rule(
    rule_id: int,
    rule: CategoryRuleUpdate,
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    updated = await application_service.update_rule(rule_id, rule)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return updated


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    deleted = await application_service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return None


@router.get("/transactions/uncategorised", response_model=list[TransactionRead])
async def list_uncategorised(
    limit: int = 100,
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    return await application_service.list_uncategorised(limit=limit)


@router.post("/transactions/recategorise", response_model=RecategoriseResult)
async def recategorise_transactions(
    application_service: ProcessFilesApplicationService = Depends(get_etl_service),
):
    updated = await application_service.recategorise_transactions()
    return {"updated": updated}
