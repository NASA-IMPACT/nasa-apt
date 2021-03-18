"""NASA-APT app."""

# from app import version
from app import config
from app.api.v1.api import api_router
from app.db.db_session import DbSession
from app.db.models import Atbds, AtbdVersions
from app.search.elasticsearch import index_atbd

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from sqlalchemy import event


app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    description="A lightweight Cloud Optimized GeoTIFF tile server",
    # version=version,
)

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins = [origin.strip() for origin in config.BACKEND_CORS_ORIGINS.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=0)

app.include_router(api_router, prefix=config.API_VERSION_STR)


# TODO: figure out if we want to use an event listener or directly index
# after update operations directly in the API
# TODO: figure out if this should be a separate lambda invocation,
# or an asynchronous event, or something else
@event.listens_for(DbSession, "before_commit")
def atbd_listener(session):
    # Add all ids to a set, to deduplicate ID from
    # sessions that update both an ATBD and it's version
    atbds_to_index = set()
    for instance in session.dirty:
        if isinstance(instance, Atbds):
            atbds_to_index.add(instance.id)
        if isinstance(instance, AtbdVersions):
            atbds_to_index.add(instance.atbd_id)

    for atbd_id in atbds_to_index:
        index_atbd(atbd_id=atbd_id, db=session)


@app.get("/ping", description="Health Check")
def ping():
    """Health check."""
    return {"ping": "pong!"}
