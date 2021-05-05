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


class AtbdVersionSummaryOutput(AtbdVersionsBase):
    major: int
    minor: int
    version: Optional[str]
    citation: Optional[dict]
    changelog: Optional[str]

    @validator("version", always=True)
    def generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"


class AtbdVersionsLink(BaseModel):

    roles: str
    atbd_version: AtbdVersionSummaryOutput

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
        print("MECHANSISM VALUE: ", v)

        v = [i.strip('\\"(){}') for i in v.split(",")]

        return [
            ContactsMechanism(mechanism_type=v[i], mechanism_value=v[i + 1])
            for i in range(0, len(v) - 1, 2)
        ]


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
