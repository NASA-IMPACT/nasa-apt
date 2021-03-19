from pydantic import BaseModel
from typing import Optional, List
import enum


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


class Mechanisms(BaseModel):
    # TODO: use enum from above
    contact_mechanism_type: Optional[str]
    mechanism_value: Optional[str]
    pass


class Roles(BaseModel):
    # TODO: use enum from above
    role: Optional[str]
    pass


class Create(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    uuid: Optional[str]
    url: Optional[str]
    mechanisms: List[Mechanisms]
    roles: List[Roles]
    title: Optional[str]


class Output(Create):
    id: int


class Update(BaseModel):
    first_name: Optional[str]
    middle_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
    mechanisms: Optional[List[Mechanisms]]
    roles: Optional[List[Roles]]
    title: Optional[Optional[str]]


class Lookup(BaseModel):
    id: int


# TODO: implement filtering based on _mechanism in Contact.mechanisms: []
# TODO: implement filtering based on _role in Contact.roles: []
class ListFilters(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    uuid: Optional[str]
    url: Optional[str]
    title: Optional[str]
