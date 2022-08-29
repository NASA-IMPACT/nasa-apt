"""Elasticsearch Endpoint."""

import boto3
import requests
from requests_aws4auth import AWS4Auth

from app.config import ELASTICSEARCH_URL
from app.logs import logger

# from app.auth.saml import User, get_user
from app.schemas.users import User
from app.users.auth import get_user

from fastapi import APIRouter, Depends, HTTPException

logger.info("ELASTICSEARCH_URL %s", ELASTICSEARCH_URL)

router = APIRouter()


def aws_auth():
    """Returns AWS credentials, to be used when signing requests against
    Elasticsearch. Credentials will be based off of the lambda's runtime
    IAM role.
    """
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


@router.post("/search")
def search_elastic(request: dict, user: User = Depends(get_user)):
    """
    Proxies POST json to elastic search endpoint
    """
    url = f"{ELASTICSEARCH_URL}/atbd/_search"

    logger.info("User %s", user)
    logger.info("data: %s", request)

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
