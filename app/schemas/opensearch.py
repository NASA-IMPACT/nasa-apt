"""Pydantic Models for data that get's indexed and searched in OpenSearch"""
import re
from typing import Any, List, Optional

from pydantic import BaseModel, validator

from app.schemas import document as _document
from app.schemas.document import Document
from app.schemas.versions import Keyword
from app.schemas.versions_contacts import ContactsLinkOutput


class OpensearchAtbdVersion(BaseModel):
    """Opensearch document representing an AtbdVersion"""

    major: int
    minor: int
    version: Optional[str]
    citation: Optional[dict]
    keywords: Optional[List[Keyword]] = []
    document: Optional[Document]
    doi: Optional[str]
    contacts_link: Optional[List[ContactsLinkOutput]]

    class Config:
        """Config."""

        title = "OpensearchAtbdVersion"
        orm_mode = True

    @validator("version", always=True)
    def _generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"

    @validator("document")
    def _cleanup_document(cls, v: _document.Document) -> dict:
        def _clean(d: Any) -> Any:
            if not d:
                return
            if isinstance(d, _document.PublicationReference):
                return d.dict(exclude_none=True, exclude_unset=True)
            if isinstance(d, str):

                return " ".join(re.findall(r"\w+", d))

            if isinstance(d, list):
                return [_clean(_d) for _d in d]

            if isinstance(d, _document.AlgorithmVariable):
                return [_clean(d.name), _clean(d.unit)]

            if isinstance(d, _document.DataAccessUrl):
                return [_clean(d.url), _clean(d.description)]

            if isinstance(d, _document.TextLeaf):
                return _clean(d.text)

            # Skipping equation indexing because those
            # are all latex code
            if isinstance(d, _document.EquationNode):
                return

            if isinstance(d, _document.EquationInlineNode):
                return

            if any(
                isinstance(d, i)
                for i in (
                    _document.SectionWrapper,
                    _document.DivWrapperNode,
                    _document.BaseNode,
                )
            ):
                return _clean(d.children)

            raise Exception("Unhandled Node! ", d)

        return {
            field: _clean(getattr(v, field))
            for field in v.__fields__
            if field not in ["version_description"]
        }


class OpensearchAtbd(BaseModel):
    """Opensearch document representing an ATBD"""

    id: str
    title: str
    alias: Optional[str]
    version: OpensearchAtbdVersion

    class Config:
        """Config."""

        title = "OpensearchAtbdVersion"
        orm_mode = True
