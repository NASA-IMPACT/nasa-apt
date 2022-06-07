"""Module with functionality related to querying cognito users, and merging
(sometime anonymously) user info with Atbds, AtbdVersions, Threads and Comments
as needed"""
import functools
from typing import List, Union
from uuid import uuid4

from app import config
from app.api.utils import cognito_client
from app.db.models import Atbds, AtbdVersions, Comments, Threads
from app.email import notifications
from app.permissions import check_permissions
from app.schemas import users, versions
from app.users.auth import get_user

import fastapi_permissions as permissions
from fastapi import BackgroundTasks, Depends


def get_active_user_principals(user: users.User = Depends(get_user)) -> List[str]:
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
    """
    Replaces the `created_by`, `last_updated_by` and `published_by` fields found in
    several of the application's data models with a cognito user, appropriately anonymized
    based on the wether or not the user is the owner, an author or a reviewer of the
    document.
    """
    app_users, _ = list_cognito_users()

    version_acl = atbd_version.__acl__()

    contributors = {
        "owner": [atbd_version.owner],
        "authors": atbd_version.authors,
        "reviewers": [r["sub"] for r in atbd_version.reviewers],
        "curators": [
            u.sub for u in app_users.values() if "curator" in u.cognito_groups
        ],
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

        # This means the user sub for one of the `created_by`, `last_updated_by` or `published_by`
        # fields is not found within the `owner`, `authors`, `reviewers` lists. This can happen if
        # a curator removes an author from an ATBD version, for example.
        if not any([user_sub in i for i in contributors.values()]):
            setattr(
                data_model,
                attr,
                users.AnonymousUser(preferred_username="Unknown User").dict(
                    by_alias=True
                ),
            )
            continue
        for contributor_type, contributor_subs in contributors.items():

            if user_sub not in contributor_subs:
                continue

            if check_permissions(
                principals=principals,
                action=f"view_{contributor_type}",
                acl=version_acl,
                error=False,
            ):
                setattr(data_model, attr, app_users[user_sub].dict(by_alias=True))
            else:
                preferred_username = contributor_type.strip("s").title()
                if contributor_type != "owner":
                    preferred_username += f" {contributor_subs.index(user_sub)+1}"

                setattr(
                    data_model,
                    attr,
                    users.AnonymousUser(preferred_username=preferred_username).dict(
                        by_alias=True
                    ),
                )
    return data_model


def update_thread_contributor_info(
    principals: List[str], atbd_version: AtbdVersions, thread: Threads
) -> Threads:
    """
    Adds user info for `created_by` and `last_updated_fields` to a thread
    and all comments contained within the thread
    """
    thread.comments = [
        update_user_info(
            principals=principals, atbd_version=atbd_version, data_model=comment
        )
        for comment in thread.comments
    ]

    thread = update_user_info(
        principals=principals, atbd_version=atbd_version, data_model=thread
    )

    return thread


def update_version_contributor_info(principals: List[str], version: AtbdVersions):
    """
    Replaces the cognito subs the following fields:
    - last_created_by
    - last_updated_by
    - published_by (if not null)
    - owner
    - authors
    - reviewers
    with `CognitoUser` type objects that contain the user information
    of the users, anonymized as needed, based on the principals of the
    user requesting/accessing the information.
    """
    app_users, request_id = list_cognito_users()

    version_acl = version.__acl__()

    # Update `created_by`, `last_updated_by` and `published_by` fields
    version = update_user_info(
        principals=principals, atbd_version=version, data_model=version
    )

    if check_permissions(
        principals=principals, action="view_owner", acl=version_acl, error=False
    ):
        version.owner = app_users[version.owner].dict(by_alias=True)

    else:
        version.owner = users.AnonymousUser(preferred_username="Owner").dict(
            by_alias=True
        )

    if check_permissions(
        principals=principals, action="view_authors", acl=version_acl, error=False
    ):

        version.authors = [
            app_users[author].dict(by_alias=True) for author in version.authors
        ]
    else:
        version.authors = [
            users.AnonymousUser(preferred_username=f"Author {str(i+1)}").dict(
                by_alias=True
            )
            for i, _ in enumerate(version.authors)
        ]

    if check_permissions(
        principals=principals, action="view_reviewers", acl=version_acl, error=False
    ):

        version.reviewers = [
            users.ReviewerUser(
                **app_users[reviewer["sub"]].dict(by_alias=True),
                review_status=reviewer["review_status"],
            ).dict(by_alias=True)
            for reviewer in version.reviewers
        ]
    else:
        version.reviewers = [
            users.AnonymousReviewerUser(
                preferred_username=f"Reviewer {str(i+1)}",
                review_status=v["review_status"],
            ).dict(by_alias=True)
            for i, v in enumerate(version.reviewers)
        ]

    return version


def update_atbd_contributor_info(principals: List[str], atbd: Atbds) -> Atbds:
    """
    Insert contributor (owner, author and reviewer) user info from
    Cognito into an ATBD Version. Identifying user information is
    obfuscated in accordance with the principals of the user (eg:
    unauthenticated users cannot see ANY identifying info, authors
    and Owners cannot see identifying info of reviewers, but can
    see identifying info of other authors)
    """

    atbd.versions = [
        update_version_contributor_info(principals=principals, version=version)
        for version in atbd.versions
    ]

    return atbd


@functools.lru_cache()
def list_cognito_users(groups="curator,contributor"):
    """
    Returns a list of ALL cognito users, to be filtered against the
    users of a document (authors, reviewers, owner). Returns a unique
    ID alongside the resulting app_users array in order to validate
    that the function call was indeed cached.

    Accepts a parameters specifying which group to list (listing both
    the `contributor` and ` the `curator` groups by default). The
    parameter must a string with group names separated by a comma. This
    is because the function's parameters must be hashable in order to
    be stored in the LRU cache, since it stores a hashmap of the input
    parameters along with the function's output.
    """
    # We need the cognito groups in the user info returned, in order to
    # verify certain operations (eg: users can only be added as co-authors
    # if they are part of the contributor user group, not the curator).
    # The `list_users` operation does not return the groups the user belongs
    # to, so instead we are listing the users in each group and adding
    # the group manually to returned data. It's not pretty. I know.
    app_users = {}

    client = cognito_client()
    for group in groups.split(","):

        paginator = client.get_paginator("list_users_in_group")
        response = paginator.paginate(UserPoolId=config.USER_POOL_ID, GroupName=group)

        for page in response:
            app_users.update(
                {
                    user["Username"]: users.CognitoUser(
                        **{**user, "cognito:groups": [group]}
                    )
                    for user in page.get("Users", [])
                }
            )

    return (app_users, str(uuid4()))


def get_cognito_user(sub: str):
    client = cognito_client()
    user = client.admin_get_user(
        UserPoolId=config.USER_POOL_ID,
        Username=sub
    )
    return user


def process_users_input(
    version_input: versions.Update,
    atbd_version: AtbdVersions,
    atbd_title: str,
    atbd_id: int,
    user: users.CognitoUser,
    principals: List[str],
    background_tasks: BackgroundTasks,
):
    """Processes input related to `owner`, `authors` or `reviewers` types of users.
    In each case, the following checks are performed:
    1. Is the user performing the request permitted to? (eg: only owner or curator can
        invite authors, only curator can invite reivewers)
    2. Are the users being added to the document permitted to be added in that category (eg:
        only contributors that are NOT already authors or reviewers of a document can be
        added as authors of that document)

    Lastly, the user info + necessary notifications are returned, to be added as background tasks
    """
    app_users, _ = list_cognito_users()
    user_notifications: List[notifications.UserNotification] = []
    if version_input.reviewers:

        check_permissions(
            principals=principals,
            action="invite_reviewers",
            acl=atbd_version.__acl__(),
        )

        for reviewer in version_input.reviewers:

            cognito_reviewer = app_users[reviewer]

            check_permissions(
                principals=get_active_user_principals(cognito_reviewer),
                action="join_reviewers",
                acl=atbd_version.__acl__(),
            )
            # skip notifying reviewers who are already assigned to the document
            if reviewer in [r["sub"] for r in atbd_version.reviewers]:
                continue
            user_notifications.append(
                {
                    "email": cognito_reviewer.email,
                    "preferred_username": cognito_reviewer.preferred_username,
                    "notification": "added_as_reviewer",
                }
            )

        # version_input is a list of cognito_subs. We want to grab the status of
        # the current reveiwers and merge with `IN_PROGRESS` reviewers of the all
        # the new reviewers, in order to avoid overwritting existing reviewers
        # (and losing their status)
        reviewers = [
            x for x in atbd_version.reviewers if x["sub"] in version_input.reviewers
        ]

        # new reviewers
        reviewers.extend(
            [
                {"sub": r, "review_status": "IN_PROGRESS"}
                for r in version_input.reviewers
                if r not in [_r["sub"] for _r in atbd_version.reviewers]
            ]
        )
        version_input.reviewers = reviewers

    if version_input.authors:
        check_permissions(
            principals=principals,
            action="invite_authors",
            acl=atbd_version.__acl__(),
        )

        for author in version_input.authors:

            cognito_author = app_users[author]
            check_permissions(
                principals=get_active_user_principals(cognito_author),
                action="join_authors",
                acl=atbd_version.__acl__(),
            )
            # Skip notification for authors who are already
            # assigned to the document
            if author in atbd_version.authors:
                continue

            user_notifications.append(
                {
                    "email": cognito_author.email,
                    "preferred_username": cognito_author.preferred_username,
                    "notification": "added_as_author",
                }
            )

    if version_input.owner and version_input.owner != atbd_version.owner:
        check_permissions(
            principals=principals,
            action="offer_ownership",
            acl=atbd_version.__acl__(),
        )

        cognito_owner = app_users[version_input.owner]

        check_permissions(
            principals=get_active_user_principals(cognito_owner),
            action="receive_ownership",
            acl=atbd_version.__acl__(),
        )
        user_notifications.append(
            {
                "email": cognito_owner.email,
                "preferred_username": cognito_owner.preferred_username,
                "notification": "added_as_owner",
            }
        )

        # Remove new owner from authors list
        version_input.authors = [
            a for a in atbd_version.authors if a != version_input.owner
        ]
        # Set old owner as author
        version_input.authors.append(atbd_version.owner)

        cognito_old_owner = app_users[atbd_version.owner]
        user_notifications.append(
            {
                "email": cognito_old_owner.email,
                "preferred_username": cognito_old_owner.preferred_username,
                "notification": "ownership_revoked",
                "data": {"transferred_to": cognito_owner.preferred_username},
            }
        )

    background_tasks.add_task(
        notifications.notify_users,
        user=user,
        user_notifications=user_notifications,
        atbd_title=atbd_title,
        atbd_id=atbd_id,
        atbd_version=f"v{atbd_version.major}.{atbd_version.minor}",
    )

    return version_input
