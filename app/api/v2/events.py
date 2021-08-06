"""."""

import datetime
from typing import Any, Dict, List

from app.api.utils import (
    get_active_user_principals,
    get_major_from_version_string,
    get_user,
    update_contributor_info,
)
from app.api.v2.pdf import save_pdf_to_s3
from app.api.v2.versions import process_users_input
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import Atbds
from app.permissions import check_permissions, filter_atbds
from app.schemas import atbds, events, users, versions

# from app.schemas.atbds import SummaryOutput
# from app.schemas.events import EventInput
# from app.schemas.versions import AdminUpdate as VersionUpdate
from app.search.elasticsearch import add_atbd_to_index

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


def accept_closed_review_request_handler(
    atbd: Atbds,
    user: users.User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    [version] = atbd.versions

    version_input = versions.AdminUpdate(
        reviewers=payload["reviewers"], status="CLOSED_REVIEW"
    )
    # performs the validation checks to make sure each of the
    # requested reviewers is allowed to be a reviewer on
    # the atbd version
    version_input = process_users_input(
        version_input=version_input, atbd_version=version, principals=principals
    )

    crud_versions.update(db=db, db_obj=version, obj_in=version_input)
    atbd = crud_atbds.get(db=db, atbd_id=atbd.id, version=version.major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

    return atbd


def publish_handler(
    atbd: Atbds,
    user: users.User,
    db: DbSession,
    payload: Dict,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    [version] = atbd.versions
    crud_versions.update(
        db=db,
        db_obj=version,
        obj_in=versions.AdminUpdate(
            changelog=payload["changelog"] if version.major > 1 else version.changelog,
            status="PUBLISHED",
            published_by=user["sub"],
            published_at=datetime.datetime.now(datetime.timezone.utc),
            last_updated_by=user["sub"],
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)
    background_tasks.add_task(add_atbd_to_index, atbd)

    atbd = crud_atbds.get(db=db, atbd_id=atbd.id, version=version.major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

    return atbd


def bump_minor_version_handler(
    atbd: Atbds,
    user: users.User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    [version] = atbd.versions

    crud_versions.update(
        db=db,
        db_obj=version,
        obj_in=versions.AdminUpdate(
            changelog=payload["changelog"],
            minor=version.minor + 1,
            last_updated_by=user["sub"],
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)
    background_tasks.add_task(add_atbd_to_index, atbd)

    atbd = crud_atbds.get(db=db, atbd_id=atbd.id, version=version.major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

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
    version_update = versions.AdminUpdate()

    if payload["review_status"] not in ["IN_PROGRESS", "DONE"]:
        raise HTTPException(
            status_code=403,
            detail=f"{payload['review_status']} is not an accepted value for review_status",
        )

    version_update.reviewers = [
        {"sub": r["sub"], "review_status": payload["review_status"]}
        if r["sub"] == user["sub"]
        else r
        for r in version.reviewers
    ]

    crud_versions.update(db=db, db_obj=version, obj_in=version_update)

    atbd = crud_atbds.get(db=db, atbd_id=atbd.id, version=version.major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

    return atbd


ACTIONS: Dict[str, Dict[str, Any]] = {
    "request_closed_review": {"next_status": "CLOSED_REVIEW_REQUESTED"},
    "cancel_closed_review_request": {"next_status": "DRAFT"},
    "deny_closed_review_request": {"next_status": "DRAFT"},
    "accept_closed_review_request": {
        "custom_handler": accept_closed_review_request_handler
    },
    "open_review": {"next_status": "OPEN_REVIEW"},
    "request_publication": {"next_status": "PUBLICATION_REQUESTED"},
    "cancel_publication_request": {"next_status": "OPEN_REVIEW"},
    "deny_publication_request": {"next_status": "OPEN_REVIEW"},
    "accept_publication_request": {"next_status": "PUBLICATION"},
    "publish": {"custom_handler": publish_handler},
    "bump_minor_version": {"custom_handler": bump_minor_version_handler},
    "update_review_status": {"custom_handler": update_review_status_handler},
}


@router.post(
    "/events",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=atbds.SummaryOutput,
)
def new_event(
    event: events.EventInput,
    background_tasks: BackgroundTasks,
    user: users.User = Depends(get_user),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    major, _ = get_major_from_version_string(event.version)
    atbd = crud_atbds.get(db=db, atbd_id=event.atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)
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
    crud_versions.update(
        db=db, db_obj=version, obj_in=versions.AdminUpdate(status=next_status)
    )
    atbd = crud_atbds.get(db=db, atbd_id=event.atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

    return atbd
