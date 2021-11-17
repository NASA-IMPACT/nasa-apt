"""ATBD Versions endpoint."""
import datetime
from typing import List

from app.api.utils import get_major_from_version_string
from app.crud.atbds import crud_atbds
from app.crud.contacts import crud_contacts_associations
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import AtbdVersions
from app.permissions import check_permissions
from app.schemas import atbds, versions, versions_contacts
from app.schemas.users import CognitoUser
from app.search.elasticsearch import remove_atbd_from_index
from app.users.auth import get_user, require_user
from app.users.cognito import (
    get_active_user_principals,
    process_users_input,
    update_atbd_contributor_info,
)

from fastapi import APIRouter, BackgroundTasks, Depends

router = APIRouter()


@router.head(
    "/atbds/{atbd_id}/versions/{version}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def version_exists(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns HTTP Code 200 if the requested atbd/version exists, otherwise
    raises a 404 Exception.
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    [atbd_version] = atbd.versions
    check_permissions(principals=principals, action="view", acl=atbd_version.__acl__())

    return True


@router.get(
    "/atbds/{atbd_id}/versions/{version}",
    response_model=atbds.FullOutput,
    response_model_exclude_none=True,
)
def get_version(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns an ATBD with a single version
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    [atbd_version] = atbd.versions
    print("ATBD VERSION CONTACTS: ", atbd_version.contacts_link)
    check_permissions(principals=principals, action="view", acl=atbd_version.__acl__())
    atbd = update_atbd_contributor_info(principals, atbd)
    return atbd


@router.post(
    "/atbds/{atbd_id}/versions",
    response_model=atbds.FullOutput,
    response_model_exclude_none=True,
)
def create_new_version(
    atbd_id: str,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals=Depends(get_active_user_principals),
):
    """
    Creates a new version (with `Draft` status) from the latest version
    in the provided ATBD. Raises an exception if the latest version does
    NOT have status=`Published`.
    """
    [latest_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1).versions
    check_permissions(
        principals=principals,
        action="create_new_version",
        acl=latest_version.__acl__(),
    )
    update_document = latest_version.document
    update_document["version_description"] = None

    new_version_input = versions.Create(
        atbd_id=latest_version.atbd_id,
        major=latest_version.major + 1,
        minor=0,
        status="DRAFT",
        document=update_document,
        created_by=user.sub,
        last_updated_by=user.sub,
        owner=user.sub,
    )
    new_version = crud_versions.create(db_session=db, obj_in=new_version_input)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=new_version.major)
    atbd = update_atbd_contributor_info(principals, atbd)
    return atbd


@router.post(  # noqa : C901
    "/atbds/{atbd_id}/versions/{version}",
    response_model=atbds.FullOutput,
    response_model_exclude_none=True,
)
def update_atbd_version(
    atbd_id: str,
    version: str,
    version_input: versions.Update,
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
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

    for attribute in versions.Update.__dict__["__fields__"].keys():
        if attribute in ["journal_status", "owner", "authors", "reviewers"]:
            continue

        try:
            if getattr(version_input, attribute):
                check_permissions(
                    principals=principals, action="update", acl=version_acl
                )
        except AttributeError:
            continue

    if version_input.contacts and len(version_input.contacts):

        # Overwrite any existing `ContactAssociation` items
        # in the database - this makes updating roles on an existing
        # contacts_link item possible.
        for contact in version_input.contacts:
            print("CONTACT: ", contact)
            crud_contacts_associations.upsert(
                db_session=db,
                obj_in=versions_contacts.ContactsAssociation(
                    contact_id=contact.id,
                    atbd_id=atbd_id,
                    major=major,
                    roles=contact.roles,
                    affiliations=contact.affiliations,
                ),
            )

        # Remove contacts not in the input data contacts
        for contact in atbd_version.contacts_link:
            if contact.contact_id in [c.id for c in version_input.contacts]:
                continue
            crud_contacts_associations.remove(
                db_session=db, id=(atbd_id, major, contact.contact_id)  # type: ignore
            )

        delattr(version_input, "contacts")

    if version_input.owner or version_input.reviewers or version_input.authors:
        # No need to check action permissions here because the
        # process_users_input method has its own permissions
        # checking logic
        version_input = process_users_input(
            version_input=version_input,
            atbd_version=atbd_version,
            atbd_title=atbd.title,
            atbd_id=atbd.id,
            user=user,
            principals=principals,
            background_tasks=background_tasks,
        )

    # TODO: use enum for journal status
    if version_input.journal_status:
        action = (
            "update_journal_status"
            if version_input.journal_status
            in ["NO_PUBLICATION", "PUBLICATION_INTENDED"]
            else "update_journal_publication_status"
        )

        check_permissions(principals=principals, action=action, acl=version_acl)

    if version_input.document and not overwrite:

        version_input.document = {  # type: ignore
            **atbd_version.document,
            **version_input.document.dict(exclude_unset=True),
        }

    if version_input.sections_completed and not overwrite:

        version_input.sections_completed = {
            **atbd_version.sections_completed,
            **version_input.sections_completed,
        }

    # # This should act on the update input object, and not the db object
    # atbd_version.last_updated_by = user.sub
    # atbd_version.last_updated_at = datetime.datetime.now(datetime.timezone.utc)

    crud_versions.update(
        db=db,
        db_obj=atbd_version,
        obj_in=versions.AdminUpdate(
            **version_input.dict(),
            last_updated_by=user.sub,
            last_updated_at=datetime.datetime.now(datetime.timezone.utc)
        ),
    )

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=atbd_version.major)
    atbd = update_atbd_contributor_info(principals, atbd)

    return atbd


@router.delete(
    "/atbds/{atbd_id}/versions/{version}",
    responses={204: dict(description="ATBD Version deleted")},
)
def delete_atbd_version(
    atbd_id: str,
    version: str,
    background_tasks: BackgroundTasks,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals=Depends(get_active_user_principals),
):
    """
    Deletes the version only if it is unpublished
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions
    check_permissions(
        principals=principals, action="delete", acl=atbd_version.__acl__()
    )

    crud_versions.delete(db=db, atbd=atbd, version=atbd_version)

    background_tasks.add_task(remove_atbd_from_index, version=atbd_version)

    # TODO: this should also remove the associated PDFs in S3
    return {}
