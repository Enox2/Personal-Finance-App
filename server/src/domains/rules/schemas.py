from datetime import datetime

from pydantic import BaseModel


class CategoryRuleBase(BaseModel):
    pattern: str
    category: str
    priority: int = 0


class CategoryRuleCreate(CategoryRuleBase):
    pass


class CategoryRuleUpdate(BaseModel):
    pattern: str | None = None
    category: str | None = None
    priority: int | None = None


class CategoryRuleRead(CategoryRuleBase):
    id: int
    created_date: datetime

    model_config = {"from_attributes": True}

