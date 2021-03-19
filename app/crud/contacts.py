from app.crud.base import CRUDBase
from app.db.models import Contacts
from app.schemas.contacts import Output, Create, Update


class CRUDContacts(CRUDBase[Contacts, Output, Create, Update]):
    pass


crud_contacts = CRUDContacts(Contacts)
