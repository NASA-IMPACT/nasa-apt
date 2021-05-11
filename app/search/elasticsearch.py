import json
from app import config
from app.logs import logger
from app.crud.atbds import crud_atbds
from app.schemas.elasticsearch import ElasticsearchAtbd
from app.db.db_session import DbSession
import requests
from requests_aws4auth import AWS4Auth
import boto3

from typing import Dict
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


def send_to_elastic(data: str):
    """
    POST json to elastic endpoint
    """

    url = f"http://{config.ELASTICSEARCH_URL}/atbd/_bulk"

    auth = aws_auth()
    logger.info("sending %s %s using auth: %s", json, url, auth)
    response = requests.post(
        url,
        auth=auth,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    logger.info("%s %s %s", url, response.status_code, response.text)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


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


def index_atbd(atbd_id: str, db: DbSession):
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)

    # If the atbd itself (title, alias, etc) has been updated
    # then all of the versions will be re-index, otherwise
    # if only one version was updated the `atbd.versions` object
    # will only contain 1 version, which should be updated
    for version in atbd.versions:

        atbd.version = version
        es_atbd_version = ElasticsearchAtbd.from_orm(atbd).json(
            by_alias=True,
            exclude_none=True,
        )

        index_command = json.dumps(
            {
                "index": {
                    "_index": "atbd",
                    "_type": "atbd",
                    "_id": f"{atbd.id}_v{version.major}",
                }
            }
        )
        print("DATA TO INDEX: ", es_atbd_version)
        send_to_elastic(f"{index_command}\n{es_atbd_version}\n".encode("utf-8"))
    return
