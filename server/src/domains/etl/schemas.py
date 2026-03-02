from datetime import date, datetime
from decimal import Decimal

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


class TransactionRead(BaseModel):
    id: int
    csv_file_id: int
    transaction_date: date
    value_date: date
    transaction_type: str
    amount: Decimal
    currency: str
    merchant: str
    category: str | None
    transaction_description: str

    model_config = {"from_attributes": True}


class ProcessResult(BaseModel):
    processed: int
    uncategorised: int


class RecategoriseResult(BaseModel):
    updated: int

