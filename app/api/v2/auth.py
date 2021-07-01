"""SAML auth endpoint."""

from app import config
from app.api.utils import cognito_client, require_user
from app.schemas.users import User

from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/user/{username}")
def get_user(username: str, user: User = Depends(require_user)):
    """."""

    userinfo = cognito_client().admin_get_user(
        UserPoolId=config.USER_POOL_ID, Username=username
    )

    return userinfo
