import json
from app import config
from app.logs import logger
from app.crud.atbds import crud_atbds
from app.schemas.elasticsearch import ElasticsearchAtbd
from app.db.models import Atbds, AtbdVersions
from app.db.db_session import DbSession
import requests
from requests_aws4auth import AWS4Auth
import boto3

from typing import Dict, List
from fastapi import HTTPException


logger.info("ELASTICSEARCH_URL %s", config.ELASTICSEARCH_URL)


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


def send_to_elastic(data: List[Dict]):
    """
    POST json to elastic endpoint
    """
    # bulk commands must end with newline
    data = "\n".join(data) + "\n"

    url = f"http://{config.ELASTICSEARCH_URL}/atbd/_bulk"

    auth = aws_auth()
    logger.info("sending %s %s using auth: %s", json, url, auth)
    response = requests.post(
        url,
        auth=auth,
        data=data.encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    logger.info("%s %s %s", url, response.status_code, response.text)
    if not response.ok:
        logger.error(response.content)
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


# TODO: re-implement this method

# async def update_index(
#     connection: asyncpg.connection,
#     atbd_id: Optional[int] = None,
#     atbd_version: Optional[int] = None,
# ) -> Dict:
#     """
#     update data for Elastic from PostgreSQL Database
#     """
#     logger.info("Updating Index for %s %s", atbd_id, atbd_version)
#     content = await get_index(connection, atbd_id, atbd_version)
#     logger.info("dbcontent %s", content)
#     results = send_to_elastic(content)
#     return results


def remove_atbd_from_index(atbd: Atbds = None, version: AtbdVersions = None):

    if version:
        return send_to_elastic(
            [
                json.dumps(
                    {
                        "delete": {
                            "_index": "atbd",
                            "_id": f"{version.atbd_id}_v{version.major}",
                        }
                    }
                )
            ]
        )
    if not atbd:
        raise HTTPException(
            status_code=500,
            detail="Unable to delete ATBD/ATBDVersion from ElasticSearch",
        )
    return send_to_elastic(
        [
            json.dumps(
                {"delete": {"_index": "atbd", "_id": f"{atbd.id}_v{version.major}"}}
            )
            for version in atbd.versions
        ]
    )


def add_atbd_to_index(atbd: Atbds):
    # If the atbd itself (title, alias, etc) has been updated
    # then all of the versions will be re-index, otherwise
    # if only one version was updated the `atbd.versions` object
    # will only contain 1 version, which should be updated
    es_commands = []
    for version in atbd.versions:

        atbd.version = version

        es_commands.append(
            json.dumps(
                {
                    "index": {
                        "_index": "atbd",
                        "_type": "atbd",
                        "_id": f"{atbd.id}_v{version.major}",
                    }
                }
            )
        )
        es_commands.append(
            ElasticsearchAtbd.from_orm(atbd).json(
                by_alias=True,
                exclude_none=True,
            )
        )

    return send_to_elastic(es_commands)
