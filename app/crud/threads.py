"""CRUD operations for the Threads model"""
from typing import List

from sqlalchemy import func, orm

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import Comments, Threads
from app.schemas.threads import Create, Output, Update


class CRUDThreads(CRUDBase[Threads, Output, Create, Update]):
    """CRUDThreads."""

    def get_multi(
        self, db_session: DbSession, *, filters={}, skip=0, limit=100
    ) -> List[Output]:
        """Lists (filterable) items in db"""

        subquery = (
            db_session.query(Comments)
            .filter(Comments.thread_id == Threads.id)
            .order_by(Comments.created_at.asc())
            .limit(1)
            .subquery()
            .lateral()
        )

        count = (
            db_session.query(Threads.id, func.count(Comments.id))
            .join(Comments)
            .group_by(Threads.id)
            .subquery()
            .lateral()
        )
        return (
            db_session.query(Threads)
            .filter_by(**filters)
            .join(subquery, isouter=True)
            .options(orm.contains_eager(Threads.comments, alias=subquery))
            .join(count, isouter=True)
            .add_column(count)
            .offset(skip)
            .limit(limit)
            .all()
        )


crud_threads = CRUDThreads(Threads)
