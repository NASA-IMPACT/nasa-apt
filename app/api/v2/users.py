""" Users endpoint."""
from typing import List

from app.api.utils import (
    get_active_user_principals,
    get_db,
    list_cognito_users,
    require_user,
)
from app.db.db_session import DbSession
from app.schemas import users
from app.schemas.users import User

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get(
    "/users",
    responses={200: dict(description="Return a list of users in Cognito")},
    response_model=List[users.CognitoUser],
)
def list_users(
    atbd_id: str,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Lists Users
    """
    # TODO: implement permissions validation
    return list_cognito_users()
