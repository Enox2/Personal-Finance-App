from pydantic import BaseModel


class ProcessResult(BaseModel):
    processed: int
    uncategorised: int

