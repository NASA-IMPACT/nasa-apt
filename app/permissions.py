"""Functionality related to permissions model"""

from typing import List, Tuple

from app.db.models import Atbds

import fastapi_permissions
from fastapi import HTTPException


def filter_atbd_versions(
    principals: List[str], atbd: Atbds, raise_exception=True
) -> Atbds:
    """
    Applies a permission check to a list of ATBDs, returning only the versions
    that the user is allowed to see. If an ATBD has NO versions that the user is
    allowed to access, then the filter returns `None`.
    """

    versions = [
        version
        for version in atbd.versions
        if check_permissions(
            principals=principals,
            action="view",
            acl=version.__acl__(),
            raise_exception=False,
        )
    ]

    if not versions:
        if not raise_exception:
            return None
        raise HTTPException(status_code=404, detail="No atbds found")

    atbd.versions = versions
    return atbd


def check_atbd_permissions(
    principals: List[str],
    action: str,
    atbd: Atbds,
    all_versions: bool = True,
) -> bool:
    """
    Applies a permission check for any action to all of the atbd's versions
    of an atbd. Can be configured to consider the action valid if it
    can be performed on ANY atbd version or if it must be allowed for
    ALL atbd versions. Can also be configured to either raise an exception
    or return a boolean depending on the outcome.
    """

    if action == "create_atbd":
        if not check_permissions(
            principals=principals,
            action=action,
            acl=[(fastapi_permissions.Allow, "role:contributor", "create_atbd")],
            raise_exception=False,
        ):
            raise HTTPException(
                status_code=403, detail="User is not allowed to create a new ATBD"
            )
        return True

    if action == "rebuild_atbd_index":
        if not check_permissions(
            principals=principals,
            action=action,
            acl=[(fastapi_permissions.Allow, "role:curator", "rebuild_atbd_index")],
            raise_exception=False,
        ):
            raise HTTPException(
                status_code=403,
                detail="User is not allowed to trigger ATBDs re-index sync",
            )
        return True

    permissions = [
        check_permissions(
            principals=principals,
            action=action,
            acl=version.__acl__(),
            raise_exception=False,
        )
        for version in atbd.versions
    ]
    if all_versions and not all(permissions):
        raise HTTPException(
            status_code=400, detail=f"{action.capitalize()} for ATBD is not allowed"
        )

    if not any(permissions):
        raise HTTPException(
            status_code=400, detail=f"{action.capitalize()} for ATBD is not allowed"
        )
    return True


def check_permissions(
    principals: List[str],
    action: str,
    acl: List[Tuple],
    raise_exception=True,
) -> bool:
    """Applies permission check for the requested action. Can be configured to either
    raise an exception or return a boolean"""
    if not fastapi_permissions.has_permission(principals, action, acl):
        # don't raise an exception, return bool
        if not raise_exception:
            return False

        action_name = " ".join([x.capitalize() for x in action.split("_")])
        raise HTTPException(
            status_code=403,
            detail=f"{action_name} for ATBD Version is not allowed",
        )
    return True
