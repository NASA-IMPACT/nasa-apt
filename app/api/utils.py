"""
Provides various utilities to the API classes
"""
import re
from typing import Tuple, Union

from boto3 import client

from app.auth.cognito import get_user
from app.config import AWS_RESOURCES_ENDPOINT
from app.db.db_session import DbSession, get_session
from app.logs import logger
from app.schemas.users import User

from fastapi import Depends, HTTPException


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
    print("USER: ", user)
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
