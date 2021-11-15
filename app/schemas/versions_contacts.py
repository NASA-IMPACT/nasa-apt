"""Versions -- Contacts relationship classes"""

import re
from enum import Enum, unique
from typing import List, Optional

from pydantic import BaseModel, validator


@unique
class ContactMechanismEnum(str, Enum):
    """Enum for possible contact Mechansisms - values provided by NASA Impact."""

    DIRECT_LINE = "Direct line"
    EMAIL = "Email"
    FACEBOOK = "Facebook"
    FAX = "Fax"
    MOBILE = "Mobile"
    MODEM = "Modem"
    PRIMARY = "Primary"
    TDD_TTY_PHONE = "TDD/TTY phone"
    TELEPHONE = "Telephone"
    TWITTER = "Twitter"
    US = "U.S."
    OTHER = "Other"


@unique
class RolesEnum(str, Enum):
    """Enum for possible roles that a contact can be assigned within the context
    of an ATBD Version - values provided by NASA Impact."""

    WRITING_ORIGINAL_DRAFT = "Writing – original draft"
    WRITING_REVIEW_EDITING = "Writing – review & editing"
    VALIDATION = "Validation"
    DATA_CURATION = "Data curation"
    CONCEPTUALIZATION = "Conceptualization"
    METHODOLOGY = "Methodology"
    VISUALIZATION = "Visualization"
    FORMAL_ANALYSIS = "Formal analysis"
    SOFTWARE = "Software"
    RESOURCES = "Resources"
    PROJECT_ADMINISTRATION = "Project administration"
    SUPERVISION = "Supervision"
    INVESTIGATION = "Investigation"
    FUNDING_ACQUISITION = "Funding acquisition"
    CORRESPONDING_AUTHOR = "Corresponding Author"


class AtbdLinkOutput(BaseModel):
    """Links from Versions to Atbd (many-to-one)"""

    id: int
    title: str
    alias: Optional[str]

    class Config:
        """Config."""

        title = "AtbdLinkOutput"
        orm_mode = True


class AtbdVersionsLinkOutput(BaseModel):
    """Links from Atbd to Version (one-to-many)"""

    major: int
    minor: int
    version: Optional[str]
    status: str
    atbd: AtbdLinkOutput

    @validator("version", always=True)
    def _generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"

    class Config:
        """Config."""

        title = "AtbdVersionsLinkOutput"
        orm_mode = True


class AtbdVersionsLink(BaseModel):
    """Links from Contact to Versions (many-to-many)"""

    # No need to set a default value for roles or affiliations here since
    # the database already sets an empty list default value
    roles: str
    affiliations: str
    atbd_version: AtbdVersionsLinkOutput

    @validator("roles", "affiliations")
    def _format_roles(cls, v):
        return [i.strip('\\"(){}') for i in v.split(",") if i.strip('\\"(){}')]

    class Config:
        """Config."""

        title = "AtbdVersionsLink"
        orm_mode = True


class ContactsBase(BaseModel):
    """
    Contact Base Model. Placed in this class to avoid circluar imports where both Contacts and
    Versions have to import from each other, since the models are self refential.
    """

    first_name: str
    middle_name: Optional[str]
    last_name: str
    uuid: Optional[str]
    url: Optional[str]

    class Config:
        """Config."""

        title = "Contacts"
        orm_mode = True


class ContactsMechanism(BaseModel):
    """Contact Mechanism"""

    # TODO: use enum from above
    mechanism_type: Optional[ContactMechanismEnum]
    mechanism_value: Optional[str]


class ContactsSummary(ContactsBase):
    """Contacts summary output (doesn't include version)"""

    id: int
    mechanisms: Optional[str]
    # TODO: I couldn't get the SQLAlchemy model working with
    # composite array and composite type, so I've left them
    # as a string representation in the datamodel and then
    # converted them to a list of Mechanism objects here.
    # This is not ideal, and this kind of formatting should happen
    # at the model level

    @validator("mechanisms", always=True)
    def _format_contact_mechanisms(cls, v):

        mechanisms = []

        for result in re.findall(r"(\"\()(.*?),(.*?)(\)\")", v.strip("{}")):
            mtype, mvalue = result[1].strip('\\"'), result[2].strip('\\"')

            mechanisms.append(
                ContactsMechanism(mechanism_type=mtype, mechanism_value=mvalue)
            )
        return mechanisms


class ContactsLinkOutput(BaseModel):
    """Link from Version to Contact"""

    contact: ContactsSummary
    roles: Optional[str]
    affiliations: Optional[str]

    @validator("roles", "affiliations", always=True)
    def _format_roles(cls, v, values, field):
        if not v:
            return []
        return [i.strip('\\"(){}') for i in v.split(",") if i.strip('\\"(){}')]

    class Config:
        """Config."""

        title = "ContactsLink"
        orm_mode = True


class ContactsLinkInput(BaseModel):
    """Link from Version to Contact. This is a separate class in order to serialize
    and de-serialize the `roles` object, which gets saved as a string type in the Postgres
    because SQLAlchemy doesn't have native support for custom types
    """

    id: int
    roles: Optional[List[RolesEnum]]
    affiliations: Optional[List[str]]

    @validator("roles", "affiliations", always=True)
    def _format_roles(cls, v):
        if not v:
            v = []

        return f"{{{','.join(i for i in v)}}}"


class ContactsAssociationLookup(BaseModel):
    """Lookup model for a contact/version association object"""

    contact_id: int
    atbd_id: int
    major: int


class ContactsAssociation(ContactsAssociationLookup):
    """Contact Association output model"""

    roles: str
    affiliations: str
