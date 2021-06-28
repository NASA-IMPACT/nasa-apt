"""ATBDs endpoint."""
import datetime
from typing import List

from sqlalchemy import exc

from app.api.utils import get_db, require_user
from app.api.v2.pdf import save_pdf_to_s3
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession
from app.schemas import atbds

# from app.auth.saml import User
from app.schemas.users import User
from app.search.elasticsearch import add_atbd_to_index, remove_atbd_from_index

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


@router.get(
    "/atbds",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=List[atbds.SummaryOutput],
)
def list_atbds(db: DbSession = Depends(get_db)):
    """Lists all ATBDs with summary version info (only versions with status
    `Published` will be displayed if the user is not logged in)"""
    return crud_atbds.scan(db=db)


@router.head(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def atbd_exists(atbd_id: str, db: DbSession = Depends(get_db)):
    """Returns status 200 if ATBD exsits and raises 404 if not (or if the user is
    not logged in and the ATBD has no versions with status `Published`)"""
    return crud_atbds.exists(db=db, atbd_id=atbd_id)


@router.get(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.SummaryOutput,
)
def get_atbd(atbd_id: str, db: DbSession = Depends(get_db)):
    """Returns a single ATBD (raises 404 if the ATBD has no versions with
    status `Published` and the user is not logged in)"""
    return crud_atbds.get(db=db, atbd_id=atbd_id)


@router.post(
    "/atbds",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def create_atbd(
    atbd_input: atbds.Create,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    """Creates a new ATBD. Requires a title, optionally takes an alias.
    Raises 400 if the user is not logged in."""
    output = crud_atbds.create(db, atbd_input, user["user"])
    return output


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
):
    """Updates an ATBD (eiither Title or Alias). Raises 400 if the user
    is not logged in. Re-indexes all corresponding items in Elasticsearch
    with the new/updated values"""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    atbd.last_updated_by = user["user"]
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
    return atbd


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
    latest_version.published_by = user["user"]
    latest_version.published_at = now

    # Publishing a version counts as updating it, so we
    # update the timestamp and user
    latest_version.last_updated_by = user["user"]
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
):
    """Deletes an ATBD (and all child versions). Removes all associated
    items in the Elasticsearch index."""
    atbd = crud_atbds.remove(db=db, atbd_id=atbd_id)

    background_tasks.add_task(remove_atbd_from_index, atbd=atbd)

    return {}
