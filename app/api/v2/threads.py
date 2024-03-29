"""Threads endpoint."""

import datetime
import re
from typing import Dict, List, Union

from app.api.utils import get_major_from_version_string
from app.crud.atbds import crud_atbds
from app.crud.comments import crud_comments
from app.crud.threads import crud_threads
from app.db.db_session import DbSession, get_db_session
from app.email.notifications import notify_atbd_version_contributors
from app.permissions import check_atbd_permissions, check_permissions
from app.schemas import comments, threads
from app.schemas.users import CognitoUser
from app.users.auth import require_user
from app.users.cognito import (
    get_active_user_principals,
    update_thread_contributor_info,
    update_user_info,
)

from fastapi import APIRouter, BackgroundTasks, Depends, Query

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

    _threads = []
    for thread, _, comment_count in crud_threads.get_multi(
        db_session=db, filters=filters
    ):
        thread.comment_count = comment_count
        thread = update_thread_contributor_info(
            principals=principals,
            atbd_version=atbd_version,
            thread=thread,
        )
        _threads.append(thread)
    return sorted(_threads, key=lambda x: x.created_at, reverse=True)


@router.get("/threads/stats", response_model=List[threads.Stats])
def get_threads_stats(
    atbds: List[str] = Query([]),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Returns the count of OPEN and CLOSED status threads for a list of
    AtbdVersions. This endpoint is unsecured, meaning that any id requested
    will be returned, regardless of wether or not the user has access to that
    AtbdVersion. This is a temporary implementation to avoid the costly overhead
    of having to query each AtbdVersion individually first, in order to check
    permissions and then allow the user access to the thread stats.

    The implementation will be re-visited at a later date, to ensure a both
    efficient and secure operation."""

    atbd_version_ids = [
        {"atbd_id": atbd.split("_")[0], "major": atbd.split("_")[1]} for atbd in atbds
    ]
    atbd_version_ids = [
        {
            "atbd_id": re.match(r"(?P<atbd_id>\d*)_v(?P<major>\d*).(\d*)", atbd).group(
                "atbd_id"
            ),
            "major": re.match(r"(?P<atbd_id>\d*)_v(?P<major>\d*).(\d*)", atbd).group(
                "major"
            ),
        }
        for atbd in atbds
    ]

    return [
        {
            "atbd_id": r.AtbdVersions.atbd_id,
            "major": r.AtbdVersions.major,
            "minor": r.AtbdVersions.minor,
            "status": {"open": r.open, "closed": r.closed},
            "total": r.total,
        }
        for r in crud_threads.get_stats(atbd_versions=atbd_version_ids, db_session=db)
        if check_permissions(
            principals=principals,
            action="view",
            acl=r.AtbdVersions.__acl__(),
            raise_exception=False,
        )
    ]


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
    [atbd_version] = atbd.versions
    check_atbd_permissions(principals=principals, action="view_comments", atbd=atbd)
    thread = update_thread_contributor_info(
        principals=principals,
        atbd_version=atbd_version,
        thread=thread,
    )

    return thread


@router.post(
    "/threads",
    responses={200: dict(description="Create a new Thread")},
    response_model=threads.Output,
)
def create_thread(
    thread_input: threads.Create,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Create a thread with the first comment"""
    atbd = crud_atbds.get(
        db=db, atbd_id=thread_input.atbd_id, version=thread_input.major
    )
    [atbd_version] = atbd.versions

    check_atbd_permissions(principals=principals, action="comment", atbd=atbd)

    thread = crud_threads.create(
        db_session=db,
        obj_in=threads.AdminCreate(
            **thread_input.dict(),
            created_by=user.sub,
            last_updated_by=user.sub,
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

    thread = update_thread_contributor_info(
        principals=principals,
        atbd_version=atbd_version,
        thread=thread,
    )

    notification_meta = dict(
        atbd_version=atbd_version,
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        user=user,
    )
    background_tasks.add_task(
        notify_atbd_version_contributors,
        **notification_meta,
        notification="new_thread_created",
        data={"section": thread.section},
    )
    # For mention only
    if thread.notify:
        background_tasks.add_task(
            notify_atbd_version_contributors,
            **notification_meta,
            notification="comment_mention",
            data={"section": thread.section, "notify": thread.notify},
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
    check_permissions(principals=principals, action="delete", acl=thread.__acl__())
    crud_threads.remove(db_session=db, id=(thread.id, thread.atbd_id, thread.major))
    return {}


@router.post(
    "/threads/{thread_id}",
    responses={200: dict(description="Update an existing thread")},
    response_model=threads.Output,
)
def update_thread(
    thread_id: int,
    update_thread_input: threads.Update,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Update thread status"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    [atbd_version] = atbd.versions
    check_atbd_permissions(principals=principals, action="comment", atbd=atbd)

    if thread.status != update_thread_input.status:
        notification_type = None
        if update_thread_input.status == "CLOSED":
            notification_type = "thread_closed"
        if update_thread_input.status == "OPEN":
            notification_type = "thread_reopened"
        if notification_type:
            background_tasks.add_task(
                notify_atbd_version_contributors,
                atbd_version=atbd_version,
                notification=notification_type,
                atbd_title=atbd.title,
                atbd_id=atbd.id,
                user=user,
                data={
                    "section": thread.section,
                    "notify": [
                        atbd_version.owner,
                        thread.created_by,
                        # Comments authors
                        *[comment.created_by for comment in thread.comments],
                    ],
                },
            )

    thread = crud_threads.update(
        db=db,
        db_obj=thread,
        obj_in=threads.AdminUpdate(
            **update_thread_input.dict(),
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    thread = update_thread_contributor_info(
        principals=principals,
        atbd_version=atbd_version,
        thread=thread,
    )

    return thread


@router.post("/threads/{thread_id}/comments")
def create_comment(
    thread_id: int,
    comment_input: comments.Create,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Create comment in a thread"""
    thread = crud_threads.get(db_session=db, obj_in=threads.Lookup(id=thread_id))
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    [atbd_version] = atbd.versions
    check_atbd_permissions(principals=principals, action="comment", atbd=atbd)
    # Should this return a comment or a thread? In the case of AtbdVersions
    # the entire ATBD is returned when creating a new version
    comment = crud_comments.create(
        db_session=db,
        obj_in=comments.AdminCreate(
            body=comment_input.body,
            thread_id=thread_id,
            created_by=user.sub,
            last_updated_by=user.sub,
        ),
    )
    comment = update_user_info(
        principals=principals, atbd_version=atbd_version, data_model=comment
    )

    notification_meta = dict(
        atbd_version=atbd_version,
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        user=user,
    )
    background_tasks.add_task(
        notify_atbd_version_contributors,
        **notification_meta,
        notification="new_comment_created",
        data={
            "section": thread.section,
            "notify": [
                atbd_version.owner,
                thread.created_by,
            ],
        },
    )
    # For mention only
    if comment_input.notify:
        background_tasks.add_task(
            notify_atbd_version_contributors,
            **notification_meta,
            notification="comment_mention",
            data={
                "section": thread.section,
                "notify": comment_input.notify,
            },
        )
    return comment


@router.delete("/threads/{thread_id}/comments/{comment_id}")
def delete_comment(
    thread_id: int,
    comment_id: int,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Delete comment from thread"""

    comment = crud_comments.get(db_session=db, obj_in=comments.Lookup(id=comment_id))

    check_permissions(principals=principals, action="delete", acl=comment.__acl__())
    crud_comments.remove(db_session=db, id=(comment.id, comment.thread_id))

    return {}


@router.post("/threads/{thread_id}/comments/{comment_id}")
def update_comment(
    thread_id: int,
    comment_id: int,
    update_comment_input: comments.Update,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Update comment"""

    comment = crud_comments.get(db_session=db, obj_in=comments.Lookup(id=comment_id))
    thread = crud_threads.get(
        db_session=db, obj_in=threads.Lookup(id=comment.thread_id)
    )
    atbd = crud_atbds.get(db=db, atbd_id=thread.atbd_id, version=thread.major)
    [atbd_version] = atbd.versions

    check_permissions(principals=principals, action="update", acl=comment.__acl__())

    comment = crud_comments.update(
        db=db,
        db_obj=comment,
        obj_in=comments.AdminUpdate(
            **update_comment_input.dict(),
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    comment = update_user_info(
        principals=principals, atbd_version=atbd_version, data_model=comment
    )
    return comment
