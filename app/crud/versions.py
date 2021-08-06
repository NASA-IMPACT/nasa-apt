"""CRUD operations for ATBD Versions."""

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import Atbds, AtbdVersions
from app.schemas.versions import Create, FullOutput, Update


class CRUDVersions(CRUDBase[AtbdVersions, FullOutput, Create, Update]):
    """CRUDVersions"""

    def delete(self, db: DbSession, atbd: Atbds, version: AtbdVersions):
        db.delete(version)

        db.commit()
        db.refresh(atbd)

        if len(atbd.versions) == 0:
            db.delete(atbd)
            db.commit()
        return {}


crud_versions = CRUDVersions(AtbdVersions)
