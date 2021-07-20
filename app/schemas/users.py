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


class CognitoUser(BaseModel):
    """User contributing to an ATBD Version, as returned by Cognito"""

    # TODO: figure out how to switch this back to lowercase
    # Username: Optional[str]  # = Field(..., alias="Username")
    # username: str = Field(..., alias="Username")
    username: str
    sub: str
    preferred_username: str
    email: str


class AnonymousUser(BaseModel):
    """Obfuscated user contributing to an ATBD Version"""

    preferred_username: str


class ReviewerUserInput(BaseModel):
    """Model for input when updating reviewers in an ATBD Version"""

    sub: str
    review_status: str


class ReviewerUser(CognitoUser):
    """
    Cognito user reviewing an ATBD Version (including the user's review
    status)
    """

    # TODO: make this enum ["in_progress", "done"]
    review_status: str


class AnonymousReviewerUser(AnonymousUser):
    """
    Obfuscated user reviewing an ATBD Version (including the user's review
    status)
    """

    review_status: str
