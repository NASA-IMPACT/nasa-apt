"""Schemas for Threads Model"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, validator

from app.api.utils import get_major_from_version_string
from app.schemas import comments, users


class StatusEnum(str, Enum):
    """Enum for all possible thread statuses"""

    OPEN = "OPEN"
    CLOSED = "CLOSED"


class AdminCreate(BaseModel):
    """Backend create thread"""

    atbd_id: int
    major: int
    section: str
    created_by: str
    last_updated_by: str


class Create(BaseModel):
    """Create thread"""

    comment: comments.Create
    atbd_id: int
    version: str
    section: str
    major: Optional[int]

    @validator("major", always=True)
    def _extract_major(cls, v, values) -> int:
        major, _ = get_major_from_version_string(values["version"])
        return major


class Output(BaseModel):
    """Output thread"""

    id: int
    atbd_id: int
    major: int
    status: StatusEnum
    section: str
    comments: List[comments.Output]
    created_by: Union[users.CognitoUser, users.AnonymousUser]
    created_at: datetime
    last_updated_by: Union[users.CognitoUser, users.AnonymousUser]
    last_updated_at: datetime
    comment_count: Optional[int]

    class Config:
        """Config."""

        title = "Thread"
        orm_mode = True


class Update(BaseModel):
    """Update Thread Model."""

    status: StatusEnum


class AdminUpdate(Update):
    """Admin update model"""

    last_updated_by: str
    last_updated_at: datetime


class Lookup(BaseModel):
    """Lookup thread."""

    id: int


class StatusCounts(BaseModel):
    """Object for count of open and closed threads"""

    open: int
    closed: int


class Stats(BaseModel):
    """Object for thread counts object"""

    atbd_id: int
    status: StatusCounts
    total: int
    major: int
    minor: int
    version: Optional[str]

    @validator("version", always=True, pre=True)
    def _generate_semver(cls, v, values) -> str:

        return f"v{values['major']}.{values['minor']}"
