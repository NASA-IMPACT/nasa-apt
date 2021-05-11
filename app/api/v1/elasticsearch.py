from app import config

from app.logs import logger
from app.auth.saml import get_user, User
import requests
from requests_aws4auth import AWS4Auth
import boto3
from fastapi import HTTPException, Depends, APIRouter


logger.info("ELASTICSEARCH_URL %s", config.ELASTICSEARCH_URL)

router = APIRouter()


def aws_auth():
    logger.info("Getting AWS Auth Credentials")
    region = "us-east-1"
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        "es",
        session_token=credentials.token,
    )
    logger.info("AWS Auth: %s", awsauth)
    return awsauth


# TODO: re-implemnt
# @router.get(root_path + "reindex")
# def reindex(request: Request, user: User = Depends(require_user)):
#     """
#     Reindex all ATBD's into ElasticSearch
#     """
#     logger.info("Reindexing %s", config.ELASTICSEARCH_URL)
#     results = await update_index(connection=request.app.state.connection)
#     return JSONResponse(content=results)


@router.post("/search")
def search_elastic(request: dict, user: User = Depends(get_user)):
    """
    Proxies POST json to elastic search endpoint
    """
    url = f"{config.ELASTICSEARCH_URL}/atbd/_search"

    logger.info("User %s", user)
    logger.info("data: %s", request)

    if user is None:
        request["query"]["bool"]["filter"] = [{"match": {"status": "Published"}}]

    logger.info("Searching %s %s", url, request)
    auth = aws_auth()
    response = requests.post(
        f"http://{url}",
        auth=auth,
        json=request,
        headers={"Content-Type": "application/json"},
    )
    logger.info("status:%s response:%s", response.status_code, response.text)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
