from app.api.utils import get_major_from_version_string, get_db, s3_client
from app.crud.atbds import crud_atbds
from app.db.models import Atbds, AtbdVersionsContactsAssociation, Contacts, AtbdVersions
from app.pdf.generator import generate_pdf
from app.config import BUCKET
import os
from fastapi import BackgroundTasks, APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse


router = APIRouter()


def save_pdf_to_s3(atbd: Atbds, journal: bool = False):
    key = generate_pdf_key(atbd=atbd, journal=journal)
    local_pdf_key = generate_pdf(atbd=atbd, filepath=key, journal=journal)
    s3_client().upload_file(Filename=local_pdf_key, Bucket=BUCKET, Key=key)


def generate_pdf_key(atbd: Atbds, minor: int = None, journal: bool = False):
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
    journal: str = False,
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db),
):

    major, minor = get_major_from_version_string(version)

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    [version] = atbd.versions
    pdf_key = generate_pdf_key(atbd, minor=minor, journal=journal)

    if minor or version.status == "Published":
        print("FETCHING FROM S3: ", pdf_key)
        # TODO: pdf_key contains the lastest minor version - which gets set
        # as the filename, even though a different minor version was requested
        # TODO: add some error handling in case the PDF isn't found
        f = s3_client().get_object(Bucket=BUCKET, Key=pdf_key)["Body"]
        return StreamingResponse(
            f.iter_chunks(),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={pdf_key.split('/')[-1]}"
            },
        )
    print("GENERATING PDF")
    local_pdf_filepath = generate_pdf(atbd=atbd, filepath=pdf_key, journal=journal)

    return FileResponse(path=local_pdf_filepath, filename=pdf_key.split("/")[-1])
