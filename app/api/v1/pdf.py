from app.api.utils import get_major_from_version_string, get_db
from app.crud.atbds import crud_atbds
from fastapi import BackgroundTasks, APIRouter, Depends
from fastapi.responses import FileResponse
from tempfile import TemporaryDirectory
from typing import Type
from app.logs import logger
from app.pdf.generator import generate_pdf

router = APIRouter()


def cleanup_tmp_dir(tmp_dir: Type[TemporaryDirectory]):
    """
    Cleanup the temporary directory resource. This must wait until
    after the http response. Note: it might be cleaner to
    implement with fastapi's "dependencies with yield" feature,
    but background_tasks seems to work fine.

    https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/

    :param tmp_dir: temporary directory resource
    :type tmp_dir: TemporaryDirectory[str]
    """
    tmp_dir.cleanup()
    logger.info(f"cleaned up {tmp_dir.name}")


@router.get("/atbds/{atbd_id}/versions/{version}/pdf")
def get_pdf(
    atbd_id: str,
    version: str,
    journal: str = False,
    background_tasks: BackgroundTasks = None,
    db=Depends(get_db),
):

    major = get_major_from_version_string(version)

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)

    version_id = f"v{atbd.versions[0].major}-{atbd.versions[0].minor}"

    filename = (
        f"{atbd.alias}-{version_id}.pdf"
        if atbd.alias
        else f"atbd-{atbd.id}-{version_id}.pdf"
    )

    pdf_key = generate_pdf(atbd, journal=journal)

    return FileResponse(path=pdf_key, filename=filename)
