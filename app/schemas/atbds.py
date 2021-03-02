from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.schemas import atbd_versions


class CreateInput(BaseModel):
    title: str
    alias: Optional[str]

    class Config:
        title = "CreateAtbdInput"
        orm_mode = True


class OutputBase(BaseModel):
    created_at: datetime
    created_by: str
    title: str
    alias: str

    class Config:
        title = "Atbd"
        orm_mode = True


class SummaryOutput(OutputBase):
    versions: List[atbd_versions.SummaryOutput]


class FullOutput(OutputBase):
    versions: List[atbd_versions.FullOutput]


class Lookup(BaseModel):
    id: Optional[int]
    abtd_alias: Optional[str]


class Create(BaseModel):
    atbd_alias: str
    title: str
    created_by: str

