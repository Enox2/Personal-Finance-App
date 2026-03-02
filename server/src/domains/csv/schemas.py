from datetime import datetime

from pydantic import BaseModel


class CSVFileView(BaseModel):
    id: int
    name: str
    is_processed: bool
    created_date: datetime

    model_config = {"from_attributes": True}

