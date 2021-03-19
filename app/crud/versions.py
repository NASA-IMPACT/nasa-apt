from app.crud.base import CRUDBase
from app.db.models import AtbdVersions
from app.db.db_session import DbSession
from app.schemas.versions import FullOutput, Create, Update, StatusEnum
from app.crud.atbds import crud_atbds
from sqlalchemy import orm

from fastapi import HTTPException


class CRUDVersions(CRUDBase[AtbdVersions, FullOutput, Create, Update]):
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
        latest_version.changelog = None
        latest_version.doi = None
        latest_version.created_by = user
        # Postgres will auto-populate status with default value ("Draft")
        latest_version.status = None

        db.add(latest_version)
        db.commit()
        db.refresh(latest_version)

        return latest_version


crud_versions = CRUDVersions(AtbdVersions)
