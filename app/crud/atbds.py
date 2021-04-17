from app.crud.base import CRUDBase
from app.crud import utils
from app.db.models import Atbds, AtbdVersions, AtbdVersionsContactsAssociation
from app.db.db_session import DbSession
from app.schemas.atbds import FullOutput, Create, Update
from sqlalchemy import exc, column, select, func, orm
from fastapi import HTTPException


class CRUDAtbds(CRUDBase[Atbds, FullOutput, Create, Update]):
    def scan(self, db: DbSession):
        query = (
            db.query(Atbds)
            .join(AtbdVersions, Atbds.id == AtbdVersions.atbd_id)
            .options(orm.contains_eager(Atbds.versions))
        )

        return query.all()

    def _build_lookup_query(self, db: DbSession, atbd_id: str, version: int = None):
        query = (
            db.query(Atbds)
            .join(AtbdVersions, Atbds.id == AtbdVersions.atbd_id)
            .options(orm.contains_eager(Atbds.versions))
        )

        if version == -1:
            subquery = db.query(func.max(AtbdVersions.major))
            query = query.filter(AtbdVersions.major == subquery)

            [subquery] = utils.add_id_or_alias_filter(atbd_id, subquery)

        elif version:
            query = query.filter(AtbdVersions.major == version)

        [query] = utils.add_id_or_alias_filter(atbd_id, query)
        return query

    def get(self, db: DbSession, atbd_id: str, version: int = None):
        query = self._build_lookup_query(db=db, atbd_id=atbd_id, version=version)
        try:
            return query.one()
        except exc.SQLAlchemyError as e:
            print(e)
            raise HTTPException(
                status_code=404, detail=f"No data found for id/alias: {atbd_id}"
            )

    def exists(self, db: DbSession, atbd_id: str, version: int = None):

        lookup = self._build_lookup_query(db=db, atbd_id=atbd_id, version=version)
        result = db.query(lookup.exists()).scalar()
        if not result:
            raise HTTPException(
                status_code=404, detail=f"No data found for id/alias: {atbd_id}"
            )
        return result

    def create(self, db: DbSession, atbd_input: Create, user: str):
        # User shows up twice in input parameters, as it sets the value

        _input = (
            (atbd_input.title, user)
            if not atbd_input.alias
            else (atbd_input.title, user, atbd_input.alias)
        )
        try:
            # TODO: consider switching from using a Postgres function
            # to performing this operation directly with SQLAlchemy ORM models
            function_execution_result = db.execute(
                select(
                    [
                        column("atbds.id"),
                        column("atbds.title"),
                        column("atbds.alias"),
                        column("atbds.created_by"),
                        column("atbds.created_at"),
                        column("atbds.last_updated_by"),
                        column("atbds.last_updated_at"),
                        column("atbd_versions.major"),
                        column("atbd_versions.minor"),
                        column("atbd_versions.atbd_id"),
                        column("atbd_versions.status"),
                        column("atbd_versions.document"),
                        column("atbd_versions.sections_completed"),
                        column("atbd_versions.published_by"),
                        column("atbd_versions.published_at"),
                        column("atbd_versions.created_by"),
                        column("atbd_versions.created_at"),
                        column("atbd_versions.last_updated_by"),
                        column("atbd_versions.last_updated_at"),
                        column("atbd_versions.changelog"),
                        column("atbd_versions.doi"),
                        column("atbd_versions.citation"),
                    ]
                ).select_from(func.apt.create_atbd_version(*_input))
            )

            db.commit()

        except exc.IntegrityError as e:
            print(e)
            db.rollback()
            if atbd_input.alias:
                raise HTTPException(
                    status_code=400,
                    detail=f"An ATBD with alias {atbd_input.alias} already exists",
                )
        [created_atbd] = function_execution_result

        output = {
            k.split(".")[-1]: v
            for k, v in dict(created_atbd).items()
            if k.split(".")[0] == "atbds"
        }
        output["versions"] = [
            {
                k.split(".")[-1]: v
                for k, v in dict(created_atbd).items()
                if k.split(".")[0] == "atbd_versions"
            }
        ]
        return output


crud_atbds = CRUDAtbds(Atbds)
