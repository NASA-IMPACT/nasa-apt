"""ATBD's endpoint."""
from app.schemas import atbds
from app.db import models
from app.db.db_session import DbSession
from app.api.utils import get_db
from app.auth.saml import User, get_user
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, exc, select, column


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

    query = db.query(models.Atbds).join(
        models.AtbdVersions, models.Atbds.id == models.AtbdVersions.atbd_id
    )
    try:
        int(id)
        query = query.filter(models.Atbds.id == id)
    except ValueError:
        query = query.filter(models.Atbds.alias == id)

    try:
        return query.one()
    except exc.SQLAlchemyError:
        raise HTTPException(404, f"No document found for id/alias: {id}")


@router.post(
    "/atbds",
    responses={200: dict(description="Create a new ATBD")},
    # response_model=atbds.SummaryOutput,
)
def create_atbd(
    atbd_input: atbds.CreateInput,
    db: DbSession = Depends(get_db),
    user: User = Depends(get_user),
):
    print("User: ", user)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User must be authenticated to perform this operation",
        )

    _input = (
        (atbd_input.title, user["user"])
        if not atbd_input.alias
        else (atbd_input.title, user["user"], atbd_input.alias)
    )
    try:
        function_execution_result = db.execute(
            select(
                [
                    column("atbds.id"),
                    column("atbds.title"),
                    column("atbds.created_by"),
                    column("atbds.created_at"),
                    column("atbd_versions.id"),
                    column("atbd_versions.atbd_id"),
                    column("atbd_versions.alias"),
                    column("atbd_versions.status"),
                    column("atbd_versions.document"),
                    column("atbd_versions.published_by"),
                    column("atbd_versions.published_at"),
                ]
            ).select_from(func.apt.create_atbd_version(*_input))
        )

        db.commit()

    except exc.IntegrityError as e:
        print(e)
        db.rollback()
        if atbd_input.alias:
            raise HTTPException(
                status_code=400,
                detail=f"An ATBD with alias {atbd_input.alias} already exists",
            )
    [created_atbd] = function_execution_result

    output = {
        k.split(".")[-1]: v
        for k, v in dict(created_atbd).items()
        if k.split(".")[0] == "atbds"
    }
    output["versions"] = {
        k.split(".")[-1]: v
        for k, v in dict(created_atbd).items()
        if k.split(".")[0] == "atbd_versions"
    }

    return output
