import enum
from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    CheckConstraint,
    types,
    JSON,
    Enum,
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import utcnow


class StatusEnum(str, enum.Enum):
    Draft = "Draft"
    Review = "Review"
    Published = "Published"


class AtbdVersions(Base):
    atbd_id = Column(
        Integer(),
        ForeignKey("atbds.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    major = Column(Integer(), primary_key=True, server_default="1")
    minor = Column(Integer(), server_default="0")
    status = Column(
        Enum(StatusEnum), server_default=StatusEnum.Draft.name, nullable=False
    )
    document = Column(JSON())
    published_by = Column(String())
    published_at = Column(types.DateTime)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    changelog = Column(String())
    doi = Column(String())

    def __repr__(self):

        return (
            f"<AtbdVersions(atbd_id={self.atbd_id}, version=v{self.major}.{self.minor},"
            f" status={self.status}, document={self.document}, created_by={self.created_by},"
            f" created_at={self.created_at}, published_by={self.published_by},"
            f" published_at={self.published_by}>"
        )


class Atbds(Base):
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    title = Column(String(), nullable=False)
    alias = Column(String(), CheckConstraint("alias ~ '^[a-z0-9-]+$'"), unique=True)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    versions = relationship(
        "AtbdVersions",
        primaryjoin="foreign(Atbds.id) == AtbdVersions.atbd_id",
        backref="atbd",
        uselist=True,
        lazy="joined",
    )

    def __repr__(self):
        versions = ", ".join(f"v{v.major}.{v.minor}" for v in self.versions)
        return (
            f"<Atbds(id={self.id}, title={self.title}, alias={self.alias},"
            f" created_by={self.created_by}, created_at={self.created_at},"
            f" versions={versions})>"
        )
