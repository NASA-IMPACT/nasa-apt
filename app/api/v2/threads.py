"""Threads endpoint."""

from sqlalchemy import orm

from app.crud.comments import crud_comments

# from app.api.utils import get_active_user_principals, require_user
from app.crud.threads import crud_threads
from app.db.db_session import DbSession, get_db_session
from app.schemas import comments, threads

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter()


@router.get("/threads/{thread_id}")
def get_thread(
    thread_id: int,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Retrieve a thread and associated comments"""
    try:
        return crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    except orm.exc.NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"No contact found for id {thread_id}"
        )


@router.post(
    "/threads", responses={200: dict(description="Create a new Thread")},
)
def create_thread(
    thread_input: threads.Create,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Create a thread with the first comment"""
    comment_body = thread_input.comment.body
    del thread_input.comment
    thread = crud_threads.create(db_session=db, obj_in=thread_input)
    comment = comments.Create(body=comment_body, thread_id=thread.id)
    thread.comments = [crud_comments.create(db_session=db, obj_in=comment)]
    return thread


@router.delete("/threads/{thread_id}")
def delete_thread(
    thread_id: int,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Delete thread"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    db.delete(thread)
    db.commit()
    return {}


@router.post("/threads/{thread_id}")
def update_thread(
    thread_id: int,
    update_thread_input: threads.Update,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Update thread status"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    return crud_threads.update(db=db, db_obj=thread, obj_in=update_thread_input)


@router.post("/threads/{thread_id}/comments")
def create_comment(
    thread_id: int,
    comment_input: comments.FirstCreate,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Create comment in a thread"""
    comment = comments.Create(body=comment_input.body, thread_id=thread_id)
    return crud_comments.create(db_session=db, obj_in=comment)


@router.delete("/threads/{thread_id}/comments/{comment_id}")
def delete_comment(
    thread_id: int,
    comment_id: int,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Delete comment from thread"""
    crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    comment = crud_comments.get(db_session=db, obj_in=threads.Lookup(id=comment_id))
    db.delete(comment)
    db.commit()
    return {}


@router.post("/threads/{thread_id}/comments/{comment_id}")
def update_comment(
    thread_id: int,
    comment_id: int,
    update_comment_input: comments.Update,
    db: DbSession = Depends(get_db_session),
    # user: User = Depends(require_user),
    # principals: List[str] = Depends(get_active_user_principals)
):
    """Update comment"""
    crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    comment = crud_comments.get(db_session=db, obj_in=comments.Lookup(id=comment_id))
    return crud_comments.update(db=db, db_obj=comment, obj_in=update_comment_input)
