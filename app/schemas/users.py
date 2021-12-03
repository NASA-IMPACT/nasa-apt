"""Schemas for Cognito User models"""

from typing import List

from pydantic import BaseModel, Field, root_validator


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


class AnonymousUser(BaseModel):
    """Obfuscated user contributing to an ATBD Version"""

    preferred_username: str


class CognitoUser(AnonymousUser):
    """User contributing to an ATBD Version, as returned by Cognito"""

    sub: str
    email: str
    cognito_groups: List[str] = Field([], alias="cognito:groups")

    @root_validator(pre=True)
    def _unpack_attributes(cls, values):
        if "Attributes" not in values:
            return values

        for attribute in values["Attributes"]:
            if attribute["Name"] in [
                "email",
                "sub",
                "preferred_username",
            ]:
                values[attribute["Name"]] = attribute["Value"]
        return values


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
