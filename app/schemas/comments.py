"""Schemas for Comments Model"""
from datetime import datetime
from typing import List, Union

from pydantic import BaseModel

from app.schemas import users


class Create(BaseModel):
    """Create first comment"""

    body: str


class AdminCreate(Create):
    """Create comment"""

    thread_id: int
    created_by: str
    last_updated_by: str


class Output(BaseModel):
    """Output comment"""

    id: int
    thread_id: int
    created_by: Union[users.CognitoUser, users.AnonymousUser]
    created_at: datetime
    last_updated_by: Union[users.CognitoUser, users.AnonymousUser]
    last_updated_at: datetime
    body: str

    class Config:
        """Config."""

        title = "Comment"
        orm_mode = True


class Update(BaseModel):
    """Update comment Model."""

    body: str


class AdminUpdate(Update):
    """Extend Update class with last_updated_by and timestamp"""

    last_updated_by: str
    last_updated_at: datetime


class Lookup(BaseModel):
    """Lookup coment."""

    id: int
