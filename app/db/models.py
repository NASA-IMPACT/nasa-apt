"""SQLAlchemy models for interfacing with the database"""

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    types,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import backref, relationship

from app.db.base import Base
from app.db.types import utcnow

import fastapi_permissions as permissions


class AtbdVersions(Base):
    """AtbdVersions"""

    __tablename__ = "atbd_versions"
    atbd_id = Column(Integer(), ForeignKey("atbds.id"), primary_key=True, index=True,)
    major = Column(Integer(), primary_key=True, server_default="1")
    minor = Column(Integer(), server_default="0")
    status = Column(String(), server_default="Draft", nullable=False)
    document = Column(MutableDict.as_mutable(postgresql.JSON), server_default="{}")
    sections_completed = Column(
        MutableDict.as_mutable(postgresql.JSON), server_default="{}"
    )
    published_by = Column(String())
    published_at = Column(types.DateTime)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    changelog = Column(String())
    doi = Column(String())
    citation = Column(MutableDict.as_mutable(postgresql.JSON), server_default="{}")
    owner = Column(String(), nullable=False)
    authors = Column(postgresql.ARRAY(String), server_default="[]")
    reviewers = Column(postgresql.ARRAY(postgresql.JSONB), server_default="[]")

    def __repr__(self):
        """String representation"""
        return (
            f"<AtbdVersions(atbd_id={self.atbd_id}, version=v{self.major}.{self.minor},"
            f" status={self.status}, document={self.document},"
            f" sections_completed={self.sections_completed}, created_by={self.created_by},"
            f" created_at={self.created_at}, published_by={self.published_by},"
            f" published_at={self.published_by}, last_updated_at={self.last_updated_at}"
            f" last_updated_by={self.last_updated_by}), owner={self.owner}, authors={self.authors}>"
            f" reviewers={self.reviewers}"
        )

    def __acl__(self):
        """ "Access Control List"""
        acl = [(permissions.Allow, permissions.Authenticated, "view")]

        if self.status == "Published":
            acl.append((permissions.Allow, permissions.Everyone, "view"))
            acl.append((permissions.Allow, f"user:{self.owner}", "create_new_version"))
        if self.status == "Draft":
            acl.append((permissions.Allow, f"user:{self.owner}", "delete"))

        acl.append((permissions.Allow, permissions.Authenticated, "view"))

        # acl.append((permissions.Deny, f"user:{self.owner}", "join_authors"))
        acl.append((permissions.Deny, f"user:{self.owner}", "join_reviewers"))

        acl.append((permissions.Allow, f"user:{self.owner}", "comment"))
        acl.append((permissions.Allow, f"user:{self.owner}", "edit"))
        acl.append((permissions.Allow, f"user:{self.owner}", "invite_authors"))
        acl.append((permissions.Allow, f"user:{self.owner}", "offer_ownership"))
        acl.append((permissions.Allow, f"user:{self.owner}", "view_authors"))
        acl.append((permissions.Allow, f"user:{self.owner}", "view_owner"))
        acl.append((permissions.Allow, f"user:{self.owner}", "update"))
        acl.append((permissions.Allow, f"user:{self.owner}", "invite_authors"))

        for author in self.authors:
            acl.append((permissions.Deny, f"user:{author}", "join_reviewers"))
            acl.append((permissions.Allow, f"user:{author}", "comment"))
            acl.append((permissions.Allow, f"user:{author}", "edit"))
            acl.append((permissions.Allow, f"user:{author}", "view_authors"))
            acl.append((permissions.Allow, f"user:{author}", "view_owner"))
            acl.append((permissions.Allow, f"user:{author}", "update"))

            if self.status == "Published":
                acl.append((permissions.Allow, f"user:{author}", "create_new_version"))

        for reviewer in [r["sub"] for r in self.reviewers]:

            acl.append((permissions.Deny, f"user:{reviewer}", "receive_ownership"))
            acl.append((permissions.Deny, f"user:{reviewer}", "join_authors"))

            acl.append((permissions.Allow, f"user:{reviewer}", "comment"))
            acl.append((permissions.Allow, f"user:{reviewer}", "view_authors"))
            acl.append((permissions.Allow, f"user:{reviewer}", "view_owner"))
            acl.append((permissions.Allow, f"user:{reviewer}", "view_reviewers"))

        acl.append((permissions.Allow, "role:contributor", "receive_ownership"))
        acl.append((permissions.Allow, "role:contributor", "join_authors"))
        acl.append((permissions.Allow, "role:contributor", "join_reviewers"))

        acl.append((permissions.Deny, "role:curator", "join_authors"))
        acl.append((permissions.Deny, "role:curator", "join_reviewers"))
        acl.append((permissions.Deny, "role:curator", "receive_ownership"))

        acl.append((permissions.Allow, "role:curator", "comment"))
        acl.append((permissions.Allow, "role:curator", "invite_reviewers"))
        acl.append((permissions.Allow, "role:curator", "invite_authors"))
        acl.append((permissions.Allow, "role:curator", "offer_ownership"))
        acl.append((permissions.Allow, "role:curator", "view_authors"))
        acl.append((permissions.Allow, "role:curator", "view_owner"))
        acl.append((permissions.Allow, "role:curator", "view_reviewers"))
        acl.append((permissions.Allow, "role:curator", "delete"))

        return acl


class Atbds(Base):
    """Atbds"""

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
        """String representation"""
        versions = ", ".join(f"v{v.major}.{v.minor}" for v in self.versions)
        return (
            f"<Atbds(id={self.id}, title={self.title}, alias={self.alias},"
            f" created_by={self.created_by}, created_at={self.created_at},"
            f" last_updated_by={self.last_updated_by}, last_updated_at={self.last_updated_at}"
            f" versions={versions})>"
        )


class Contacts(Base):
    """Contacts"""

    __tablename__ = "contacts"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(), nullable=False)
    middle_name = Column(String())
    last_name = Column(String(), nullable=False)
    uuid = Column(String())
    url = Column(String())
    mechanisms = Column(String())

    def __repr__(self):
        """String representation"""
        return (
            f"<Contact(id={self.id}, first_name={self.first_name}, middle_name={self.middle_name},"
            f" last_name={self.last_name}, uuid={self.uuid}, url={self.url}, "
            f" mechanisms={self.mechanisms})>"
        )


class AtbdVersionsContactsAssociation(Base):
    """AtbdVersionContactsAssociation.
    see https://docs.sqlalchemy.org/en/14/orm/extensions/associationproxy.html for
    more information on the Association Proxy pattern used here to present the
    many to many relation that AtbdVersions and Contacts have"""

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

    atbd_id = Column(Integer(), nullable=False, primary_key=True,)
    major = Column(Integer(), nullable=False, primary_key=True,)

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
        """String representation"""
        return (
            f"<AtbdVersionContact(atbd_id={self.atbd_id}), major={self.major}, "
            f"contact_id={self.contact_id}, roles={self.roles}, "
            f"atbd_versions={self.atbd_version}, contacts={self.contact})>"
        )

class Thread(Base):
    """thread model"""
    __tablename__ = "threads"
    __table_args__ = (
        ForeignKeyConstraint(
            ["atbd_id", "major"],
            ["atbd_versions.atbd_id", "atbd_versions.major"],
            name="atbd_version_fk_constraint",
        ),
    )
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    atbd_id = Column(Integer(), nullable=False, primary_key=True,)
    major = Column(Integer(), nullable=False, primary_key=True,)

class Comment(Base):
    """comment model"""
    __tablename__ = "comments"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    thread_id = Column(Integer(), ForeignKey("threads.id"), primary_key=True, index=True,)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    comment = Column(types.Text)
