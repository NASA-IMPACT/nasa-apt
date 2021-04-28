from datetime import datetime
from app.schemas import contacts
from pydantic import BaseModel, validator
from typing import Optional, Union, Dict, Any, List
import enum
from app.schemas.document import Document


class StatusEnum(enum.Enum):
    draft = "Draft"
    review = "Review"
    published = "Published"


# TODO: use status enum above
class OutputBase(BaseModel):
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


class SummaryOutput(OutputBase):
    major: int
    minor: int
    version: Optional[str]
    citation: Optional[dict]
    changelog: Optional[str]

    @validator("version", always=True)
    def generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"


class FullOutput(SummaryOutput):
    document: Optional[Document]
    sections_completed: Optional[dict]
    doi: Optional[str]
    contacts_link: Optional[List[contacts.ContactsLinkOutput]]


class Create(BaseModel):
    atbd_id: str


class Lookup(BaseModel):
    atbd_id: str
    major: int


class Update(BaseModel):
    minor: Optional[int]
    document: Optional[Document]
    sections_completed: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]
    citation: Optional[dict]
    status: Optional[str]
    contacts: Optional[List[contacts.ContactsLinkInput]]

    @validator("document", always=True)
    def ensure_either_minor_or_document(
        cls, value: Optional[dict], values: Dict[str, Optional[Any]]
    ):
        minor = values.get("minor")
        if minor is not None and value is not None:
            raise ValueError(
                "Document data cannot be updated at the same time as the minor version number"
            )
        return value


class JSONFieldUpdate(BaseModel):
    key: str
    value: Union[str, dict]

