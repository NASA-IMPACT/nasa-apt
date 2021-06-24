"""ATBDs endpoint."""
import datetime
from typing import List, Dict

from sqlalchemy import exc

from app.api.utils import get_db, require_user
from app.api.v2.pdf import save_pdf_to_s3
from app.auth.saml import User
from app.crud.atbds import crud_atbds
from app.db.db_session import DbSession
from app.schemas import atbds
from app.search.elasticsearch import add_atbd_to_index, remove_atbd_from_index

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


@router.get(
    "/atbds",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=List[atbds.SummaryOutput],
)
def list_atbds(db: DbSession = Depends(get_db)):
    """Lists all ATBDs with summary version info (only versions with status
    `Published` will be displayed if the user is not logged in)"""
    return crud_atbds.scan(db=db)


@router.head(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def atbd_exists(atbd_id: str, db: DbSession = Depends(get_db)):
    """Returns status 200 if ATBD exsits and raises 404 if not (or if the user is
    not logged in and the ATBD has no versions with status `Published`)"""
    return crud_atbds.exists(db=db, atbd_id=atbd_id)


@router.get(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.SummaryOutput,
)
def get_atbd(atbd_id: str, db: DbSession = Depends(get_db)):
    """Returns a single ATBD (raises 404 if the ATBD has no versions with
    status `Published` and the user is not logged in)"""
    return crud_atbds.get(db=db, atbd_id=atbd_id)


@router.post(
    "/atbds",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def create_atbd(
    atbd_input: atbds.Create,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    """Creates a new ATBD. Requires a title, optionally takes an alias.
    Raises 400 if the user is not logged in."""
    output = crud_atbds.create(db, atbd_input, user["user"])
    return output


@router.post(
    "/atbds/{atbd_id}",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def update_atbd(
    atbd_id: str,
    atbd_input: atbds.Update,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    """Updates an ATBD (eiither Title or Alias). Raises 400 if the user
    is not logged in. Re-indexes all corresponding items in Elasticsearch
    with the new/updated values"""
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id)
    atbd.last_updated_by = user["user"]
    atbd.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    try:
        atbd = crud_atbds.update(db=db, db_obj=atbd, obj_in=atbd_input)
    except exc.IntegrityError:
        if atbd_input.alias:
            raise HTTPException(
                status_code=401,
                detail=f"Alias {atbd_input.alias} already exists in database",
            )

    background_tasks.add_task(add_atbd_to_index, atbd)
    return atbd


@router.post("/atbds/{atbd_id}/publish", response_model=atbds.FullOutput)
def publish_atbd(
    atbd_id: str,
    publish_input: atbds.PublishInput,
    background_tasks: BackgroundTasks,
    db=Depends(get_db),
    user=Depends(require_user),
):
    """Publishes an ATBD. Raises 400 if the `latest` version does NOT have
    status `Published` or if the user is not logged in.

    Adds PDF generation (and serialization to S3) to background tasks.
    """
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1)
    [latest_version] = atbd.versions
    if latest_version.status == "Published":
        raise HTTPException(
            status_code=400,
            detail=f"Latest version of atbd {atbd_id} already has status: `Published`",
        )
    now = datetime.datetime.now(datetime.timezone.utc)
    latest_version.status = "Published"
    latest_version.published_by = user["user"]
    latest_version.published_at = now

    # Publishing a version counts as updating it, so we
    # update the timestamp and user
    latest_version.last_updated_by = user["user"]
    latest_version.last_updated_at = now

    if publish_input.changelog is not None and publish_input.changelog != "":
        latest_version.changelog = publish_input.changelog

    db.commit()
    db.refresh(latest_version)

    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
    background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=latest_version.major)


@router.delete("/atbds/{atbd_id}", responses={204: dict(description="ATBD deleted")})
def delete_atbd(
    atbd_id: str,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    """Deletes an ATBD (and all child versions). Removes all associated
    items in the Elasticsearch index."""
    atbd = crud_atbds.remove(db=db, atbd_id=atbd_id)

    background_tasks.add_task(remove_atbd_from_index, atbd=atbd)

    return {}


import os
import urllib
import json
from jose import jwk, jwt
from jose.utils import base64url_decode
import time
import boto3


@router.post(
    "/auth-test", responses={200: dict(description="Auth token successfully read")}
)
def validate_token(token_input: Dict[str, str]):
    token = token_input["token"]
    user_pool_id = os.environ["USER_POOL_ID"]
    app_client_id = os.environ["APP_CLIENT_ID"]
    region = "us-east-1"

    print("USER POOL ID: ", user_pool_id)
    print("REGION: ", region)

    keys_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"

    with urllib.request.urlopen(keys_url) as f:
        response = f.read()
    keys = json.loads(response.decode("utf-8"))["keys"]

    headers = jwt.get_unverified_headers(token)

    kids = [k for k in keys if k["kid"] == headers["kid"]]

    if len(kids) < 1:
        raise HTTPException(status_code=500, detail="Public key not found in jwks.json")

    if len(kids) > 1:
        raise HTTPException(status_code=500, detail="Multiple keys found in jwks.json")

    kid = kids[0]

    public_key = jwk.construct(kid)

    message, encoded_signature = str(token).rsplit(".", 1)

    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise HTTPException(status_code=400, detail="Signature validation failed")

    claims = jwt.get_unverified_claims(token)

    if time.time() > claims["exp"]:
        raise HTTPException(status_code=400, detail="Token is expired")

    if claims.get("aud") and claims["aud"] != app_client_id:
        raise HTTPException(
            status_code=400, detail="Token was not issued for this app client"
        )

    if not token_input.get("username"):
        return claims

    email_to_query = token_input["username"]
    cognito_client = boto3.client("cognito-idp")
    userinfo = cognito_client.admin_get_user(
        UserPoolId=user_pool_id, Username=email_to_query
    )
    claims["queried_user"] = userinfo

    return claims
