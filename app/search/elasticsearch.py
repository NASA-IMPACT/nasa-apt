from app import config
from app.logs import logger
from app.crud.atbds import crud_atbds
from app.schemas.elasticsearch import ElasticsearchAtbdVersion
from app.schemas.versions import FullOutput as VersionFullOutput
from app.db.db_session import DbSession
import requests
from requests_aws4auth import AWS4Auth
import boto3

from typing import Optional, Dict
from fastapi import HTTPException, Depends
import jq

# import asyncpg
# import asyncio

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


# TODO: figure out how to get this working, or replace it
def prep_json(json: Dict) -> Dict:
    """
    Cleans up json document returned from the database to be added
    to Elasticsearch Index
    """

    query = """
    def atbddoc:
    del(._id)
    | del(..|.type?)
    | del(..|.object?)
    | del(.|..|.atbd_id?)
    | del(.|..|.major?)
    | del(.|..|.minor?)
    | del(.|..|.published_at?)
    | del(.|..|.created_at?)
    | del(.|..|.version?)
    | walk(
        if type=="object"
        then with_entries(
            select(
                .value != null and .value != "" and .value != [] and .value != {})
            )
        else . end
    )
    | .document
    | walk(
        if type=="object" and has("document")
        then ( .. | select(.text?) )
        else . end
    );

    . | {"index": {"_index": "atbd", "_type": "atbd", "_id": ._id}}, atbddoc
    """
    return jq.compile(query).input(text=json).text() + "\n"


def send_to_elastic(json: Dict):
    """
    POST json to elastic endpoint
    """
    json = prep_json(json).encode("utf-8")
    url = f"{config.ELASTICURL}/atbd/_bulk"
    auth = aws_auth()
    logger.info("sending %s %s using auth: %s", json, url, auth)
    response = requests.post(
        url, auth=auth, data=json, headers={"Content-Type": "application/json"}
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
    # This operation appends an ATBD title and alias to an ATBD Verions
    # such that the title and alias remain searchable but will always
    # return a single version as a unit of data
    for version in atbd.versions:
        es_atbd_params = dict(
            **version.__dict__,
            title=atbd.title,
            _id=f"{atbd_id}_v{version.major}.{version.major}",
        )

        if atbd.alias:
            es_atbd_params["alias"] = atbd.alias
        es_atbd_version = ElasticsearchAtbdVersion(**es_atbd_params).json(by_alias=True)

        # TODO: do something with the `result` object
        result = send_to_elastic(es_atbd_version)
    return
