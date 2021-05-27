"""Schemas for Contacts Model"""
import enum
from typing import List, Optional

from pydantic import BaseModel, validator

from app.schemas import versions_contacts


class ContactMechanismEnum(str, enum.Enum):
    """Enum for possible contact Mechansisms - values provided by NASA Impact."""

    direct_line = "Direct line"
    email = "Email"
    facebook = "Facebook"
    fax = "Fax"
    mobile = "Mobile"
    modem = "Modem"
    primary = "Primary"
    tdd_tty_phone = "TDD/TTY phone"
    telephone = "Telephone"
    twitter = "Twitter"
    us = "U.S."
    other = "Other"


class RolesEnum(str, enum.Enum):
    """Enum for possible roles that a contact can be assigned within the context
    of an ATBD Version - values provided by NASA Impact."""

    data_center_contact = "Data center contact"
    technical_contact = "Technical contact"
    science_contact = "Science contact"
    investigator = "Investigator"
    metadata_author = "Metadata author"
    user_services = "User services"
    science_software_development = "Science software development"


class Roles(BaseModel):
    """Roles."""

    # TODO: use enum from above
    role: Optional[str]


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
