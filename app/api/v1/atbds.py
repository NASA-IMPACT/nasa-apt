"""ATBD's endpoint."""
from app import config
from app.schemas import atbds, versions
from app.db.db_session import DbSession
from app.api.utils import (
    get_db,
    require_user,
    get_major_from_version_string,
    s3_client,
)
from app.api.v1.pdf import save_pdf_to_s3
from app.auth.saml import User
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.db.models import Atbds, AtbdVersionsContactsAssociation
from sqlalchemy import exc
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    responses,
    File,
    UploadFile,
    BackgroundTasks,
)
from typing import List
import datetime
import botocore

router = APIRouter()


@router.get(
    "/atbds",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=List[atbds.SummaryOutput],
)
def list_atbds(db: DbSession = Depends(get_db)):
    return crud_atbds.scan(db=db)


@router.head(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def atbd_exists(atbd_id: str, db: DbSession = Depends(get_db)):
    return crud_atbds.exists(db=db, atbd_id=atbd_id)


@router.get(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.SummaryOutput,
)
def get_atbd(atbd_id: str, db: DbSession = Depends(get_db)):
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
    return atbd


@router.delete("/atbds/{atbd_id}", responses={204: dict(description="ATBD deleted")})
def delete_atbd(
    atbd_id: str, db: DbSession = Depends(get_db), user: User = Depends(require_user),
):
    crud_atbds.remove(db_session=db, id=atbd_id)
    return {}


@router.head(
    "/atbds/{atbd_id}/versions/{version}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def version_exists(atbd_id: str, version: str, db: DbSession = Depends(get_db)):
    major, _ = get_major_from_version_string(version)
    return crud_atbds.exists(db=db, atbd_id=atbd_id, version=major)


@router.get("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def get_version(atbd_id: str, version: str, db=Depends(get_db)):

    major, _ = get_major_from_version_string(version)
    print(
        crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
        .versions[0]
        .document.keys()
    )
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
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db=Depends(get_db),
    user=Depends(require_user),
):

    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    [version] = atbd.versions

    if version_input.contacts and len(version_input.contacts):
        for contact in version_input.contacts:
            db.add(
                AtbdVersionsContactsAssociation(
                    atbd_id=atbd.id,
                    major=version.major,
                    contact_id=contact.id,
                    roles=contact.roles,
                )
            )

    # # TODO: get this contact info into the PDF
    # # TODO: make this contact link info updateable (add/remove contact from version)
    # for c in version.contacts_link:
    #     print(c.contact_id)
    #     print(c.roles)

    if version_input.minor and version.status != "Published":
        raise HTTPException(
            status_code=400,
            detail="ATBD must have status `published` in order to increment the minor version number",
        )

    if version_input.minor == version.minor + 1:
        # A new version has been created - generate a cache a PDF for both the regular
        # PDF format, and the journal PDF format
        _add_pdf_generation_to_background_tasks(
            atbd=atbd, background_tasks=background_tasks
        )

    if version_input.document and not overwrite:
        version_input.document = {**version.document, **version_input.document.dict()}

    if version_input.sections_completed and not overwrite:
        version_input.sections_completed = {
            **version.sections_completed,
            **version_input.sections_completed,
        }

    version.last_updated_by = user["user"]
    version.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    crud_versions.update(db=db, db_obj=version, obj_in=version_input)

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.delete(
    "/atbds/{atbd_id}/versions/{version}",
    responses={204: dict(description="ATBD Version deleted")},
)
def delete_atbd_version(
    atbd_id: str, version: str, db=Depends(get_db), user=Depends(require_user),
):
    major, _ = get_major_from_version_string(version)
    [version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    if version.status == "Published":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an atbd version with status `Published`",
        )
    db.delete(version)
    db.commit()
    return {}


@router.post("/atbds/{atbd_id}/publish", response_model=atbds.FullOutput)
def publish_atbd(
    atbd_id: str,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    user=Depends(require_user),
):
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1)
    [latest_version] = atbd.versions
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
    # TODO: ATBD has been published, generate and cache v1.0 PDF

    _add_pdf_generation_to_background_tasks(
        atbd=atbd, background_tasks=background_tasks
    )

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=latest_version.major)


@router.get("/atbds/{atbd_id}/images/{image_key}")
def get_image(atbd_id: str, image_key: str, db: DbSession = Depends(get_db)):
    if not crud_atbds.exists(db=db, atbd_id=atbd_id):
        raise HTTPException(
            status_code=404, detail=f"ATBD {atbd_id} not found in database",
        )
    key = f"{atbd_id}/images/{image_key}"
    try:
        return responses.StreamingResponse(
            s3_client().get_object(Bucket=config.BUCKET, Key=key)["Body"]
        )
    except botocore.exceptions.ClientError as error:
        print(error.response["Error"])
        if error.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=404, detail=f"Image {key} not found in database",
            )


@router.post("/atbds/{atbd_id}/images/{image_key}")
def upload_iamge(
    atbd_id: str,
    image_key: str,
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):

    if not crud_atbds.exists(db=db, atbd_id=atbd_id):
        raise HTTPException(
            status_code=404, detail=f"ATBD {atbd_id} not found in database",
        )
    key = f"{atbd_id}/images/{image_key}"

    return s3_client().upload_fileobj(file.file, Bucket=config.BUCKET, Key=key)


def _add_pdf_generation_to_background_tasks(
    atbd: Atbds, background_tasks: BackgroundTasks
):

    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)

