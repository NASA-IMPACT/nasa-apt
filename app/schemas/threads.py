"""Schemas for Threads Model"""
from enum import Enum
from typing import List

from pydantic import BaseModel

from app.schemas import comments


class StatusEnum(str, Enum):
    """Enum for all possible thread statuses"""

    OPEN = "Open"
    CLOSED = "Closed"


class Create(BaseModel):
    """Create thread"""

    comment: comments.FirstCreate
    atbd_id: int
    major: int
    section: str


class Output(BaseModel):
    """Output thread"""

    id: int
    atbd_id: int
    major: int
    status: StatusEnum
    section: str
    comments: List[comments.Output]


class Update(BaseModel):
    """Update Thread Model."""

    id: int
    atbd_id: int
    major: int
    status: StatusEnum
    section: str


class Lookup(BaseModel):
    """Lookup thread."""

    id: int
