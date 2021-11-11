"""Pydantic models for AtbdVersions"""
from __future__ import annotations

import enum
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, validator

# import document as _document to avoid namespace collision with the
# `document` field of the AtbdVersion's SummaryOutput and FullOutput classes
from app.schemas import document as _document
from app.schemas import versions_contacts
from app.schemas.users import (
    AnonymousReviewerUser,
    AnonymousUser,
    CognitoUser,
    ReviewerUser,
)


class JournalStatusEnum(str, enum.Enum):
    """Status for Journal ATBD, values provided by NASA impact"""

    NO_PUBLICATION = "NO_PUBLICATION"
    PUBLICATION_INTENDED = "PUBLICATION_INTENDED"
    PUBLICATION_REQUESTED = "PUBLICATION_REQUESTED"
    PUBLISHED = "PUBLISHED"


class StatusEnum(str, enum.Enum):
    """Status for ATBD, values provided by NASA impact"""

    DRAFT = "DRAFT"
    CLOSED_REVIEW_REQUESTED = "CLOSED_REVIEW_REQUESTED"
    CLOSED_REVIEW = "CLOSED_REVIEW"
    OPEN_REVIEW = "OPEN_REVIEW"
    PUBLICATION_REQUESTED = "PUBLICATION_REQUESTED"
    PUBLICATION = "PUBLICATION"
    PUBLISHED = "PUBLISHED"


class SuggestedReviewer(BaseModel):
    """Suggested Reviewer"""

    name: str
    email: str


class PublicationChecklist(BaseModel):
    """Top level `publication_checklist` node"""

    suggested_reviewers: Optional[List[SuggestedReviewer]]
    review_roles: bool = False
    journal_editor: str = "Chelle Gentemann"
    author_affirmations: bool = False

    @validator("suggested_reviewers", whole=True)
    def _check_if_list_has_value(cls, value):
        return value or None


class PublicationUnits(BaseModel):
    """
    Publication Units (contains numbers of words, images and tables)
    """

    words: int = 0
    images: int = 0
    tables: int = 0

    def __add__(self, d: PublicationUnits) -> PublicationUnits:
        """Overloaded `+` operator so that I can combine the publication
        units for 2 leaves (or sub-trees) within a document with a single
        addition operation. Eg:
        >>> leaf_1 = PublicationUnits(words=2, images=2, tables=2)
        >>> leaf_2 = PublicationUnits(words=4, images=4, tables=4)

        >>> sub_tree = leaf_1 + leaf_2
        >>> sub_tree
        PublicationUnits(words=6, images=6, tables=6)
        """
        return PublicationUnits(
            words=self.words + d.words,
            images=self.images + d.images,
            tables=self.tables + d.tables,
        )

    def __radd__(self, d: PublicationUnits) -> PublicationUnits:
        """Overloaded `__radd__` operand (reverse add) in order to enable
        the `sum()` operation (which attempts to add items in reverse if
        it can resolve the types going forward)
        >>> leaf_1 = PublicationUnits(words=2, images=2, tables=2)
        >>> leaf_2 = PublicationUnits(words=4, images=4, tables=4)
        >>> leaf_3 = PublicationUnits(words=6, images=6, tables=6)

        >>> sub_tree = sum([leaf_1, leaf_2, leaf_3])
        >>> sub_tree
        PublicationUnits(words=12, images=12, tables=12ß)

        """
        return PublicationUnits(
            words=d + self.words, images=d + self.images, tables=d + self.tables,
        )


class AtbdVersionSummaryOutput(BaseModel):
    """Summary output for AtbdVersion (does NOT include full document).
    TODO: use status enum above"""

    major: int
    minor: int
    version: Optional[str]
    status: StatusEnum
    published_by: Optional[Union[CognitoUser, AnonymousUser]]
    published_at: Optional[datetime]
    sections_completed: Optional[dict]
    created_by: Union[CognitoUser, AnonymousUser]
    created_at: datetime
    last_updated_by: Union[CognitoUser, AnonymousUser]
    last_updated_at: datetime
    citation: Optional[dict]
    document: Optional[_document.DocumentSummary]
    owner: Union[CognitoUser, AnonymousUser]
    authors: Union[List[CognitoUser], List[AnonymousUser]]
    reviewers: Union[List[ReviewerUser], List[AnonymousReviewerUser]]
    journal_status: Optional[JournalStatusEnum]

    @validator("version", always=True)
    def _generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"

    class Config:
        """Config."""

        title = "AtbdVersion"
        orm_mode = True


class FullOutput(AtbdVersionSummaryOutput):
    """Version output, including document, sections completed, doi, and contacts"""

    document: Optional[_document.Document]
    publication_checklist: Optional[PublicationChecklist]
    sections_completed: Optional[dict]
    doi: Optional[str]
    contacts_link: Optional[List[versions_contacts.ContactsLinkOutput]]
    publication_units: Optional[PublicationUnits]

    @validator("publication_units", always=True)
    def _generate_publication_units(cls, v, values: Dict[str, Any]) -> PublicationUnits:
        if not values.get("document"):
            return PublicationUnits(images=0, tables=0, words=0)

        # "words" field is initialized to 58, the number of
        # words in all of the titles of the journal sections
        # TODO: calculate this dynamically based on the sections
        # in the document
        # The following line is ignore because mypy assumes that `sum()`
        # returns a numerical type, and complains that PublicationUnits()
        # can't be added to the PublicationUnits type
        return PublicationUnits(
            images=0, tables=0, words=58
        ) + cls._count_images_tables_words(  # type: ignore
            values["document"]
        )

    def _count_images_tables_words(
        doc: _document.Document,
    ) -> PublicationUnits:  # noqa: C901
        def _helper(d: Any) -> PublicationUnits:
            if not d or any(
                isinstance(d, i)
                for i in (bool, _document.PublicationReference, _document.ReferenceNode)
            ):
                return PublicationUnits(images=0, tables=0, words=0)

            if isinstance(d, _document.AlgorithmVariable):
                return _helper(d.name) + _helper(d.unit)

            if isinstance(d, _document.DataAccessUrl):
                return _helper(d.url) + _helper(d.description)

            if isinstance(d, _document.TextLeaf):
                return _helper(d.text)

            if isinstance(d, _document.EquationNode):
                return PublicationUnits(images=0, tables=0, words=1)

            if isinstance(d, _document.TableNode):
                return PublicationUnits(images=0, tables=1, words=0)

            if isinstance(d, _document.ImageNode):
                return PublicationUnits(images=1, tables=0, words=0)

            if isinstance(d, str):
                return PublicationUnits(
                    images=0, tables=0, words=len(re.findall(r"\w+", d))
                )

            if isinstance(d, list):
                # the following line is ignored for the same reason as
                # above - mypy assumes that sum returns a numerical type
                # which is incompatible with the return type of the method
                return sum(_helper(_d) for _d in d)  # type: ignore

            if any(
                isinstance(d, i)
                for i in (
                    _document.SectionWrapper,
                    _document.DivWrapperNode,
                    _document.BaseNode,
                )
            ):
                return _helper(d.children)

            raise Exception("Unhandled Node!")

        # MyPy ignore that the overridden `+` operator makes it such that
        # the `sum()` operation now returns a PublicationUnits class
        # instead of int
        return sum(  # type: ignore
            [
                _helper(getattr(doc, field))
                for field in doc.__fields__
                if field not in ["version_description", "plain_summary"]
            ]
        )


class Create(BaseModel):
    """Create new version (empty since new versions get created blank and then their content gets updated)"""

    atbd_id: str
    major: int
    minor: int
    status: StatusEnum
    document: _document.Document
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

    document: Optional[_document.Document]
    publication_checklist: Optional[PublicationChecklist]
    sections_completed: Optional[dict]
    doi: Optional[str]
    citation: Optional[Citation]
    status: Optional[StatusEnum]
    contacts: Optional[List[versions_contacts.ContactsLinkInput]]
    owner: Optional[str]
    authors: Optional[List[str]]
    reviewers: Optional[List[str]]
    journal_status: Optional[JournalStatusEnum]


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
