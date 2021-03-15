from datetime import datetime
from pydantic import BaseModel, root_validator
from typing import Optional, List
from app.schemas import versions


class Update(BaseModel):
    alias: Optional[str]
    title: Optional[str]


class Create(BaseModel):
    title: str
    alias: Optional[str]

    class Config:
        title = "CreateAtbdInput"
        orm_mode = True


class OutputBase(BaseModel):
    id: int
    created_at: datetime
    created_by: str
    title: str
    alias: Optional[str]

    class Config:
        title = "Atbd"
        orm_mode = True


class SummaryOutput(OutputBase):
    versions: List[versions.SummaryOutput]


class FullOutput(OutputBase):
    versions: List[versions.FullOutput]


class Lookup(BaseModel):
    id: Optional[int]
    alias: Optional[str]
