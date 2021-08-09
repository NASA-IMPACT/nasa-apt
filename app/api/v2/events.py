"""Modules for handling AtbdVersion events"""
import datetime
from typing import Any, Dict, List

from app.api.utils import get_major_from_version_string
from app.api.v2.pdf import save_pdf_to_s3
from app.api.v2.versions import process_users_input
from app.crud.atbds import crud_atbds
from app.crud.comments import crud_comments
from app.crud.threads import crud_threads
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import Atbds
from app.email.notifications import UserNotification, notify_users
from app.permissions import check_permissions
from app.schemas import atbds, comments, events, threads, users, versions
from app.search.elasticsearch import add_atbd_to_index
from app.users.cognito import (
    get_active_user_principals,
    get_user,
    list_cognito_users,
    update_version_contributor_info,
)

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


def deny_closed_review_request_handler(
    atbd: Atbds,
    user: users.User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    """Handles deny closed review request"""
    [version] = atbd.versions

    version_input = versions.AdminUpdate(
        status="DRAFT",
        last_updated_by=user.sub,
        last_updated_at=datetime.datetime.now(datetime.timezone.utc),
    )
    version = crud_versions.update(db=db, db_obj=version, obj_in=version_input)

    # version = update_atbd_contributor_info()
    thread = crud_threads.create(
        db_session=db,
        obj_in=threads.AdminCreate(
            atbd_id=atbd.id,
            major=version.major,
            section="introduction",
            created_by=user.sub,
            last_updated_by=user.sub,
        ),
    )
    crud_comments.create(
        db_session=db,
        obj_in=comments.AdminCreate(
            body=payload["denial_reason"],
            thread_id=thread.id,
            created_by=user.sub,
            last_updated_by=user.sub,
        ),
    )

    version = update_version_contributor_info(principals=principals, version=version)
    background_tasks.add_task(
        notify_users,
        user_notifications=[
            UserNotification(
                **version.owner.dict,
                notification="closed_review_request_denied",
                data={"denial_reason": payload["denial_reason"]},
            )
        ],
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        atbd_version=f"v{version.major}.{version.minor}",
        user=user,
    )
    return atbd


def accept_closed_review_request_handler(
    atbd: Atbds,
    user: users.User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    """Handler for accept closed review"""
    [version] = atbd.versions

    version_input = versions.AdminUpdate(
        reviewers=payload["reviewers"],
        status="CLOSED_REVIEW",
        last_updated_by=user.sub,
        last_updated_at=datetime.datetime.now(datetime.timezone.utc),
    )

    # performs the validation checks to make sure each of the
    # requested reviewers is allowed to be a reviewer on
    # the atbd version
    version_input = process_users_input(
        version_input=version_input,
        atbd_version=version,
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        user=user,
        principals=principals,
        background_tasks=background_tasks,
    )
    # TODO:  notify owner

    version = crud_versions.update(db=db, db_obj=version, obj_in=version_input)

    version = update_version_contributor_info(principals=principals, version=version)

    return atbd


def publish_handler(
    atbd: Atbds,
    user: users.User,
    db: DbSession,
    payload: Dict,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    """Handler for ATBD Publication"""
    [version] = atbd.versions
    version = crud_versions.update(
        db=db,
        db_obj=version,
        obj_in=versions.AdminUpdate(
            changelog=payload["changelog"] if version.major > 1 else version.changelog,
            status="PUBLISHED",
            published_by=user.sub,
            published_at=datetime.datetime.now(datetime.timezone.utc),
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)
    background_tasks.add_task(add_atbd_to_index, atbd)

    version = update_version_contributor_info(principals=principals, version=version)

    # TODO: notify owner, authors and reviewers
    return atbd


def bump_minor_version_handler(
    atbd: Atbds,
    user: users.User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    """Handler for bumping minor version number. Regenerates PDF"""
    [version] = atbd.versions

    crud_versions.update(
        db=db,
        db_obj=version,
        obj_in=versions.AdminUpdate(
            changelog=payload["changelog"],
            minor=version.minor + 1,
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)
    background_tasks.add_task(add_atbd_to_index, atbd)

    version = update_version_contributor_info(principals=principals, version=version)

    # TODO: notify owner
    return atbd


def update_review_status_handler(
    atbd: Atbds,
    user: users.User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    """Loops through the `reviewers` array, setting `review_status` to done
    where the reviewer sub is equal to the sub of the user performing the request
    (ensures that reviewers can only update their own review status). Then checks
    if ALL the reviewers have marked their review as done, and if so, sets the
    atbd version status to `OPEN_REVIEW`"""

    [version] = atbd.versions
    version_update = versions.AdminUpdate(
        last_updated_by=user.sub,
        last_updated_at=datetime.datetime.now(datetime.timezone.utc),
    )

    # TODO: validate this using a pydantic model
    if payload["review_status"] not in ["IN_PROGRESS", "DONE"]:
        raise HTTPException(
            status_code=403,
            detail=f"{payload['review_status']} is not an accepted value for review_status",
        )

    version_update.reviewers = [
        {"sub": r["sub"], "review_status": payload["review_status"]}
        if r["sub"] == user.sub
        else r
        for r in version.reviewers
    ]

    version = crud_versions.update(db=db, db_obj=version, obj_in=version_update)

    version = update_version_contributor_info(principals=principals, version=version)

    # TODO: notify curators if all reviews marked as done

    return atbd


ACTIONS: Dict[str, Dict[str, Any]] = {
    "request_closed_review": {
        "next_status": "CLOSED_REVIEW_REQUESTED",
        "notify": ["curators"],
    },
    "cancel_closed_review_request": {"next_status": "DRAFT", "notify": ["curators"]},
    "deny_closed_review_request": {
        "custom_handler": deny_closed_review_request_handler,
    },
    "accept_closed_review_request": {
        "custom_handler": accept_closed_review_request_handler,
    },
    "open_review": {"next_status": "OPEN_REVIEW", "notify": ["owner", "authors"]},
    "request_publication": {
        "next_status": "PUBLICATION_REQUESTED",
        "notify": ["curators"],
    },
    "cancel_publication_request": {
        "next_status": "OPEN_REVIEW",
        "notify": ["curators"],
    },
    "deny_publication_request": {
        "next_status": "OPEN_REVIEW",
        "notify": ["owner"],  # authors too?
    },
    "accept_publication_request": {
        "next_status": "PUBLICATION",
        "notify": ["owner"],  # authors too?
    },
    "publish": {"custom_handler": publish_handler},
    "bump_minor_version": {"custom_handler": bump_minor_version_handler},
    "update_review_status": {"custom_handler": update_review_status_handler},
}


@router.post(
    "/events",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=atbds.SummaryOutput,
)
def event_handler(
    event: events.EventInput,
    background_tasks: BackgroundTasks,
    user: users.User = Depends(get_user),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Handles creation of new event. Checks ACL for the requested
    event and either simply updates the status, or executes a custom
    handler for more complex logic (notifying users, re-generating
    pdfs, etc)"""
    major, _ = get_major_from_version_string(event.version)
    atbd = crud_atbds.get(db=db, atbd_id=event.atbd_id, version=major)

    [version] = atbd.versions

    check_permissions(principals=principals, action=event.action, acl=version.__acl__())

    if ACTIONS[event.action].get("custom_handler"):
        return ACTIONS[event.action]["custom_handler"](
            atbd=atbd,
            user=user,
            payload=event.payload,
            db=db,
            principals=principals,
            background_tasks=background_tasks,
        )  # noqa

    next_status = ACTIONS[event.action]["next_status"]
    version = crud_versions.update(
        db=db,
        db_obj=version,
        obj_in=versions.AdminUpdate(
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
            status=next_status,
        ),
    )
    version = update_version_contributor_info(principals=principals, version=version)

    for user_type in ACTIONS[event.action]["notify"]:

        if user_type == "curators":
            users_to_notify = list_cognito_users(groups="curator")

        else:
            users_to_notify = getattr(version, user_type)

            # in the case of owner, there is only one user to
            # notify, so we wrap it in a list to avoid having to
            # accept different parameters types for the same parameter
            # in notify_users
            if not isinstance(users_to_notify, list):
                users_to_notify = [users_to_notify]

        user_notifications = UserNotification(**user, notification=event.action)

        background_tasks.add_task(
            notify_users,
            user_notifications=user_notifications,
            atbd_title=atbd.title,
            atbd_id=atbd.id,
            atbd_version=f"v{version.major}.{version.minor}",
            user=user,
        )

    return atbd
