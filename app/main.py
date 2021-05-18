"""NASA-APT app."""


from app import config
from app.api.v2.api import api_router

from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

app = FastAPI(
    title=config.PROJECT_NAME,
    openapi_url="/api/v1/openapi.json",
    description="A lightweight Cloud Optimized GeoTIFF tile server",
    version=config.API_VERSION_STRING,
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


app.include_router(api_router, prefix=config.API_VERSION_STRING)


@app.get("/ping", description="Health Check")
def ping():
    """Health check."""
    return {"ping": "pong!"}
