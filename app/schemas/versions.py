from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional
import enum


class StatusEnum(enum.Enum):
    draft = "Draft"
    review = "Review"
    published = "Published"


# TODO: use enum above
class OutputBase(BaseModel):
    status: str
    published_by: Optional[str]
    published_at: Optional[datetime]
    created_by: str
    created_at: datetime

    class Config:
        title = "Atbd"
        orm_mode = True


class SummaryOutput(OutputBase):
    major: int
    minor: int
    version: Optional[str]

    @validator("version", always=True)
    def generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"


class FullOutput(SummaryOutput):
    document: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]


class Create(BaseModel):
    atbd_id: str


class Lookup(BaseModel):
    atbd_id: str
    major: int


class Update(BaseModel):
    minor: Optional[int]
    document: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]
    status: Optional[str]

