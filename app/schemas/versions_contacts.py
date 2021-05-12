from datetime import datetime
from pydantic import validator, BaseModel
from typing import List, Optional
import re


class AtbdLinkOutput(BaseModel):
    id: int
    title: str
    alias: Optional[str]

    class Config:
        title = "AtbdLinkOutput"
        orm_mode = True


class AtbdVersionsLinkOutput(BaseModel):
    major: int
    minor: int
    version: Optional[str]
    status: str
    atbd: AtbdLinkOutput

    @validator("version", always=True)
    def generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"

    class Config:
        title = "AtbdVersionsLinkOutput"
        orm_mode = True


class AtbdVersionsLink(BaseModel):

    roles: str
    atbd_version: AtbdVersionsLinkOutput

    @validator("roles")
    def format_roles(cls, v):

        return [i.strip('\\"(){}') for i in v.split(",") if i.strip('\\"(){}')]

    class Config:
        title = "AtbdVersionsLink"
        orm_mode = True


class ContactsBase(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    uuid: Optional[str]
    url: Optional[str]

    class Config:
        title = "Contacts"
        orm_mode = True


class ContactsMechanism(BaseModel):
    # TODO: use enum from above
    mechanism_type: Optional[str]
    mechanism_value: Optional[str]


class ContactsSummary(ContactsBase):
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
        if v is None:
            return []

        mechanisms = []

        for result in re.findall(r"(\"\()(.*?),(.*?)(\)\")", v.strip("{}")):
            mtype, mvalue = result[1].strip('\\"'), result[2].strip('\\"')

            mechanisms.append(
                ContactsMechanism(mechanism_type=mtype, mechanism_value=mvalue)
            )
        return mechanisms


class ContactsLinkOutput(BaseModel):
    contact: ContactsSummary
    roles: str

    @validator("roles")
    def format_roles(cls, v):

        return [i.strip('\\"(){}') for i in v.split(",") if i.strip('\\"(){}')]

    class Config:
        title = "ContactsLink"
        orm_mode = True


# TODO; role should be enum
class ContactsLinkInput(BaseModel):
    id: int
    roles: List[str]

    @validator("roles")
    def format_roles(cls, v):

        s = ",".join(i for i in v)
        return f"{{{s}}}"


class ContactsAssociationLookup(BaseModel):
    contact_id: int
    atbd_id: int
    major: int


class ContactsAssociation(ContactsAssociationLookup):
    roles: str