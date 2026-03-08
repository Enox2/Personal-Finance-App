from datetime import date
from decimal import Decimal

from pydantic import BaseModel


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

