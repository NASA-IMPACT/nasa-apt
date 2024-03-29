"""ATBD Versions endpoint."""
import datetime
from copy import deepcopy
from typing import List

from app.api.utils import get_major_from_version_string
from app.crud.atbds import crud_atbds
from app.crud.contacts import crud_contacts_associations
from app.crud.uploads import crud_uploads
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import AtbdVersions
from app.email.notifications import notify_atbd_version_contributors
from app.permissions import check_permissions
from app.schemas import atbds, versions, versions_contacts
from app.schemas.atbds import AtbdDocumentTypeEnum
from app.schemas.users import CognitoUser
from app.schemas.versions_contacts import RolesEnum
from app.search.opensearch import remove_atbd_from_index
from app.users.auth import get_user, require_user
from app.users.cognito import (
    get_active_user_principals,
    get_cognito_user,
    process_users_input,
    update_atbd_contributor_info,
)

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

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
    update_document = latest_version.document.copy()
    update_document["version_description"] = None

    new_version_input = versions.Create(
        atbd_id=latest_version.atbd_id,
        major=latest_version.major + 1,
        minor=0,
        status="DRAFT",
        publication_checklist=latest_version.publication_checklist,
        document=update_document,
        created_by=user.sub,
        last_updated_by=user.sub,
        owner=user.sub,
    )

    new_version = crud_versions.create(db_session=db, obj_in=new_version_input)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=new_version.major)
    atbd = update_atbd_contributor_info(principals, atbd)
    return atbd


@router.post(
    "/atbds/{atbd_id}/versions/{version}",
    response_model=atbds.FullOutput,
    response_model_exclude_none=True,
)
def update_atbd_version(  # noqa : C901
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

    Updates to the ATBD will also trigger re-indexing of the atbd in opensearch

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

    if version_input.contacts is not None:

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

    if atbd.document_type == AtbdDocumentTypeEnum.PDF:
        # Check if user have enough permission to attach new pdf to the atbd
        if version_input.pdf_id and version_input.pdf_id != atbd_version.pdf_id:
            pdf_upload = crud_uploads.get(
                db=db,
                pdf_id=version_input.pdf_id,
                filters=dict(
                    atbd_id=atbd_id,
                ),
            )
            check_permissions(
                principals=principals, action="add_to_atbds", acl=pdf_upload.__acl__()
            )
    else:
        # Let's unset pdf for HTML
        if version_input.pdf_id:
            version_input.pdf_id = None

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
            last_updated_at=datetime.datetime.now(datetime.timezone.utc),
        ),
    )

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=atbd_version.major)
    atbd = update_atbd_contributor_info(principals, atbd)

    return atbd


@router.put(
    "/atbds/{atbd_id}/versions/{version}/lock", response_model=versions.LockOutput
)
def secure_atbd_version_lock(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db_session),
    override: bool = False,
    user: CognitoUser = Depends(require_user),
    principals=Depends(get_active_user_principals),
):
    """
    Sets locked_by field of ATBD Version to current user.
    Succeeds if either the `locked_by` field is empty or already belongs
    to the user requesting the operation.
    Raises an exception if the `locked_by` field belongs to a different user
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)

    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions

    if not override and not check_permissions(
        principals=principals,
        action="secure_lock",
        acl=atbd_version.__acl__(),
        raise_exception=False,
    ):
        # return exception
        lock_owner = get_cognito_user(atbd_version.locked_by)

        raise HTTPException(
            status_code=423,
            detail={
                "message": f"ATBD Version locked, {lock_owner.preferred_username} ({lock_owner.email}) is currently editing this document",
                "lock_owner": {
                    "email": lock_owner.email,
                    "preferred_username": lock_owner.preferred_username,
                },
            },
        )

    crud_versions.set_lock(db, version=atbd_version, locked_by=user.sub)
    return {
        "locked_by": {
            "email": user.email,
            "preferred_username": user.preferred_username,
        }
    }


@router.delete("/atbds/{atbd_id}/versions/{version}/lock")
def release_atbd_version_lock(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db_session),
    user: CognitoUser = Depends(require_user),
    principals=Depends(get_active_user_principals),
):
    """
    Sets ATBD Version lock back to None.
    Returns 200 if the ATBD Version lock belongs to the user AND
    the `override` flag IS NOT set to True
    Returns 200 if the ATBD Version lock DOES NOT belong to the user
    AND the `override` flag IS set to True
    Raises exception if the ATBD Version lock belongs to a different
    user AND the override flag is not set to True
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)

    atbd_version: AtbdVersions
    [atbd_version] = atbd.versions

    # return 200 + empty object is no lock exists to ensure idempotency
    # of delete request (ie: can make the same call multiple times with
    # the same)
    if atbd_version.locked_by is None:
        return {}

    if not check_permissions(
        principals=principals,
        action="release_lock",
        acl=atbd_version.__acl__(),
        raise_exception=False,
    ):
        lock_owner = get_cognito_user(atbd_version.locked_by)
        raise HTTPException(
            status_code=423,
            detail={
                "message": f"ATBD Version locked, {lock_owner.preferred_username} ({lock_owner.email}) is currently editing this document",
                "lock_owner": {
                    "email": lock_owner.email,
                    "preferred_username": lock_owner.preferred_username,
                },
            },
        )

    crud_versions.set_lock(db, version=atbd_version, locked_by=None)
    return {}


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

    # Send email to users
    background_tasks.add_task(
        notify_atbd_version_contributors,
        data=dict(
            notify=[atbd_version.owner, "curators"],
        ),
        notification="delete_atbd",
        atbd_version=deepcopy(atbd_version),
        atbd_title=atbd.title,
        atbd_id=atbd.id,
        user=user,
    )

    return {}
