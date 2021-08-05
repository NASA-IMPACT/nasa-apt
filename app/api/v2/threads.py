"""Threads endpoint."""

import datetime
from typing import Dict, List, Union

from app.api.utils import (
    get_active_user_principals,
    get_major_from_version_string,
    require_user,
    update_thread_contributor_info,
)
from app.crud.atbds import crud_atbds
from app.crud.comments import crud_comments
from app.crud.threads import crud_threads
from app.db.db_session import DbSession, get_db_session
from app.permissions import check_atbd_permissions, check_permissions
from app.schemas import comments, threads
from app.schemas.users import CognitoUser

from fastapi import APIRouter, Depends

router = APIRouter()


# TODO: make status and section into an Enum
@router.get(
    "/threads",
    responses={200: dict(description="A list of threads belonging to an ATBD")},
    response_model=List[threads.Output],
)
def get_threads(
    atbd_id: int,
    version: str,
    status: str = None,
    section: str = None,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns all threads related to a single AtbdVersion. Filterable
    by status (`OPEN`/`CLOSED`) and an AtbdVersion document section
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    [atbd_version] = atbd.versions
    check_atbd_permissions(principals, action="view_comments", atbd=atbd)

    filters: Dict[str, Union[str, int]] = {"atbd_id": atbd_id, "major": major}
    if status:
        filters["status"] = status
    if section:
        filters["section"] = section

    return [
        threads.Output(
            **update_thread_contributor_info(
                principals=principals, atbd_version=atbd_version, thread=thread,
            ).__dict__,
            comment_count=comment_count,
        )
        for thread, _, comment_count in crud_threads.get_multi(
            db_session=db, filters=filters
        )
    ]


# # Is this get method required? Or will threads always be accessed by
# # atbd_id and major
@router.get("/threads/{thread_id}", response_model=threads.Output)
def get_thread(
    thread_id: int,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Retrieve a thread and associated comments"""
    # TODO: Handle the raised error if lookup doesn't find what it's looking for
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    check_atbd_permissions(principals=principals, action="view_comments", atbd=atbd)

    return thread


@router.post(
    "/threads",
    responses={200: dict(description="Create a new Thread")},
    response_model=threads.Output,
)
def create_thread(
    thread_input: threads.Create,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Create a thread with the first comment"""
    atbd = crud_atbds.get(
        db=db, atbd_id=thread_input.atbd_id, version=thread_input.major
    )
    check_atbd_permissions(principals=principals, action="comment", atbd=atbd)

    thread = crud_threads.create(
        db_session=db,
        obj_in=threads.AdminCreate(
            **thread_input.dict(), created_by=user.sub, last_updated_by=user.sub,
        ),
    )
    crud_comments.create(
        db_session=db,
        obj_in=comments.AdminCreate(
            body=thread_input.comment.body,
            thread_id=thread.id,
            created_by=user.sub,
            last_updated_by=user.sub,
        ),
    )
    return thread


@router.delete("/threads/{thread_id}")
def delete_thread(
    thread_id: int,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Delete thread"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    check_atbd_permissions(principals=principals, action="delete_thread", atbd=atbd)
    crud_threads.remove(db_session=db, id=thread_id)
    return {}


@router.post(
    "/threads/{thread_id}",
    responses={200: dict(description="Update an existing thread")},
    response_model=threads.Output,
)
def update_thread(
    thread_id: int,
    update_thread_input: threads.Update,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Update thread status"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    check_atbd_permissions(principals=principals, action="comment", atbd=atbd)

    return crud_threads.update(db=db, db_obj=thread, obj_in=update_thread_input)


@router.post("/threads/{thread_id}/comments")
def create_comment(
    thread_id: int,
    comment_input: comments.Create,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Create comment in a thread"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    check_atbd_permissions(principals=principals, action="comment", atbd=atbd)
    # Should this return a comment or a thread? In the case of AtbdVersions
    # the entire ATBD is returned when creating a new version
    return crud_comments.create(
        db_session=db,
        obj_in=comments.AdminCreate(
            body=comment_input.body,
            thread_id=thread_id,
            created_by=user.sub,
            last_updated_by=user.sub,
        ),
    )


@router.delete("/threads/{thread_id}/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Delete comment from thread"""

    comment = crud_comments.get(db_session=db, obj_in=comments.Lookup(id=comment_id))
    check_permissions(principals=principals, action="delete", acl=comment.__acl__())
    crud_comments.remove(db_session=db, id=comment_id)

    return {}


@router.post("/threads/{thread_id}/comments/{comment_id}")
def update_comment(
    comment_id: int,
    update_comment_input: comments.Update,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Update comment"""

    comment = crud_comments.get(db_session=db, obj_in=comments.Lookup(id=comment_id))
    check_permissions(principals=principals, action="update", acl=comment.__acl__())
    comment = crud_comments.update(
        db=db,
        db_obj=comment,
        obj_in=comments.AdminUpdate(
            **update_comment_input.asdict(),
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    return comment
