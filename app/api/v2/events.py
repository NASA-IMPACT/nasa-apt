"""."""

from typing import Any, Dict, List

from app.api.utils import (
    get_active_user_principals,
    get_major_from_version_string,
    get_user,
)
from app.api.v2.pdf import save_pdf_to_s3
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import Atbds
from app.permissions import check_permissions, filter_atbds
from app.schemas.events import EventInput
from app.schemas.users import User
from app.schemas.versions import Update as VersionUpdate

from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter()


def bump_minor_version_handler(
    atbd: Atbds,
    user: User,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
):
    [version] = atbd.versions
    crud_versions.update(
        db=db, db_obj=version, obj_in=VersionUpdate(minor=version.minor + 1)
    )
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)

    return {}


def mark_review_done_handler(
    atbd: Atbds, user: User, db: DbSession = Depends(get_db_session),
):
    [version] = atbd.versions
    version_update: Dict[str, Any] = {
        "reviewers": [
            {"sub": r["sub"], "review_status": "DONE"} if r["sub"] == user["sub"] else r
            for r in version.reviewers
        ]
    }

    if all([r["review_status"] == "DONE" for r in version.reviewers]):
        version_update["status"] = "OPEN_REVIEW"

    crud_versions.update(db=db, db_obj=version, obj_in=VersionUpdate(**version_update))
    return {}


ACTIONS: Dict[str, Dict[str, Any]] = {
    "request_closed_review": {"next_status": "CLOSED_REVIEW_REQUESTED"},
    "cancel_closed_review_request": {"next_status": "DRAFT"},
    "deny_closed_review_request": {"next_status": "DRAFT"},
    "accept_closed_review": {"next_status": "CLOSED_REVIEW"},
    "open_review": {"next_status": "OPEN_REVIEW"},
    "request_publication": {"next_status": "PUBLICATION_REQUESTED"},
    "cancel_publication_request": {"next_status": "OPEN_REVIEW"},
    "deny_publication_request": {"next_status": "OPEN_REVIEW"},
    "accept_publication_request": {"next_status": "PUBLICATION"},
    "publish": {"next_status": "PUBLISHED"},
    "bump_minor_version": {"custom_handler": bump_minor_version_handler},
}


@router.post(
    "/events",
    responses={200: dict(description="Return a list of all available ATBDs")},
)
def new_event(
    event: EventInput,
    user: User = Depends(get_user),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    major, _ = get_major_from_version_string(event.version)
    atbd = crud_atbds.get(db=db, atbd_id=event.atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)
    [version] = atbd.versions
    check_permissions(principals=principals, action=event.action, acl=version.__acl__())

    if ACTIONS[event.actions].get("custom_handler"):
        return ACTIONS[event.actions]["custom_handler"](atbd=atbd, user=user)  # noqa

    next_status = ACTIONS[event.action]["next_status"]
    crud_versions.update(
        db=db, db_obj=version, obj_in=VersionUpdate(status=next_status)
    )

    return {}
