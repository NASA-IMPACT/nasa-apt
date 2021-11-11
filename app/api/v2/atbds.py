"""ATBDs endpoint."""
import datetime
from typing import List

from sqlalchemy import exc

from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession, get_db_session
from app.permissions import check_atbd_permissions, filter_atbd_versions
from app.schemas import atbds, users
from app.search.elasticsearch import remove_atbd_from_index
from app.users.auth import get_user, require_user
from app.users.cognito import get_active_user_principals, update_atbd_contributor_info

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
    user: users.CognitoUser = Depends(get_user),
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Lists all ATBDs with summary version info (only versions with status
    `Published` will be displayed if the user is not logged in)"""
    if role:
        if not user:
            raise HTTPException(
                status_code=403,
                detail=f"User must be logged in to filter by role: {role}",
            )
        role = f"{role}:{user.sub}"

    # apply permissions filter to remove any versions/
    # ATBDs that the user does not have access to
    # TODO: use a generator and only yield non `None` objects?

    atbds = [
        filter_atbd_versions(principals, atbd, error=False)
        for atbd in crud_atbds.scan(db=db, role=role, status=status)
        if filter_atbd_versions(principals, atbd, error=False) is not None
    ]

    for atbd in atbds:
        atbd = update_atbd_contributor_info(principals, atbd)

    return atbds


@router.head(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def atbd_exists(
    atbd_id: str,
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Returns status 200 if ATBD exsits and raises 404 if not (or if the user is
    not logged in and the ATBD has no versions with status `Published`)"""

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    atbd = filter_atbd_versions(principals, atbd)

    return True


@router.get(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.SummaryOutput,
)
def get_atbd(
    atbd_id: str,
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Returns a single ATBD (raises 404 if the ATBD has no versions with
    status `Published` and the user is not logged in)"""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    atbd = filter_atbd_versions(principals, atbd)

    atbd = update_atbd_contributor_info(principals, atbd)

    return atbd


@router.post(
    "/atbds",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def create_atbd(
    atbd_input: atbds.Create,
    db: DbSession = Depends(get_db_session),
    user: users.CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Creates a new ATBD. Requires a title, optionally takes an alias.
    Raises 400 if the user is not logged in."""

    check_atbd_permissions(principals=principals, action="create_atbd", atbd=None)
    atbd = crud_atbds.create(db, atbd_input, user.sub)
    atbd = update_atbd_contributor_info(principals, atbd)
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
    db: DbSession = Depends(get_db_session),
    user: users.CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Updates an ATBD (either Title or Alias). Raises 400 if the user
    is not logged in. Re-indexes all corresponding items in Elasticsearch
    with the new/updated values"""

    # Get latest version - ability to udpate an atbd is given
    # to whoever is allowed to update the latest version of that atbd
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    check_atbd_permissions(
        principals=principals, action="update", atbd=atbd, all_versions=False
    )

    if atbd_input.alias and any([v.status == "PUBLISHED" for v in atbd.versions]):
        raise HTTPException(
            status_code=400,
            detail="Update not allowed for an ATBD with a published version",
        )

    atbd.last_updated_by = user.sub
    atbd.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    try:
        atbd = crud_atbds.update(db=db, db_obj=atbd, obj_in=atbd_input)
    except exc.IntegrityError:
        if atbd_input.alias:
            raise HTTPException(
                status_code=401,
                detail=f"Alias {atbd_input.alias} already exists in database",
            )

    atbd = update_atbd_contributor_info(principals, atbd)
    return atbd


@router.delete("/atbds/{atbd_id}", responses={204: dict(description="ATBD deleted")})
def delete_atbd(
    atbd_id: str,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
    user: users.CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Deletes an ATBD (and all child versions). Removes all associated
    items in the Elasticsearch index."""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    check_atbd_permissions(principals=principals, action="delete", atbd=atbd)

    atbd = crud_atbds.remove(db=db, atbd_id=atbd_id)

    background_tasks.add_task(remove_atbd_from_index, atbd=atbd)
    # TODO: this should also remove all associated PDFs in S3.

    return {}
