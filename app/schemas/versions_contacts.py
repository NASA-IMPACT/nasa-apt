from datetime import datetime
from pydantic import validator, BaseModel
from typing import List, Optional


# TODO: use status enum above
class AtbdVersionsBase(BaseModel):
    status: str
    published_by: Optional[str]
    published_at: Optional[datetime]
    sections_completed: Optional[dict]
    created_by: str
    created_at: datetime
    last_updated_by: str
    last_updated_at: datetime

    class Config:
        title = "AtbdVersion"
        orm_mode = True


class AtbdVersionsLink(BaseModel):

    roles: str
    atbd_version: AtbdVersionsBase

    @validator("roles")
    def format_roles(cls, v):

        return [i.strip('\\"(){}') for i in v.split(",")]

    class Config:
        title = "AtbdVersionsLink"
        orm_mode = True


class ContactsBase(BaseModel):
    first_name: str
    middle_name: Optional[str]
    last_name: str
    uuid: Optional[str]
    url: Optional[str]
    # atbd_versions_link: Optional[AtbdVersionsLink]

    class Config:
        title = "Contacts"
        orm_mode = True


class ContactsLinkOutput(BaseModel):
    contact: ContactsBase
    roles: str

    @validator("roles")
    def format_roles(cls, v):

        return [i.strip('\\"(){}') for i in v.split(",")]

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
