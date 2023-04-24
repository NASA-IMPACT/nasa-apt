"""opensearch Endpoint."""
import json
import os

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from app.config import OPENSEARCH_PORT, OPENSEARCH_URL
from app.logs import logger
from app.schemas.users import User
from app.search.opensearch import aws_auth
from app.users.auth import get_user

from fastapi import APIRouter, Depends

REGION = os.getenv("AWS_REGION", "us-west-2")

router = APIRouter()


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
