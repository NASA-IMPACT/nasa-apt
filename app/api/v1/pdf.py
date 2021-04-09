from app.api.utils import get_major_from_version_string, get_db, s3_client
from app.crud.atbds import crud_atbds
from app.db.models import Atbds
from app.pdf.generator import generate_pdf
from app.config import BUCKET
import os
from fastapi import BackgroundTasks, APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse
from tempfile import TemporaryDirectory
from typing import Type
from app.logs import logger

router = APIRouter()


# def cleanup_tmp_dir(tmp_dir: Type[TemporaryDirectory]):
#     """
#     Cleanup the temporary directory resource. This must wait until
#     after the http response. Note: it might be cleaner to
#     implement with fastapi's "dependencies with yield" feature,
#     but background_tasks seems to work fine.

#     https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/

#     :param tmp_dir: temporary directory resource
#     :type tmp_dir: TemporaryDirectory[str]
#     """
#     tmp_dir.cleanup()
#     logger.info(f"cleaned up {tmp_dir.name}")


def save_pdf_to_s3(atbd: Atbds, journal: bool = False):
    key = generate_pdf_key(atbd=atbd, journal=journal)
    local_pdf_key = generate_pdf(atbd=atbd, filepath=key, journal=journal)
    # print("UPLOADING FILE TO BUCKET: ", BUCKET)
    s3_client().upload_file(Filename=local_pdf_key, Bucket=BUCKET, Key=key)


def generate_pdf_key(atbd: Atbds, journal: bool = False):
    [version] = atbd.versions
    version_string = f"v{version.major}-{version.minor}"
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

    pdf_key = generate_pdf_key(atbd, journal)

    if minor:
        # TODO: add some error handling in case the PDF isn't found
        f = s3_client().get_object(Bucket=BUCKET, Key=pdf_key)["Body"]
        return StreamingResponse(
            f.iter_chunks(),
            media_type="application/pdf",
            filename=pdf_key.split("/")[-1],
        )

    local_pdf_filepath = generate_pdf(atbd=atbd, filepath=pdf_key, journal=journal)

    return FileResponse(path=local_pdf_filepath, filename=pdf_key.split("/")[-1])
