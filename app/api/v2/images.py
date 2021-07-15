"""Images endpoint."""


import botocore

from app import config
from app.api.utils import get_db, require_user, s3_client
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession

# from app.auth.saml import User
from app.schemas.users import User

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, responses

router = APIRouter()


@router.post("/atbds/{atbd_id}/images/{image_key}")
def upload_image(
    atbd_id: str,
    image_key: str,
    file: UploadFile = File(...),
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    """Saves an image to S3 under a folder prefix corresponding to
    an ATBD id. Raises a 404 exception if the ATBD doesn't exist"""

    if not crud_atbds.exists(db=db, atbd_id=atbd_id):
        raise HTTPException(
            status_code=404, detail=f"ATBD {atbd_id} not found in database",
        )
    key = f"{atbd_id}/images/{image_key}"

    return s3_client().upload_fileobj(file.file, Bucket=config.S3_BUCKET, Key=key)


@router.get("/atbds/{atbd_id}/images/{image_key}")
def get_image(atbd_id: str, image_key: str, db: DbSession = Depends(get_db)):
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
                status_code=404, detail=f"Image {key} not found in database",
            )
