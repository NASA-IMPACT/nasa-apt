"""ATBD Versions endpoint."""
import datetime
from typing import List

from app.api.utils import (
    atbd_permissions_filter,
    get_active_user_principals,
    get_db,
    get_major_from_version_string,
    get_user,
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
    atbd_id: str, db: DbSession = Depends(get_db), user=Depends(require_user)
):
    """
    Creates a new version (with `Draft` status) from the latest version
    in the provided ATBD. Raises an exception if the latest version does
    NOT have status=`Published`.
    """
    version = crud_versions.create(db=db, atbd_id=atbd_id, user=user["sub"])
    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.post("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def update_atbd_version(
    atbd_id: str,
    version: str,
    version_input: versions.Update,
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db: DbSession = Depends(get_db),
    user=Depends(require_user),
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

    if version_input.contacts and len(version_input.contacts):

        for contact in version_input.contacts:
            # This will overwrite an existing `ContactAssociation` items
            # in the database - this makes updating roles on an existing
            # contacts_link item possible
            crud_contacts_associations.upsert(
                db_session=db,
                obj_in=versions_contacts.ContactsAssociation(
                    contact_id=contact.id,
                    atbd_id=atbd_id,
                    major=major,
                    roles=contact.roles,
                ),
            )

        for contact in atbd_version.contacts_link:
            if contact.contact_id in [c.id for c in version_input.contacts]:
                continue
            crud_contacts_associations.remove(
                db_session=db, id=(atbd_id, major, contact.contact_id)  # type: ignore
            )

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

    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=atbd_version.major)

    # Indexes the updated vesion as well as atbd info
    # (title, alias, etc)
    background_tasks.add_task(add_atbd_to_index, atbd)
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
):

    """
    Deletes the version only if it is unpublished
    """
    major, _ = get_major_from_version_string(version)
    atbd_version: AtbdVersions
    [atbd_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    if atbd_version.status == "Published":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an atbd version with status `Published`",
        )
    db.delete(atbd_version)
    db.commit()
    background_tasks.add_task(remove_atbd_from_index, version=atbd_version)
    return {}
