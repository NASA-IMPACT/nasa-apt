import requests
import sys
from os import environ
from typing import Optional, Dict
from fastapi import HTTPException

rest_api_endpoint: str = environ.get("REST_API_ENDPOINT") or sys.exit(
    "REST_API_ENDPOINT env var required"
)


def get_atbd(atbd_id: Optional[int] = None, alias: Optional[str] = None) -> Dict:
    """
    Query postgrest api for an atbd document by an id or an alias.

    :param atbd_id: database id
    :type atbd_id: Optional[int]
    :param alias: atbd alias (slug)
    :type alias: Optional[str]
    :return: atbd doc
    :rtype: dict (from json)
    :raises HTTPException: if the api request fails
    """

    if alias:
        from_column = "alias"
        q = alias
    else:
        from_column = "atbd_id"
        q = atbd_id

    url: str = (
        f"{rest_api_endpoint}/atbds?{from_column}=eq.{q}&select=*,contacts(*),contact_groups(*),atbd_versions(atbd_id,atbd_version,status)&limit=1"
        if alias
        else f"{rest_api_endpoint}/atbds?atbd_id=eq.{atbd_id}&select=*,contacts(*),contact_groups(*),atbd_versions(atbd_id,atbd_version,status)&limit=1"
    )
    response = requests.get(url)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    records = response.json()

    if not len(records):
        raise HTTPException(status_code=404, detail="not found")

    [atbd_metadata] = records
    atbd_id = atbd_metadata["atbd_id"]
    [version] = atbd_metadata["atbd_versions"]
    version_id: int = version["atbd_version"]

    # fetch the atbd doc using the atbd_id and version_id
    url: str = f"{rest_api_endpoint}/atbd_versions?atbd_id=eq.{atbd_id}&atbd_version=eq.{version_id}&select=*,atbd(*),algorithm_input_variables(*),algorithm_output_variables(*),algorithm_implementations(*),publication_references(*),data_access_input_data(*),data_access_output_data(*),data_access_related_urls(*),citations(*)"
    response = requests.get(url)
    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    records = response.json()
    if not len(records):
        raise HTTPException(status_code=404, detail="not found")
    [atbd_content] = records

    # combine the two results to make json style atbd doc (here just emulating what the nasa-apt-frontend does)
    return {**atbd_content, "atbd": atbd_metadata}
