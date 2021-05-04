"""ATBD Versions endpoint."""
from app.schemas import atbds, versions, contacts, versions_contacts
from app.db.db_session import DbSession
from app.api.utils import (
    get_db,
    require_user,
    get_major_from_version_string,
)
from app.api.v1.pdf import add_pdf_generation_to_background_tasks
from app.crud.atbds import crud_atbds
from app.crud.versions import crud_versions
from app.crud.contacts import crud_contacts_associations
from app.db.models import Atbds
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
)
import datetime

router = APIRouter()


@router.head(
    "/atbds/{atbd_id}/versions/{version}",
    responses={200: dict(description="Atbd with given ID/alias exists in backend")},
)
def version_exists(atbd_id: str, version: str, db: DbSession = Depends(get_db)):
    major, _ = get_major_from_version_string(version)
    return crud_atbds.exists(db=db, atbd_id=atbd_id, version=major)


@router.get("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def get_version(atbd_id: str, version: str, db=Depends(get_db)):

    major, _ = get_major_from_version_string(version)
    return crud_atbds.get(db=db, atbd_id=atbd_id, version=major)


@router.post("/atbds/{atbd_id}/versions", response_model=atbds.FullOutput)
def create_new_version(atbd_id: str, db=Depends(get_db), user=Depends(require_user)):
    version = crud_versions.create(db=db, atbd_id=atbd_id, user=user["user"])
    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.post("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def update_atbd_version(
    atbd_id: str,
    version: str,
    version_input: versions.Update,
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db=Depends(get_db),
    user=Depends(require_user),
):

    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    [version] = atbd.versions

    if version_input.contacts and len(version_input.contacts):

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

        for contact in version.contacts_link:
            if contact.contact_id in [c.id for c in version_input.contacts]:
                continue
            crud_contacts_associations.remove(
                db_session=db, id=(atbd_id, major, contact.contact_id)
            )

    if version_input.minor and version.status != "Published":
        raise HTTPException(
            status_code=400,
            detail="ATBD must have status `published` in order to increment the minor version number",
        )

    if version_input.minor and version_input.minor != version.minor + 1:
        raise HTTPException(
            status_code=400,
            detail="New version number must be exactly 1 greater than previous",
        )

    if version_input.minor:
        # A new version has been created - generate a cache a PDF for both the regular
        # PDF format, and the journal PDF format
        add_pdf_generation_to_background_tasks(
            atbd=atbd, background_tasks=background_tasks
        )

    if version_input.document and not overwrite:
        version_input.document = {
            **version.document,
            **version_input.document.dict(exclude_unset=True),
        }

    if version_input.sections_completed and not overwrite:
        version_input.sections_completed = {
            **version.sections_completed,
            **version_input.sections_completed,
        }

    version.last_updated_by = user["user"]
    version.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
    crud_versions.update(db=db, db_obj=version, obj_in=version_input)

    return crud_atbds.get(db=db, atbd_id=atbd_id, version=version.major)


@router.delete(
    "/atbds/{atbd_id}/versions/{version}",
    responses={204: dict(description="ATBD Version deleted")},
)
def delete_atbd_version(
    atbd_id: str,
    version: str,
    db=Depends(get_db),
    user=Depends(require_user),
):
    major, _ = get_major_from_version_string(version)
    [version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=major).versions
    if version.status == "Published":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete an atbd version with status `Published`",
        )
    db.delete(version)
    db.commit()
    return {}
