"""Keywords (GCMD KMS API passthrough) endpoint."""
from enum import Enum

import requests as re

from app.config import API_VERSION_STRING

from fastapi import APIRouter, Request, Response

router = APIRouter()

BASEURL = "https://gcmd.earthdata.nasa.gov/kms/"


class HTTPActions(str, Enum):
    """Enum for accepted HTTP Methods"""

    GET = "GET"
    PUT = "PUT"
    POST = "POST"
    DELETE = "DELETE"


@router.api_route(
    "/kms/concepts/concept_scheme/{scheme}/pattern/{pattern}",
    methods=HTTPActions,
    responses={200: dict(description="Successfull response from the GCMD KMS API")},
)
@router.api_route(
    "/kms/keyword/{uuid}",
    methods=HTTPActions,
    responses={200: dict(description="Successfull response from the GCMD KMS API")},
)
def gcmd_kms_passthrough(request: Request):
    """
    Send keywords query to GCMD API and return response directly
    """

    params = {**dict(request.query_params), "format": "json"}
    url = request.url.path.replace(f"{API_VERSION_STRING}/kms/", BASEURL)
    r = re.request(method=request.method, url=url, params=params,)
    return Response(content=r.content, status_code=r.status_code, headers=r.headers)
