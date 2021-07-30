"""CRUD operations for the Threads model"""

import datetime

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import Comment
from app.schemas.comments import Create, Output, Update

from fastapi.encoders import jsonable_encoder


class CRUDComments(CRUDBase[Comment, Output, Create, Update]):
    """CRUDComments."""

    def create(  # type: ignore
        self, db_session: Session, comment_input: Create, user_sub: str
    ) -> Comment:
        """Insert a new comment into the DB"""
        obj_in_data = jsonable_encoder(comment_input)
        db_obj = self.model(**obj_in_data)
        db_obj.created_by = user_sub
        db_obj.last_updated_by = user_sub
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def update(  # type: ignore
        self, db: Session, db_obj: Comment, update_comment_input: Update, user_sub: str
    ) -> Comment:
        """Queries the comment in the DB, updates the class's attributes and
        re-inserts into the DB."""
        obj_data = jsonable_encoder(db_obj)
        update_data = update_comment_input.dict(skip_defaults=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db_obj.last_updated_by = user_sub
        db_obj.last_updated_at = datetime.datetime.now(datetime.timezone.utc)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    pass


crud_comments = CRUDComments(Comment)
