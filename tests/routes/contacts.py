import pytest
import json
from typing import List
from datetime import datetime
from fastapi import HTTPException
from app.schemas.contacts import Output as Contacts
from app.db.models import Contacts as ContactsModel


def test_list_contacts(test_client, db_session, contacts_factory):

    assert json.loads(test_client.get("/contacts").content) == []
    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    result = json.loads(test_client.get("/contacts").content)
    assert len(result) == 1
    assert result[0]["first_name"] == contact.first_name
    assert result[0]["mechanisms"] == [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Twitter", "mechanism_value": "@test_handle"},
    ]


def test_get_contact_by_id(test_client, db_session, contacts_factory):
    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    result = json.loads(test_client.get(f"/contacts/{contact.id}").content)
    assert result["first_name"] == contact.first_name
    assert result["mechanisms"] == [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Twitter", "mechanism_value": "@test_handle"},
    ]


def test_create_contact(
    test_client, db_session, contacts_factory, authenticated_headers
):
    contact = contacts_factory.create().__dict__
    del contact["_sa_instance_state"]

    with pytest.raises(Exception):
        result = test_client.post("/contacts", data=json.dumps(contact))
        result.raise_for_status()

    with pytest.raises(Exception):
        contact = contacts_factory.create().__dict__
        del contact["first_name"]
        del contact["_sa_instance_state"]
        result = test_client.post(
            "/contacts", headers=authenticated_headers, data=json.dumps(contact),
        )
        result.raise_for_status()

    contact = contacts_factory.create().__dict__
    del contact["_sa_instance_state"]
    result = json.loads(
        test_client.post(
            "/contacts", headers=authenticated_headers, data=json.dumps(contact),
        ).content
    )

    assert result["first_name"] == contact["first_name"]
    assert result["mechanisms"] == [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Twitter", "mechanism_value": "@test_handle"},
    ]


def test_update_contact(
    test_client, db_session, contacts_factory, authenticated_headers
):
    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()

    with pytest.raises(Exception):
        result = test_client.post(f"/contacts/{contact.id}", data=json.dumps(contact))
        result.raise_for_status()

    test_client.post(
        f"/contacts/{contact.id}",
        data=json.dumps({"first_name": "new_first_name", "last_name": "new_last_name"}),
        headers=authenticated_headers,
    )
    db_session.refresh(contact)
    assert contact.first_name == "new_first_name"
    assert contact.last_name == "new_last_name"
    assert contact.mechanisms == contact.mechanisms


def test_delete_contact(
    test_client, db_session, contacts_factory, authenticated_headers
):
    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()

    with pytest.raises(Exception):
        result = test_client.delete(f"/contacts/{contact.id}", data=json.dumps(contact))
        result.raise_for_status()

    test_client.delete(
        f"/contacts/{contact.id}", headers=authenticated_headers,
    )

    assert db_session.query(ContactsModel).all() == []


def test_update_contacts_in_atbds_version(
    test_client, db_session, contacts_factory, authenticated_headers
):
    # TODO: implement test for adding and removing a contact from an atbd
    pass
    # contact = contacts_factory.create()
    # contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    # db_session.add(contact)
    # db_session.commit()

    # with pytest.raises(Exception):
    #     result = test_client.delete(f"/contacts/{contact.id}", data=json.dumps(contact))
    #     result.raise_for_status()

    # test_client.delete(
    #     f"/contacts/{contact.id}", headers=authenticated_headers,
    # )

    # assert db_session.query(ContactsModel).all() == []
