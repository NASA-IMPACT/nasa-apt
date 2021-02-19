from app import config
from app.main import logger
from app.auth.saml import User, require_user, get_user
from app.search.searchindex import update_index, aws_auth
from starlette.requests import Request
from fastapi import APIRouter, Depends, responses, HTTPException
import requests

router = APIRouter()


@router.get(config.root_path + "reindex",)
async def reindex(request: Request, user: User = Depends(require_user)):
    """
    Reindex all ATBD's into ElasticSearch
    """
    logger.info("Reindexing %s", config.ELASTICURL)
    results = await update_index(connection=request.app.state.connection)
    return responses.JSONResponse(content=results)


@router.post(config.root_path + "search",)
async def search_elastic(request: Request, user: User = Depends(get_user)):
    """
    Proxies POST json to elastic search endpoint
    """
    url = f"{config.ELASTICURL}/atbd/_search"
    data = await request.json()
    logger.info("User %s", user)
    logger.info("data: %s", data)

    if user is None:
        data["query"]["bool"]["filter"] = [{"match": {"status": "published"}}]
    logger.info("Searching %s %s", url, data)
    auth = aws_auth()
    response = requests.post(
        url, auth=auth, json=data, headers={"Content-Type": "application/json"},
    )
    logger.info("status:%s response:%s", response.status_code, response.text)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
