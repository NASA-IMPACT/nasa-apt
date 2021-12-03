"""CRUD operations for the Threads model"""


from app.crud.base import CRUDBase
from app.db.models import Comments
from app.schemas.comments import Create, Output, Update


class CRUDComments(CRUDBase[Comments, Output, Create, Update]):
    """CRUDComments."""

    pass


crud_comments = CRUDComments(Comments)
