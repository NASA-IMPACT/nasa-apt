"""NASA-APT api nasa"""

from app.api.v1 import atbds, auth, contacts, elasticsearch, images, pdf, versions

from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(atbds.router, tags=["atbds"])
api_router.include_router(versions.router, tags=["versions"])
api_router.include_router(images.router, tags=["images"])
api_router.include_router(auth.router, tags=["saml"], prefix="/saml")
api_router.include_router(pdf.router, tags=["pdfs"])
api_router.include_router(elasticsearch.router, tags=["elasticsearch"])
api_router.include_router(contacts.router, tags=["contacts"])
