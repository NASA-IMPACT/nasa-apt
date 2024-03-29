"""NASA-APT API router"""

from app.api.v2 import (
    atbds,
    base,
    contacts,
    events,
    images,
    keywords,
    opensearch,
    pdf,
    threads,
    users,
    versions,
)

from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(base.router, tags=["base"])
api_router.include_router(atbds.router, tags=["atbds"])
api_router.include_router(versions.router, tags=["versions"])
api_router.include_router(images.router, tags=["images"])
api_router.include_router(pdf.router, tags=["pdfs"])
api_router.include_router(opensearch.router, tags=["opensearch"])
api_router.include_router(contacts.router, tags=["contacts"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(events.router, tags=["events"])
api_router.include_router(threads.router, tags=["threads"])
api_router.include_router(keywords.router, tags=["keywords"])
