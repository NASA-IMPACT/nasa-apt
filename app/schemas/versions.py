"""Pydantic models for AtbdVersions"""
import enum
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, validator

from app.schemas import versions_contacts
from app.schemas.document import Document, DocumentSummary
from app.schemas.publication_checklist import PublicationChecklist
from app.schemas.users import (
    AnonymousReviewerUser,
    AnonymousUser,
    CognitoUser,
    ReviewerUser,
)


class StatusEnum(enum.Enum):
    """Status for ATBD, values provided by NASA impact"""

    draft = "Draft"
    review = "Review"
    published = "Published"


class AtbdVersionSummaryOutput(BaseModel):
    """Summary output for AtbdVersion (does NOT include full document).
    TODO: use status enum above"""

    major: int
    minor: int
    version: Optional[str]
    status: str
    published_by: Optional[Union[CognitoUser, AnonymousUser]]
    published_at: Optional[datetime]
    sections_completed: Optional[dict]
    created_by: Union[CognitoUser, AnonymousUser]
    created_at: datetime
    last_updated_by: Union[CognitoUser, AnonymousUser]
    last_updated_at: datetime
    citation: Optional[dict]
    document: Optional[DocumentSummary]
    owner: Union[CognitoUser, AnonymousUser]
    authors: Union[List[CognitoUser], List[AnonymousUser]]
    reviewers: Union[List[ReviewerUser], List[AnonymousReviewerUser]]
    journal_status: Optional[str]

    @validator("version", always=True)
    def _generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"

    class Config:
        """Config."""

        title = "AtbdVersion"
        orm_mode = True


class FullOutput(AtbdVersionSummaryOutput):
    """Version output, including document, sections completed, doi, and contacts"""

    document: Optional[Document]
    publication_checklist: Optional[PublicationChecklist]
    sections_completed: Optional[dict]
    doi: Optional[str]
    contacts_link: Optional[List[versions_contacts.ContactsLinkOutput]]


class Create(BaseModel):
    """Create new version (empty since new versions get created blank and then their content gets updated)"""

    atbd_id: str
    major: int
    minor: int
    status: str  # TODO: make this enum
    document: Document
    publication_checklist: PublicationChecklist
    created_by: str
    last_updated_by: str
    owner: str


class Lookup(BaseModel):
    """Atbd Version lookup model"""

    atbd_id: str
    major: int


class Citation(BaseModel):
    """Atbd Version citation"""

    creators: Optional[str]
    editors: Optional[str]
    title: Optional[str]
    series_name: Optional[str]
    release_date: Optional[str]
    release_place: Optional[str]
    publisher: Optional[str]
    version: Optional[str]
    issue: Optional[str]
    additional_details: Optional[str]
    online_resource: Optional[str]


class CompletednessEnum(str, enum.Enum):
    """Enum for Atbd verions sections completedness. TODO: use this enum in SectionsCompleted below"""

    incomplete = "incomplete"
    complete = "complete"


class SectionsCompleted(BaseModel):
    """Sections completed - each value is a str equal to either `incomplete` or `complete`.
    Gets set by the user"""

    version_description: CompletednessEnum
    citation: CompletednessEnum
    contacts: CompletednessEnum
    introduction: CompletednessEnum
    context_background: CompletednessEnum
    scientific_theory: CompletednessEnum
    mathematical_theory: CompletednessEnum
    input_variables: CompletednessEnum
    output_variables: CompletednessEnum
    constraints: CompletednessEnum
    validation: CompletednessEnum
    algorithm_availability: CompletednessEnum
    data_access_input_data: CompletednessEnum
    data_access_output_data: CompletednessEnum
    data_access_related_urls: CompletednessEnum
    abstract: CompletednessEnum
    discussion: CompletednessEnum
    acknowledgements: CompletednessEnum


class Update(BaseModel):
    """Update ATBD Version. Cannot increment minor version number AND update document content at
    the same time."""

    document: Optional[Document]
    publication_checklist: Optional[PublicationChecklist]
    sections_completed: Optional[dict]
    doi: Optional[str]
    citation: Optional[Citation]
    status: Optional[str]
    contacts: Optional[List[versions_contacts.ContactsLinkInput]]
    owner: Optional[str]
    authors: Optional[List[str]]
    reviewers: Optional[List[str]]
    journal_status: Optional[str]


class AdminUpdate(Update):
    """Update model when update comes from the API
    through the /events endpoint"""

    minor: Optional[int]
    published_by: Optional[str]
    published_at: Optional[datetime]
    last_updated_by: str
    last_updated_at: datetime
    # reviewers gets re-defined here as a list of Dict
    # since from the API side, each reviewer should have
    # a review status associated with their user sub
    reviewers: Optional[List[Dict[str, str]]]  # type: ignore
