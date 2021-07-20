"""ATBD Versions endpoint."""
import datetime
from typing import List

from app.api.utils import (
    atbd_permissions_filter,
    get_active_user_principals,
    get_db,
    get_major_from_version_string,
    get_user,
    list_cognito_users,
    require_user,
    update_contributor_info,
)
from app.api.v2.pdf import save_pdf_to_s3
from app.crud.atbds import crud_atbds
from app.crud.contacts import crud_contacts_associations
from app.crud.versions import crud_versions
from app.db.db_session import DbSession
from app.db.models import AtbdVersions
from app.schemas import atbds, versions, versions_contacts
from app.schemas.users import User
from app.search.elasticsearch import add_atbd_to_index, remove_atbd_from_index

import fastapi_permissions as permissions
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

router = APIRouter()


@router.head(
    "/atbds/{atbd_id}/versions/{version}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def version_exists(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns HTTP Code 200 if the requested atbd/version exists, otherwise
    raises a 404 Exception.
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    if not atbd_permissions_filter(principals, atbd, "view"):
        raise HTTPException(
            status_code=404, detail=f"No data found for id/alias: {atbd_id}"
        )
    return True


@router.get("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def get_version(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns an ATBD with a single version
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    if not atbd_permissions_filter(principals, atbd, "view"):
        raise HTTPException(
            status_code=404, detail=f"No data found for id/alias: {atbd_id}"
        )
    atbd = update_contributor_info(principals, atbd)
    return atbd


@router.post("/atbds/{atbd_id}/versions", response_model=atbds.FullOutput)
def create_new_version(
    atbd_id: str,
    db: DbSession = Depends(get_db),
    user=Depends(require_user),
    principals=Depends(get_active_user_principals),
):
    """
    Creates a new version (with `Draft` status) from the latest version
    in the provided ATBD. Raises an exception if the latest version does
    NOT have status=`Published`.
    """
    [latest_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1).versions
    if not permissions.has_permission(
        principals, "create_new_version", latest_version.__acl__()
    ):
        raise HTTPException(
            status_code=400, detail=f"Cannot create a new version for ATBD {atbd_id}"
        )
    new_version_input = versions.Create(
        atbd_id=latest_version.atbd_id,
        major=latest_version.major + 1,
        minor=0,
        status="Draft",
        document=latest_version.document,
        created_by=user["sub"],
        last_updated_by=user["sub"],
        owner=user["sub"],
    )
    new_version = crud_versions.create(db_session=db, obj_in=new_version_input)
    # version = crud_versions.create(db=db, atbd_id=atbd_id, user=user["sub"])
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=new_version.major)
    atbd = update_contributor_info(principals, atbd)
    return atbd


@router.post("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def update_atbd_version(
    atbd_id: str,
    version: str,
    version_input: versions.Update,
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db: DbSession = Depends(get_db),
    user=Depends(require_user),
    principals=Depends(get_active_user_principals),
):
    """
    Updates an ATBD versions. If `overwrite` is True then the data supplied under
    the `document` and `sections_completed` keys will overwrite those values in the
    data model, otherwise the data provided under `document` and `sections_completed`
    will be merged into the existing data for those attributes.

    Contacts provided will overwrite all the contacts currently associated with the
    atbd version. This makes it possible to update the roles of a contact_link without
    having to delete and recreate it.

    Updates to the ATBD will also trigger re-indexing of the atbd in elasticsearch

    Raises an exception if: minor is provided but the version does NOT have
    status=`Published` or if minor is provided but is not exactly one more than the
    current minor version number.

    """

    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)

    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions
    version_acl = atbd_version.__acl__()

    if version_input.contacts and len(version_input.contacts):

        # Overwrite any existing `ContactAssociation` items
        # in the database - this makes updating roles on an existing
        # contacts_link item possible.
        for contact in version_input.contacts:
            crud_contacts_associations.upsert(
                db_session=db,
                obj_in=versions_contacts.ContactsAssociation(
                    contact_id=contact.id,
                    atbd_id=atbd_id,
                    major=major,
                    roles=contact.roles,
                ),
            )

        # Remove contacts not in the input data contacts
        for contact in atbd_version.contacts_link:
            if contact.contact_id in [c.id for c in version_input.contacts]:
                continue
            crud_contacts_associations.remove(
                db_session=db, id=(atbd_id, major, contact.contact_id)  # type: ignore
            )
    # TODO: move bumping minor versions to the `/events` endpoint
    if version_input.minor and atbd_version.status != "Published":
        raise HTTPException(
            status_code=400,
            detail="ATBD must have status `published` in order to increment the minor version number",
        )

    if version_input.minor and version_input.minor != atbd_version.minor + 1:
        raise HTTPException(
            status_code=400,
            detail="New version number must be exactly 1 greater than previous",
        )

    if version_input.minor:
        # A new version has been created - generate a cache a PDF for both the regular
        # PDF format, and the journal PDF format
        background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=True)
        background_tasks.add_task(save_pdf_to_s3, atbd=atbd, journal=False)

    app_users = []
    if version_input.owner or version_input.reviewers or version_input.authors:
        app_users = list_cognito_users()

    if version_input.owner and version_input.owner != atbd_version.owner:

        # User performing transfer ownership operation is not allowed
        if not permissions.has_permission(principals, "offer_ownership", version_acl):
            raise HTTPException(
                status_code=400,
                detail=f"User {user['preferred_username']} is not allowed to transfer ownership to another user",
            )

        [cognito_owner] = [
            user for user in app_users if user["sub"] == version_input.owner
        ]

        # User being transferred ownership to, is not allowed (either because
        # they are a reviewer of the document, or a curator)
        if not permissions.has_permission(
            get_active_user_principals(cognito_owner), "receive_ownership", version_acl,
        ):
            raise HTTPException(
                status_code=400,
                detail=f"User {cognito_owner['preferred_username']} is not allowed to receive ownership of this document",
            )

        # Checks did not fail - perform ownership transfer
        atbd_version.owner = version_input.owner

    if version_input.reviewers:
        if not permissions.has_permission(principals, "invite_reviewers", version_acl):
            raise HTTPException(
                status_code=400,
                detail=f"User {user['preferred_username']} is not allowed to add reviewers this document",
            )

        for reviewer in version_input.reviewers:
            print("REVIEWER SUB: ", reviewer.sub)
            print("USERS: ", [user["sub"] for user in app_users])
            [cognito_user] = [user for user in app_users if user["sub"] == reviewer.sub]
            if not permissions.has_permission(
                get_active_user_principals(cognito_user), "join_reviewers", version_acl,
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"User {cognito_user['preferred_username']} cannot be added as a reviewer of this document",
                )

        atbd_version.reviewers = version_input.reviewers

    if version_input.authors:
        if not permissions.has_permission(principals, "invite_authors", version_acl):
            raise HTTPException(
                status_code=400,
                detail=f"User {user['preferred_username']} is not allowed to add authors this document",
            )

        for author in version_input.authors:
            [cognito_author] = [user for user in app_users if user["sub"] == author]
            if not permissions.has_permission(
                get_active_user_principals(cognito_author), "join_authors", version_acl,
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"User {cognito_author['preferred_username']} cannot be added as an author of this document",
                )
        atbd_version.authors = version_input.authors

    if version_input.document and not overwrite:
        version_input.document = {
            **atbd_version.document,
            **version_input.document.dict(exclude_unset=True),
        }  # type: ignore

    if version_input.sections_completed and not overwrite:
        version_input.sections_completed = {
            **atbd_version.sections_completed,
            **version_input.sections_completed,
        }

    atbd_version.last_updated_by = user["sub"]
    atbd_version.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    crud_versions.update(db=db, db_obj=atbd_version, obj_in=version_input)

    # Indexes the updated vesion as well as atbd info
    # (title, alias, etc)
    background_tasks.add_task(add_atbd_to_index, atbd)

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=atbd_version.major)

    atbd = update_contributor_info(principals, atbd)

    return atbd


@router.delete(
    "/atbds/{atbd_id}/versions/{version}",
    responses={204: dict(description="ATBD Version deleted")},
)
def delete_atbd_version(
    atbd_id: str,
    version: str,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db),
    user=Depends(require_user),
    principals=Depends(get_active_user_principals),
):

    """
    Deletes the version only if it is unpublished
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions
    if not permissions.has_permission(principals, "delete", atbd_version.__acl__()):
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an atbd version with status `Published`",
        )
    db.delete(atbd_version)
    db.commit()
    db.refresh(atbd)

    if len(atbd.versions) == 0:
        db.delete(atbd)
        db.commit()

    background_tasks.add_task(remove_atbd_from_index, version=atbd_version)
    return {}
