import json
import logging
from datetime import datetime, timedelta
from unittest.mock import patch

import boto3
import factory
import faker
import pytest
import testing.postgresql
from factory import fuzzy
from jose import jwt
from moto import mock_cognitoidp, mock_s3, mock_secretsmanager
from sqlalchemy import create_engine, engine, text
from sqlalchemy.orm import scoped_session

from app.db.models import Atbds, AtbdVersions, AtbdVersionsContactsAssociation, Contacts

from fastapi.testclient import TestClient


@pytest.fixture
def monkeysession(request):
    """Session-scoped monkey patch"""
    # https://github.com/pytest-dev/pytest/issues/363#issuecomment-406536200
    from _pytest.monkeypatch import MonkeyPatch

    mpatch = MonkeyPatch()
    mpatch.setenv("AWS_ACCESS_KEY_ID", "patch")
    mpatch.setenv("AWS_SECRET_ACCESS_KEY", "patch")
    mpatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    mpatch.setenv("ELASTICSEARCH_URL", "patch")
    mpatch.setenv("POSTGRES_ADMIN_CREDENTIALS_ARN", "mocked_secrets_manager_arn")
    mpatch.setenv("API_VERSION_STRING", "/v2")
    mpatch.setenv("PROJECT_NAME", "project_name")
    mpatch.setenv("APT_FRONTEND_URL", "http://mocked_frontend_url")
    mpatch.setenv("S3_BUCKET", "mocked_bucket")
    mpatch.setenv("USER_POOL_NAME", "mock")
    mpatch.setenv("APP_CLIENT_NAME", "mock")

    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def database_connection():
    """
    yields a dict of connection details to a Test DB
    """

    with testing.postgresql.Postgresql() as postgresql:
        yield postgresql.dsn()


@pytest.fixture(scope="session")
def empty_db(database_connection):
    """Bind DB engine for application user to TestSession"""
    url = engine.url.URL(
        "postgresql",
        username=database_connection["user"],
        password=database_connection.get("password"),
        host=database_connection["host"],
        database=database_connection["database"],
        port=database_connection["port"],
    )
    test_db_engine = create_engine(
        url,
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10, "options": "-csearch_path=apt,public"},
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

        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
    yield test_db_engine


@pytest.fixture(scope="function")
def test_db_engine(empty_db):

    yield empty_db
    empty_db.execute(
        "DELETE FROM atbd_versions_contacts; DELETE FROM atbd_versions; DELETE FROM contacts; DELETE FROM atbds; "
    )


@pytest.fixture
def db_session(test_db_engine, secrets, cognito):

    from app.db.db_session import DbSession

    # This TestSession should be bound to a test DB when one is created
    TestSession = scoped_session(DbSession)

    TestSession.configure(bind=test_db_engine)

    session = TestSession()
    yield session

    session.rollback()
    session.close()


@pytest.fixture
def test_client(db_session, cognito):

    from app.main import app

    yield TestClient(app)


@mock_s3
@pytest.fixture
def s3_bucket(monkeysession, s3_resource):
    from app.config import S3_BUCKET

    bucket = s3_resource.Bucket(name=S3_BUCKET)
    bucket.create()

    yield bucket


@pytest.fixture
def s3_resource(monkeysession):
    with mock_s3():
        yield boto3.resource("s3", region_name="us-east-1")


@pytest.fixture
def cognito_client(monkeysession):
    with mock_cognitoidp():
        yield boto3.client("cognito-idp", region_name="us-east-1")


@pytest.fixture
def cognito(cognito_client):
    user_pool = cognito_client.create_user_pool(PoolName="mock")
    cognito_client.create_user_pool_client(
        UserPoolId=user_pool["UserPool"]["Id"], ClientName="mock", CallbackURLs=["mock"]
    )


@pytest.fixture
def secretsmanager_client(monkeysession):
    with mock_secretsmanager():
        yield boto3.client("secretsmanager", region_name="us-east-1")


@pytest.fixture
def secrets(secretsmanager_client, database_connection, monkeysession):

    secretsmanager_client.create_secret(
        Name="mocked_secrets_manager_arn",
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
    secretsmanager_client.create_secret(
        Name="mocked_jwt_arn", SecretString="mockedsecretkeyforsigningjwttokens"
    )


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
        "mockedsecretkeyforsigningjwttokens",
    )


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def create(cls, **kwargs):
        model = super().create(**kwargs)
        # Ensure that model is in DB
        cls._meta.sqlalchemy_session.commit()
        cls._meta.sqlalchemy_session.refresh(model)
        return model


with open("./tests/document_test_fixture.json") as f:
    DOCUMENT = json.loads(f.read())


@pytest.fixture
def atbd_versions_factory(db_session):
    class AtbdVersionsFactory(BaseFactory):
        major = factory.Faker("pyint")
        minor = factory.Faker("pyint")
        status = factory.Faker(
            "random_element", elements=["Draft", "Review", "Published"],
        )
        document = DOCUMENT

        sections_completed = faker.Faker().pydict(4, True, "str")
        published_by = factory.Faker("user_name")
        published_at = factory.Faker("date_object")
        created_by = factory.Faker("user_name")
        last_updated_by = factory.Faker("user_name")
        changelog = factory.Faker("pystr")
        doi = factory.Faker("pystr")
        citation = faker.Faker().pydict(10, True, "str")

        class Meta:
            model = AtbdVersions
            sqlalchemy_session = db_session

    yield AtbdVersionsFactory


@pytest.fixture
def atbds_factory(db_session):
    class AtbdsFactory(BaseFactory):
        title = factory.Faker("pystr")
        alias = fuzzy.FuzzyText(
            length=15, prefix="x9-", chars="qwertyuiopasdfghjklzxcvbnm",
        )
        created_by = factory.Faker("pystr")
        last_updated_by = factory.Faker("pystr")

        class Meta:
            model = Atbds
            sqlalchemy_session = db_session

    yield AtbdsFactory


@pytest.fixture
def contacts_factory(db_session):
    class ContactsFactory(BaseFactory):

        first_name = fuzzy.FuzzyText(length=10)
        middle_name = fuzzy.FuzzyText(length=10)
        last_name = fuzzy.FuzzyText(length=10)
        uuid = fuzzy.FuzzyText(length=10)
        url = fuzzy.FuzzyText(length=10, prefix="http://")

        # mechanisms = [
        #     {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        #     {"mechanism_type": "Twitter", "mechanism_value": "@test_handle"},
        # ]
        mechanisms = '{"(Email,test@email.com)", "(Mobile,\\"(123) 456 7891\\")"}'

        class Meta:
            model = Contacts
            sqlalchemy_session = db_session

    yield ContactsFactory


@pytest.fixture
def versions_contacts_association_factory(db_session):
    class VersionsContactsAssociationFactory(factory.alchemy.SQLAlchemyModelFactory):
        atbd_id = factory.Faker("pyint")
        major = factory.Faker("pyint")
        contact_id = factory.Faker("pyint")
        roles = '{{"Investigator", "Science contact"}}'

        class Meta:
            model = AtbdVersionsContactsAssociation
            sqlalchemy_session = db_session

    yield VersionsContactsAssociationFactory


@pytest.fixture
def mocked_send_to_elasticsearch():
    with patch(
        "app.search.elasticsearch.send_to_elastic"
    ) as mocked_send_to_elasticsearch:
        yield mocked_send_to_elasticsearch


@pytest.fixture
def mocked_validate_cognito_token():
    with patch("app.auth.cognito.validate_token") as mocked_validate_cognito_token:
        mocked_validate_cognito_token.return_value = {
            "sub": "123abc456def",
        }
        yield mocked_validate_cognito_token
