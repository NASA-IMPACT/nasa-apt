"""Provides various utilities to the API classes
"""
import re
from typing import Tuple, Union

from boto3 import client

from app.config import AWS_RESOURCES_ENDPOINT

from fastapi import HTTPException


def ses_client() -> client:
    """
    Returns a boto3 ses client - configured to point at a specifc endpoint url if provided
    """
    if AWS_RESOURCES_ENDPOINT:
        return client("ses", endpoint_url=AWS_RESOURCES_ENDPOINT)

    return client("ses")


def cognito_client() -> client:
    """
    Returns a boto3 cognito client - configured to point at a specifc endpoint url if provided
    """
    if AWS_RESOURCES_ENDPOINT:
        return client("cognito-idp", endpoint_url=AWS_RESOURCES_ENDPOINT)

    return client("cognito-idp")


def s3_client() -> client:
    """
    Returns a boto3 s3 client - configured to point at a specfic endpoint url if provided
    """
    if AWS_RESOURCES_ENDPOINT:
        return client("s3", endpoint_url=AWS_RESOURCES_ENDPOINT)
    return client("s3")


def sqs_client() -> client:
    """
    Returns a boto3 sqs client - configured to point at a specfic endpoint url if provided
    """
    if AWS_RESOURCES_ENDPOINT:
        return client("sqs", endpoint_url=AWS_RESOURCES_ENDPOINT)
    return client("sqs")


def get_major_from_version_string(version: str) -> Tuple[int, Union[int, None]]:
    """
    Operations on versions can be performed using just the major version number:
    `/atbds/1/versions/2` or using the full semver number: `/atds/1/versions/v2.1`.
    This utility parses the given string and returns the major (and possibly minor)
    version number
    """

    if version == "latest":
        return -1, None

    try:
        return int(version), None

    except ValueError:

        search = re.search(r"^v(?P<major>\d+)\.(?P<minor>\d+)$", version)
        if not search:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Malformed version string: {version}. Expected format to be one of: "
                    f'v<major:int>.<minor:int>, <major:int>, or "latest"'
                ),
            )
        return int(search.group("major")), int(search.group("minor"))
