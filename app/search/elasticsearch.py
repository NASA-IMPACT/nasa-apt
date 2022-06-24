"""Provide functionality for indexing and searching documents in ElasticSearch"""
import datetime
import json
from typing import Any, Dict, List

import boto3
import os
import requests
from requests_aws4auth import AWS4Auth

from app import config
from app.db.models import Atbds, AtbdVersions
from app.logs import logger
from app.schemas.elasticsearch import ElasticsearchAtbd

from fastapi import HTTPException

logger.info("ELASTICSEARCH_URL %s", config.ELASTICSEARCH_URL)

REGION = os.getenv("AWS_REGION", "us-west-2")

def aws_auth():
    """Provides an AWS4AUth object in ordere to authenticate against the
    ElasticSearch instance"""
    logger.info("Getting AWS Auth Credentials")
    credentials = boto3.Session(region_name=REGION).get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        "es",
        session_token=credentials.token,
    )
    logger.info("AWS Auth: %s", awsauth)
    return awsauth


def _default(i: Any):
    if isinstance(i, (datetime.date, datetime.datetime)):
        return i.isoformat()
    return str(i)


def send_to_elastic(data: List[Dict]):
    """
    POST json to elastic endpoint.
    TODO: update this to use the `elasticsearch-py` python client
    """
    # bulk commands must end with newline
    data_string = "\n".join(json.dumps(d, default=_default) for d in data) + "\n"
    url = f"http://{config.ELASTICSEARCH_URL}/atbd/_bulk"

    auth = aws_auth()
    print("SENDING DATA: ", data_string)
    print("TO URL : ", url)
    print("WITH AUTH: ", auth)

    logger.info("sending %s %s using auth: %s", data_string, url, auth)
    response = requests.post(
        url,
        auth=auth,
        data=data_string.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    logger.info("%s %s %s", url, response.status_code, response.text)
    if not response.ok:
        logger.error(response.content)
        raise HTTPException(status_code=response.status_code, detail=response.text)
    print("RESPONSE: ", response.content)
    return response.json()


def remove_atbd_from_index(atbd: Atbds = None, version: AtbdVersions = None):
    """Deletes documents indexed in ElasticSearch that correspond to
    either a single version or all versions belonging to an ATBD"""

    if version:
        return send_to_elastic(
            [
                {
                    "delete": {
                        "_index": "atbd",
                        "_id": f"{version.atbd_id}_v{version.major}",
                    }
                }
            ]
        )
    if not atbd:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete ATBD/ATBDVersion from ElasticSearch",
        )
    return send_to_elastic(
        [
            {"delete": {"_index": "atbd", "_id": f"{atbd.id}_v{version.major}"}}
            for version in atbd.versions
        ]
    )


def add_atbd_to_index(atbd: Atbds):
    """Indexes an ATBD in ElasticSearch. If the ATBD metadata (title, alias) is
    to be updated, then the `atbd` input param will contain all associated versions,
    wich will all be updated in the ElasticSearch. If the ATBD version data (document,
    citation, etc) has been updated, then the `atbd` input param
    will only contain a single version, and only that version will be updated."""

    es_commands = []
    for version in atbd.versions:

        atbd.version = version

        es_commands.append(
            {
                "index": {
                    "_index": "atbd",
                    "_type": "atbd",
                    "_id": f"{atbd.id}_v{version.major}",
                }
            }
        )
        es_commands.append(
            ElasticsearchAtbd.from_orm(atbd).dict(by_alias=True, exclude_none=True)
        )

    return send_to_elastic(es_commands)
