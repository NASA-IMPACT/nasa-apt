import json

import pytest

from app.db.models import Contacts


def test_list_contacts(
    test_client, db_session, contacts_factory, authenticated_headers
):

    contact = contacts_factory.create()

    with pytest.raises(Exception):
        result = test_client.get("/v2/contacts")
        result.raise_for_status()

    result = json.loads(
        test_client.get("/v2/contacts", headers=authenticated_headers).content
    )
    assert len(result) == 1
    assert result[0]["first_name"] == contact.first_name
    assert result[0]["mechanisms"] == [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Mobile", "mechanism_value": "(123) 456 7891"},
    ]

    contact = contacts_factory.create()

    result = json.loads(
        test_client.get("/v2/contacts", headers=authenticated_headers).content
    )
    assert len(result) == 2


def test_get_contact_by_id(
    test_client,
    atbds_factory,
    atbd_versions_factory,
    versions_contacts_association_factory,
    authenticated_headers,
    db_session,
    contacts_factory,
):
    # Test contact without mechanisms
    contact = contacts_factory.create(mechanisms="{}")

    with pytest.raises(Exception):
        result = test_client.get(f"/v2/contacts/{contact.id}")
        result.raise_for_status()

    result = json.loads(
        test_client.get(
            f"/v2/contacts/{contact.id}", headers=authenticated_headers
        ).content
    )
    assert result["first_name"] == contact.first_name
    assert result["mechanisms"] == []

    # Test contact with mechanisms
    contact = contacts_factory.create()
    db_session.refresh(contact)

    result = json.loads(
        test_client.get(
            f"/v2/contacts/{contact.id}", headers=authenticated_headers
        ).content
    )
    assert result["first_name"] == contact.first_name
    assert result["mechanisms"] == [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Mobile", "mechanism_value": "(123) 456 7891"},
    ]

    atbd = atbds_factory.create()
    db_session.refresh(atbd)

    version = atbd_versions_factory.create(atbd_id=atbd.id)
    db_session.refresh(version)

    versions_contacts_association_factory.create(
        atbd_id=atbd.id,
        major=version.major,
        contact_id=contact.id,
        roles='{{"Investigator", "Science contact"}}',
    )
    db_session.commit()

    result = test_client.get(
        f"/v2/contacts/{contact.id}", headers=authenticated_headers
    )
    result.raise_for_status()
    result = json.loads(result.content)

    assert len(result["atbd_versions_link"]) > 0
    assert result["atbd_versions_link"][0]["atbd_version"]["major"] == version.major
    assert (
        result["atbd_versions_link"][0]["atbd_version"]["atbd"]["title"] == atbd.title
    )
    assert result["atbd_versions_link"][0]["atbd_version"]["atbd"]["id"] == atbd.id
    assert (
        result["atbd_versions_link"][0]["atbd_version"]["atbd"]["alias"] == atbd.alias
    )


def test_create_contact(
    test_client, db_session, contacts_factory, authenticated_headers
):
    with pytest.raises(Exception):
        contact = contacts_factory.create()
        del contact["_sa_instance_state"]
        result = test_client.post("/contacts", data=json.dumps(contact))
        result.raise_for_status()

    with pytest.raises(Exception):
        contact = contacts_factory.create().__dict__
        del contact["first_name"]
        del contact["_sa_instance_state"]
        result = test_client.post(
            "/v2/contacts", headers=authenticated_headers, data=json.dumps(contact),
        )
        result.raise_for_status()

    contact = contacts_factory.create().__dict__
    contact["mechanisms"] = [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Mobile", "mechanism_value": "(123) 456 7891"},
    ]
    del contact["_sa_instance_state"]
    result = test_client.post(
        "/v2/contacts", headers=authenticated_headers, data=json.dumps(contact),
    )
    db_session.close()

    contact_from_db = db_session.query(Contacts).get(contact["id"])
    assert contact_from_db.first_name == contact["first_name"]
    assert contact_from_db.last_name == contact["last_name"]
    assert (
        contact_from_db.mechanisms
        == '{"(Email,test@email.com)","(Mobile,\\"(123) 456 7891\\")"}'
    )

    # Test that mechansism values with parentheses are handled
    contact = contacts_factory.create().__dict__
    contact["mechanisms"] = [
        {"mechanism_type": "Email", "mechanism_value": "test@email.com"},
        {"mechanism_type": "Mobile", "mechanism_value": "(123) 456 7891"},
    ]
    del contact["_sa_instance_state"]

    result = test_client.post(
        "/v2/contacts", headers=authenticated_headers, data=json.dumps(contact),
    )
    result.raise_for_status()
    db_session.close()

    contact_from_db = db_session.query(Contacts).get(contact["id"])
    assert contact_from_db.first_name == contact["first_name"]
    assert contact_from_db.last_name == contact["last_name"]
    assert (
        contact_from_db.mechanisms
        == '{"(Email,test@email.com)","(Mobile,\\"(123) 456 7891\\")"}'
    )


def test_update_contact(
    test_client, db_session, contacts_factory, authenticated_headers
):
    contact = contacts_factory.create()

    with pytest.raises(Exception):

        result = test_client.post(
            f"/v2/contacts/{contact.id}",
            data=json.dumps(
                {"first_name": "new_first_name", "last_name": "new_last_name"}
            ),
        )
        result.raise_for_status()

    result = test_client.post(
        f"/v2/contacts/{contact.id}",
        data=json.dumps({"first_name": "new_first_name", "last_name": "new_last_name"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    db_session.refresh(contact)
    assert contact.first_name == "new_first_name"
    assert contact.last_name == "new_last_name"
    assert contact.mechanisms == contact.mechanisms


def test_delete_contact(
    test_client,
    db_session,
    contacts_factory,
    atbds_factory,
    atbd_versions_factory,
    versions_contacts_association_factory,
    authenticated_headers,
):
    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()

    with pytest.raises(Exception):
        result = test_client.delete(f"/v2/contacts/{contact.id}")
        result.raise_for_status()

    result = test_client.delete(
        f"/v2/contacts/{contact.id}", headers=authenticated_headers,
    )
    result.raise_for_status()
    assert db_session.query(Contacts).all() == []

    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()

    atbd = atbds_factory.create()
    atbd.alias = atbd.alias.lower()
    db_session.add(atbd)
    db_session.commit()

    version = atbd_versions_factory.create(atbd_id=atbd.id)
    db_session.add(version)
    db_session.commit()

    version_contact_association = versions_contacts_association_factory.create(
        atbd_id=atbd.id,
        major=version.major,
        contact_id=contact.id,
        roles='{{"Investigator", "Science contact"}}',
    )
    db_session.add(version_contact_association)
    db_session.commit()

    db_session.refresh(version)
    db_session.refresh(contact)
    assert len(version.contacts_link) > 0
    assert version.contacts_link[0].contact.id == contact.id

    test_client.delete(f"/v2/contacts/{contact.id}", headers=authenticated_headers)
    db_session.refresh(version)
    assert len(version.contacts_link) == 0
