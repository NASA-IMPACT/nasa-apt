"""Provides functionality for validating user tokens from Cognito"""
import json
import time
import urllib
from typing import Dict, Union

from jose import jwk, jwt
from jose.utils import base64url_decode

from app import config

from fastapi import HTTPException, Request


def get_user(request: Request) -> Union[Dict, bool]:
    """
    Validates JWT Token (Authorization Bearer: ...) against cognito,
    returns a dict representing user info from Cognito.
    To be used as a dependency injection in API routes.
    """
    token = request.headers.get("Authorization", None)

    if not token:
        return False

    if not token.startswith("Bearer "):
        raise HTTPException("Expected a Bearer token")

    token = token.replace("Bearer ", "")

    return validate_token(token)


def validate_token(token: str) -> Dict:
    """
    Does the ground work of unpacking the token, decrypting it using
    cognito's public key, and returning the claims contained within
    """
    print("TOKEN: ", token)

    with urllib.request.urlopen(config.COGNITO_KEYS_URL) as f:  # type: ignore
        response = f.read()

    keys = json.loads(response.decode("utf-8"))["keys"]

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
