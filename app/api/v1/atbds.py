"""ATBD's endpoint."""
from app.schemas import atbds, versions
from app.db.db_session import DbSession
from app.api.utils import get_db, require_user, get_major_from_version_string
from app.auth.saml import User
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from sqlalchemy import exc
from fastapi import APIRouter, Depends, HTTPException
from typing import List
import datetime

router = APIRouter()


@router.get(
    "/atbds",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=List[atbds.SummaryOutput],
)
def list_atbds(db: DbSession = Depends(get_db)):
    return crud_atbds.scan(db=db)


@router.get(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.FullOutput,
)
def get_atbd(atbd_id: str, fields: str = None, db: DbSession = Depends(get_db)):
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
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    try:
        atbd = crud_atbds.update(db=db, db_obj=atbd, obj_in=atbd_input)
    except exc.IntegrityError:
        if atbd_input.alias:
            raise HTTPException(
                status_code=401,
                detail=f"Alias {atbd_input.alias} already exists in database",
            )
    return atbd


@router.get("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def get_version(atbd_id: str, version: str, db=Depends(get_db)):

    major = get_major_from_version_string(version)
    return crud_atbds.get(db=db, atbd_id=atbd_id, version=major)


@router.post("/atbds/{atbd_id}/versions", response_model=atbds.FullOutput)
def create_new_version(atbd_id: str, db=Depends(get_db), user=Depends(require_user)):
    version = crud_versions.create(db=db, atbd_id=atbd_id, user=user["user"])
    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.post("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def update_atbd_version(
    atbd_id: str,
    version: str,
    version_input: versions.Update,
    db=Depends(get_db),
    user=Depends(require_user),
):
    major = get_major_from_version_string(version)
    [version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    crud_versions.update(db=db, db_obj=version, obj_in=version_input)

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.post("/atbds/{atbd_id}/publish", response_model=atbds.FullOutput)
def publish_atbd(atbd_id: str, db=Depends(get_db), user=Depends(require_user)):
    [latest_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1).versions
    if latest_version.status == "Published":
        raise HTTPException(
            status_code=400,
            detail=f"Latest version of atbd {atbd_id} already has status: `Published`",
        )
    latest_version.status = "Published"
    latest_version.published_by = user["user"]
    latest_version.published_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(latest_version)
    return crud_atbds.get(db=db, atbd_id=atbd_id, version=latest_version.major)
