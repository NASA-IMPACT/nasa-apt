"""ATBDs endpoint."""
import datetime
from typing import List

from sqlalchemy import exc

from app.api.utils import (
    atbd_permissions_filter,
    get_active_user_principals,
    get_db,
    get_user,
    require_user,
    update_contributor_info,
)
from app.api.v2.pdf import save_pdf_to_s3
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession
from app.schemas import atbds
from app.schemas.users import User
from app.search.elasticsearch import add_atbd_to_index, remove_atbd_from_index

import fastapi_permissions as permissions
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


@router.get(
    "/atbds",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=List[atbds.SummaryOutput],
)
def list_atbds(
    role: str = None,
    status: str = None,
    user: User = Depends(get_user),
    db: DbSession = Depends(get_db),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Lists all ATBDs with summary version info (only versions with status
    `Published` will be displayed if the user is not logged in)"""
    if role:
        if not user:
            raise HTTPException(
                status_code=404,
                detail=f"User must be logged in to filter by role: {role}",
            )
        role = f"{role}:{user['sub']}"

    # apply permissions filter to remove any versions/
    # ATBDs that the user does not have access to
    # TODO: use a generator and only yield non `None` objects?

    atbds = [
        atbd_permissions_filter(principals, atbd, "view")
        for atbd in crud_atbds.scan(db=db, role=role, status=status)
        if atbd_permissions_filter(principals, atbd, "view") is not None
    ]

    for atbd in atbds:
        atbd = update_contributor_info(principals, atbd)

    return atbds


@router.head(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def atbd_exists(
    atbd_id: str,
    db: DbSession = Depends(get_db),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Returns status 200 if ATBD exsits and raises 404 if not (or if the user is
    not logged in and the ATBD has no versions with status `Published`)"""

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    if not atbd_permissions_filter(principals, atbd, "view"):
        raise HTTPException(
            status_code=404, detail=f"No data found for id/alias: {atbd_id}"
        )
    return True


@router.get(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.SummaryOutput,
)
def get_atbd(
    atbd_id: str,
    db: DbSession = Depends(get_db),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Returns a single ATBD (raises 404 if the ATBD has no versions with
    status `Published` and the user is not logged in)"""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    if not atbd_permissions_filter(principals, atbd, "view"):
        raise HTTPException(
            status_code=404, detail=f"No data found for id/alias: {atbd_id}"
        )
    atbd = update_contributor_info(principals, atbd)
    return atbd


@router.post(
    "/atbds",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def create_atbd(
    atbd_input: atbds.Create,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Creates a new ATBD. Requires a title, optionally takes an alias.
    Raises 400 if the user is not logged in."""
    if "role:contributor" not in principals:
        raise HTTPException(
            status_code=400, detail="User is not allowed to create a new ATBD"
        )
    atbd = crud_atbds.create(db, atbd_input, user["sub"])
    atbd = update_contributor_info(principals, atbd)
    return atbd


@router.post(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def update_atbd(
    atbd_id: str,
    atbd_input: atbds.Update,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Updates an ATBD (eiither Title or Alias). Raises 400 if the user
    is not logged in. Re-indexes all corresponding items in Elasticsearch
    with the new/updated values"""

    # Get latest version - ability to udpate an atbd is given
    # to whoever is allowed to update the latest version of that atbd
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1)

    if not all(
        [
            permissions.has_permission(principals, "update", version.__acl__())
            for version in atbd.versions
        ]
    ):
        raise HTTPException(
            status_code=404, detail=f"Update for ATBD id/alias: {atbd_id} not allowed"
        )

    atbd.last_updated_by = user["sub"]
    atbd.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    try:
        atbd = crud_atbds.update(db=db, db_obj=atbd, obj_in=atbd_input)
    except exc.IntegrityError:
        if atbd_input.alias:
            raise HTTPException(
                status_code=401,
                detail=f"Alias {atbd_input.alias} already exists in database",
            )

    background_tasks.add_task(add_atbd_to_index, atbd)
    atbd = update_contributor_info(principals, atbd)
    return atbd


# TODO: migrate to the `/events` endpoint
@router.post("/atbds/{atbd_id}/publish", response_model=atbds.FullOutput)
def publish_atbd(
    atbd_id: str,
    publish_input: atbds.PublishInput,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    user=Depends(require_user),
):
    """Publishes an ATBD. Raises 400 if the `latest` version does NOT have
    status `Published` or if the user is not logged in.

    Adds PDF generation (and serialization to S3) to background tasks.
    """
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1)
    [latest_version] = atbd.versions
    if latest_version.status == "Published":
        raise HTTPException(
            status_code=400,
            detail=f"Latest version of atbd {atbd_id} already has status: `Published`",
        )
    now = datetime.datetime.now(datetime.timezone.utc)
    latest_version.status = "Published"
    latest_version.published_by = user["sub"]
    latest_version.published_at = now

    # Publishing a version counts as updating it, so we
    # update the timestamp and user
    latest_version.last_updated_by = user["sub"]
    latest_version.last_updated_at = now

    if publish_input.changelog is not None and publish_input.changelog != "":
        latest_version.changelog = publish_input.changelog

    db.commit()
    db.refresh(latest_version)

    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=latest_version.major)


@router.delete("/atbds/{atbd_id}", responses={204: dict(description="ATBD deleted")})
def delete_atbd(
    atbd_id: str,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Deletes an ATBD (and all child versions). Removes all associated
    items in the Elasticsearch index."""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    if "role:curator" not in principals:
        raise HTTPException(
            status_code=400, detail=f"User not allowed to delete ATBD (id:{atbd_id})"
        )
    atbd = crud_atbds.remove(db=db, atbd_id=atbd_id)

    background_tasks.add_task(remove_atbd_from_index, atbd=atbd)

    return {}
