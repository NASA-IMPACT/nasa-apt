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
from app.permissions import check_permissions
from app.schemas import users
from app.schemas.users import User

from fastapi import APIRouter, Depends

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
        check_permissions(
            principals=principals, action="offer_ownership", acl=version_acl
        )

        eligible_users = [
            user
            for user in app_users
            if check_permissions(
                principals=get_active_user_principals(user),
                action="receive_ownership",
                acl=version_acl,
                error=False,
            )
        ]
    if user_filter == "invite_authors":
        check_permissions(
            principals=principals, action="invite_authors", acl=version_acl
        )

        eligible_users = [
            user
            for user in app_users
            if check_permissions(
                principals=get_active_user_principals(user),
                action="join_authors",
                acl=version_acl,
                error=False,
            )
        ]
    if user_filter == "invite_reviewers":
        check_permissions(
            principals=principals, action="invite_reviewers", acl=version_acl
        )

        eligible_users = [
            user
            for user in app_users
            if check_permissions(
                principals=get_active_user_principals(user),
                action="join_reviewers",
                acl=version_acl,
                error=False,
            )
        ]

    return sorted(eligible_users, key=lambda x: x["preferred_username"].lower())
