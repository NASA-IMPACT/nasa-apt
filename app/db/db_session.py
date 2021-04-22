from app import config
from sqlalchemy import engine, create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_CONNECTION_URL = engine.url.URL(
    "postgresql",
    username=config.POSTGRES_ADMIN_USER,
    password=config.POSTGRES_ADMIN_PASSWORD,
    host=config.POSTGRES_HOST,
    database=config.POSTGRES_DB_NAME,
)


engine = create_engine(
    DATABASE_CONNECTION_URL,
    pool_pre_ping=True,
    connect_args={"connect_timeout": 10, "options": "-csearch_path=apt,public"},
)


# DbSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
DbSession = sessionmaker(bind=engine)


async def get_session():
    try:
        db = DbSession()
        db.execute(
            "SET SESSION AUTHORIZATION anonymous;"  # SET SEARCH_PATH to apt,public;"
        )
        yield db
    finally:
        db.rollback()
        db.close()
