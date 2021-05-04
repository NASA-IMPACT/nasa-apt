from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    ForeignKeyConstraint,
    CheckConstraint,
    types,
    JSON,
    Enum,
    Table,
    Text,
    cast,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.associationproxy import association_proxy
import sqlalchemy.types as types
from sqlalchemy_utils import CompositeArray, CompositeType

from app.db.base import Base
from app.db.types import utcnow
from app.schemas.versions import StatusEnum
from app.schemas.contacts import RolesEnum, ContactMechanismEnum
import re


class AtbdVersions(Base):
    __tablename__ = "atbd_versions"
    atbd_id = Column(
        Integer(),
        ForeignKey("atbds.id"),
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
            f" published_at={self.published_by}, last_updated_at={self.last_updated_at}"
            f" last_updated_by={self.last_updated_by})>"
        )


class Atbds(Base):
    __tablename__ = "atbds"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    title = Column(String(), nullable=False)
    alias = Column(String(), CheckConstraint("alias ~ '^[a-z0-9-]+$'"), unique=True)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)

    versions = relationship(
        "AtbdVersions",
        backref="atbd",
        uselist=True,
        lazy="joined",
        order_by="AtbdVersions.created_at",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        versions = ", ".join(f"v{v.major}.{v.minor}" for v in self.versions)
        return (
            f"<Atbds(id={self.id}, title={self.title}, alias={self.alias},"
            f" created_by={self.created_by}, created_at={self.created_at},"
            f" last_updated_by={self.last_updated_by}, last_updated_at={self.last_updated_at}"
            f" versions={versions})>"
        )


# class MechanismArray(postgresql.ARRAY):
#     def bind_expression(self, bindvalue):
#         return cast(bindvalue, self)

#     def result_processor(self, dialect, coltype):
#         super_rp = super(MechanismArray, self).result_processor(dialect, coltype)

#         def handle_raw_string(value):

#             return re.findall(r"([\"'])(?:(?=(\\?))\2.)*?\1", value)

#         def process(value):
#             return super_rp(handle_raw_string(value))

#         return process


class Contacts(Base):
    __tablename__ = "contacts"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(), nullable=False)
    middle_name = Column(String())
    last_name = Column(String(), nullable=False)
    uuid = Column(String())
    url = Column(String())
    mechanisms = Column(String())

    def __repr__(self):
        return (
            f"<Contact(id={self.id}, first_name={self.first_name}, middle_name={self.middle_name},"
            f" last_name={self.last_name}, uuid={self.uuid}, url={self.url}, "
            f" mechanisms={self.mechanisms})>"
        )


class AtbdVersionsContactsAssociation(Base):
    __tablename__ = "atbd_versions_contacts"
    # Foreign keys are defined up here in order
    # to use a composite foreign key. The FK constraint
    # for contact_id is declared further.
    __table_args__ = (
        ForeignKeyConstraint(
            ["atbd_id", "major"],
            ["atbd_versions.atbd_id", "atbd_versions.major"],
            name="atbd_version_fk_constraint",
        ),
    )

    atbd_id = Column(
        Integer(),
        nullable=False,
        primary_key=True,
    )
    major = Column(
        Integer(),
        nullable=False,
        primary_key=True,
    )

    contact_id = Column(
        Integer(), ForeignKey("contacts.id"), nullable=False, primary_key=True
    )
    roles = Column(String())

    atbd_version = relationship(
        "AtbdVersions",
        backref=backref("contacts_link", cascade="all, delete-orphan"),
        lazy="joined",
    )

    contact = relationship(
        "Contacts",
        backref=backref("atbd_versions_link", cascade="all, delete-orphan"),
        lazy="joined",
    )

    def __repr__(self):
        return (
            f"<AtbdVersionContact(atbd_id={self.atbd_id}), major={self.major}, "
            f"contact_id={self.contact_id}, roles={self.roles}, "
            f"atbd_versions={self.atbd_version}, contacts={self.contact})>"
        )
