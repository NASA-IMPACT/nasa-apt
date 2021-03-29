import requests
import sys
from os import environ
from typing import Optional, Dict
from fastapi import HTTPException
from ..saml import SamlAuth, User
from jose import jwt
from datetime import datetime, timedelta

secret: str = environ.get("JWT_SECRET") or exit("JWT_SECRET ENV var required")
token_life: int = 3600

rest_api_endpoint: str = environ.get("REST_API_ENDPOINT") or sys.exit(
    "REST_API_ENDPOINT env var required"
)


def create_token_data(user: User):
    exp = datetime.utcnow() + timedelta(seconds=token_life)
    data = {
        "userdata": user,
        "exp": exp,
        "role": "app_user",
    }
    return data


def create_token(user: User):
    return jwt.encode(create_token_data(user=user), secret)


def get_atbd(
    atbd_id: Optional[int] = None,
    alias: Optional[str] = None,
    user: Optional[User] = None,
) -> Dict:
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
    
    request_params = {"url": url}
    if user:
        request_params["headers"] = {"Authorization": f"Bearer {create_token(user)}"}
    

    response = requests.get(**request_params)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    records = response.json()

    if not len(records):
        raise HTTPException(status_code=404, detail="not found")

    [atbd_metadata] = records
    atbd_id = atbd_metadata["atbd_id"]
    print("ATBD Metdata: ", atbd_metadata)
    [version] = atbd_metadata["atbd_versions"]
    version_id: int = version["atbd_version"]

    # fetch the atbd doc using the atbd_id and version_id
    url: str = f"{rest_api_endpoint}/atbd_versions?atbd_id=eq.{atbd_id}&atbd_version=eq.{version_id}&select=*,atbd(*),algorithm_input_variables(*),algorithm_output_variables(*),algorithm_implementations(*),publication_references(*),data_access_input_data(*),data_access_output_data(*),data_access_related_urls(*),citations(*)"
    request_params = {"url": url}
    if user:
        request_params["headers"] = {"Authorization": f"Bearer {create_token(user)}"}

    response = requests.get(**request_params)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    records = response.json()
    if not len(records):
        raise HTTPException(status_code=404, detail="not found")
    [atbd_content] = records

    # combine the two results to make json style atbd doc (here just emulating what the nasa-apt-frontend does)
    return {**atbd_content, "atbd": atbd_metadata}
