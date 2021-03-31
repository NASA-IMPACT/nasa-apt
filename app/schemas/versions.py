from datetime import datetime
from pydantic import BaseModel, validator
from typing import Optional, Union
import enum


class StatusEnum(enum.Enum):
    draft = "Draft"
    review = "Review"
    published = "Published"


# TODO: use status enum above
class OutputBase(BaseModel):
    status: str
    published_by: Optional[str]
    published_at: Optional[datetime]
    sections_completed: Optional[dict]
    created_by: str
    created_at: datetime
    last_updated_by: str
    last_updated_at: datetime

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
    sections_completed: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]
    citation: Optional[dict]


class Create(BaseModel):
    atbd_id: str


class Lookup(BaseModel):
    atbd_id: str
    major: int


class Update(BaseModel):
    minor: Optional[int]
    document: Optional[dict]
    sections_completed: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]
    citation: Optional[dict]
    status: Optional[str]


class JSONFieldUpdate(BaseModel):
    key: str
    value: Union[str, dict]

