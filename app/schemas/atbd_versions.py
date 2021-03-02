from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class SummaryOutput(BaseModel):
    alias: str
    status: str
    published_by: Optional[str]
    published_at: Optional[datetime]

    class Config:
        title = "Asset"
        orm_mode = True


class FullOutput(SummaryOutput):
    document: dict


class Create(BaseModel):
    atbd_id: Optional[str]
    atbd_alias: Optional[str]
    # TODO: add validator that one of atbd_id and atbd_alias are set


class Lookup(BaseModel):
    atbd_id: str
    atbd_alias: str
