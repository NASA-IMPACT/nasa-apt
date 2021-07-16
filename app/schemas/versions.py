"""Pydantic models for AtbdVersions"""
import enum
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, validator

from app.schemas import versions_contacts
from app.schemas.document import Document


class StatusEnum(enum.Enum):
    """Status for ATBD, values provided by NASA impact"""

    draft = "Draft"
    review = "Review"
    published = "Published"


class CognitoUser(BaseModel):
    """User contributing to an ATBD Version, as returned by Cognito"""

    username: str
    sub: str
    preferred_username: str
    email: str


class AnonymousUser(BaseModel):
    """Obfuscated user contributing to an ATBD Version"""

    preferred_username: str


class ReviewerUser(CognitoUser):
    """
    Cognito user reviewing an ATBD Version (including the user's review
    status)
    """

    # TODO: make this enum ["in_progress", "done"]
    review_status: str


class AnonymousReviewerUser(AnonymousUser):
    """
    Obfuscated user reviewing an ATBD Version (including the user's review
    status)
    """

    review_status: str


class AtbdVersionSummaryOutput(BaseModel):
    """Summary output for AtbdVersion (does NOT include full document).
    TODO: use status enum above"""

    major: int
    minor: int
    version: Optional[str]
    status: str
    published_by: Optional[str]
    published_at: Optional[datetime]
    sections_completed: Optional[dict]
    created_by: str
    created_at: datetime
    last_updated_by: str
    last_updated_at: datetime
    citation: Optional[dict]
    changelog: Optional[str]
    owner: Union[CognitoUser, AnonymousUser]
    authors: Union[List[CognitoUser], List[AnonymousUser]]
    reviewers: Union[List[ReviewerUser], List[AnonymousReviewerUser]]

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

    introduction: CompletednessEnum
    historical_perspective: CompletednessEnum
    algorithm_description: CompletednessEnum
    scientific_theory: CompletednessEnum
    scientific_theory_assumptions: CompletednessEnum
    mathematical_theory: CompletednessEnum
    mathematical_theory_assumptions: CompletednessEnum
    algorithm_input_variables: CompletednessEnum
    algorithm_output_variables: CompletednessEnum
    algorithm_implementations: CompletednessEnum
    algorithm_usage_constraints: CompletednessEnum
    performance_assessment_validation_methods: CompletednessEnum
    performance_assessment_validation_uncertainties: CompletednessEnum
    performance_assessment_validation_errors: CompletednessEnum
    data_access_input_data: CompletednessEnum
    data_access_output_data: CompletednessEnum
    data_access_related_urls: CompletednessEnum
    journal_dicsussion: CompletednessEnum
    journal_acknowledgements: CompletednessEnum
    publication_references: CompletednessEnum


class Update(BaseModel):
    """Update ATBD Version. Cannot increment minor version number AND update document content at
    the same time."""

    minor: Optional[int]
    document: Optional[Document]
    sections_completed: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]
    citation: Optional[Citation]
    status: Optional[str]
    contacts: Optional[List[versions_contacts.ContactsLinkInput]]
    owner: Optional[str]

    @validator("document", always=True)
    def _ensure_either_minor_or_document(
        cls, value: Optional[dict], values: Dict[str, Optional[Any]]
    ):
        minor = values.get("minor")
        if minor is not None and value is not None:
            raise ValueError(
                "Document data cannot be updated at the same time as the minor version number"
            )
        return value
