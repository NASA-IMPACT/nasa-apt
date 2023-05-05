"""Provide functionality for indexing and searching documents in OpenSearch"""
import datetime
import json
import os
from typing import Any, Dict, List

import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from opensearchpy.exceptions import NotFoundError
from requests_aws4auth import AWS4Auth
from sqlalchemy import orm

from app.config import OPENSEARCH_PORT, OPENSEARCH_URL
from app.db.db_session import DbSession
from app.db.models import Atbds, AtbdVersions
from app.logs import logger
from app.schemas.opensearch import OpensearchAtbd
from app.utils import run_once

from fastapi import HTTPException

logger.info("OPENSEARCH_URL %s", OPENSEARCH_URL)

REGION = os.getenv("AWS_REGION", "us-west-2")


@run_once
def create_search_indices(opensearch_client):
    """
    Create atbd index if it doesn't exists
    """
    if not opensearch_client.indices.exists("atbd"):
        logger.info("Creating index: atbd")
        opensearch_client.indices.create("atbd")


def get_opensearch_client():
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
    create_search_indices(opensearch_client)
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
        opensearch_client = get_opensearch_client()
        # bulk index
        response = opensearch_client.bulk(body=data_string, index="atbd")

    except Exception as e:
        raise e

    else:
        # return value of 'object' is expected
        return dict(response)


def remove_atbd_from_index(atbd: Atbds = None, version: AtbdVersions = None):
    """Deletes documents indexed in opensearch that correspond to
    either a single version or all versions belonging to an ATBD"""

    # init client
    opensearch_client = get_opensearch_client()

    if version:
        try:
            # directly delete the document
            # TODO Verify how to get correct atbd id
            response = opensearch_client.delete(
                index="atbd", id=f"{version.atbd_id}_v{version.major}"
            )
            return dict(response)
        except NotFoundError:
            return dict()

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
    except NotFoundError:
        pass
    return dict()


def generate_add_atbd_to_index_es_commands(atbd: Atbds):
    """Generate Indexes command for an ATBD in opensearch. If the ATBD metadata (title, alias) is
    to be updated, then the `atbd` input param will contain all associated versions,
    which will all be updated in the opensearch. If the ATBD version data (document,
    citation, etc) has been updated, then the `atbd` input param
    will only contain a single version, and only that version will be updated."""
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

    return es_commands


def add_atbd_to_index(atbd: Atbds):
    """Indexes single ATBD to opensearch."""
    return send_to_opensearch(generate_add_atbd_to_index_es_commands(atbd))


def add_atbds_to_index(atbds: List[Atbds]):
    """Indexes multiple ATBDs to opensearch."""
    es_commands = []
    for atbd in atbds:
        es_commands.extend(generate_add_atbd_to_index_es_commands(atbd))
    if es_commands:
        return send_to_opensearch(es_commands)


def rebuild_atbd_index():
    """Rebuild atbd index from scratch using published ATBDs"""
    db = DbSession()
    # Clean up everything
    opensearch_client = get_opensearch_client()
    opensearch_client.indices.delete("atbd")
    opensearch_client.indices.create("atbd")
    del opensearch_client
    # Index all published atbds in chunks
    limit = 100
    atbds_query = (
        db.query(Atbds)
        .filter(Atbds.versions.any(AtbdVersions.published_at != None))  # noqa:E711
        .join(AtbdVersions, Atbds.id == AtbdVersions.atbd_id)
        .options(orm.contains_eager(Atbds.versions))
        .limit(limit)
    )
    offset = 0
    while True:
        atbds = atbds_query.offset(offset).all()
        if not atbds:
            break
        add_atbds_to_index(atbds)
        offset += limit
