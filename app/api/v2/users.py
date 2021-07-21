""" Users endpoint."""
from typing import List

from app.api.utils import (
    get_active_user_principals,
    get_db,
    get_major_from_version_string,
    list_cognito_users,
    require_user,
)
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession
from app.schemas import users
from app.schemas.users import User

import fastapi_permissions as permissions
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


# TOOD: make filter an enum of `tranfser_ownership`, `invite_coauthors`, `invite_reviewers`
@router.get(
    "/users",
    responses={200: dict(description="Return a list of users in Cognito")},
    response_model=List[users.CognitoUser],
)
def list_users(
    atbd_id: str,
    version: str,
    user_filter: str,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Lists Users
    """
    major, _ = get_major_from_version_string(version)
    [atbd_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    version_acl = atbd_version.__acl__()
    app_users = list_cognito_users()

    if user_filter == "transfer_ownership":
        if not permissions.has_permission(principals, "offer_ownership", version_acl):
            raise HTTPException(
                status_code=400,
                detail=f"User {user['preferred_username']} is not allowed to transfer ownership",
            )

        eligible_users = [
            user
            for user in app_users
            if permissions.has_permission(
                get_active_user_principals(user), "receive_ownership", version_acl
            )
        ]
    if user_filter == "invite_authors":
        if not permissions.has_permission(principals, "invite_authors", version_acl):
            raise HTTPException(
                status_code=400,
                detail=f"User {user['preferred_username']} is not allowed to invite authors",
            )

        eligible_users = [
            user
            for user in app_users
            if permissions.has_permission(
                get_active_user_principals(user), "join_authors", version_acl
            )
        ]
    if user_filter == "invite_reviewers":
        if not permissions.has_permission(principals, "invite_reviewers", version_acl):
            raise HTTPException(
                status_code=400,
                detail=f"User {user['preferred_username']} is not allowed to invite reviewers",
            )

        eligible_users = [
            user
            for user in app_users
            if permissions.has_permission(
                get_active_user_principals(user), "join_reviewers", version_acl
            )
        ]

    return eligible_users
