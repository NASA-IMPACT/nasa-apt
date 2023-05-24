"""SQLAlchemy models for interfacing with the database"""

# from sqlalchemy_utils import CompositeArray, CompositeType
import re

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
    types,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import backref, relationship

from app import acls
from app.db.base import Base
from app.db.types import utcnow
from app.schemas.versions_contacts import ContactMechanismEnum

import fastapi_permissions


class Atbds(Base):
    """Atbds"""

    __tablename__ = "atbds"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    document_type = Column(String())  # AtbdDocumentTypeEnum
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
        lazy="select",
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


class AtbdVersions(Base):
    """AtbdVersions"""

    __tablename__ = "atbd_versions"
    atbd_id = Column(
        Integer(),
        ForeignKey("atbds.id"),
        primary_key=True,
        index=True,
    )
    major = Column(Integer(), primary_key=True, server_default="1")
    minor = Column(Integer(), server_default="0")
    status = Column(String(), server_default="DRAFT", nullable=False)
    document = Column(MutableDict.as_mutable(postgresql.JSON), server_default="{}")
    pdf_id = Column(
        Integer(),
        ForeignKey("pdf_uploads.id"),
        index=True,
    )
    publication_checklist = Column(
        MutableDict.as_mutable(postgresql.JSON), server_default="{}"
    )
    sections_completed = Column(
        MutableDict.as_mutable(postgresql.JSON), server_default="{}"
    )
    published_by = Column(String())
    published_at = Column(types.DateTime)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    doi = Column(String())
    citation = Column(MutableDict.as_mutable(postgresql.JSON), server_default="{}")
    owner = Column(String(), nullable=False)
    authors = Column(postgresql.ARRAY(String()), server_default="{{}}")
    reviewers = Column(postgresql.ARRAY(postgresql.JSONB), server_default="{{}}")
    journal_status = Column(String())
    keywords = Column(postgresql.ARRAY(postgresql.JSONB), server_default="{{}}")
    locked_by = Column(String(), nullable=True)

    pdf = relationship(
        "PDFUpload",
        backref=backref("atbd_version", cascade="all, delete-orphan"),
        lazy="select",
    )

    def __repr__(self):
        """String representation"""
        return (
            f"<AtbdVersions(atbd_id={self.atbd_id}, version=v{self.major}.{self.minor},"
            f" status={self.status}, document={self.document}, publication_checklist={self.publication_checklist},"
            f" sections_completed={self.sections_completed}, created_by={self.created_by},"
            f" created_at={self.created_at}, published_by={self.published_by},"
            f" published_at={self.published_by}, last_updated_at={self.last_updated_at}"
            f" last_updated_by={self.last_updated_by}), owner={self.owner}, authors={self.authors}"
            f" reviewers={self.reviewers})>"
        )

    def __acl__(self):
        """Generates a list of TUPLES representing actions that principals are either
        allowed or denied from executing"""

        acl = []
        for grantee, actions in acls.ATBD_VERSION_ACLS.items():
            if grantee == "lock_owner":
                grantee = f"user:{self.locked_by}"

            if grantee == "owner":
                grantee = f"user:{self.owner}"

            if grantee == "reviewers":
                grantee = [f"user:{r['sub']}" for r in self.reviewers]

            if grantee == "authors":
                grantee = [f"user:{a}" for a in self.authors]

            for action in actions:

                permission = fastapi_permissions.Deny

                if not action.get("deny") and all(
                    [
                        getattr(self, key) in allowed_values
                        for key, allowed_values in action.get("conditions", {}).items()
                    ]
                ):
                    permission = fastapi_permissions.Allow

                if isinstance(grantee, str):
                    acl.append((permission, grantee, action["action"]))

                if isinstance(grantee, list):
                    acl.extend([(permission, g, action["action"]) for g in grantee])

        return acl


class ContactMechanism:
    """
    Custom object class used to mimic a SQLAlchemy object, that
    gets built by the custom type deserializer below
    """

    mechanism_type: str
    mechanism_value: str

    def __init__(self, mechanism_type: ContactMechanismEnum, mechanism_value: str):
        """Init custom ContactMechanism class"""
        self.mechanism_type = mechanism_type
        self.mechanism_value = mechanism_value

    def __repr__(self):
        """String representation"""
        return f"Contact Mechanism(type: {self.mechanism_type}, value: {self.mechanism_value})"


class ContactMechanismArray(types.TypeDecorator):
    """
    Custom SQLAlchemy type that converts back and forth between
    the Postgres string and the python object respresenting an
    author's contact mechanisms
    """

    impl = types.String

    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Serialize to string when writing to database"""

        s = ",".join(
            f'"(\\"{m["mechanism_type"]}\\",\\"{m["mechanism_value"]}\\")"'
            for m in value
        )
        return f"{{{s}}}"

    def process_result_value(self, value, dialect):
        """De-serialize from String to python class when reading
        from database"""
        mechanisms = []
        for result in re.findall(r"(\"\()(.*?),(.*?)(\)\")", value.strip("{}")):
            mtype, mvalue = result[1].strip('\\"'), result[2].strip('\\"')

            mechanisms.append(
                ContactMechanism(mechanism_type=mtype, mechanism_value=mvalue)
            )

        return mechanisms


class Contacts(Base):
    """Contacts"""

    __tablename__ = "contacts"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(), nullable=False)
    middle_name = Column(String())
    last_name = Column(String(), nullable=False)
    uuid = Column(String())
    url = Column(String())
    mechanisms = Column(ContactMechanismArray)

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

    roles = Column(postgresql.ARRAY(String()), server_default="{{}}")

    affiliations = Column(postgresql.ARRAY(String()), server_default="{{}}")

    atbd_version = relationship(
        "AtbdVersions",
        backref=backref("contacts_link", cascade="all, delete-orphan"),
        lazy="select",
    )

    contact = relationship(
        "Contacts",
        backref=backref("atbd_versions_link", cascade="all, delete-orphan"),
        lazy="select",
    )

    def __repr__(self):
        """String representation"""
        return (
            f"<AtbdVersionContact(atbd_id={self.atbd_id}), major={self.major}, "
            f"contact_id={self.contact_id}, roles={self.roles}, "
            f"affiliations={self.affiliations}, "
            f"atbd_versions={self.atbd_version}, contacts={self.contact})>"
        )


class Threads(Base):
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
    status = Column(String(), server_default="OPEN", nullable=False)
    section = Column(String(), nullable=False)
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    notify = Column(types.ARRAY(String), nullable=True)

    comments = relationship(
        "Comments",
        backref="thread",
        uselist=True,
        lazy="select",
        order_by="Comments.created_at",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        """String representation"""
        comments = ", ".join(f"{c.id}: {c.body}" for c in self.comments)
        return (
            f"<Threads(id={self.id}, atbd_id={self.atbd_id}, major={self.major},"
            f" status={self.status}, section={self.section},"
            f" comments={comments})>"
        )

    def __acl__(self):
        """Access Control List for Comments"""
        acl = []
        for grantee, actions in acls.THREAD_ACLS.items():

            if grantee == "owner":
                grantee = f"user:{self.created_by}"

            acl.extend(
                [(fastapi_permissions.Allow, grantee, a["action"]) for a in actions]
            )
        return acl


class Comments(Base):
    """comment model"""

    __tablename__ = "comments"
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    thread_id = Column(
        Integer(),
        ForeignKey("threads.id"),
        primary_key=True,
        index=True,
    )
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    last_updated_by = Column(String(), nullable=False)
    last_updated_at = Column(types.DateTime, server_default=utcnow(), nullable=False)
    body = Column(types.Text)

    def __repr__(self):
        """String representation"""
        return (
            f"<Comments(id={self.id}, thread_id={self.thread_id}, created_at={self.created_by},"
            f" created_by={self.created_by}, last_updated_at={self.last_updated_at},"
            f" last_updated_by={self.last_updated_by}, body={self.body})>"
        )

    def __acl__(self):
        """Access Control List for Comments"""
        acl = []
        for grantee, actions in acls.COMMENT_ACLS.items():

            if grantee == "owner":
                grantee = f"user:{self.created_by}"

            acl.extend(
                [(fastapi_permissions.Allow, grantee, a["action"]) for a in actions]
            )

        return acl


class Upload(Base):
    """Upload model"""

    __abstract__ = True
    id = Column(Integer(), primary_key=True, index=True, autoincrement=True)
    file_path = Column(String(), nullable=False)
    storage = Column(String(), default="s3")
    created_by = Column(String(), nullable=False)
    created_at = Column(types.DateTime, server_default=utcnow(), nullable=False)

    @declared_attr
    def atbd_id(cls):
        """ATBD relation"""
        return Column(Integer(), ForeignKey("atbds.id"), nullable=False)

    def __acl__(self):
        """Access Control List for Uploads"""
        acl = []
        for grantee, actions in acls.UPLOADED_PDF_ACLS.items():

            if grantee == "owner":
                grantee = f"user:{self.created_by}"

            acl.extend(
                [(fastapi_permissions.Allow, grantee, a["action"]) for a in actions]
            )

        return acl


class PDFUpload(Upload):
    """Model to represent an uploaded PDF"""

    __tablename__ = "pdf_uploads"

    def __repr__(self):
        """String representation"""
        return (
            f"<PDFUpload(id={self.id}, atbd_id={self.atbd_id}, file_path={self.file_path},"
            f" storage={self.storage}, created_by={self.created_by},"
            f" created_at={self.created_at},"
        )
