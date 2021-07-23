"""."""

from typing import List

from app.api.utils import (
    get_active_user_principals,
    get_major_from_version_string,
    get_user,
    update_contributor_info,
)
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.permissions import check_permissions, filter_atbds
from app.schemas.events import EventInput
from app.schemas.users import User
from app.schemas.versions import Update as VersionUpdate

from fastapi import APIRouter, Depends

router = APIRouter()

ACTIONS = {
    "request_closed_review": {"next_status": "CLOSED_REVIEW_REQUESTED"},
    "cancel_closed_review_request": {"next_status": "DRAFT"},
    "deny_closed_review_request": {"next_status": "DRAFT"},
    "accept_closed_review": {"next_status": "CLOSED_REVIEW"},
    "open_review": {"next_status": "OPEN_REVIEW"},
    "request_publication": {"next_status", "PUBLICATION_REQUESTED"},
    "cancel_publication_request": {"next_status": "OPEN_REVIEW"},
    "deny_publication_request": {"next_status": "OPEN_REVIEW"},
    "accept_publication_request": {"next_status": "PUBLICATION"},
    "publish": {"next_status": "PUBLISHED"},
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
    next_status = ACTIONS[event.action]["next_status"]
    crud_versions.update(
        db=db, db_obj=version, obj_in=VersionUpdate(status=next_status)
    )

    return {}
