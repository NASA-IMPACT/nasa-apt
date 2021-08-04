"""CRUD operations for the Threads model"""
from typing import List

from app.crud.base import CRUDBase
from app.db.db_session import DbSession
from app.db.models import Threads
from app.schemas.threads import Create, Output, Update


class CRUDThreads(CRUDBase[Threads, Output, Create, Update]):
    """CRUDThreads."""

    def get_multi(
        self, db_session: DbSession, *, filters={}, skip=0, limit=100
    ) -> List[Output]:
        """Lists (filterable) items in db"""

        # subquery = (
        #     db_session.select(
        #         (articles_table.c.title, articles_table.c.views),
        #     )
        #     .where(
        #         articles_table.c.author_id == authors_table.c.id,
        #     )
        #     .order_by(
        #         articles_table.c.views.desc(),
        #     )
        #     .limit(3)
        #     .lateral("top_3_articles")
        # )

        # query = db_session.select(
        #     (authors_table.c.name, subquery.c.title, subquery.c.views),
        # ).select_from(
        #     authors_table.join(subquery, db_session.true()),
        # )

        return (
            db_session.query(self.model)
            .filter_by(**filters)
            .offset(skip)
            .limit(limit)
            .all()
        )


crud_threads = CRUDThreads(Threads)
