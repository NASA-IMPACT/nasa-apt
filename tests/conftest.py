from app.db.models import Atbds, AtbdVersions
from unittest.mock import patch
import pytest
from sqlalchemy import engine, create_engine, text, MetaData
import testing.postgresql
from sqlalchemy.orm import scoped_session
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
import os
import boto3
import json
from moto import mock_secretsmanager
import factory
import faker
import logging


@pytest.fixture
def monkeysession(request):
    """ Session-scoped monkey patch """
    # https://github.com/pytest-dev/pytest/issues/363#issuecomment-406536200
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    mpatch.setenv("AWS_ACCESS_KEY_ID", "patch")
    mpatch.setenv("AWS_SECRET_ACCESS_KEY", "patch")
    mpatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    mpatch.setenv("ELASTICSEARCH_URL", "patch")
    yield mpatch
    mpatch.undo()


@pytest.fixture
def database_connection():
    """
    yields a dict of connection details to a Test DB
    """

    with testing.postgresql.Postgresql() as postgresql:
        yield postgresql.dsn()


@pytest.fixture
def test_db_engine(database_connection):
    """ Bind DB engine for application user to TestSession """
    url = engine.url.URL(
        "postgresql",
        username=database_connection["user"],
        password=database_connection.get("password"),
        host=database_connection["host"],
        database=database_connection["database"],
        port=database_connection["port"],
    )
    test_db_engine = create_engine(
        url, pool_pre_ping=True, connect_args={"connect_timeout": 1}
    )

    with test_db_engine.connect() as conn:
        for e in ["appschema", "tables", "anonymous", "functions"]:
            with open(f"./db/deploy/{e}.sql", "r") as f:
                conn.execute(
                    text(
                        f.read()
                        # Replace these values manually, because I couldn't get
                        # the postgresql.dns() methods to work with custom
                        # username, and database name
                        .replace("masteruser", "postgres").replace("nasadb", "test")
                    )
                )
        conn.execute(
            # "SET SESSION AUTHORIZATION anonymous; SET SEARCH_PATH to apt, public;"
            "SET SEARCH_PATH to apt,public;"
        )
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
    yield test_db_engine


@pytest.fixture
def db_session(test_db_engine, secrets):

    from app.db.db_session import DbSession

    # This TestSession should be bound to a test DB when one is created
    TestSession = scoped_session(DbSession)

    TestSession.configure(bind=test_db_engine)

    session = TestSession()
    yield session

    session.rollback()
    session.close()


@mock_secretsmanager
@pytest.fixture
def test_client(db_session):

    from app.main import app

    yield TestClient(app)


@pytest.fixture
def secretsmanager_client(monkeysession):
    with mock_secretsmanager():
        yield boto3.client("secretsmanager", region_name="us-east-1")


@pytest.fixture
def secrets(secretsmanager_client, database_connection, monkeysession):

    secretsmanager_client.create_secret(
        Name=os.environ["POSTGRES_ADMIN_CREDENTIALS_ARN"],
        SecretString=json.dumps(
            {
                "username": database_connection["user"],
                "password": database_connection.get("password", ""),
                "host": database_connection["host"],
                "dbname": database_connection["database"],
                "port": database_connection["port"],
            }
        ),
    )
    monkeysession.setenv("POSTGRES_ADMIN_CREDENTIALS_ARN", "mocked_credentials_arn")


@pytest.fixture
def authenticated_headers(authenticated_jwt):
    yield {"Authorization": f"Bearer {authenticated_jwt}"}


@pytest.fixture
def authenticated_jwt():
    yield jwt.encode(
        {
            "userdata": {"user": "mocked-auth-user"},
            "name_id": "nameid",
            "nq": "np",
            "spnq": "spnq",
            "name_id_format": "formate",
            "session_index": "index",
            "exp": datetime.utcnow() + timedelta(seconds=60),
            "role": "app_user",
        },
        os.environ["JWT_SECRET"],
    )


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def create(cls, **kwargs):
        model = super().create(**kwargs)
        # Ensure that model is in DB
        cls._meta.sqlalchemy_session.commit()
        cls._meta.sqlalchemy_session.refresh(model)
        yield model


@pytest.fixture
def atbd_versions_factory(db_session):
    class AtbdVersionsFactory(factory.alchemy.SQLAlchemyModelFactory):
        major = factory.Faker("pyint")
        minor = factory.Faker("pyint")
        status = factory.Faker(
            "random_element", elements=["Draft", "Review", "Published"],
        )
        document = faker.Faker().pydict(10, True, "str")
        sections_completed = faker.Faker().pydict(4, True, "str")
        published_by = factory.Faker("user_name")
        published_at = factory.Faker("date_object")
        created_by = factory.Faker("user_name")
        created_at = factory.Faker("date_object")
        last_updated_by = factory.Faker("user_name")
        last_updated_at = factory.Faker("date_object")
        changelog = factory.Faker("pystr")
        doi = factory.Faker("pystr")
        citation = faker.Faker().pydict(10, True, "str")

        class Meta:
            model = AtbdVersions
            sqlalchemy_session = db_session

    yield AtbdVersionsFactory


@pytest.fixture
def atbds_factory(db_session, atbd_versions_factory):
    class AtbdsFactory(factory.alchemy.SQLAlchemyModelFactory):
        title = factory.Faker("pystr")
        alias = factory.Faker(
            "pystr_format",
            string_format="?#-###{{random_int}}{{random_letter}}",
            letters="qwertyuiopasdfghjklzxcvbnm",
        )
        created_by = factory.Faker("pystr")
        last_updated_by = factory.Faker("pystr")

        class Meta:
            model = Atbds
            sqlalchemy_session = db_session

    yield AtbdsFactory


@pytest.fixture
def atbd_creation_input():
    yield {"title": "Test ATBD 1", "alias": "test-atbd-1"}


@pytest.fixture
def mocked_event_listener():
    with patch("app.main.index_atbd") as mocked_event_listener:

        yield mocked_event_listener
