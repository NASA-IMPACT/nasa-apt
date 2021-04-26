from app.crud.base import CRUDBase
from app.db.models import AtbdVersions, AtbdVersionsContactsAssociation
from app.db.db_session import DbSession
from app.schemas.versions import FullOutput, Create, Update, Contact
from app.crud.atbds import crud_atbds
from sqlalchemy import orm
from typing import List

from fastapi import HTTPException


class CRUDVersions(CRUDBase[AtbdVersions, FullOutput, Create, Update]):
    def update_contacts(
        self,
        db: DbSession,
        crt_contacts: List[AtbdVersionsContactsAssociation],
        input_contacts: List[Contact],
        atbd_id: int,
        major: int,
    ):
        contacts_to_add = [
            contact
            for contact in input_contacts
            if contact.id in [c.id for c in crt_contacts]
        ]
        contacts_to_remove = [
            contact
            for contact in crt_contacts
            if contact.id not in [c.id for c in input_contacts]
        ]
        for contact in contacts_to_add:
            db.add(
                AtbdVersionsContactsAssociation(
                    atbd_id=atbd_id,
                    major=major,
                    contact_id=contact.id,
                    roles=contact.roles,
                )
            )
        for contact in contacts_to_remove:
            contact_link = (
                db.query(AtbdVersionsContactsAssociation)
                .filter(atbd_id=atbd_id)
                .filter(major=major)
                .filter(contact_id=contact.id)
                .one()
            )
            db.delete(contact_link)
        db.commit()

    def create(self, db: DbSession, atbd_id: str, user: str):

        [latest_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1).versions

        if latest_version.status != "Published":
            raise HTTPException(
                status_code=400,
                detail=(
                    "A new version can only be created if the latest verison has status: "
                    f"`Published`"
                ),
            )

        db.expunge(latest_version)
        orm.make_transient(latest_version)

        latest_version.major = latest_version.major + 1
        latest_version.minor = 0
        latest_version.changelog = None
        latest_version.doi = None
        latest_version.citation = None
        latest_version.created_by = user
        latest_version.last_updated_by = user

        # Postgres will auto-populate status with default value ("Draft")
        latest_version.status = None

        db.add(latest_version)
        db.commit()
        db.refresh(latest_version)

        return latest_version


crud_versions = CRUDVersions(AtbdVersions)
