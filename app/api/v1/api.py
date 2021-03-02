"""NASA-APT api nase"""

from app.api.v1 import atbds
from app.api.v1 import auth


from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(atbds.router, tags=["atbds"])
api_router.include_router(auth.router, tags=["saml"], prefix="/saml")
