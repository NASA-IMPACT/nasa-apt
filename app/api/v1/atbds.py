"""ATBD's endpoint."""
from app import config
from app.schemas import atbds, versions
from app.db.db_session import DbSession
from app.api.utils import get_db, require_user, get_major_from_version_string, s3_client
from app.auth.saml import User
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.db.models import AtbdVersions
from sqlalchemy import exc
from fastapi import APIRouter, Depends, HTTPException, responses, File, UploadFile
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
    major = get_major_from_version_string(version)
    return crud_atbds.exists(db=db, atbd_id=atbd_id, version=major)


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
    major = get_major_from_version_string(version)
    # TODO: figure how to get the commented out method to work - as executing raw SQL directly
    # the API code is VERY ugly. This is only intended to be a temporary/stopgap solution
    # db.execute(
    #    f"DELETE FROM atbd_versions where atbd_versions.atbd_id={atbd_id} and atbd_versions.major={major}"
    # )
    # db.commit()
    [version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    db.delete(version)
    db.commit()
    return {}


@router.post(
    "/atbds/{atbd_id}/versions/{version}/document", response_model=atbds.FullOutput
)
def update_atbd_version_document(
    atbd_id: str,
    version: str,
    document_input: versions.JSONFieldUpdate,
    db=Depends(get_db),
    user=Depends(require_user),
):
    major = get_major_from_version_string(version)
    [version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    # https://docs.sqlalchemy.org/en/13/core/type_basics.html?highlight=json#sqlalchemy.types.JSON
    version.document[document_input.key] = document_input.value
    version.last_updated_by = user["user"]
    version.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(version)
    db.commit()
    db.refresh(version)
    print("VERSION after refresh:", version)

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.post(
    "/atbds/{atbd_id}/versions/{version}/sections_completed",
    response_model=atbds.FullOutput,
)
def update_atbd_version_sections_completed(
    atbd_id: str,
    version: str,
    document_input: versions.JSONFieldUpdate,
    db=Depends(get_db),
    user=Depends(require_user),
):
    major = get_major_from_version_string(version)
    [version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    version.last_updated_by = user["user"]
    version.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.add(version)
    version.sections_completed[document_input.key] = document_input.value
    db.add(version)
    db.commit()
    db.refresh(version)

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


# @router.get("/atbds/{atbd_id}/images/{image_key}")
# def get_image_presigned_url(
#     atbd_id: str, image_key: str, db: DbSession = Depends(get_db)
# ):
#     if not crud_atbds.exists(db=db, atbd_id=atbd_id):
#         raise HTTPException(
#             status_code=404, detail=f"ATBD {atbd_id} not found in database",
#         )
#         key = f"{atbd_id}/images/{image_key}"
#     try:
#         return responses.RedirectResponse(
#             s3_client().generate_presigned_url(
#                 ClientMethod="get_object",
#                 Params={"Bucket": config.BUCKET, "Key": image_key},
#                 ExpiresIn=60 * 60,
#             )
#         )
#     except botocore.exceptions.ClientError as error:
#         print(error.response["Error"])
#         if error.response["Error"]["Code"] == "NoSuchKey":
#             raise HTTPException(
#                 status_code=404, detail=f"Image {key} not found in database",
#             )


# # TODO: add response model
# # TODO: verify atbd exists
# @router.post("/atbds/{atbd_id}/images/{image_key}")
# def upload_image_presigned_url(
#     atbd_id: str,
#     image_key: str,
#     db: DbSession = Depends(get_db),
#     user: User = Depends(require_user),
# ):

#     if not crud_atbds.exists(db=db, atbd_id=atbd_id):
#         raise HTTPException(
#             status_code=404, detail=f"ATBD {atbd_id} not found in database",
#         )
#     key = f"{atbd_id}/images/{image_key}"
#     return s3_client().generate_presigned_post(
#         Bucket=config.BUCKET, Key=key, ExpiresIn=60 * 60
#     )
