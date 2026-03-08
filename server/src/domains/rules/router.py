from fastapi import APIRouter, Depends, HTTPException, status

from src.domains.auth.dependencies import get_current_user
from src.domains.rules.dependencies import get_rules_service
from src.domains.rules.schemas import CategoryRuleCreate, CategoryRuleRead, CategoryRuleUpdate
from src.domains.rules.service import RulesService

router = APIRouter(
    prefix="/rules", tags=["rules"], dependencies=[Depends(get_current_user)]
)


@router.get("", response_model=list[CategoryRuleRead])
async def list_rules(
    service: RulesService = Depends(get_rules_service),
):
    return await service.list_rules()


@router.post("", response_model=CategoryRuleRead, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: CategoryRuleCreate,
    service: RulesService = Depends(get_rules_service),
):
    return await service.create_rule(rule)


@router.put("/{rule_id}", response_model=CategoryRuleRead)
async def update_rule(
    rule_id: int,
    rule: CategoryRuleUpdate,
    service: RulesService = Depends(get_rules_service),
):
    updated = await service.update_rule(rule_id, rule)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return updated


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: int,
    service: RulesService = Depends(get_rules_service),
):
    deleted = await service.delete_rule(rule_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    return None

