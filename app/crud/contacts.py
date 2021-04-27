from app.crud.base import CRUDBase
from app.db.models import Contacts, AtbdVersionsContactsAssociation
from app.schemas.contacts import (
    Output,
    Create,
    Update,
    ContactsAssociation,
    ContactsAssociationLookup,
)


class CRUDContacts(CRUDBase[Contacts, Output, Create, Update]):
    pass


class CRUDContactsAssociation(
    CRUDBase[
        AtbdVersionsContactsAssociation,
        ContactsAssociation,
        ContactsAssociation,
        ContactsAssociationLookup,
    ]
):
    pass


crud_contacts = CRUDContacts(Contacts)
crud_contacts_associations = CRUDContactsAssociation(AtbdVersionsContactsAssociation)
