from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domains.rules.models import CategoryRule
from src.domains.rules.schemas import CategoryRuleCreate, CategoryRuleUpdate


class RulesService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_rules(self) -> list[CategoryRule]:
        result = await self.session.execute(
            select(CategoryRule).order_by(CategoryRule.priority.desc(), CategoryRule.id)
        )
        return list(result.scalars().all())

    async def create_rule(self, rule: CategoryRuleCreate) -> CategoryRule:
        rule_model = CategoryRule(
            pattern=rule.pattern,
            category=rule.category,
            priority=rule.priority,
        )
        self.session.add(rule_model)
        await self.session.commit()
        await self.session.refresh(rule_model)
        return rule_model

    async def update_rule(
        self, rule_id: int, rule_update: CategoryRuleUpdate
    ) -> CategoryRule | None:
        result = await self.session.execute(
            select(CategoryRule).where(CategoryRule.id == rule_id)
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            return None

        update_data = rule_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)

        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: int) -> bool:
        result = await self.session.execute(
            select(CategoryRule).where(CategoryRule.id == rule_id)
        )
        rule = result.scalar_one_or_none()
        if rule is None:
            return False

        await self.session.delete(rule)
        await self.session.commit()
        return True
