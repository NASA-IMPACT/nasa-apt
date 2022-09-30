"""opensearch Endpoint."""
import json
import os

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from app.config import OPENSEARCH_PORT, OPENSEARCH_URL
from app.logs import logger
from app.schemas.users import User
from app.users.auth import get_user

from fastapi import APIRouter, Depends

REGION = os.getenv("AWS_REGION", "us-west-2")

router = APIRouter()


def aws_auth():
    """Outputs an Opensearch service client. Low level client authorizes against the boto3 session and associated AWS credentials"""
    logger.info("Getting AWS Auth Credentials")
    credentials = boto3.Session(region_name=REGION).get_credentials()
    service = "es"
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        service,
        session_token=credentials.token,
    )
    opensearch_client = OpenSearch(
        hosts=[{"host": OPENSEARCH_URL, "port": OPENSEARCH_PORT}],
        http_auth=awsauth,
        use_ssl=False,
        verify_certs=False,
        connection_class=RequestsHttpConnection,
    )

    return opensearch_client


@router.post("/search")
def search_opensearch(query: dict, user: User = Depends(get_user)):
    """
    Receives the user input query from frontend search field
    Then uses client to search opensearch search endpoint
    """

    document = query

    opensearch_client = aws_auth()
    try:
        response = opensearch_client.search(body=document, index="atbd")
        # logger.info("status:%s opensearch_client:%s", opensearch_client.status_code, opensearch_client.text)
        # if not opensearch_client.ok:
        #     raise HTTPException(status_code=opensearch_client.status_code, detail=opensearch_client.text)
    except Exception as e:
        raise e

    else:
        # return value of 'object' is expected
        return dict(response)
