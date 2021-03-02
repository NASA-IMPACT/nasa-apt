from app.db.db_session import DbSession

from app.auth.saml import get_user, User
from app.db.db_session import get_session
from fastapi import Depends


def get_db(
    db_session: DbSession = Depends(get_session), user: User = Depends(get_user),
) -> DbSession:

    if user:
        print("User is authenticated. Elevating session")
        db_session.execute("SET SESSION AUTHORIZATION app_user;")

    return db_session

