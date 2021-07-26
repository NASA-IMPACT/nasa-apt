"""."""

from typing import Any, Dict, List

from app.api.utils import (
    get_active_user_principals,
    get_major_from_version_string,
    get_user,
    update_contributor_info,
)
from app.api.v2.pdf import save_pdf_to_s3
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import Atbds
from app.permissions import check_permissions, filter_atbds
from app.schemas.events import EventInput
from app.schemas.users import User
from app.schemas.versions import AdminUpdate as VersionUpdate
from app.search.elasticsearch import add_atbd_to_index

from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter()


def publish_handler(
    atbd: Atbds,
    user: User,
    db: DbSession,
    payload: Dict,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    [version] = atbd.versions
    crud_versions.update(
        db=db, db_obj=version, obj_in=VersionUpdate(status="PUBLISHED")
    )
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)
    background_tasks.add_task(add_atbd_to_index, atbd)

    atbd = crud_atbds.get(db=db, atbd_id=atbd.id, version=version.major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

    return atbd

    return {}


def bump_minor_version_handler(
    atbd: Atbds,
    user: User,
    payload: Dict,
    db: DbSession,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    [version] = atbd.versions

    crud_versions.update(
        db=db, db_obj=version, obj_in=VersionUpdate(minor=version.minor + 1)
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
    user: User,
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

    print("PAYLOAD: ", payload)

    [version] = atbd.versions
    version_update = VersionUpdate()
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
    "accept_closed_review_request": {"next_status": "CLOSED_REVIEW"},
    "open_review": {"next_status": "OPEN_REVIEW"},
    "request_publication": {"next_status": "PUBLICATION_REQUESTED"},
    "cancel_publication_request": {"next_status": "OPEN_REVIEW"},
    "deny_publication_request": {"next_status": "OPEN_REVIEW"},
    "accept_publication_request": {"next_status": "PUBLICATION"},
    "publish": {"custom_handler": publish_handler},
    "bump_minor_version": {"custom_handler": bump_minor_version_handler},
    "update_review_status": {"custom_handler": update_review_status_handler},
    # "create_new_version": {"custom_handler": create_new_version},
}


@router.post(
    "/events",
    responses={200: dict(description="Return a list of all available ATBDs")},
)
def new_event(
    event: EventInput,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_user),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    major, _ = get_major_from_version_string(event.version)
    atbd = crud_atbds.get(db=db, atbd_id=event.atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)
    [version] = atbd.versions
    print("PRINCIPALS: ", principals)
    print("ACTION: ", event.action)
    print("ACL: ", version.__acl__())
    check_permissions(principals=principals, action=event.action, acl=version.__acl__())
    print(
        "PERMITTED: ",
        check_permissions(
            principals=principals, action=event.action, acl=version.__acl__()
        ),
    )
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
        db=db, db_obj=version, obj_in=VersionUpdate(status=next_status)
    )
    atbd = crud_atbds.get(db=db, atbd_id=event.atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)
    atbd = update_contributor_info(principals=principals, atbd=atbd)

    return atbd
