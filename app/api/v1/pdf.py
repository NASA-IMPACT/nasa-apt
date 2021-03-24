from app.pdf.json_to_latex import json_to_latex, JsonToLatexException
from app.pdf.latex_to_pdf import latex_to_pdf, LatexToPDFException
from app.api.utils import get_major_from_version_string, get_db
from app.schemas import atbds
from app.crud.atbds import crud_atbds
from fastapi import HTTPException, BackgroundTasks, APIRouter, Depends
from fastapi.responses import FileResponse, RedirectResponse
from tempfile import TemporaryDirectory
from typing import Type, Dict, Union
from app.logs import logger

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


def atbd_pdf_handler(
    atbd_doc: Dict, background_tasks: BackgroundTasks, journal=False
) -> Type[Union[Type[RedirectResponse], Type[FileResponse]]]:
    """
    For Published atbd: Issues redirect response upon cache hit,
    or streams file response for cache failure.
    (Should always return a PDF unless the serialization pipeline has failed)
    For Draft atbd: stream file response and does not cache.

    :param atbd_doc: json
    :type atbd_doc: dict
    :param background_tasks: background tasks callback
    s:type background_tasks: BackgroundTasks
    :return: fastapi response
    :rtype: RedirectResponse|FileResponse|HTTPException
    :raises HTTPException:
    """
    # status: Status = get_status(atbd_doc)
    # cache_key: str = get_cache_key(atbd_doc, journal=journal)
    # if status == Status.Published.name:
    #     # check cache: published atbds may be cached in s3
    #     try:
    #         cache_url = cache.get_file_url(key=cache_key)
    #         if cache_url is not None:
    #             return RedirectResponse(url=cache_url)
    #     except CacheException as e:
    #         # log and continue with pdf serialization workflow
    #         logger.error(e)
    tmp_dir_resource: TemporaryDirectory[str] = TemporaryDirectory(
        prefix="nasa-apt-pdf-service-"
    )
    tmp_dir: str = tmp_dir_resource.name
    background_tasks.add_task(cleanup_tmp_dir, tmp_dir_resource)
    for k, v in atbd_doc["versions"][0]["document"].items():
        atbd_doc[k] = v
    del atbd_doc["versions"]
    try:
        (latex_filename, _) = json_to_latex(
            atbd_doc=atbd_doc, tmp_dir=tmp_dir, journal=journal
        )

    except JsonToLatexException as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    try:
        tmp_pdf_filename: str = latex_to_pdf(
            latex_filename=latex_filename, tmp_dir=tmp_dir
        )
        # if status == Status.Published.name:
        #     try:
        #         cache_url = cache.put_file(key=cache_key, filename=tmp_pdf_filename)
        #         return RedirectResponse(url=cache_url)
        #     except CacheException as e:
        #         logger.error(str(e))
        alias: str = atbd_doc.get("alias")
        filename = f"{alias}.pdf" if alias else "nasa-atbd.pdf"
        print("Done generating PDF. Path: ", tmp_pdf_filename)
        print("Filename: ", filename)
        return FileResponse(path=tmp_pdf_filename, filename=filename)
    except LatexToPDFException as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/atbds/{atbd_id}/versions/{version}/pdf")
def generate_pdf(
    atbd_id: str,
    version: str,
    background_tasks: BackgroundTasks,
    journal: str = False,
    db=Depends(get_db),
):

    major = get_major_from_version_string(version)
    atbd_version = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    atbd_version = atbds.FullOutput.from_orm(atbd_version).dict()
    return atbd_pdf_handler(
        atbd_version, background_tasks=background_tasks, journal=journal
    )
