from starlette.requests import Request
from app.db.db_session import get_session


async def db_session_middleware(request: Request, call_next):
    """
    Inject a DB connection into the request.state object, making it available
    to controllers.
    """
    with get_session() as db:
        request.state.db = db
        response = await call_next(request)
    return response
