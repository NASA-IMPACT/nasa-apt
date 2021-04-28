from app.db.db_session import DbSession
from app.auth.saml import get_user, User
from app.db.db_session import get_session
from app import config
from fastapi import Depends, HTTPException
from boto3 import client
from typing import Tuple
import re


def s3_client():
    if config.AWS_RESOURCES_ENDPOINT:
        return client("s3", endpoint_url=config.AWS_RESOURCES_ENDPOINT)
    return client("s3")


# TODO: remove this method in favor of the `require_user` already present in `auth/saml`
def require_user(user: User = Depends(get_user)):

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User must be authenticated to perform this operation",
        )
    return user


def get_db(
    db_session: DbSession = Depends(get_session), user: User = Depends(get_user),
) -> DbSession:
    if user:
        print("User is authenticated. Elevating session")
        db_session.execute("SET SESSION AUTHORIZATION app_user;")

    return db_session


def get_major_from_version_string(version: str) -> Tuple[int]:

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

