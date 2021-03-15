from app.db.db_session import DbSession

from app.auth.saml import get_user, User
from app.db.db_session import get_session
from fastapi import Depends, HTTPException
import re


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


def get_major_from_version_string(version: str) -> int:

    if version == "latest":
        return -1

    try:
        return int(version)

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
        return int(search.group("major"))

