import factory
import pytest
from app.db.models import Atbds, AtbdVersions
from tests.conftest import db_session
import faker


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def create(cls, **kwargs):
        model = super().create(**kwargs)
        # Ensure that model is in DB
        cls._meta.sqlalchemy_session.commit()
        cls._meta.sqlalchemy_session.refresh(model)
        return model


@pytest.fixture
def username(faker) -> str:
    """
    Generate a single username for test. Useful for sharing a username between fixtures
    (e.g. if a test relies on an "auth_token" fixture and this "username" fixture,
    the "auth_token" will be made with the same username as is provided by the
    "username" fixture)
    """
    return faker.user_name()


@pytest.fixture(scope="session")
def atbd_versions_factory(db_session):
    class AtbdVersionsFactory(factory.alchemy.SQLAlchemyModelFactory):

        major = factory.Faker("pyint")
        minor = factory.Faker("pyint")
        status = factory.Faker(
            "random_choices", elements=["Draft", "Review", "Published"]
        )
        document = faker.Faker().pydict(10, True, "str")
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

        return AtbdVersionsFactory


@pytest.fixture(scope="session")
def atbds_factory(db_session):
    class AtbdsFactory(factory.alchemy.SQLAlchemyModelFactory):
        title = factory.Faker("pystr")
        alias = factory.Faker("pystr")
        created_by = factory.Faker("pystr")
        # versions = factory.SubFactory()

        class Meta:
            model = Atbds
            sqlalchemy_session = db_session

        # @factory.post_generation
        # def players(obj, create, extracted, **kwargs):
        #     if not create:
        #         return
        #     if extracted:
        #         for n in range(extracted):

    return AtbdsFactory

