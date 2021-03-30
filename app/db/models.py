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
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableDict

from app.db.base import Base
from app.db.types import utcnow
from app.schemas.versions import StatusEnum
from app.schemas.contacts import RolesEnum, ContactMechanismEnum

# TODO: break this up into individual files


class AtbdVersions(Base):
    atbd_id = Column(
        Integer(),
        ForeignKey("atbds.id"),  # onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )
    major = Column(Integer(), primary_key=True, server_default="1")
    minor = Column(Integer(), server_default="0")
    status = Column(String(), server_default="Draft", nullable=False)
    document = Column(MutableDict.as_mutable(JSON), server_default="{}")
    sections_completed = Column(MutableDict.as_mutable(JSON), server_default="{}")
    published_by = Column(String())
    published_at = Column(types.DateTime)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    changelog = Column(String())
    doi = Column(String())
    citation = Column(MutableDict.as_mutable(JSON), server_default="{}")

    def __repr__(self):

        return (
            f"<AtbdVersions(atbd_id={self.atbd_id}, version=v{self.major}.{self.minor},"
            f" status={self.status}, document={self.document},"
            f" sections_completed={self.sections_completed}, created_by={self.created_by},"
            f" created_at={self.created_at}, published_by={self.published_by},"
            f" published_at={self.published_by}, last_updated_at={self.last_updated_at}>"
            f" last_updated_by={self.last_updated_by}"
        )


class Atbds(Base):
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    title = Column(String(), nullable=False)
    alias = Column(String(), CheckConstraint("alias ~ '^[a-z0-9-]+$'"), unique=True)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)

    versions = relationship(
        "AtbdVersions",
        primaryjoin="foreign(Atbds.id) == AtbdVersions.atbd_id",
        backref="atbd",
        uselist=True,
        lazy="joined",
        order_by="AtbdVersions.created_at",
    )

    def __repr__(self):
        versions = ", ".join(f"v{v.major}.{v.minor}" for v in self.versions)
        return (
            f"<Atbds(id={self.id}, title={self.title}, alias={self.alias},"
            f" created_by={self.created_by}, created_at={self.created_at},"
            f" last_updated_by={self.last_updated_by}, last_updated_at={self.last_updated_at}"
            f" versions={versions})>"
        )


class Contacts(Base):
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(), nullable=False)
    middle_name = Column(String())
    last_name = Column(String(), nullable=False)
    uuid = Column(String())
    url = Column(String())
    mechanisms = Column(ARRAY(String()))
    roles = Column(ARRAY(String()))
    title = Column(String())

    def __repr__(self):
        return (
            f"<Contact(id={self.id}, first_name={self.first_name}, middle_name={self.middle_name},"
            f" last_name={self.last_name}, uuid={self.uuid}, url={self.url}, title={self.title}, "
            f" no. mechanisms={len(self.mechanisms)}, no. roles={len(self.roles)}"
        )
