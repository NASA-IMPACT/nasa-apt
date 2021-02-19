"""ATBD's endpoint."""
# from covid_api.api import utils
# from covid_api.core import config
# from covid_api.db.memcache import CacheLayer
# from covid_api.db.static.datasets import datasets
# from covid_api.db.static.errors import InvalidIdentifier
# from covid_api.models.static import Datasets
from app.schemas.atbds import Output
from app.db import models
from app.db.db_session import DbSession
from app.api.utils import get_db
from app import config
from fastapi import APIRouter, Depends

from typing import List

router = APIRouter()


@router.get(
    config.ROOT_PATH + "atbds",
    responses={200: dict(description="return a list of all available atbds")},
    response_model=List[Output],
)
def list_atbds(fields: str = None, db: DbSession = Depends(get_db)):

    query = db.query(models.Atbds).join(
        models.AtbdVersions, models.Atbds.id == models.AtbdVersions.atbd_id
    )
    print(
        db.query(models.Atbds)
        .join(models.AtbdVersions, models.Atbds.id == models.AtbdVersions.atbd_id)
        .all()
    )
    return query.all()
