"""."""

from typing import List

from app.api.utils import get_active_user_principals, get_user
from app.db.db_session import DbSession, get_db_session
from app.schemas.users import User

from fastapi import APIRouter, Depends

router = APIRouter()


@router.post(
    "/events",
    responses={200: dict(description="Return a list of all available ATBDs")},
)
def new_event(
    atbd_id: str,
    version: str,
    user: User = Depends(get_user),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """."""
