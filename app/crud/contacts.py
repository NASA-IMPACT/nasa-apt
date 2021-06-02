"""CRUD operations for the Contacts model"""
from app.crud.base import CRUDBase
from app.db.models import AtbdVersionsContactsAssociation, Contacts
from app.schemas.contacts import Create, Output, Update
from app.schemas.versions_contacts import ContactsAssociation, ContactsAssociationLookup


class CRUDContacts(CRUDBase[Contacts, Output, Create, Update]):
    """CRUDContacts."""

    pass


class CRUDContactsAssociation(
    CRUDBase[
        AtbdVersionsContactsAssociation,
        ContactsAssociation,
        ContactsAssociation,
        ContactsAssociationLookup,
    ]
):
    """CRUDContactsAssociation."""

    pass


crud_contacts = CRUDContacts(Contacts)
crud_contacts_associations = CRUDContactsAssociation(AtbdVersionsContactsAssociation)
