from os import environ
from sys import exit
from tempfile import TemporaryDirectory
from typing import Union, Dict, Type

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.logger import logger
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .atbd.checksum_atbd import checksum_atbd
from .atbd.get_atbd import get_atbd
from .atbd.get_status import get_status
from .atbd.Status import Status
from .cache import Cache, CacheException
from .latex.json_to_latex import json_to_latex, JsonToLatexException
from .pdf.latex_to_pdf import latex_to_pdf, LatexToPDFException
from .search.searchindex import update_index, index_atbd, ELASTICURL

import asyncpg
import requests
import logging


logger.setLevel(logging.DEBUG)

root_path: str = environ.get("API_PREFIX", "/")
rest_api_endpoint: str = environ.get("REST_API_ENDPOINT") or exit(
    "REST_API_ENDPOINT env var required"
)
s3_endpoint: str = environ.get("S3_ENDPOINT") or exit(
    "S3_ENDPOINT env var required"
)
pdfs_bucket_name: str = environ.get("PDFS_S3_BUCKET") or exit(
    "PDFS_S3_BUCKET env var required"
)
figures_bucket_name: str = environ.get("FIGURES_S3_BUCKET") or exit(
    "FIGURES_S3_BUCKET env var required"
)
DBURL: str = environ.get("DBURL") or exit("DBURL env var required")

app: FastAPI = FastAPI()
cache: Cache = Cache(s3_endpoint=s3_endpoint, bucket_name=pdfs_bucket_name)


origins = [
    "http://localhost:3000",
    "http://localhost:3006",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.on_event("startup")
async def startup() -> None:
    """
    Create database connection when FastAPI App has started.
    Add listener to atbd channel on database connection.
    """
    app.state.connection = await asyncpg.connect(
        DBURL, server_settings={"search_path": "apt,public"}
    )
    await app.state.connection.add_listener("atbd", index_atbd())


@app.on_event("shutdown")
async def shutdown() -> None:
    # await app.state.connection.remove_listener('atbd', index_atbd)
    await app.state.connection.close()


def get_cache_key(atbd_doc: Dict) -> str:
    """
    Helper function to construct a cache keys from
    the checksum and the alias of the atbd doc.
    :param atbd_doc: json atbd doc
    :type atbd_doc: dict
    :return: cache key in the format {hex_digest}/{alias}.pdf'
    :rtype: str
    """
    hex_digest: str = checksum_atbd(atbd_doc)
    alias: str = atbd_doc["atbd"]["alias"]
    return (
        f"{hex_digest}/{alias}.pdf" if alias else f"{hex_digest}/nasa-atbd.pdf"
    )


def atbd_pdf_handler(
    atbd_doc: Dict, background_tasks: BackgroundTasks
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
    status: Status = get_status(atbd_doc)
    cache_key: str = get_cache_key(atbd_doc)
    if status == Status.Published.name:
        # check cache: published atbds may be cached in s3
        try:
            cache_url = cache.get_file_url(key=cache_key)
            if cache_url is not None:
                return RedirectResponse(url=cache_url)
        except CacheException as e:
            # log and continue with pdf serialization workflow
            logger.error(e)
    tmp_dir_resource: TemporaryDirectory[str] = TemporaryDirectory(
        prefix="nasa-apt-pdf-service-"
    )
    tmp_dir: str = tmp_dir_resource.name
    background_tasks.add_task(cleanup_tmp_dir, tmp_dir_resource)
    try:
        (latex_filename, _) = json_to_latex(atbd_doc=atbd_doc, tmp_dir=tmp_dir)
    except JsonToLatexException as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    try:
        tmp_pdf_filename: str = latex_to_pdf(
            latex_filename=latex_filename, tmp_dir=tmp_dir
        )
        if status == Status.Published.name:
            try:
                cache_url = cache.put_file(
                    key=cache_key, filename=tmp_pdf_filename
                )
                return RedirectResponse(url=cache_url)
            except CacheException as e:
                logger.error(str(e))
        alias: str = atbd_doc["atbd"]["alias"]
        filename = f"{alias}.pdf" if alias else "nasa-atbd.pdf"
        return FileResponse(path=tmp_pdf_filename, filename=filename)
    except LatexToPDFException as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get(root_path + "atbds/id/{atbd_id}.pdf")
def get_atbd_by_id(atbd_id: int, background_tasks: BackgroundTasks):
    atbd_doc = get_atbd(atbd_id=atbd_id)
    return atbd_pdf_handler(atbd_doc, background_tasks=background_tasks)


@app.get(root_path + "atbds/alias/{alias}.pdf")
def get_atbd_pdf_by_alias(alias: str, background_tasks: BackgroundTasks):
    atbd_doc = get_atbd(alias=alias)
    return atbd_pdf_handler(atbd_doc, background_tasks=background_tasks)


@app.get(root_path)
def health_check():
    """
    The root_path is only used by the ELB healthcheck.
    """
    return "ok"


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


@app.get("/reindex",)
async def reindex(request: Request):
    """
    Reindex all ATBD's into ElasticSearch
    """
    results = await update_index(connection=request.app.state.connection)
    return JSONResponse(content=results)


@app.post("/search",)
async def search_elastic(request: Request):
    """
    Proxies POST json to elastic search endpoint
    """
    url = f"{ELASTICURL}/atbd/_search"
    data = await request.body()
    response = requests.post(url, data=data, headers=request.headers)
    logger.debug(response.status_code, response.text)
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code, detail=response.text
        )
    return response.json()
