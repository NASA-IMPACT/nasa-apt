"""CRUD operations for the Threads model"""
from app.crud.base import CRUDBase
from app.db.models import Thread
from app.schemas.threads import Create, Output, Update


class CRUDThreads(CRUDBase[Thread, Output, Create, Update]):
    """CRUDThreads."""

    pass


crud_threads = CRUDThreads(Thread)
