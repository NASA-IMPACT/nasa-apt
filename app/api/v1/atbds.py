"""ATBD's endpoint."""
from app.schemas import atbds
from app.db import models
from app.db.db_session import DbSession
from app.api.utils import get_db
from app.auth.saml import User, get_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func

from typing import List

router = APIRouter()


@router.get(
    "/atbds",
    responses={200: dict(description="Return a list of all available ATBDs")},
    response_model=List[atbds.SummaryOutput],
)
def list_atbds(fields: str = None, db: DbSession = Depends(get_db)):

    query = db.query(models.Atbds).join(
        models.AtbdVersions, models.Atbds.id == models.AtbdVersions.atbd_id
    )

    return query.all()


@router.get(
    "/atbds/{id}",
    responses={200: dict(description="Return a single ATBD")},
    response_model=atbds.FullOutput,
)
def get_atbd(id: str, fields: str = None, db: DbSession = Depends(get_db)):

    query = (
        db.query(models.Atbds)
        .join(models.AtbdVersions, models.Atbds.id == models.AtbdVersions.atbd_id)
        .filter(models.Atbds.id == id)
    )
    return query.one()


@router.post(
    "/atbds",
    responses={200: dict(description="Create a new ATBD")},
    response_model=atbds.SummaryOutput,
)
def create_atbd(
    atbd_input: atbds.CreateInput,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_user),
):
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User must be authenticated to perform this operation",
        )

    _input = {**atbd_input.dict(), "created_by": user["user"]}

    atbd = models.Atbds(**_input)
    db.add(atbd)
    db.commit()
    db.refresh(atbd)

    atbd_version = models.AtbdVersions(atbd_id=atbd.id)
    db.add(atbd_version)
    db.commit()
    db.refresh(atbd)
    return atbd
