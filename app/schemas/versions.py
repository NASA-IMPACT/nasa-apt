from pydantic import BaseModel, validator
from typing import Optional, Union, Dict, Any, List
import enum


from app.schemas.document import Document
from app.schemas import versions_contacts


class StatusEnum(enum.Enum):
    draft = "Draft"
    review = "Review"
    published = "Published"


class AtbdVersionSummaryOutput(versions_contacts.AtbdVersionsBase):

    major: int
    minor: int
    version: Optional[str]
    citation: Optional[dict]
    changelog: Optional[str]

    @validator("version", always=True)
    def generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"


class FullOutput(AtbdVersionSummaryOutput):
    document: Optional[Document]
    sections_completed: Optional[dict]
    doi: Optional[str]
    contacts_link: Optional[List[versions_contacts.ContactsLinkOutput]]


class Create(BaseModel):
    atbd_id: str


class Lookup(BaseModel):
    atbd_id: str
    major: int


class Citation(BaseModel):
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
    incomplete = "incomplete"
    complete = "complete"


class SectionsCompleted(BaseModel):
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
    minor: Optional[int]
    document: Optional[Document]
    sections_completed: Optional[dict]
    changelog: Optional[str]
    doi: Optional[str]
    citation: Optional[Citation]
    status: Optional[str]
    contacts: Optional[List[versions_contacts.ContactsLinkInput]]

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
