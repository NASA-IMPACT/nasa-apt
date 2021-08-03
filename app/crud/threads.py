"""CRUD operations for the Threads model"""
from app.crud.base import CRUDBase
from app.db.models import Threads
from app.schemas.threads import Create, Output, Update


class CRUDThreads(CRUDBase[Threads, Output, Create, Update]):
    """CRUDThreads."""

    pass


crud_threads = CRUDThreads(Threads)
