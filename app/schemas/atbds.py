from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from app.schemas.atbd_versions import Output as ATBDVersionOutput


class Output(BaseModel):
    created_at: datetime
    created_by: str
    title: str
    alias: str
    versions: List[ATBDVersionOutput]

    class Config:
        title = "Atbd"
        orm_mode = True


class Lookup(BaseModel):
    id: Optional[int]
    abtd_alias: Optional[str]


class Create(BaseModel):
    atbd_alias: str
    title: str
    created_by: str

