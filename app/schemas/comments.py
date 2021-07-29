"""Schemas for Comments Model"""
from pydantic import BaseModel


class FirstCreate(BaseModel):
    """Create first comment"""

    body: str


class Create(FirstCreate):
    """Create comment"""

    thread_id: int


class Output(BaseModel):
    """Output comment"""

    id: int
    thread_id: int
    created_by: str
    created_at: str
    last_updated_by: str
    last_updated_at: str
    body: str


class Update(BaseModel):
    """Update comment Model."""

    body: str


class Lookup(BaseModel):
    """Lookup coment."""

    id: int
