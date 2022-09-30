"""Provide functionality for indexing and searching documents in OpenSearch"""
import datetime
import json
import os
from typing import Any, Dict, List

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

from app.config import OPENSEARCH_URL, OPENSEARCH_PORT
from app.db.models import Atbds, AtbdVersions
from app.logs import logger
from app.schemas.opensearch import OpensearchAtbd

from fastapi import HTTPException

logger.info("OPENSEARCH_URL %s", OPENSEARCH_URL)

REGION = os.getenv("AWS_REGION", "us-west-2")


def aws_auth():
    """
    Outputs an Opensearch service client. Low level client authorizes against the boto3 session and associated AWS credentials
    host is hardcoded as to reference the container within the same network
    """
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
    logger.info("AWS Auth: %s", awsauth)
    return opensearch_client


def _default(i: Any):
    if isinstance(i, (datetime.date, datetime.datetime)):
        return i.isoformat()
    return str(i)


def send_to_opensearch(data: List[Dict]):
    """
    Receives the data for bulk indexing
    Then uses client to bulk index documents to open search
    """
    # bulk commands must end with newline
    data_string = "\n".join(json.dumps(d, default=_default) for d in data) + "\n"

    try:
        # init client
        opensearch_client = aws_auth()
        print("SENDING DATA: ", data_string)

        logger.info("sending %s", data_string)

        # bulk index
        response = opensearch_client.bulk(body=data_string, index="atbd")

        logger.info(f"bulk indexing {data_string}")

    except Exception as e:
        raise e

    else:
        print("RESPONSE: ", response)
        # return value of 'object' is expected
        return dict(response)


def remove_atbd_from_index(atbd: Atbds = None, version: AtbdVersions = None):
    """Deletes documents indexed in opensearch that correspond to
    either a single version or all versions belonging to an ATBD"""

    # init client
    opensearch_client = aws_auth()

    if version:

        try:
            # directly delete the document
            # TODO Verify how to get correct atbd id
            response = opensearch_client.delete(
                index="atbd", id=f"{version.atbd_id}_v{version.major}"
            )

        except Exception as e:
            raise e

        else:
            return dict(response)

    if not atbd:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete ATBD/ATBDVersion from opensearch",
        )

    try:
        for version in atbd.versions:
            # TODO use Opensearch DSL query lang to cover expected documents

            response = opensearch_client.delete(
                index="atbd", id=f"{atbd.id}_v{version.major}"
            )
    except Exception as e:
        raise e

    else:
        # return value of 'object' is expected
        return dict(response)


def add_atbd_to_index(atbd: Atbds):
    """Indexes an ATBD in opensearch. If the ATBD metadata (title, alias) is
    to be updated, then the `atbd` input param will contain all associated versions,
    wich will all be updated in the opensearch. If the ATBD version data (document,
    citation, etc) has been updated, then the `atbd` input param
    will only contain a single version, and only that version will be updated."""
    # TODO, remove comment
    print("################ \n")
    print("ADD ATBD TO INDEX CALLED")
    print("################ \n")
    es_commands = []
    for version in atbd.versions:

        atbd.version = version

        es_commands.append(
            {
                "index": {
                    "_index": "atbd",
                    # "_type": "atbd", specifying types in bulk requests is deprecated in >ES7
                    "_id": f"{atbd.id}_v{version.major}",
                }
            }
        )
        es_commands.append(
            OpensearchAtbd.from_orm(atbd).dict(by_alias=True, exclude_none=True)
        )

    return send_to_opensearch(es_commands)
