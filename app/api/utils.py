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
from app.db.models import Atbds, AtbdVersions, Comments, Threads
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


def update_user_info(
    principals: List[str],
    atbd_version: AtbdVersions,
    data_model: Union[Comments, Threads, AtbdVersions],
):
    app_users, _ = list_cognito_users()

    version_acl = atbd_version.__acl__()

    contributors = {
        "owner": [atbd_version.owner],
        "authors": atbd_version.authors,
        "reviewers": [r["sub"] for r in atbd_version.reviewers],
    }
    for attr in ["created_by", "last_updated_by", "published_by"]:
        try:
            user_sub = getattr(data_model, attr)
        # published_by field is only relevant to AtbdVersions, not
        # Atbds, Threads or Comments. In those cases, if the published_by
        # attribute is not present, skip it.
        except AttributeError:
            continue

        # The `published_by` field IS present but it's value
        # is none because the document hasn't been published yet.
        # Skip.
        if user_sub is None:
            continue

        if not any([user_sub in i for i in contributors.values()]):

            if "curator" in app_users[user_sub].cognito_groups:
                setattr(data_model, attr, app_users[user_sub].dict(by_alias=True))
            else:
                setattr(
                    data_model,
                    attr,
                    AnonymousUser(preferred_username="Unknown User").dict(
                        by_alias=True
                    ),
                )
                continue
        for contributor_type, contributor_subs in contributors.items():
            if user_sub in contributor_subs:
                if check_permissions(
                    principals=principals,
                    action=f"view_{contributor_type}",
                    acl=version_acl,
                    error=False,
                ):
                    setattr(data_model, attr, app_users[user_sub].dict(by_alias=True))
                else:
                    preferred_username = contributor_type.title()
                    if contributor_type != "owner":
                        preferred_username += f" {contributor_subs.index(user_sub)}"

                    setattr(
                        data_model,
                        attr,
                        AnonymousUser(preferred_username=preferred_username).dict(
                            by_alias=True
                        ),
                    )
    return data_model


def update_thread_contributor_info(
    principals: List[str], atbd_version: AtbdVersions, thread: Threads
) -> Threads:

    for comment in thread.comments:
        update_user_info(
            principals=principals, atbd_version=atbd_version, data_model=comment
        )

    thread = update_user_info(
        principals=principals, atbd_version=atbd_version, data_model=thread
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

    for version in atbd.versions:
        version_acl = version.__acl__()

        # Update `created_by` and `last_updated_by` fields
        version = update_user_info(
            principals=principals, atbd_version=version, data_model=version
        )

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
                ).dict(by_alias=True)
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
