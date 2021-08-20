""" Users endpoint."""
from typing import List

from app import config
from app.api.utils import cognito_client, get_major_from_version_string
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession, get_db_session
from app.permissions import check_permissions
from app.schemas import users
from app.schemas.users import User
from app.users.auth import require_user
from app.users.cognito import get_active_user_principals, list_cognito_users

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
    db: DbSession = Depends(get_db_session),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Lists Users
    """
    major, _ = get_major_from_version_string(version)

    [atbd_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    version_acl = atbd_version.__acl__()
    app_users, _ = list_cognito_users()

    if user_filter == "transfer_ownership":
        check_permissions(
            principals=principals, action="offer_ownership", acl=version_acl
        )

        eligible_users = [
            user
            for user in app_users.values()
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
            for user in app_users.values()
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
            for user in app_users.values()
            if check_permissions(
                principals=get_active_user_principals(user),
                action="join_reviewers",
                acl=version_acl,
                error=False,
            )
        ]

    return sorted(eligible_users, key=lambda x: x.preferred_username.lower())


@router.post(
    "/users/auth",
    responses={
        200: dict(
            description="AWS Cognito JWT (id token) for the requested user-password combo"
        )
    },
)
def get_id_token(username: str, password: str):
    """Returns an Id Token for the given user/password combo"""
    return {
        "IdToken": cognito_client().initiate_auth(
            ClientId=config.APP_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
        )["AuthenticationResult"]["IdToken"]
    }
