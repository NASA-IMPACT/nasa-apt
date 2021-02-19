from app.db.db_session import DbSession

from starlette.requests import Request
from app.auth.saml import get_user, User
from fastapi import Depends


def get_db(request: Request, user: User = Depends(get_user)) -> DbSession:

    if user:
        request.state.db.execute("SET SESSION AUTHORIZATION app_user;")

    return request.state.db

