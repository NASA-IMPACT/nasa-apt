"""Schemas for the events objects"""
from typing import Any, Dict, Optional

from pydantic import BaseModel, validator

from app.api.v2 import events


# TODO: make action enum
class EventInput(BaseModel):
    """Schemas for the object inputted to an event"""

    atbd_id: str
    version: str
    action: str
    payload: Optional[Dict[str, Any]]

    @validator("action")
    def validate_requested_action(cls, v):
        """Ensure requested action is one of the
        allowed actions. TODO: make this an enum.
        """
        if v not in events.ACTIONS.keys():
            raise ValueError("Unrecognized action")
        return v
