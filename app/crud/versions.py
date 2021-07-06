"""CRUD operations for ATBD Versions."""
from sqlalchemy import orm

from app.crud.atbds import crud_atbds
from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import AtbdVersions
from app.schemas.versions import Create, FullOutput, Update

from fastapi import HTTPException


class CRUDVersions(CRUDBase[AtbdVersions, FullOutput, Create, Update]):
    """CRUDVersions"""

    def create(self, db: DbSession, atbd_id: str, user: str):  # type: ignore
        """Creates a new version from a previous one, by incrementing the major version number
        from the latest version, and clearing out all other fields. Raises an exception if the
        latest version does not have status=`Published` because an ATBD cannot have more than
        one `Draft` versions at a time."""
        [latest_version] = crud_atbds.get(db=db, atbd_id=atbd_id, version=-1).versions

        if latest_version.status != "Published":
            raise HTTPException(
                status_code=400,
                detail=(
                    "A new version can only be created if the latest version has status: "
                    "`Published`"
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
        latest_version.created_at = None

        latest_version.last_updated_by = user
        latest_version.last_updated_at = None

        latest_version.published_at = None
        latest_version.published_by = None
        # Postgres will auto-populate status with default value ("Draft")
        latest_version.status = None

        db.add(latest_version)
        db.commit()
        db.refresh(latest_version)

        return latest_version


crud_versions = CRUDVersions(AtbdVersions)
