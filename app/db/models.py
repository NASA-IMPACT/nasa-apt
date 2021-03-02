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
    func,
)
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.db.types import utcnow


class Atbds(Base):
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    title = Column(String(), nullable=False)
    alias = Column(
        String(),
        CheckConstraint("alias ~ '^[a-z0-9-]+$'"),
        unique=True,
        nullable=False,
    )
    created_by = Column(String())
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    versions = relationship(
        "AtbdVersions",
        primaryjoin="foreign(Atbds.id) == AtbdVersions.atbd_id",
        backref="atbd",
        uselist=True,
    )

    def __repr__(self):
        return "<Atbds(id={}, title={}, alias={}, created_by={}, created_at={}, versions={})>".format(
            self.id,
            self.title,
            self.alias,
            self.created_by,
            self.created_at,
            ",".join([f"{v.id}:{v.alias}" for v in self.versions]),
        )


class StatusEnum(str, enum.Enum):
    Draft = "Draft"
    Review = "Review"
    Published = "Published"


class AtbdVersions(Base):
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    atbd_id = Column(
        Integer(),
        ForeignKey("atbds.id", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    alias = Column(
        String(),
        CheckConstraint("alias ~ '^[.a-z0-9-]+$'"),
        unique=True,
        nullable=False,
        server_default="1.0",
    )
    status = Column(
        Enum(StatusEnum), server_default=StatusEnum.Draft.name, nullable=False
    )
    document = Column(JSON())
    published_by = Column(String())
    published_at = Column(types.DateTime)

    def __repr__(self):
        return "<AtbdVersions(id={}, atbd_id={}, alias={}, status={}, document={}, published_by={}, published_at={}>".format(
            self.id,
            self.atbd_id,
            self.alias,
            self.status,
            self.document,
            self.published_at,
            self.published_by,
        )

