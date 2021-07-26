from typing import Any, Dict, Optional

from pydantic import BaseModel, validator


# TODO: make action enum
class EventInput(BaseModel):
    atbd_id: str
    version: str
    action: str
    payload: Optional[Dict[str, Any]]

    @validator("action")
    def validate_requested_action(cls, v):
        if v not in [
            "request_closed_review",
            "cancel_closed_review_request",
            "deny_closed_review_request",
            "accept_closed_review_request",
            "open_review",
            "request_publication",
            "cancel_publication_request",
            "deny_publication_request",
            "accept_publication_request",
            "publish",
            "bump_minor_version",
            "update_review_status",
        ]:
            raise ValueError("Unrecognized action")
        return v
