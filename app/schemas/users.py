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
        # list_users_in_group response model has user attributes
        # under `Attributes` whereas the admin_get_user response model
        # lists user attributes under `UserAttributes`. The following
        # line searches through the provided values, searching for
        # either the `Attribuets` or the `UserAttributes` key to then
        # use to reformat the values of the data model.

        user_attributes_key = next(
            (k for k in values.keys() if k in ["Attributes", "UserAttributes"]), None
        )

        if not user_attributes_key:
            return values

        for attribute in values[user_attributes_key]:
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
