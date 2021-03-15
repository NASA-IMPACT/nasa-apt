from typing import Optional
from app.schemas.versions import FullOutput


class ElasticSearchAtbdVersion(FullOutput):
    id: str
    title: str
    alias: Optional[str]

    # attribute names starting with `_` don't get serialized by Pydantic
    # so we use a field alias to convert it. Elasticsearch requires that
    # each document contain a field with key `_id` that uniquely identifies that document
    class Config:
        fields = {"id": "_id"}

