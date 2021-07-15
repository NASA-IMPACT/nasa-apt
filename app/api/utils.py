"""
Provides various utilities to the API classes
"""
import re
from typing import List, Tuple, Union

from boto3 import client

from app import config
from app.auth.cognito import get_user
from app.config import AWS_RESOURCES_ENDPOINT
from app.db.db_session import DbSession, get_session
from app.db.models import Atbds
from app.logs import logger
from app.schemas.users import User
from app.schemas.versions import (
    AnonymousReviewerUser,
    AnonymousUser,
    CognitoUser,
    ReviewerUser,
)

import fastapi_permissions as permissions
from fastapi import Depends, HTTPException


def get_active_user_principals(user: User = Depends(get_user)) -> List[str]:
    """Returns the principals for a user, to be used when validating permissions
    to perform certain actions or requests"""
    print("user: ", user)
    # TODO: check groups
    principals = [permissions.Everyone]
    if user:
        principals.extend([permissions.Authenticated, f"user:{user['sub']}"])
        principals.extend(
            [f"role:{groupname}" for groupname in user.get("cognito:groups", [])]
        )

    return principals


def update_contributor_info(principals: List[str], atbd: Atbds):
    """
    Insert contributor (owner, author and reviewer) user info from
    Cognito into an ATBD Version. Identifying user information is
    obfuscated in accordance with the principals of the user (eg:
    unauthenticated users cannot see ANY identifying info, ATBDVersions
    cannot see identifying info of reviewers, but can see identifying
    info of other authors)
    """
    app_users = list_cognito_users()

    for version in atbd.versions:
        version_acl = version.__acl__()

        if permissions.has_permission(principals, "view_owner", version_acl):
            [version.owner] = [
                CognitoUser(**app_user)
                for app_user in app_users
                if app_user["sub"] == version.owner
            ]
        else:
            version.owner = AnonymousUser(preferred_username="Owner")

        if permissions.has_permission(principals, "view_authors", version_acl):

            version.authors = [
                CognitoUser(**app_user)
                for app_user in app_users
                if app_user["sub"] in version.authors
            ]
        else:
            version.authors = [
                AnonymousUser(preferred_username=f"Author {str(i)}")
                for i, _ in enumerate(version.authors)
            ]

        if permissions.has_permission(principals, "view_reviewers", version_acl):
            version.reviewers = [
                ReviewerUser(**app_user, review_status=reviewer["review_status"])
                for reviewer in version.reviewers
                for app_user in app_users
                if app_user["sub"] == reviewer["sub"]
            ]
        else:
            version.reviewers = [
                AnonymousReviewerUser(
                    preferred_username=f"Reviewer {str(i)}",
                    review_status=v["review_status"],
                )
                for i, v in enumerate(version.reviewers)
            ]

    return atbd


def list_cognito_users():
    """
    Returns a list of ALL cognito users, to be filtered against the
    users of a document (authors, reviewers, owner)
    """
    list_user_params = dict(
        UserPoolId=config.USER_POOL_ID,
        AttributesToGet=["email", "sub", "preferred_username"],
        Limit=500,
    )
    users = []
    client = cognito_client()
    response = client.list_users(**list_user_params)
    users.extend(response.get("Users", []))
    while response.get("PaginationToken"):
        list_user_params["PaginationToken"] = response["PaginationToken"]
        response = client.list_users(**list_user_params)
        users.extend(response.get("Users", []))

    for user in users:
        for attribute in user["Attributes"]:
            user[attribute["Name"]] = attribute["Value"]
        del user["Attributes"]

    return users


def atbd_permissions_filter(principals: List[str], atbd: Atbds, action: str = "view"):
    """
    Applies a permission check to a list of ATBDs, returning only the versions
    that the user is allowed to see. If an ATBD has NO versions that the user is
    allowed to access, then the filter returns `None`.
    """

    versions = [
        version
        for version in atbd.versions
        if permissions.has_permission(principals, action, version.__acl__())
    ]
    if not versions:
        return None
    atbd.versions = versions
    return atbd


def cognito_client() -> client:
    """
    Returns a boto3 cognito client - configured to point at a specifc endpoint url if provided
    """
    if AWS_RESOURCES_ENDPOINT:
        return client("cognito-idp", endpoint_url=AWS_RESOURCES_ENDPOINT)

    return client("cognito-idp")


def s3_client() -> client:
    """
    Returns a boto3 s3 client - configured to point at a specfic endpoint url if provided
    """
    if AWS_RESOURCES_ENDPOINT:
        return client("s3", endpoint_url=AWS_RESOURCES_ENDPOINT)
    return client("s3")


def require_user(user: User = Depends(get_user)) -> User:

    """
    Raises an exception if not user user token is supplied

    TODO: remove this method in favor of the `require_user` already present in `auth/saml`
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User must be authenticated to perform this operation",
        )
    return user


def get_db(
    db_session: DbSession = Depends(get_session), user: User = Depends(get_user),
) -> DbSession:
    """
    Returns an db session with the correct permission level set (`anonymous` by
    default and `app_user` if the user is authenticated)
    """
    if user:
        logger.info(f"User {user['sub']} is authenticated. Elevating session")
        db_session.execute("SET SESSION AUTHORIZATION app_user;")

    return db_session


def get_major_from_version_string(version: str) -> Tuple[int, Union[int, None]]:
    """
    Operations on versions can be performed using just the major version number:
    `/atbds/1/versions/2` or using the full semver number: `/atds/1/versions/v2.1`.
    This utility parses the given string and returns the major (and possibly minor)
    version number
    """

    if version == "latest":
        return -1, None

    try:
        return int(version), None

    except ValueError:

        search = re.search(r"^v(?P<major>\d+)\.(?P<minor>\d+)$", version)
        if not search:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Malformed version string: {version}. Expected format to be one of: "
                    f'v<major:int>.<minor:int>, <major:int>, or "latest"'
                ),
            )
        return int(search.group("major")), int(search.group("minor"))
