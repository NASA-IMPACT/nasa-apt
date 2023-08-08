"""PDF Endpoint."""
import base64
import hashlib
import json
import os
import pickle
from typing import List

from app import config
from app.api.utils import get_major_from_version_string, s3_client
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession, get_db_session
from app.db.models import Atbds, AtbdVersions
from app.logs import logger
from app.permissions import filter_atbd_versions
from app.schemas import users, versions
from app.schemas.atbds import AtbdDocumentTypeEnum
from app.users.auth import get_user
from app.users.cognito import get_active_user_principals, update_atbd_contributor_info
from app.utils import get_task_queue

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

router = APIRouter()


# TODO: will this break if the ATBD is created without an alias and then
# an alias is added later?
def generate_pdf_key(atbd: Atbds, minor: int = None, journal: bool = False):
    """
    Generates a key for the PDF, using the ATBD alias, if present, and the
    ATBD ID, if not
    """
    [version] = atbd.versions

    version_string = f"v{version.major}-{minor if minor is not None else version.minor}"
    filename = (
        f"{atbd.alias}-{version_string}"
        if atbd.alias
        else f"atbd-{atbd.id}-{version_string}"
    )
    if journal:
        filename = f"{filename}-journal"

    # Generate a hash of the title, version and content of the ATBD to make
    # sure that the filename is unique for each version of the ATBD.
    version_json = versions.FullOutput.from_orm(version).json()
    version_data = {
        "atbd_id": atbd.id,
        "title": atbd.title,
        "version": version_json,
    }
    version_hash = hashlib.md5(json.dumps(version_data).encode("utf-8")).hexdigest()

    filename = f"{filename}-{version_hash}.pdf"

    return os.path.join(str(atbd.id), "pdf", filename)


def generate_presigned_url(key: str, file_name: str, content_type: str):
    """
    Generates a presigned URL for the PDF in S3
    """
    logger.debug(f"Generating presigned URL for key: {key}, filename: {file_name}")
    url = s3_client().generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": config.S3_BUCKET,
            "Key": key,
            "ResponseContentDisposition": f"attachment; filename={file_name}",
            "ResponseContentType": content_type,
        },
        ExpiresIn=3600,
    )
    # hack to fix the issue with the presigned url not working in the browser
    # on the development environment
    # In the development environment, the localstack container is used to
    # emulate S3. The presigned URL generated by localstack is not valid
    # in the browser because it uses the localstack container's internal
    # hostname. The following line replaces the hostname with localhost
    # so that the URL is valid in the browser.
    if config.APT_DEBUG:
        url = url.replace("http://localstack", "http://localhost")
    logger.debug(f"Generated presigned URL: {url}")
    return url


@router.get("/atbds/{atbd_id}/versions/{version}/pdf")
def get_pdf(
    atbd_id: str,
    version: str,
    journal: bool = False,
    retry: bool = False,
    db: DbSession = Depends(get_db_session),
    principals: List[str] = Depends(get_active_user_principals),
    user: users.CognitoUser = Depends(get_user),
    request: Request = None,
):
    """
    Returns a PDF to the user - either as a stream of Bytes from S3 or as a
    FileResponse object, from a PDF generated and stored locally in the
    Lambda's runtime memory.

    Returns a JSON response with code 404 if the ATBD is not found or if the user
    does not have permission to view the ATBD.

    Returns a JSON response with code 404 if the PDF is not found in S3.

    Return a JSON response with code 200 if PDF generation is successfully requested.
    When requesting PDF generation, the request must contain the following headers:
    - `authorization`: the user's Cognito ID token as a Bearer token
    - `x-access-token`: the user's Cognito access token


    The PDF will be served from S3 if either the user specifies a minor version
    number or if the lastest version has status `Published` or if it was already
    generated and stored in S3 (eg: when retry=True).
    """

    major, minor = get_major_from_version_string(version)

    atbd: Atbds = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    atbd = filter_atbd_versions(principals, atbd)
    if atbd is None:
        return JSONResponse(status_code=404, content={"message": "ATBD not found"})
    atbd = update_atbd_contributor_info(principals, atbd)

    # Unpacking the versions list into an array of a single element
    # enforces the assumption that the ATBD will only contain a single
    # version if a version.major value was supplied to the the
    # crud_atbds.get() method
    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions

    if atbd.document_type == AtbdDocumentTypeEnum.PDF:
        pdf_key = atbd_version.pdf.file_path
    else:
        pdf_key = generate_pdf_key(atbd, minor=minor, journal=journal)

    logger.info(f"FETCHING FROM S3: {pdf_key}")
    try:
        # Check if PDF already exists in S3
        client = s3_client()
        client.get_object(Bucket=config.S3_BUCKET, Key=pdf_key)
        pdf_url = generate_presigned_url(
            key=pdf_key,
            file_name=pdf_key.split("/")[-1],
            content_type="application/pdf",
        )
        return JSONResponse(status_code=200, content={"pdf_url": pdf_url})
    except client.exceptions.NoSuchKey:
        if retry:
            # retry is used by the frontend to request a recently generated PDF
            # If the PDF is not found in S3, that means the PDF generation task
            # has not yet completed. In this case, we return a 404 response to
            # the frontend, which will then poll the API until the PDF is found
            logger.info(f"PDF not found in S3: {pdf_key}")
            return JSONResponse(status_code=404, content={"message": "PDF not found"})
        else:
            # Generate the PDF locally and upload it to S3
            logger.info(f"GENERATING PDF: {pdf_key}")
            try:
                # clean up any existing PDFs for this ATBD version
                s3_client().delete_object(Bucket=config.S3_BUCKET, Key=pdf_key)
                # Queue the PDF generation task into SQS
                # We only use this to generate "Document" PDFs, not "Journal" PDFs for now
                if user:
                    id_token = request.headers.get("authorization", "").replace(
                        "Bearer ", ""
                    )
                    access_token = request.headers.get("x-access-token", "")
                    if not id_token or not access_token:
                        return JSONResponse(
                            status_code=400,
                            content={
                                "message": "Missing authorization headers. "
                                "Please include the 'authorization' and 'x-access-token' headers in your request."
                            },
                        )

                    auth_data = {
                        "id_token": id_token,
                        "access_token": access_token,
                        "user_email": user.email,
                    }
                else:
                    auth_data = {}

                task_queue = get_task_queue()
                task_queue.send_message(
                    MessageBody=base64.b64encode(
                        pickle.dumps(
                            {
                                "task_type": "make_pdf",
                                "payload": {
                                    "atbd_id": atbd.id,
                                    "filepath": pdf_key,
                                    "major": major,
                                    "minor": minor,
                                    "auth_data": auth_data,
                                    "atbd_alias": atbd.alias,
                                    "journal": journal,
                                },
                            }
                        )
                    ).decode()
                )
                return JSONResponse(
                    status_code=201,
                    content={"message": "PDF generation in progress"},
                )
            except Exception as e:
                logger.exception("Error occurred while generating PDF")
                return JSONResponse(
                    status_code=500,
                    content={"message": f"Error occurred while generating PDF: {e}"},
                )
    except Exception:
        logger.exception("Could not generate PDF")
        return JSONResponse(
            status_code=500, content={"message": "Could not generate PDF"}
        )
