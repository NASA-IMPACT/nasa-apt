"""CRUD Operations for Atbds model"""
from sqlalchemy import exc, func, orm

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import Atbds, AtbdVersions
from app.schemas.atbds import Create, FullOutput, Update

from fastapi import HTTPException


class CRUDAtbds(CRUDBase[Atbds, FullOutput, Create, Update]):
    """CRUDAtbds."""

    def scan(self, db: DbSession, status: str = None, role: str = None):
        """List operation - uses orm.contains_earger to join Versions only once,
        as opposed to re-loading the relation everytime the model is loaded."""
        query = (
            db.query(Atbds)
            .join(AtbdVersions, Atbds.id == AtbdVersions.atbd_id)
            .options(orm.contains_eager(Atbds.versions))
        )

        if status:
            query = query.filter(AtbdVersions.status == status)

        if role:
            [role, sub] = role.split(":")
        if role == "owner":
            query = query.filter(AtbdVersions.owner == sub)
        if role == "author":
            query = query.filter(AtbdVersions.authors.any(sub))
        if role == "reviewer":
            query = query.filter(
                AtbdVersions.reviewers.op("&&")(
                    [
                        {"sub": f"{sub}", "review_status": "IN_PROGRESS"},
                        {"sub": f"{sub}", "review_status": "DONE"},
                    ]
                )
            )
        return query.all()

    def _build_lookup_query(self, db: DbSession, atbd_id: str, version: int = None):
        try:
            int(atbd_id)
            alias = None
        except ValueError:
            alias = atbd_id

        query = (
            db.query(Atbds)
            .join(AtbdVersions, Atbds.id == AtbdVersions.atbd_id)
            .options(orm.contains_eager(Atbds.versions))
        )

        if version == -1:

            subquery = db.query(func.max(AtbdVersions.major)).filter(
                AtbdVersions.atbd_id
                == (
                    db.query(Atbds.id).filter(Atbds.alias == alias)
                    if alias
                    else atbd_id
                )
            )

            query = query.filter(AtbdVersions.major == subquery)

        elif version:
            query = query.filter(AtbdVersions.major == version)

        query = (
            query.filter(Atbds.alias == alias)
            if alias
            else query.filter(Atbds.id == atbd_id)
        )

        return query

    def get(self, db: DbSession, atbd_id: str, version: int = None):
        """Query a single ATBD."""
        query = self._build_lookup_query(db=db, atbd_id=atbd_id, version=version)
        try:
            return query.one()
        except exc.SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=404, detail=f"No data found for id/alias: {atbd_id}"
            )

    def create(  # type: ignore
        self, db: DbSession, atbd_input: Create, user_sub: str
    ) -> Atbds:
        """Creates a new Atbd along with an Atbd Version v1.0. It's necessary to add
        and commit the Atbd before creating the Atbd Version because the Atbd's id,
        which needs to be saved as a field of the AtbdVersion, gets generated when
        serializing the Atbd to the database."""

        atbd = Atbds(
            **atbd_input.dict(), created_by=user_sub, last_updated_by=user_sub,
        )
        db.add(atbd)
        db.commit()
        db.refresh(atbd)
        version = AtbdVersions(
            atbd_id=atbd.id,
            created_by=user_sub,
            last_updated_by=user_sub,
            owner=user_sub,
            major=1,
            minor=0,
        )
        db.add(version)
        db.commit()
        db.refresh(atbd)
        return atbd

    def remove(self, db: DbSession, atbd_id: str) -> Atbds:  # type: ignore
        """Deletes an ATBD."""
        atbd = self.get(db=db, atbd_id=atbd_id)
        db.delete(atbd)
        db.commit()
        return atbd


crud_atbds = CRUDAtbds(Atbds)
