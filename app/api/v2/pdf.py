"""PDF Endpoint."""
import os

from app import config
from app.api.utils import get_major_from_version_string, s3_client
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession, get_db_session
from app.db.models import Atbds, AtbdVersions
from app.pdf.error_handler import generate_html_content_for_error
from app.pdf.generator import generate_pdf

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse

router = APIRouter()


def save_pdf_to_s3(atbd: Atbds, journal: bool = False):
    """
    Uploads a generated PDF from local execution environment to S3
    """
    try:
        key = generate_pdf_key(atbd=atbd, journal=journal)
        local_pdf_key = generate_pdf(atbd=atbd, filepath=key, journal=journal)
        s3_client().upload_file(
            Filename=local_pdf_key, Bucket=config.S3_BUCKET, Key=key
        )
    except Exception as e:
        print(f"PDF generation ({'journal' if journal else 'regular'}) failed with: ")
        print(e)


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

    filename = f"{filename}.pdf"

    return os.path.join(str(atbd.id), "pdf", filename)


@router.get("/atbds/{atbd_id}/versions/{version}/pdf")
def get_pdf(
    atbd_id: str,
    version: str,
    journal: bool = False,
    background_tasks: BackgroundTasks = None,
    db: DbSession = Depends(get_db_session),
):
    """
    Returns a PDF to the user - either as a stream of Bytes from S3 or as a
    FileResponse object, from a PDF generated and stored locally in the
    Lambda's runtime memory.

    The PDF will be served from S3 if either the user specifies a minor version
    number or if the lastest version has status `Published`
    """

    major, minor = get_major_from_version_string(version)

    atbd: Atbds = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)

    # Unpacking the versions list into an array of a single element
    # enforces the assumption that the ATBD will only contain a single
    # version if a version.major value was supplied to the the
    # crud_atbds.get() method
    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions

    pdf_key = generate_pdf_key(atbd, minor=minor, journal=journal)

    if minor or atbd_version.status == "Published":
        print("FETCHING FROM S3: ", pdf_key)

        # TODO: add some error handling in case the PDF isn't found
        f = s3_client().get_object(Bucket=config.S3_BUCKET, Key=pdf_key)["Body"]
        return StreamingResponse(
            f.iter_chunks(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={pdf_key.split('/')[-1]}"
            },
        )
    print("GENERATING PDF")
    try:
        local_pdf_filepath = generate_pdf(atbd=atbd, filepath=pdf_key, journal=journal)
    except Exception as e:
        raise e
        atbd_link = f"{config.FRONTEND_URL.strip('/')}/documents/{atbd.alias if atbd.alias else atbd.id}/v{major}.{minor}"

        return HTMLResponse(
            content=generate_html_content_for_error(
                error=e,
                return_link=atbd_link,
                atbd_id=atbd.id,
                atbd_title=atbd.title,
                atbd_version=f"v{atbd_version.major}.{atbd_version.minor}",
                pdf_type="Journal" if journal else "Regular",
            )
        )

    return FileResponse(path=local_pdf_filepath, filename=pdf_key.split("/")[-1])
