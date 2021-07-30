"""Provides functionality for validating user tokens from Cognito"""
import time
from typing import Dict, Union

import requests
from jose import jwk, jwt
from jose.utils import base64url_decode

from app import config

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer

# In some cases (images and PDFs) the JWT token
# is passed as a query parameter (as opposed to an Authorization header).
# This is not necessarily "best practice" (https://stackoverflow.com/questions/32722952/is-it-safe-to-put-a-jwt-into-the-url-as-a-query-parameter-of-a-get-request)
# TODO: review wether or not there is another, better way to do this

token_scheme = HTTPBearer()


def get_user(request: Request, token=Depends(token_scheme)) -> Union[Dict, bool]:
    """
    Validates JWT Token (Header: "Authorization Bearer: ... ") against cognito,
    returns a dict representing user info from Cognito. If no `Authorization`
    Header was submitted, it will search for the token in the query params
    To be used as a dependency injection in API routes.
    """

    if not token:
        token = request.query_params.get("token")
    else:
        token = token.credentials

    if not token:
        return False
    print(token)
    return validate_token(token)


def validate_token(token: str) -> Dict:
    """
    Does the ground work of unpacking the token, decrypting it using
    cognito's public key, and returning the claims contained within
    """

    keys = requests.get(config.COGNITO_KEYS_URL).json()["keys"]

    headers = jwt.get_unverified_headers(token)

    [kid] = [k for k in keys if k["kid"] == headers["kid"]]

    public_key = jwk.construct(kid)

    message, encoded_signature = str(token).rsplit(".", 1)

    decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))

    if not public_key.verify(message.encode("utf-8"), decoded_signature):
        raise HTTPException(status_code=400, detail="Signature validation failed")

    claims = jwt.get_unverified_claims(token)

    if time.time() > claims["exp"]:
        raise HTTPException(status_code=400, detail="Token is expired")

    if claims.get("aud") and claims["aud"] != config.APP_CLIENT_ID:
        raise HTTPException(
            status_code=400, detail="Token was not issued for this app client"
        )

    return claims
