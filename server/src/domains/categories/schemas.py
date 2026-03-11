from datetime import datetime

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryUpdate(BaseModel):
    name: str


class CategoryRead(BaseModel):
    id: int
    name: str
    created_date: datetime

    model_config = {"from_attributes": True}
