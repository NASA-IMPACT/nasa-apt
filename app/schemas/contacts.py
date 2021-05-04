from pydantic import BaseModel, validator
from typing import Optional, List
import enum

from app.schemas.versions_contacts import ContactsBase


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


class Mechanism(BaseModel):
    # TODO: use enum from above
    mechanism_type: Optional[str]
    mechanism_value: Optional[str]


class Roles(BaseModel):
    # TODO: use enum from above
    role: Optional[str]


class Create(ContactsBase):

    mechanisms: Optional[List[Mechanism]]

    @validator("mechanisms")
    def format_contact_mechanisms(cls, v):

        s = ",".join(f'"({m.mechanism_type},{m.mechanism_value})"' for m in v)
        return f"{{{s}}}"


class Output(ContactsBase):
    id: int
    mechanisms: Optional[str]

    # TODO: I couldn't get the SQLAlchemy model working with
    # composite array and composite type, so I've left them
    # as a string representation in the datamodel and then
    # converted them to a list of Mechanism objects here.
    # This is not ideal, and this kind of formatting should happen
    # at the model level
    @validator("mechanisms")
    def format_contact_mechanisms(cls, v):
        v = [i.strip('\\"(){}') for i in v.split(",")]

        return [
            Mechanism(mechanism_type=v[i], mechanism_value=v[i + 1])
            for i in range(0, len(v) - 1, 2)
        ]


class Update(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
    mechanisms: Optional[List[Mechanism]]

    @validator("mechanisms")
    def format_contact_mechanisms(cls, v):

        s = ",".join(f'"({m.mechanism_type},{m.mechanism_value})"' for m in v)
        return f"{{{s}}}"


class Lookup(BaseModel):
    id: int


# TODO: implement filtering
class ListFilters(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
