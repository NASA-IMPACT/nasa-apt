from app import config
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker


engine = create_engine(
    config.DBURL, pool_pre_ping=True, connect_args={"connect_timeout": 10}
)


# @event.listens_for(engine, "connect")
# def connect(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     cursor.execute(
#         "SET SESSION AUTHORIZATION anonymous; SET SEARCH_PATH to apt, public;"
#     )
#     cursor.close()


DbSession = sessionmaker(autocommit=False, bind=engine)


@contextmanager
def get_session():
    try:
        db = DbSession()
        db.execute(
            "SET SESSION AUTHORIZATION anonymous; SET SEARCH_PATH to apt, public;"
        )
        yield db
    finally:
        db.close()

