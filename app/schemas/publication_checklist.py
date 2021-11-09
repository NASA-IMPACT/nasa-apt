"""
Models for the Versions.publication_checklist field
TODO: does this have to be a separate file? Can we
include it in `./version.py`
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, validator


class SuggestedReviewer(BaseModel):
    """Suggested Reviewer"""

    name: str
    email: str


class PublicationChecklist(BaseModel):
    """Top level `publication_checklist` node"""

    suggested_reviewers: Optional[List[SuggestedReviewer]]
    review_roles: bool = False
    journal_editor: str = "Chelle Gentemann"
    author_affiliations: bool = False

    @validator("suggested_reviewers", whole=True)
    def _check_if_list_has_value(cls, value):
        return value or None
