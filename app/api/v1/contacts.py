from app.schemas import contacts
from app.db.db_session import DbSession
from app.crud.contacts import crud_contacts
from app.db.models import Contacts
from app.api.utils import get_db, require_user
from app.auth.saml import User
from sqlalchemy import func, orm
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()


@router.get(
    "/contacts",
    responses={
        200: dict(
            description="Return a list of contacts, filterable by field such as `first_name` , `last_name`, etc"
        )
    },
    response_model=List[contacts.Output],
)
def list_contacts(
    filters: contacts.ListFilters = None,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    if filters:
        return crud_contacts.get_multi(db_session=db, filters=filters)
    return crud_contacts.get_multi(db_session=db)


@router.get(
    "/contacts/{contact_id}",
    responses={
        200: dict(
            description="Returns the contact corresponding to the given contact id"
        )
    },
    response_model=contacts.Output,
)
def get_contact(
    contact_id: str, db: DbSession = Depends(get_db), user: User = Depends(require_user)
):
    try:

        # print(
        #     "ATBD VERSIONS LINK FOR CONTACT: ",
        #     crud_contacts.get(
        #         db_session=db, obj_in=contacts.Lookup(id=contact_id)
        #     ).atbd_versions_link,
        # )
        return crud_contacts.get(db_session=db, obj_in=contacts.Lookup(id=contact_id))
    except orm.exc.NoResultFound:
        raise HTTPException(
            status_code=404, detail=f"No contact found for id {contact_id}"
        )


@router.post(
    "/contacts",
    responses={200: dict(description="Create a new contact")},
    response_model=contacts.Output,
)
def create_contact(
    create_contact_input: contacts.Create,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    print("Create Contact Input: ", create_contact_input)
    return crud_contacts.create(db_session=db, obj_in=create_contact_input)


@router.post(
    "/contacts/{contact_id}",
    responses={
        200: dict(description="Update a contact corresponding to the given contact id")
    },
    response_model=contacts.Output,
)
def update_contact(
    contact_id: int,
    update_contact_input: contacts.Update,
    db: DbSession = Depends(get_db),
    user: User = Depends(require_user),
):
    contact = crud_contacts.get(db_session=db, obj_in=contacts.Lookup(id=contact_id))

    return crud_contacts.update(db=db, db_obj=contact, obj_in=update_contact_input)


@router.delete(
    "/contacts/{contact_id}",
    responses={
        200: dict(
            description="Delete the contact corresponding to the given contact id"
        )
    },
)
def delete_contact(
    contact_id: int, db: DbSession = Depends(get_db), user: User = Depends(require_user)
):
    contact = crud_contacts.get(db_session=db, obj_in=contacts.Lookup(id=contact_id))
    db.delete(contact)
    db.commit()
    return []
