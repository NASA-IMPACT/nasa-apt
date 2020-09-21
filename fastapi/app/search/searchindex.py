import requests
from requests_aws4auth import AWS4Auth
import boto3
import sys
from os import environ
from typing import Optional, Dict
from fastapi import HTTPException
import jq
import asyncpg
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ELASTICURL: str = environ.get("ELASTICURL") or sys.exit(
    "ELASTICURL env var required"
)
logger.info('ELASTICURL %s', ELASTICURL)


def aws_auth():
    logger.info('Getting AWS Auth Credentials')
    region = 'us-east-1'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )
    logger.info('AWS Auth: %s', awsauth)
    return awsauth


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
    | del(.[]|..|.atbd_id?)
    | del(.[]|..|.atbd_version?)
    | walk(if type=="object" then
    with_entries(select(.value != null and .value != ""
    and .value != [] and .value != {})) else . end)
    | walk(if type=="object" and has("document")
    then {document:( .. | select(.text?) )} else . end);

    .[] | {"index": {"_index": "atbd", "_type": "atbd", "_id": ._id}}, atbddoc
    """
    return jq.compile(query).input(text=json).text() + "\n"


def send_to_elastic(json: Dict):
    """
    POST json to elastic endpoint
    """
    json = prep_json(json).encode("utf-8")
    url = f"{ELASTICURL}/atbd/_bulk"
    auth = aws_auth()
    logger.info("sending %s %s using auth: %s", json, url, auth)
    response = requests.post(
        url,
        auth=auth,
        data=json,
        headers={"Content-Type": "application/json"}
    )
    logger.info("%s %s %s", url, response.status_code, response.text)
    if not response.ok:
        raise HTTPException(
            status_code=response.status_code, detail=response.text
        )
    return response.json()


async def get_index(
    connection: asyncpg.connection,
    atbd_id: Optional[int] = None,
    atbd_version: Optional[int] = None,
) -> Dict:
    """
    Get data for Index from PostgreSQL Database
    """
    where = ""
    args = ()
    if atbd_id is not None:
        where = " WHERE atbd_id=$1"
        args = (atbd_id,)
        if atbd_version is not None:
            where = f"{where} AND atbd_version=$2"
            args = (
                atbd_id,
                atbd_version,
            )
    query = f"""
    WITH t AS (
    SELECT
    v.atbd_id *10000 + v.atbd_version as _id,
    atbds.title, atbds.alias,
    v.*,
    (SELECT json_agg(c) FROM (
        SELECT * FROM atbd_contacts LEFT JOIN contacts
        USING (contact_id) WHERE atbd_id=atbds.atbd_id
    ) as c ) as contacts,
    (SELECT json_agg(c) FROM (
        SELECT * FROM atbd_contact_groups LEFT JOIN contact_groups
        USING (contact_group_id) WHERE atbd_id=atbds.atbd_id
    ) as c ) as contact_groups,
    (SELECT json_agg(c) FROM (
        SELECT * FROM atbd_contacts LEFT JOIN contacts
        USING (contact_id) WHERE atbd_id=atbds.atbd_id
    ) as c ) as contacts,
    (SELECT json_agg(c) FROM (
        SELECT * FROM citations WHERE
        atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as citations,
    (SELECT json_agg(c) FROM (
        SELECT * FROM algorithm_input_variables
        WHERE atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as algorithm_input_variables,
    (SELECT json_agg(c) FROM (
        SELECT * FROM algorithm_output_variables
        WHERE atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as algorithm_output_variables,
    (SELECT json_agg(c) FROM (
        SELECT * FROM publication_references
        WHERE atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as publication_references,
    (SELECT json_agg(c) FROM (
        SELECT * FROM data_access_input_data
        WHERE atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as data_access_input_data,
    (SELECT json_agg(c) FROM (
        SELECT * FROM data_access_output_data
        WHERE atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as data_access_output_data,
    (SELECT json_agg(c) FROM (
        SELECT * FROM data_access_related_urls
        WHERE atbd_id=atbds.atbd_id and atbd_version=v.atbd_version
    ) as c ) as data_access_related_urls
    FROM
    atbds
    JOIN atbd_versions v USING (atbd_id)
    {where}
    )
    SELECT json_agg(json_strip_nulls(row_to_json(t))) FROM t;
    """
    return await connection.fetchval(query, *args)


async def update_index(
    connection: asyncpg.connection,
    atbd_id: Optional[int] = None,
    atbd_version: Optional[int] = None,
) -> Dict:
    """
    update data for Elastic from PostgreSQL Database
    """
    logger.info("Updating Index for %s %s", atbd_id, atbd_version)
    content = await get_index(connection, atbd_id, atbd_version)
    logger.info('dbcontent %s', content)
    results = send_to_elastic(content)
    return results


def index_atbd(
    connection: asyncpg.connection = None,
    pid: int = None,
    channel: str = None,
    payload: str = None,
):
    """
    Callback function to update index for an ATBD document
    """

    def callback(
        connection: asyncpg.connection, pid: int, channel: str, payload: str
    ):
        logger.info("Listen %s %s %s", pid, channel, payload)
        asyncio.ensure_future(
            update_index(connection=connection, atbd_id=int(payload))
        )

    return callback
