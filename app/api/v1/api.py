"""NASA-APT api nase"""

from app.api.v1 import atbds

from app.api.v1 import auth
from app.api.v1 import pdf
from app.api.v1 import elasticsearch
from app.api.v1 import contacts

from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(atbds.router, tags=["atbds"])
api_router.include_router(auth.router, tags=["saml"], prefix="/saml")
api_router.include_router(pdf.router, tags=["pdfs"])
api_router.include_router(elasticsearch.router, tags=["elasticsearch"])
api_router.include_router(contacts.router, tags=["contacts"])
