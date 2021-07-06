"""Schemas for Cognito User models"""
from pydantic import BaseModel, Field


class User(BaseModel):
    """."""

    at_hash: str
    sub: str
    cognito_groups: str = Field(..., alias="cognito:groups")
    email_verified: bool
    iss: str
    cognito_username: str = Field(..., alias="cognito:username")
    preferred_username: str
    aud: str
    token_us: str
    auth_time: int
    exp: int
    iat: int
    jti: str
    email: str
