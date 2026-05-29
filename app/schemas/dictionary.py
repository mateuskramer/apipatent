from datetime import datetime

from pydantic import BaseModel, Field


class DictionaryItem(BaseModel):
    id: int
    term: str
    class_: str | None = Field(None, alias="class")
    status: str | None = None
    created_at: datetime | None = None

    class Config:
        validate_by_name = True
