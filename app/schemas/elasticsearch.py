"""Pydantic Models for data that get's indexed and searched in ElasticSearch"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.schemas.document import Document


class ElasticsearchAtbdVersion(BaseModel):
    """Elasticsearch document representing an AtbdVersion"""

    major: int
    minor: int
    version: Optional[str]
    # They should all have status == "PUBLISHED"
    # status: str
    # published_by: Optional[str]
    # published_at: Optional[datetime]
    # created_by: str
    # created_at: datetime
    # last_updated_by: str
    # last_updated_at: datetime
    citation: Optional[dict]
    document: Optional[Document]
    doi: Optional[str]
    changelog: Optional[str]

    class Config:
        """Config."""

        title = "ElasticsearchAtbdVersion"
        orm_mode = True

    @validator("version", always=True)
    def _generate_semver(cls, v, values) -> str:
        return f"v{values['major']}.{values['minor']}"

    @validator("document")
    def _cleanup_document(cls, v) -> dict:
        def _clean(d):

            if isinstance(d, dict) and d.get("text") == "":
                return " "

            if isinstance(d, dict) and d.get("text"):
                return d["text"]

            if isinstance(d, dict) and d.get("description") and d.get("url"):
                return [d["description"], d["url"]]

            if isinstance(d, dict) and d.get("children"):
                return _clean(d["children"])
            if isinstance(d, dict):
                return {
                    k: (_d if k == "publication_references" else _clean(_d))
                    for k, _d in d.items()
                }
            if isinstance(d, list):
                return [_clean(_d) for _d in d]

        return _clean(v.dict(exclude_unset=True, exclude_none=True))


class ElasticsearchAtbd(BaseModel):
    """Elasticsearch document representing an ATBD"""

    id: str
    title: str
    alias: Optional[str]
    created_by: str
    created_at: datetime
    last_updated_by: str
    last_updated_at: datetime
    version: ElasticsearchAtbdVersion

    # attribute names starting with `_` don't get serialized by Pydantic
    # so we use a field alias to convert it. Elasticsearch requires that
    # each document contain a field with key `_id` that uniquely identifies that document
    class Config:
        """Config."""

        title = "ElasticsearchAtbdVersion"
        orm_mode = True
