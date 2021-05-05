import pytest
import json
from app.db.models import Contacts


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

    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)
    result = json.loads(test_client.get("/contacts").content)
    assert len(result) == 2


def test_get_contact_by_id(
    test_client,
    atbds_factory,
    atbd_versions_factory,
    versions_contacts_association_factory,
    db_session,
    contacts_factory,
):
    # Test contact without mechanisms
    contact = contacts_factory.create()
    contact.mechanisms = None
    db_session.add(contact)
    db_session.commit()
    db_session.refresh(contact)

    result = json.loads(test_client.get(f"/contacts/{contact.id}").content)
    assert result["first_name"] == contact.first_name
    assert result["mechanisms"] == []

    # Test contact with mechanisms
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
    assert len(contact.atbd_versions_link) > 0
    assert contact.atbd_versions_link[0].atbd_version.major == version.major


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
            "/contacts",
            headers=authenticated_headers,
            data=json.dumps(contact),
        )
        result.raise_for_status()

    contact = contacts_factory.create().__dict__
    del contact["_sa_instance_state"]
    result = test_client.post(
        "/contacts",
        headers=authenticated_headers,
        data=json.dumps(contact),
    )

    # Autoflush was causing the query to fail as it
    # was trying to insert an object with
    with db_session.no_autoflush:
        contacts_from_db = db_session.query(Contacts).all()
        assert len(contacts_from_db) > 0
        assert contacts_from_db[0].first_name == contact["first_name"]
        assert contacts_from_db[0].last_name == contact["last_name"]
        assert (
            contacts_from_db[0].mechanisms
            == '{"(Email,test@email.com)","(Twitter,@test_handle)"}'
        )

    # Test that mechansism values with parentheses are handled
    contact = contacts_factory.create()
    contact.mechanisms = [
        {"mechanism_type": "Mobile", "mechanism_value": "(123) 456 7891"}
    ]
    contact = contact.__dict__
    del contact["_sa_instance_state"]

    result = test_client.post(
        "/contacts",
        headers=authenticated_headers,
        data=json.dumps(contact),
    )
    result.raise_for_status()

    # Autoflush was causing the query to fail as it
    # was trying to insert an object with
    with db_session.no_autoflush:
        contacts_from_db = db_session.query(Contacts).all()
        assert len(contacts_from_db) > 0
        assert contacts_from_db[1].first_name == contact["first_name"]
        assert contacts_from_db[1].last_name == contact["last_name"]
        assert contacts_from_db[1].mechanisms == '{"(Mobile,\\"(123) 456 7891\\")"}'

    result = test_client.get("/contacts", headers=authenticated_headers)
    result.raise_for_status()
    returned_contact = json.loads(result.content)[1]
    assert returned_contact["mechanisms"] == [
        {"mechanism_type": "Mobile", "mechanism_value": "(123) 456 7891"}
    ]


def test_update_contact(
    test_client, db_session, contacts_factory, authenticated_headers
):
    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)
    db_session.commit()

    with pytest.raises(Exception):

        result = test_client.post(
            f"/contacts/{contact.id}",
            data=json.dumps(
                {"first_name": "new_first_name", "last_name": "new_last_name"}
            ),
        )
        result.raise_for_status()

    result = test_client.post(
        f"/contacts/{contact.id}",
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
        result = test_client.delete(f"/contacts/{contact.id}")
        result.raise_for_status()

    result = test_client.delete(
        f"/contacts/{contact.id}",
        headers=authenticated_headers,
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

    test_client.delete(f"/contacts/{contact.id}", headers=authenticated_headers)
    db_session.refresh(version)
    assert len(version.contacts_link) == 0


def test_update_contacts_in_atbds_version(
    test_client,
    db_session,
    contacts_factory,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):

    contact = contacts_factory.create()
    contact.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact)

    atbd = atbds_factory.create()
    atbd.alias = atbd.alias.lower()
    db_session.add(atbd)
    db_session.commit()

    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")
    db_session.add(version)
    db_session.commit()

    with pytest.raises(Exception):
        result = test_client.post(
            f"/atbds/{atbd.id}/versions/{version.major}",
            data=json.dumps(
                {
                    "contacts": [
                        {"id": contact.id, "roles": ["Science contact", "Investigator"]}
                    ]
                }
            ),
        )
        result.raise_for_status()

    db_session.refresh(version)

    assert version.contacts_link == []

    result = test_client.post(
        f"/atbds/{atbd.id}/versions/{version.major}",
        data=json.dumps(
            {
                "contacts": [
                    {"id": contact.id, "roles": ["Science contact", "Investigator"]}
                ]
            }
        ),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    db_session.refresh(version)
    db_session.refresh(atbd)
    assert len(version.contacts_link) == 1
    assert version.contacts_link[0].contact_id == contact.id
    assert version.contacts_link[0].atbd_id == atbd.id
    assert version.contacts_link[0].major == version.major
    assert version.contacts_link[0].contact == contact
    assert version.contacts_link[0].atbd_version == version

    contact2 = contacts_factory.create()
    contact2.mechanisms = '{"(Email,test@email.com)", "(Twitter,@test_handle)"}'
    db_session.add(contact2)
    db_session.commit()
    db_session.refresh(contact2)

    result = test_client.post(
        f"/atbds/{atbd.id}/versions/{version.major}",
        data=json.dumps(
            {
                "contacts": [
                    {"id": contact2.id, "roles": ["Investigator"]},
                    {"id": contact.id, "roles": ["Science contact", "Investigator"]},
                ]
            }
        ),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    db_session.refresh(version)
    db_session.refresh(atbd)
    assert len(version.contacts_link) == 2
    assert version.contacts_link[1].contact_id == contact2.id
    assert version.contacts_link[1].atbd_id == atbd.id
    assert version.contacts_link[1].major == version.major
    assert version.contacts_link[1].contact == contact2
    assert version.contacts_link[1].atbd_version == version

    result = test_client.post(
        f"/atbds/{atbd.id}/versions/{version.major}",
        data=json.dumps({"contacts": [{"id": contact.id, "roles": []}]}),
        headers=authenticated_headers,
    )
    result.raise_for_status()
    db_session.refresh(version)
    db_session.refresh(atbd)
    assert len(version.contacts_link) == 1
    assert version.contacts_link[0].roles == "{}"

    # This should be moved to the `atbd_versions` unit tests
    result = test_client.get(
        f"/atbds/{atbd.id}/versions/{version.major}",
        data=json.dumps({"contacts": [{"id": contact.id, "roles": []}]}),
        headers=authenticated_headers,
    )

    result.raise_for_status()
    result = json.loads(result.content)
    assert result["versions"][0]["contacts_link"][0]["roles"] == []