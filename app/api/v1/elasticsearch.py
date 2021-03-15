from app import config
from app.main import app, logger
from app.db.models import AtbdVersions, Atbds
from app.db.db_session import DbSession
from app.auth.saml import get_user, User
import requests
from requests_aws4auth import AWS4Auth
import boto3
import sys
from os import environ
from typing import Optional, Dict
from fastapi import HTTPException, Depends
import jq


from sqlalchemy import event

logger.info("ELASTICURL %s", config.ELASTICURL)


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
# @app.get(root_path + "reindex")
# def reindex(request: Request, user: User = Depends(require_user)):
#     """
#     Reindex all ATBD's into ElasticSearch
#     """
#     logger.info("Reindexing %s", config.ELASTICURL)
#     results = await update_index(connection=request.app.state.connection)
#     return JSONResponse(content=results)


@app.post("/search")
def search_elastic(request: dict, user: User = Depends(get_user)):
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

