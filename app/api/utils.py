"""
Provides various utilities to the API classes
"""
import functools
import re
from typing import List, Tuple, Union
from uuid import uuid4

from boto3 import client

from app import config
from app.auth.cognito import get_user
from app.config import AWS_RESOURCES_ENDPOINT
from app.db.models import Atbds, AtbdVersions, Threads
from app.permissions import check_permissions
from app.schemas.users import User
from app.schemas.versions import (
    AnonymousReviewerUser,
    AnonymousUser,
    CognitoUser,
    ReviewerUser,
)

import fastapi_permissions as permissions
from fastapi import Depends, HTTPException


def get_active_user_principals(user: User = Depends(get_user)) -> List[str]:
    """Returns the principals for a user, to be used when validating permissions
    to perform certain actions or requests"""

    principals = [permissions.Everyone]
    if user:
        principals.extend([permissions.Authenticated, f"user:{user.sub}"])
        principals.extend([f"role:{groupname}" for groupname in user.cognito_groups])

    return principals


def update_thread_contributor_info(
    principals: List[str], atbd_version: AtbdVersions, thread: Threads
) -> Threads:
    app_users, _ = list_cognito_users()
    version_acl = atbd_version.__acl__()
    reviewers = [r["sub"] for r in atbd_version.reviewers]

    for comment in thread.comments:
        anon_count = 0
        if comment.created_by == atbd_version.owner:
            if check_permissions(
                principals=principals, action="view_owner", acl=version_acl, error=False
            ):
                comment.created_by = app_users[comment.created_by]

            else:
                comment.created_by = AnonymousUser(preferred_username="Owner")

        elif comment.created_by in atbd_version.authors:
            if check_permissions(
                principals=principals,
                action="view_authors",
                acl=version_acl,
                error=False,
            ):
                comment.created_by = app_users[comment.created_by]
            else:
                comment.created_by = AnonymousUser(
                    preferred_username=f"Author {atbd_version.authors.index(comment.created_by)}"
                )

        elif comment.created_by in reviewers:
            if check_permissions(
                principals=principals,
                action="view_reviewers",
                acl=version_acl,
                error=False,
            ):
                comment.created_by = app_users[comment.created_by]
            else:
                comment.created_by = AnonymousUser(
                    preferred_username=f"Reviewer {reviewers.index(comment.created_by)}"
                )
        else:
            anon_count += 1
            comment.created_by = AnonymousUser(
                preferred_username=f"Anonymous User {anon_count}"
            )
    return thread


def update_atbd_contributor_info(principals: List[str], atbd: Atbds) -> Atbds:
    """
    Insert contributor (owner, author and reviewer) user info from
    Cognito into an ATBD Version. Identifying user information is
    obfuscated in accordance with the principals of the user (eg:
    unauthenticated users cannot see ANY identifying info, authors
    and Owners cannot see identifying info of reviewers, but can
    see identifying info of other authors)
    """
    app_users, request_id = list_cognito_users()
    print("REQUEST ID: ", request_id)

    for version in atbd.versions:
        version_acl = version.__acl__()

        if check_permissions(
            principals=principals, action="view_owner", acl=version_acl, error=False
        ):
            version.owner = app_users[version.owner].dict(by_alias=True)

        else:
            version.owner = AnonymousUser(preferred_username="Owner")

        if check_permissions(
            principals=principals, action="view_authors", acl=version_acl, error=False
        ):

            version.authors = [
                app_users[author].dict(by_alias=True) for author in version.authors
            ]
        else:
            version.authors = [
                AnonymousUser(preferred_username=f"Author {str(i+1)}")
                for i, _ in enumerate(version.authors)
            ]

        if check_permissions(
            principals=principals, action="view_reviewers", acl=version_acl, error=False
        ):

            version.reviewers = [
                ReviewerUser(
                    **app_users[reviewer["sub"]].dict(by_alias=True),
                    review_status=reviewer["review_status"],
                )
                for reviewer in version.reviewers
            ]
        else:
            version.reviewers = [
                AnonymousReviewerUser(
                    preferred_username=f"Reviewer {str(i+1)}",
                    review_status=v["review_status"],
                )
                for i, v in enumerate(version.reviewers)
            ]
    return atbd


@functools.lru_cache(maxsize=1)
def list_cognito_users():
    """
    Returns a list of ALL cognito users, to be filtered against the
    users of a document (authors, reviewers, owner)
    """
    # We need the cognito groups in the user info returned, in order to
    # verify certain operations (eg: users can only be added as co-authors
    # if they are part of the contributor user group, not the curator).
    # The `list_users` operation does not return the groups the user belongs
    # to, so instead we are listing the users in each group and adding
    # the group manually to returned data. It's not pretty. I know.
    app_users = {}
    client = cognito_client()
    for group in ["curator", "contributor"]:

        paginator = client.get_paginator("list_users_in_group")
        response = paginator.paginate(UserPoolId=config.USER_POOL_ID, GroupName=group)

        for page in response:
            app_users.update(
                {
                    user["Username"]: CognitoUser(**{**user, "cognito:groups": [group]})
                    for user in page.get("Users", [])
                }
            )

        # params = di
        # users = []

        # users.extend(
        #     {**user, "cognito:groups": [group]} for user in response.get("Users", [])
        # )
        # while response.get("PaginationToken"):
        #     params["PaginationToken"] = response["PaginationToken"]
        #     response = client.list_users_in_group(**params)
        #     users.extend(
        #         {**user, "cognito:groups": [group]}
        #         for user in response.get("Users", [])
        #     )

        # for user in users:
        #     for attribute in user["Attributes"]:
        #         if attribute["Name"] not in [
        #             "email",
        #             "sub",
        #             "preferred_username",
        #             "username",
        #         ]:
        #             continue
        #         user[attribute["Name"]] = attribute["Value"]
        #     # TODO: figure out a better way to do this
        #     user["username"] = user["Username"]
        #     del user["Username"]

        #     del user["Attributes"]
        # app_users.extend(users)
    # print("APP USERS: ", app_users)
    return (app_users, str(uuid4()))


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


def require_user(user: User = Depends(get_user)) -> User:

    """
    Raises an exception if not user user token is supplied

    TODO: remove this method in favor of the `require_user` already present in `auth/saml`
    """
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User must be authenticated to perform this operation",
        )
    return user


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
