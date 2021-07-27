"""ATBD Versions endpoint."""
import datetime
from typing import List

from app.api.utils import (
    get_active_user_principals,
    get_major_from_version_string,
    get_user,
    list_cognito_users,
    require_user,
    update_contributor_info,
)
from app.crud.atbds import crud_atbds
from app.crud.contacts import crud_contacts_associations
from app.crud.versions import crud_versions
from app.db.db_session import DbSession, get_db_session
from app.db.models import AtbdVersions
from app.permissions import check_permissions, filter_atbds
from app.schemas import atbds, versions, versions_contacts
from app.schemas.users import User
from app.search.elasticsearch import remove_atbd_from_index

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
    user: User = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns HTTP Code 200 if the requested atbd/version exists, otherwise
    raises a 404 Exception.
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)

    return True


@router.get("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def get_version(
    atbd_id: str,
    version: str,
    db: DbSession = Depends(get_db_session),
    user: User = Depends(get_user),
    principals: List[str] = Depends(get_active_user_principals),
):
    """
    Returns an ATBD with a single version
    """
    major, _ = get_major_from_version_string(version)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=major)
    atbd = filter_atbds(principals, atbd)

    atbd = update_contributor_info(principals, atbd)
    return atbd


@router.post("/atbds/{atbd_id}/versions", response_model=atbds.FullOutput)
def create_new_version(
    atbd_id: str,
    db: DbSession = Depends(get_db_session),
    user=Depends(require_user),
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

    new_version_input = versions.Create(
        atbd_id=latest_version.atbd_id,
        major=latest_version.major + 1,
        minor=0,
        status="DRAFT",
        document=latest_version.document,
        created_by=user["sub"],
        last_updated_by=user["sub"],
        owner=user["sub"],
    )
    new_version = crud_versions.create(db_session=db, obj_in=new_version_input)
    atbd = crud_atbds.get(db=db, atbd_id=atbd_id, version=new_version.major)
    atbd = update_contributor_info(principals, atbd)
    return atbd


@router.post("/atbds/{atbd_id}/versions/{version}", response_model=atbds.FullOutput)
def update_atbd_version(  # noqa : C901
    atbd_id: str,
    version: str,
    version_input: versions.Update,
    background_tasks: BackgroundTasks,
    overwrite: bool = False,
    db: DbSession = Depends(get_db_session),
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

    # blanket update permission check - more specific permissions checks will
    # occer later
    check_permissions(principals=principals, action="update", acl=version_acl)

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

    if version_input.owner or version_input.reviewers or version_input.authors:
        version_input = process_users_input(
            version_input=version_input,
            atbd_version=atbd_version,
            principals=principals,
        )

    if version_input.journal_status:
        check_permissions(
            principals=principals, action="update_journal_status", acl=version_acl
        )

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
    db: DbSession = Depends(get_db_session),
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
    check_permissions(
        principals=principals, action="delete", acl=atbd_version.__acl__()
    )

    crud_versions.delete(db=db, atbd=atbd, version=atbd_version)

    background_tasks.add_task(remove_atbd_from_index, version=atbd_version)
    return {}


def process_users_input(
    version_input: versions.Update, atbd_version: AtbdVersions, principals: List[str]
):
    app_users = list_cognito_users()

    if version_input.reviewers:

        check_permissions(
            principals=principals,
            action="invite_reviewers",
            acl=atbd_version.__acl__(),
        )

        for reviewer in version_input.reviewers:

            [cognito_user] = [user for user in app_users if user["sub"] == reviewer]

            check_permissions(
                principals=get_active_user_principals(cognito_user),
                action="join_reviewers",
                acl=atbd_version.__acl__(),
            )

        reviewers = [
            x for x in atbd_version.reviewers if x["sub"] in version_input.reviewers
        ]

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
            principals=principals, action="invite_authors", acl=atbd_version.__acl__(),
        )

        for author in version_input.authors:
            [cognito_author] = [user for user in app_users if user["sub"] == author]
            check_permissions(
                principals=get_active_user_principals(cognito_author),
                action="join_authors",
                acl=atbd_version.__acl__(),
            )

    if version_input.owner and version_input.owner != atbd_version.owner:
        # User performing transfer ownership operation is not allowed
        check_permissions(
            principals=principals, action="offer_ownership", acl=atbd_version.__acl__(),
        )

        [cognito_owner] = [
            user for user in app_users if user["sub"] == version_input.owner
        ]

        # User being transferred ownership to, is not allowed (either because
        # they are a reviewer of the document, or a curator)

        check_permissions(
            principals=get_active_user_principals(cognito_owner),
            action="receive_ownership",
            acl=atbd_version.__acl__(),
        )

        # Remove new owner from authors list
        version_input.authors = [
            a for a in atbd_version.authors if a != version_input.owner
        ]
        # Set old owner as author
        version_input.authors.append(atbd_version.owner)

    return version_input
