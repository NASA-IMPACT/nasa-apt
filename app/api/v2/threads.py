"""Threads endpoint."""

from sqlalchemy import orm

# from app.api.utils import get_active_user_principals, require_user
from app.crud.threads import crud_threads
from app.db.db_session import DbSession, get_db_session
from app.schemas import threads

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/threads/{thread_id}")
def get_thread(
    thread_id: int,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Retrieve a thread an associated comments"""
    try:
        return crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    except orm.exc.NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"No contact found for id {thread_id}"
        )
