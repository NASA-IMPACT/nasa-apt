from pydantic import BaseModel, validator
from typing import Optional, List
import enum

from app.schemas.versions_contacts import (
    ContactsBase,
    ContactsSummary,
    ContactsMechanism,
    AtbdVersionsLink,
)


class ContactMechanismEnum(str, enum.Enum):
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
    data_center_contact = "Data center contact"
    technical_contact = "Technical contact"
    science_contact = "Science contact"
    investigator = "Investigator"
    metadata_author = "Metadata author"
    user_services = "User services"
    science_software_development = "Science software development"


class Roles(BaseModel):
    # TODO: use enum from above
    role: Optional[str]


class Create(ContactsBase):

    mechanisms: Optional[List[ContactsMechanism]]

    @validator("mechanisms")
    def format_contact_mechanisms(cls, v):

        s = ",".join(
            f'"(\\"{m.mechanism_type}\\",\\"{m.mechanism_value}\\")"' for m in v
        )
        return f"{{{s}}}"


class Output(ContactsSummary):

    atbd_versions_link: Optional[List[AtbdVersionsLink]]


class Update(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
    mechanisms: Optional[List[ContactsMechanism]]

    @validator("mechanisms")
    def format_contact_mechanisms(cls, v):

        s = ",".join(
            f'"(\\"{m.mechanism_type}\\",\\"{m.mechanism_value}\\")"' for m in v
        )
        return f"{{{s}}}"


class Lookup(BaseModel):
    id: int


# TODO: implement filtering
class ListFilters(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
