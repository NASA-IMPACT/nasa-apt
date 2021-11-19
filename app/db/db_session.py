"""
This module provides functionality to generate a new SQLAlchemy session object
to perform database transactions
"""
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker

from app.config import (
    POSTGRES_ADMIN_PASSWORD,
    POSTGRES_ADMIN_USER,
    POSTGRES_DB_NAME,
    POSTGRES_HOST,
)

# from sqlalchemy_utils import register_composites

DATABASE_CONNECTION_URL = engine.url.URL(
    "postgresql",
    username=POSTGRES_ADMIN_USER,
    password=POSTGRES_ADMIN_PASSWORD,
    host=POSTGRES_HOST,
    database=POSTGRES_DB_NAME,
)


engine = create_engine(
    DATABASE_CONNECTION_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10, "options": "-csearch_path=apt,public"},
)


DbSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# TODO: should this remain async?
async def get_db_session():
    """
    Yields a SQLAlchemy database session, with the authorization level
    set to `anonymous`. Upon successfull authenticating a JWT, the
    session's authorization will be set to `app_user`.
    """
    try:
        db = DbSession()
        # register_composites(engine.connect())
        db.execute("SET SESSION AUTHORIZATION app_user;")
        yield db
    finally:
        db.rollback()
        db.close()
