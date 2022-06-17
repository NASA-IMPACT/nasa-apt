"""CRUD operations for ATBD Versions."""

from typing import Union

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import Atbds, AtbdVersions
from app.schemas.versions import Create, FullOutput, Update


class CRUDVersions(CRUDBase[AtbdVersions, FullOutput, Create, Update]):
    """CRUDVersions"""

    def set_lock(
        self, db: Session, *, version: AtbdVersions, locked_by: Union[str, None]
    ):
        """Custom method used instead of CRUDBase update, which ignores
        None type fields"""

        version.locked_by = locked_by

        db.add(version)
        db.commit()
        db.refresh(version)
        return version

    def delete(self, db: DbSession, atbd: Atbds, version: AtbdVersions):
        """
        Delete atbd version - if it was the last AtbdVersion in the Atbd,
        delete the Atbd as well.
        """
        db.delete(version)

        db.commit()
        db.refresh(atbd)

        if len(atbd.versions) == 0:
            db.delete(atbd)
            db.commit()
        return {}


crud_versions = CRUDVersions(AtbdVersions)
