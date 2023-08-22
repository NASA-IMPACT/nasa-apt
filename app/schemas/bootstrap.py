"""Schema for frontend bootstrap data."""

from pydantic import BaseModel


class BootstrapResponse(BaseModel):
    """Bootstrap Response."""

    metadata: dict
    feature_flags: dict
