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
    print("REQUEST: ", json)
    response = requests.post(
        url, auth=auth, data=json, headers={"Content-Type": "application/json"}
    )
    logger.info("%s %s %s", url, response.status_code, response.text)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()


# async def get_index(
#     connection: asyncpg.connection,
#     atbd_id: Optional[int] = None,
#     atbd_version: Optional[int] = None,
# ) -> Dict:
#     """
#     Get data for Index from PostgreSQL Database
#     """
#     where = ""
#     args = ()
#     if atbd_id is not None:
#         where = " WHERE atbd_id=$1"
#         args = (atbd_id,)
#         if atbd_version is not None:
#             where = f"{where} AND atbd_version=$2"
#             args = (
#                 atbd_id,
#                 atbd_version,
#             )
#     query = f"""
#     WITH t AS (
#     SELECT
#     v.atbd_id *10000 + v.atbd_version as _id,
#     atbds.title, atbds.alias,
#     v.*,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM atbd_contacts LEFT JOIN contacts
#         USING (id) WHERE atbd_id=atbds.id
#     ) as c ) as contacts,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM atbd_contact_groups LEFT JOIN contact_groups
#         USING (id) WHERE atbd_id=atbds.id
#     ) as c ) as contact_groups,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM atbd_contacts LEFT JOIN contacts
#         USING (id) WHERE atbd_id=atbds.id
#     ) as c ) as contacts,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM citations WHERE
#         atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as citations,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM algorithm_input_variables
#         WHERE atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as algorithm_input_variables,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM algorithm_output_variables
#         WHERE atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as algorithm_output_variables,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM publication_references
#         WHERE atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as publication_references,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM data_access_input_data
#         WHERE atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as data_access_input_data,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM data_access_output_data
#         WHERE atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as data_access_output_data,
#     (SELECT json_agg(c) FROM (
#         SELECT * FROM data_access_related_urls
#         WHERE atbd_id=atbds.id and atbd_version=v.atbd_version
#     ) as c ) as data_access_related_urls
#     FROM
#     atbds
#     JOIN atbd_versions v USING (atbd_id)
#     {where}
#     )
#     SELECT json_agg(json_strip_nulls(row_to_json(t))) FROM t;
#     """
#     return await connection.fetchval(query, *args)


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


# def index_atbd(
#     connection: asyncpg.connection = None,
#     pid: int = None,
#     channel: str = None,
#     payload: str = None,
# ):
#     """
#     Callback function to update index for an ATBD document
#     """

#     def callback(connection: asyncpg.connection, pid: int, channel: str, payload: str):
#         logger.info("Listen %s %s %s", pid, channel, payload)
#         asyncio.ensure_future(update_index(connection=connection, atbd_id=int(payload)))

#     return callback
