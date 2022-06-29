"""Images endpoint."""


from typing import List

import botocore

from app import config
from app.api.utils import s3_client
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession, get_db_session
from app.permissions import filter_atbd_versions
from app.schemas.users import User
from app.users.auth import require_user
from app.users.cognito import get_active_user_principals

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, responses

router = APIRouter()


@router.post("/atbds/{atbd_id}/images/{image_key}")
def upload_image(
    atbd_id: str,
    image_key: str,
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db_session),
    user: User = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Saves an image to S3 under a folder prefix corresponding to
    an ATBD id. Raises a 404 exception if the ATBD doesn't exist"""

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    atbd = filter_atbd_versions(principals, atbd)

    key = f"{atbd_id}/images/{image_key}"

    return s3_client().upload_fileobj(file.file, Bucket=config.S3_BUCKET, Key=key)


@router.get("/atbds/{atbd_id}/images/{image_key}")
def get_image(
    atbd_id: str,
    image_key: str,
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Returns an image belonging to an ATBD. Raises an exception if the image
    is not included in any ATBD Versions with status `Published` AND the user
    is not logged in.
    """

    key = f"{atbd_id}/images/{image_key}"
    try:
        return responses.StreamingResponse(
            s3_client().get_object(Bucket=config.S3_BUCKET, Key=key)["Body"]
        )
    except botocore.exceptions.ClientError as error:
        print(error.response["Error"])
        if error.response["Error"]["Code"] == "NoSuchKey":
            raise HTTPException(
                status_code=404,
                detail=f"Image {key} not found in database",
            )
