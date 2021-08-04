"""Module with Basic CRUD operations - each DB model extends this ."""
from typing import Any, Generic, List, Tuple, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session

from app.db.base import Base

from fastapi.encoders import jsonable_encoder

ModelType = TypeVar("ModelType", bound=Base)
LookupSchemaType = TypeVar("LookupSchemaType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(
    Generic[ModelType, LookupSchemaType, CreateSchemaType, UpdateSchemaType]
):
    """Generic CRUD operations base class"""

    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def exists(
        self, db_session: Session, *, obj_in: LookupSchemaType, filters={}
    ) -> bool:
        """Returns True if the requested item exists in the database"""
        obj_in_data = jsonable_encoder(obj_in)
        lookup = db_session.query(self.model).filter_by(**filters, **obj_in_data)
        return db_session.query(lookup.exists()).scalar()

    def get(
        self, db_session: Session, obj_in: LookupSchemaType, filters={}
    ) -> ModelType:
        """Select a single item by id. TODO: use query.get(id)"""
        obj_in_data = jsonable_encoder(obj_in)
        lookup = db_session.query(self.model).filter_by(**filters, **obj_in_data)
        # lookup = db_session.query(self.model).get(**obj_in.dict())
        return lookup.one()

    def get_multi(
        self, db_session: Session, *, filters={}, skip=0, limit=100
    ) -> List[ModelType]:
        """Lists (filterable) items in db"""

        return (
            db_session.query(self.model)
            .filter_by(**filters)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(
        self, db_session: Session, *, obj_in: CreateSchemaType, commit=True,
    ) -> ModelType:
        """Insert a new item into the DB"""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db_session.add(db_obj)
        if commit:
            db_session.commit()
            db_session.refresh(db_obj)
        return db_obj

    def upsert(
        self, db_session: Session, *, commit=True, obj_in: CreateSchemaType,
    ) -> None:
        """
        Create object if object does not exist in DB. Update record to new
        values if object does exist in DB. Existance determined via its primary
        key(s).
        """
        table = self.model.__table__  # type: ignore
        stmt = postgresql.insert(self.model)
        update_dict = {c.name: c for c in stmt.excluded if not c.primary_key}
        db_session.execute(
            (
                stmt.on_conflict_do_update(
                    constraint=table.primary_key, set_=update_dict or None
                )
                if update_dict
                else stmt.on_conflict_do_nothing(constraint=table.primary_key)
            ),
            [obj_in.dict()],
        )

        if commit:
            db_session.commit()

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """Queries the item in the DB, updates the class's attributes and
        re-inserts into the DB."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db_session: Session, *, id: Union[int, Tuple[Any]]) -> ModelType:
        """Deletes an item by id"""
        obj = db_session.query(self.model).get(id)
        db_session.delete(obj)
        db_session.commit()
        return obj
