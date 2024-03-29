"""ATBDs endpoint."""
import base64
import datetime
import pickle
from copy import deepcopy
from pathlib import Path
from typing import List

from sqlalchemy import exc

from app import config
from app.api.utils import s3_client
from app.crud.atbds import crud_atbds
from app.crud.uploads import crud_uploads
from app.db.db_session import DbSession, get_db_session
from app.db.models import PDFUpload
from app.email.notifications import (
    UserNotification,
    notify_atbd_version_contributors,
    notify_users,
)
from app.logs import logger  # noqa
from app.permissions import check_atbd_permissions, filter_atbd_versions
from app.schemas import atbds, uploads, users
from app.search.opensearch import remove_atbd_from_index
from app.users.auth import get_user, require_user
from app.users.cognito import (
    get_active_user_principals,
    list_cognito_users,
    update_atbd_contributor_info,
)
from app.utils import get_task_queue

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
        filter_atbd_versions(principals, atbd, raise_exception=False)
        for atbd in crud_atbds.scan(db=db, role=role, status=status)
        if filter_atbd_versions(principals, atbd, raise_exception=False) is not None
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
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
    user: users.CognitoUser = Depends(require_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Creates a new ATBD. Requires a title, optionally takes an alias.
    Raises 400 if the user is not logged in."""

    check_atbd_permissions(principals=principals, action="create_atbd", atbd=None)
    atbd = crud_atbds.create(db, atbd_input, user.sub)
    atbd = update_atbd_contributor_info(principals, atbd)
    [version] = atbd.versions
    app_users, _ = list_cognito_users()
    user_notifications = [
        # For the owner
        UserNotification(
            **app_users[atbd.created_by].dict(by_alias=True),
            notification="new_atbd",
        ),
        # For all the curators
        *[
            UserNotification(
                **user.dict(by_alias=True),
                notification="new_atbd_for_curators",
            )
            for (user_sub, user) in app_users.items()
            if user_sub != atbd.created_by and "curator" in user.cognito_groups
        ],
    ]
    background_tasks.add_task(
        notify_users,
        user_notifications=user_notifications,
        atbd_version=f"v{version.major}.{version.minor}",
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        user=user,
    )
    return atbd


@router.post("/atbds/rebuild-index")
def rebuild_atbd_index(
    principals: List[str] = Depends(get_active_user_principals),
):
    """Rebuild ATBD index from scratch"""
    check_atbd_permissions(
        principals=principals, action="rebuild_atbd_index", atbd=None
    )
    task_queue = get_task_queue()
    task_queue.send_message(
        MessageBody=base64.b64encode(
            pickle.dumps(
                {
                    "task_type": "rebuild_atbd_index",
                    "payload": {},
                }
            )
        ).decode()
    )
    return dict()


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
    is not logged in. Re-indexes all corresponding items in opensearch
    with the new/updated values"""

    # Get latest version - ability to udpate an atbd is given
    # to whoever is allowed to update the latest version of that atbd
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    check_atbd_permissions(
        principals=principals, action="update", atbd=atbd, all_versions=False
    )

    if atbd.alias != atbd_input.alias and any(
        [v.status == "PUBLISHED" for v in atbd.versions]
    ):
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
    items in the opensearch index."""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    check_atbd_permissions(principals=principals, action="delete", atbd=atbd)

    atbd = crud_atbds.remove(db=db, atbd_id=atbd_id)

    [version] = atbd.versions
    background_tasks.add_task(
        notify_atbd_version_contributors,
        notification="delete_atbd",
        data=dict(
            notify=[
                version.owner,
                "curators",
            ],
        ),
        atbd_version=deepcopy(version),
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        user=user,
    )

    background_tasks.add_task(remove_atbd_from_index, atbd=atbd)
    # TODO: this should also remove all associated PDFs in S3.

    return {}


@router.post("/atbds/{atbd_id}/upload", response_model=uploads.CreateReponse)
def get_upload_url(
    atbd_id: int,
    db: DbSession = Depends(get_db_session),
    user: users.CognitoUser = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """Get a signed URL for uploading a PDF to S3 directory for a specific
    ATBD"""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    check_atbd_permissions(
        principals=principals, action="update", atbd=atbd, all_versions=False
    )
    pdf_upload = crud_uploads.create(
        db=db,
        obj_in=uploads.Create(
            atbd_id=atbd_id,
            created_by=user.sub,
        ),
    )
    client = s3_client()
    response = client.generate_presigned_post(
        Bucket=config.S3_BUCKET,
        Key=str(pdf_upload.file_path),
        ExpiresIn=3600,
    )
    presigned_url = response["url"]
    if config.APT_DEBUG:
        # localstack is available on localhost when running in dev mode
        presigned_url = presigned_url.replace("localstack", "localhost")
    logger.info(f"Generated presigned URL: {presigned_url}")
    return {
        "upload_url": presigned_url,
        "upload_fields": response["fields"],
        "upload_id": pdf_upload.id,
    }
