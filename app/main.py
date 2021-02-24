"""NASA-APT app."""

# from app import version
from app.api.v1.api import api_router

from app.db.middleware import db_session_middleware

from app import config
from app.search.searchindex import index_atbd
import asyncpg

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

DATABASE_CONNECTION_URL = f"postgres://{config.POSTGRES_ADMIN_USER}:{config.POSTGRES_ADMIN_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB_NAME}"

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
# app.middleware("http")(db_session_middleware)


@app.on_event("startup")
async def startup() -> None:
    """
    Create database connection when FastAPI App has started.
    Add listener to atbd channel on database connection.
    """
    print(f"Attempting to connect to: {DATABASE_CONNECTION_URL}")
    app.state.connection = await asyncpg.connect(
        DATABASE_CONNECTION_URL, server_settings={"search_path": "apt,public"}
    )
    await app.state.connection.add_listener("atbd", index_atbd())


@app.on_event("shutdown")
async def shutdown() -> None:
    await app.state.connection.remove_listener("atbd", index_atbd)
    await app.state.connection.close()


@app.get("/ping", description="Health Check")
def ping():
    """Health check."""
    return {"ping": "pong!"}
