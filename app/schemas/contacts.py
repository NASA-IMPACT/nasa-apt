"""Schemas for Contacts Model"""
from typing import List, Optional

from pydantic import BaseModel, validator

from app.schemas import versions_contacts


class Create(versions_contacts.ContactsBase):
    """Create contact - uses validator to serialize the contact mechanisms to string
    since SQLAlchemy doesn't have native support for Postgres custom types."""

    mechanisms: Optional[List[versions_contacts.ContactsMechanism]]

    @validator("mechanisms")
    def _format_contact_mechanisms(cls, v):

        s = ",".join(
            f'"(\\"{m.mechanism_type}\\",\\"{m.mechanism_value}\\")"' for m in v
        )
        return f"{{{s}}}"


class Output(versions_contacts.ContactsSummary):
    """Contacts Full Output (contains a list of Versions this contact has
    contrubuted to)."""

    atbd_versions_link: Optional[List[versions_contacts.AtbdVersionsLink]]


class Update(BaseModel):
    """Update Contact Model."""

    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
    mechanisms: Optional[List[versions_contacts.ContactsMechanism]]

    @validator("mechanisms")
    def _format_contact_mechanisms(cls, v):

        s = ",".join(
            f'"(\\"{m.mechanism_type}\\",\\"{m.mechanism_value}\\")"' for m in v
        )
        return f"{{{s}}}"


class Lookup(BaseModel):
    """Lookup Contact."""

    id: int


# TODO: implement filtering
class ListFilters(BaseModel):
    """Possible filters for listing contacts"""

    first_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
