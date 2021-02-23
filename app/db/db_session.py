from app import config

# from app.main import app

from contextlib import contextmanager
from app.search.searchindex import index_atbd

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

DATABASE_CONNECTION_URL = f"postgres://{config.POSTGRES_ADMIN_USER}:{config.POSTGRES_ADMIN_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB_NAME}"
engine = create_engine(
    DATABASE_CONNECTION_URL, pool_pre_ping=True, connect_args={"connect_timeout": 10}
)


@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute(
        "SET SESSION AUTHORIZATION anonymous; SET SEARCH_PATH to apt, public;"
    )
    cursor.close()


# DbSession = sessionmaker(autocommit=False, bind=app.state.connection)
DbSession = sessionmaker(autocommit=False, bind=engine)


@contextmanager
def get_session():
    try:
        db = DbSession()
        yield db
    finally:
        db.close()

