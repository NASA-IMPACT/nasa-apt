"""Schemas for ATBDS models"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator

from app.schemas import versions


class PublishInput(BaseModel):
    """Input for publishing an ATBD"""

    changelog: Optional[str]


class Update(BaseModel):
    """Atbd Update"""

    alias: Optional[str]
    title: Optional[str]


class Create(BaseModel):
    """Atbd Create"""

    title: str
    alias: Optional[str]

    class Config:
        """Config."""

        title = "CreateAtbdInput"
        orm_mode = True


class OutputBase(BaseModel):
    """Base Model for ATBD Output"""

    id: int
    created_by: str
    created_at: datetime
    last_updated_by: str
    last_updated_at: datetime
    title: str
    alias: Optional[str]

    class Config:
        """Config."""

        title = "Atbd"
        orm_mode = True


class SummaryOutput(OutputBase):
    """Model for ATBD Output that doesn't NOT include each versions' document field
    (To avoid execssively large payloads)"""

    versions: List[versions.AtbdVersionSummaryOutput]

    @validator("versions")
    def _enforce_version_ordering(cls, versions):
        return sorted([v.dict() for v in versions], key=lambda d: d["created_at"])


class FullOutput(OutputBase):
    """Model for ATBD Output including each versions's document field"""

    versions: List[versions.FullOutput]

    @validator("versions")
    def _enforce_version_ordering(cls, versions):
        return sorted([v.dict() for v in versions], key=lambda d: d["created_at"])


class Lookup(BaseModel):
    """Lookup model for ATBDs"""

    id: Optional[int]
    alias: Optional[str]
