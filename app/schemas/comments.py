"""Schemas for Comments Model"""
from pydantic import BaseModel


class Create(BaseModel):
    """Create comment"""

    thread_id: int
    comment: str


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

    id: int
    thread_id: int
    created_by: str
    created_at: str
    last_updated_by: str
    last_updated_at: str
    body: str


class Lookup(BaseModel):
    """Lookup coment."""

    id: int
