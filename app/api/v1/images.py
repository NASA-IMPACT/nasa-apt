"""Images endpoint."""
from app import config
from app.schemas import atbds, versions, contacts
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
from app.crud.contacts import crud_contacts_associations
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
            status_code=404,
            detail=f"ATBD {atbd_id} not found in database",
        )
    key = f"{atbd_id}/images/{image_key}"

    return s3_client().upload_fileobj(file.file, Bucket=config.BUCKET, Key=key)


@router.get("/atbds/{atbd_id}/images/{image_key}")
def get_image(atbd_id: str, image_key: str, db: DbSession = Depends(get_db)):
    if not crud_atbds.exists(db=db, atbd_id=atbd_id):
        raise HTTPException(
            status_code=404,
            detail=f"ATBD {atbd_id} not found in database",
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
                status_code=404,
                detail=f"Image {key} not found in database",
            )
