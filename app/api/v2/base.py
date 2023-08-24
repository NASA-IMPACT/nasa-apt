"""Base API endpoints"""

from app import config
from app.schemas.bootstrap import BootstrapResponse

from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/bootstrap",
    responses={
        200: dict(description="Return feature flags and metadata for the frontend")
    },
    response_model=BootstrapResponse,
)
def bootstrap():
    """Return feature flags and metadata for the frontend"""
    return {
        "metadata": {
            "version": config.API_VERSION_STRING,
        },
        "feature_flags": config.FEATURE_FLAGS,
    }
