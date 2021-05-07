from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, List
from app.schemas import versions_contacts
from app.schemas import versions


class PublishInput(BaseModel):
    changelog: Optional[str]


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
    created_by: str
    created_at: datetime
    last_updated_by: str
    last_updated_at: datetime
    title: str
    alias: Optional[str]

    class Config:
        title = "Atbd"
        orm_mode = True


class SummaryOutput(OutputBase):
    versions: List[versions.AtbdVersionSummaryOutput]

    @validator("versions")
    def enforce_version_ordering(cls, versions):
        return sorted([v.dict() for v in versions], key=lambda d: d["created_at"])


class FullOutput(OutputBase):
    versions: List[versions.FullOutput]

    @validator("versions")
    def enforce_version_ordering(cls, versions):
        return sorted([v.dict() for v in versions], key=lambda d: d["created_at"])


class Lookup(BaseModel):
    id: Optional[int]
    alias: Optional[str]
