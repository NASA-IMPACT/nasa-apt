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
                AtbdVersions.reviewers.op("@>")(f'[{{"sub": "{sub}"}}]')
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

    # def exists(self, db: DbSession, atbd_id: str, version: int = None):  # type: ignore
    #     """Raise exception if ATBD is not found in DB, otherwise returns 200."""

    #     lookup = self._build_lookup_query(db=db, atbd_id=atbd_id, version=version)
    #     result = db.query(lookup.exists()).scalar()
    #     if not result:
    #         raise HTTPException(
    #             status_code=404, detail=f"No data found for id/alias: {atbd_id}"
    #         )

    #     return result

    # TODO: migrate this from a custom Postgres function to a SQLAlchemy
    # operation that executes within a single transaction
    def create(self, db: DbSession, atbd_input: Create, user_sub: str):  # type: ignore
        """Creates a new ATBD (using a custom Postgres function, in order to also create the
        necessary Version)"""

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

        # atbd_id, created_by, last_updated_by, major, minor
        # title = Column(String(), nullable=False)
        # alias = Column(String(), CheckConstraint("alias ~ '^[a-z0-9-]+$'"), unique=True)
        # created_by = Column(String(), nullable=False)
        # created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
        # last_updated_by = Column(String(), nullable=False)
        # last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)

        # _input = (
        #     (atbd_input.title, user)
        #     if not atbd_input.alias
        #     else (atbd_input.title, user, atbd_input.alias)
        # )
        # try:
        #     # TODO: consider switching from using a Postgres function
        #     # to performing this operation directly with SQLAlchemy ORM models
        #     function_execution_result = db.execute(
        #         select(
        #             [
        #                 column("atbds.id"),
        #                 column("atbds.title"),
        #                 column("atbds.alias"),
        #                 column("atbds.created_by"),
        #                 column("atbds.created_at"),
        #                 column("atbds.last_updated_by"),
        #                 column("atbds.last_updated_at"),
        #                 column("atbd_versions.major"),
        #                 column("atbd_versions.minor"),
        #                 column("atbd_versions.atbd_id"),
        #                 column("atbd_versions.status"),
        #                 column("atbd_versions.document"),
        #                 column("atbd_versions.sections_completed"),
        #                 column("atbd_versions.published_by"),
        #                 column("atbd_versions.published_at"),
        #                 column("atbd_versions.created_by"),
        #                 column("atbd_versions.created_at"),
        #                 column("atbd_versions.last_updated_by"),
        #                 column("atbd_versions.last_updated_at"),
        #                 column("atbd_versions.changelog"),
        #                 column("atbd_versions.doi"),
        #                 column("atbd_versions.citation"),
        #             ]
        #         ).select_from(func.apt.create_atbd_version(*_input))
        #     )

        #     db.commit()

        # except exc.IntegrityError:
        #     if atbd_input.alias:
        #         raise HTTPException(
        #             status_code=400,
        #             detail=f"An ATBD with alias {atbd_input.alias} already exists",
        #         )
        # [created_atbd] = function_execution_result

        # output = {
        #     k.split(".")[-1]: v
        #     for k, v in dict(created_atbd).items()
        #     if k.split(".")[0] == "atbds"
        # }
        # output["versions"] = [
        #     {
        #         k.split(".")[-1]: v
        #         for k, v in dict(created_atbd).items()
        #         if k.split(".")[0] == "atbd_versions"
        #     }
        # ]
        # return output

    def remove(self, db: DbSession, atbd_id: str) -> Atbds:  # type: ignore
        """Deletes an ATBD."""
        atbd = self.get(db=db, atbd_id=atbd_id)
        db.delete(atbd)
        db.commit()
        return atbd


crud_atbds = CRUDAtbds(Atbds)
