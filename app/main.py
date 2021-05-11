"""NASA-APT app."""

# from app import version
from app import config
from app.api.v1.api import api_router
from app.db.db_session import DbSession
from app.db.models import Atbds, AtbdVersions
from app.search.elasticsearch import add_atbd_to_index

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
        allow_methods=["HEAD", "GET", "POST", "DELETE"],
        allow_headers=["*"],
    )

app.add_middleware(GZipMiddleware, minimum_size=0)

app.include_router(api_router, prefix=config.API_VERSION_STR)


@app.get("/ping", description="Health Check")
def ping():
    """Health check."""
    return {"ping": "pong!"}
