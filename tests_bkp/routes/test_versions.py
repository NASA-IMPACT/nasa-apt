import json
import random
import time
from datetime import datetime

import pytest

# TODO: add tests for image upload/download
# TODO: add tests for pdf generation


def test_check_version_exists(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
    authenticated_headers,
):
    atbd = atbds_factory.create()

    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")

    # check unauthenticated access
    with pytest.raises(Exception):
        result = test_client.head(f"/v2/atbds/{atbd.id}/versions/{version.major}")
        result.raise_for_status()

    # check non-existent atbd_id
    with pytest.raises(Exception):
        result = test_client.head(
            f"/v2/atbds/999/versions/{version.major}", headers=authenticated_headers
        )
        result.raise_for_status()
    # check non-existent version major
    with pytest.raises(Exception):
        result = test_client.head(
            f"/v2/atbds/{atbd.id}/versions/999", headers=authenticated_headers
        )
        result.raise_for_status()

    result = test_client.head(
        f"/v2/atbds/{atbd.id}/versions/{version.major}", headers=authenticated_headers
    )

    result.raise_for_status()
    result = test_client.head(
        f"/v2/atbds/{atbd.id}/versions/v{version.major}.{version.minor}",
        headers=authenticated_headers,
    )
    result.raise_for_status()

    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Published")
    db_session.add(version)
    db_session.commit()

    result = test_client.head(f"/v2/atbds/{atbd.id}/versions/{version.major}")
    result.raise_for_status()
    result = test_client.head(
        f"/v2/atbds/{atbd.id}/versions/v{version.major}.{version.minor}"
    )
    result.raise_for_status()


def test_get_version(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
    authenticated_headers,
):
    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")

    with pytest.raises(Exception):
        result = test_client.get(f"/v2/atbds/{atbd.id}/versions/{version.major}")
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.get(
            f"/v2/atbds/999/versions/{version.major}", headers=authenticated_headers
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.get(
            f"/v2/atbds/{atbd.id}/versions/999", headers=authenticated_headers
        )
        result.raise_for_status()

    result = test_client.get(
        f"/v2/atbds/{atbd.id}/versions/{version.major}", headers=authenticated_headers
    )
    result.raise_for_status()
    result = json.loads(result.content)

    assert result["versions"][0]["doi"] == version.doi
    assert result["versions"][0]["changelog"] == version.changelog
    assert len(result["versions"][0]["document"].values()) > 0


def test_create_version(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
    authenticated_headers,
):

    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")

    # check unauthenticated access
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions",
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.post(
            "/v2/atbds/999/versions",
            headers=authenticated_headers,
        )
        result.raise_for_status()
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions",
            headers=authenticated_headers,
        )
        result.raise_for_status()

    version.status = "Published"
    db_session.add(version)
    db_session.commit()

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions",
        headers=authenticated_headers,
    )
    result.raise_for_status()
    db_session.refresh(atbd)
    assert len(atbd.versions) == 2


def test_update_version(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
    authenticated_headers,
):

    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")

    # check unauthenticated access
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions/999",
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/999/versions/{version.major}",
            headers=authenticated_headers,
        )
        result.raise_for_status()

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
        data=json.dumps(
            {
                "changelog": "updated changelog",
                "this_key_should_be_ignored": "This value should be ignored",
            }
        ),
        headers=authenticated_headers,
    )
    result.raise_for_status()
    db_session.refresh(version)

    assert version.changelog == "updated changelog"
    mocked_send_to_elasticsearch.assert_called()
    mocked_validate_cognito_token.assert_called()

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/v{version.major}.{version.minor}",
        data=json.dumps({"changelog": "updated changelog part 2"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()
    db_session.refresh(version)

    assert version.changelog == "updated changelog part 2"
    mocked_send_to_elasticsearch.assert_called()


def test_update_version_contacts(
    test_client,
    db_session,
    contacts_factory,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
):

    contact = contacts_factory.create()
    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")

    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions/{version.major}",
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
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
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

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
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
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
        data=json.dumps({"contacts": [{"id": contact.id, "roles": []}]}),
        headers=authenticated_headers,
    )
    result.raise_for_status()
    db_session.refresh(version)
    db_session.refresh(atbd)
    assert len(version.contacts_link) == 1
    assert version.contacts_link[0].roles == "{}"

    result = test_client.get(
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
        headers=authenticated_headers,
    )

    result.raise_for_status()
    result = json.loads(result.content)
    assert result["versions"][0]["contacts_link"][0]["roles"] == []


def test_update_version_document(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
):

    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions/{version.major}",
            headers=authenticated_headers,
            data=json.dumps({"document": {"not_a_valid_key": {"NOT A VALID VALUE"}}}),
        )
        result.raise_for_status()
    original_output_vars = version.document["algorithm_output_variables"]
    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
        headers=authenticated_headers,
        data=json.dumps(
            {
                "document": {
                    "journal_acknowledgements": {
                        "children": [
                            {
                                "type": "p",
                                "children": [{"text": "Updated TEXT", "bold": True}],
                            }
                        ]
                    }
                }
            }
        ),
    )
    result.raise_for_status()
    db_session.refresh(version)
    assert version.document["journal_acknowledgements"] == {
        "children": [
            {"type": "p", "children": [{"text": "Updated TEXT", "bold": True}]}
        ]
    }
    assert version.document["algorithm_output_variables"] == original_output_vars

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}?overwrite=True",
        headers=authenticated_headers,
        data=json.dumps(
            {
                "document": {
                    "journal_acknowledgements": {
                        "children": [
                            {
                                "type": "p",
                                "children": [{"text": "Updated TEXT", "bold": True}],
                            }
                        ]
                    }
                }
            }
        ),
    )
    result.raise_for_status()
    db_session.refresh(version)
    assert version.document["journal_acknowledgements"] == {
        "children": [
            {"type": "p", "children": [{"text": "Updated TEXT", "bold": True}]}
        ]
    }
    assert version.document.get("algorithm_output_variables") is None


def test_update_version_sections_completed(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
):

    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(
        atbd_id=atbd.id,
        status="Draft",
        sections_completed={"algorithm_input_variables": "incomplete"},
    )
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions/{version.major}",
            headers=authenticated_headers,
            data=json.dumps(
                {"sections_completed": {"not_a_valid_key": {"NOT A VALID VALUE"}}}
            ),
        )
        result.raise_for_status()

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
        headers=authenticated_headers,
        data=json.dumps(
            {"sections_completed": {"algorithm_output_variables": "complete"}}
        ),
    )
    result.raise_for_status()
    db_session.refresh(version)
    assert version.sections_completed["algorithm_output_variables"] == "complete"
    assert version.sections_completed["algorithm_input_variables"] == "incomplete"

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}?overwrite=True",
        headers=authenticated_headers,
        data=json.dumps(
            {"sections_completed": {"algorithm_output_variables": "complete"}}
        ),
    )
    result.raise_for_status()
    db_session.refresh(version)
    assert version.sections_completed["algorithm_output_variables"] == "complete"
    assert version.sections_completed.get("algorithm_input_variables") is None


# Ensure PDF generation get's added to background_task
def test_update_minor_version_number(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
    s3_bucket,
):

    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(
        atbd_id=atbd.id,
        minor=1,
        status="Draft",
    )
    # check can't bump minor version on un-published Version
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions/{version.major}",
            headers=authenticated_headers,
            data=json.dumps({"minor": 2}),
        )
        result.raise_for_status()
    # check can't bump minor version more than crt + 1
    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}/versions/{version.major}",
            headers=authenticated_headers,
            data=json.dumps({"minor": 3}),
        )
        result.raise_for_status()

    version.status = "Published"
    db_session.add(version)
    db_session.commit()

    # Upload the image that the ATBD needs to generate the pdf
    with open("./tests/fullmoon.jpg", "rb") as f:
        s3_bucket.put_object(Key=f"{atbd.id}/images/fullmoon.jpg", Body=f.read())

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/versions/{version.major}",
        headers=authenticated_headers,
        data=json.dumps({"minor": 2}),
    )
    result.raise_for_status()
    db_session.refresh(version)
    assert version.minor == 2

    # ensure a new version of the pdf was created
    s3_bucket.Object(
        f"{atbd.id}/pdf/{atbd.alias}-v{version.major}-{version.minor}.pdf"
    ).load()

    s3_bucket.Object(
        f"{atbd.id}/pdf/{atbd.alias}-v{version.major}-{version.minor}-journal.pdf"
    ).load()


def test_delete_version(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
):
    atbd = atbds_factory.create()
    version = atbd_versions_factory.create(
        atbd_id=atbd.id,
        minor=1,
        status="Draft",
    )
    with pytest.raises(Exception):
        result = test_client.delete(
            f"/v2/atbds/9999/versions/{version.major}",
        )
        result.raise_for_status()
    with pytest.raises(Exception):
        result = test_client.delete(
            f"/v2/atbds/{atbd.id}/versions/9999",
        )
        result.raise_for_status()
    with pytest.raises(Exception):
        result = test_client.delete(
            f"/v2/atbds/{atbd.id}/versions/{version.major}",
        )
        result.raise_for_status()

    result = test_client.delete(
        f"/v2/atbds/{atbd.id}/versions/{version.major}", headers=authenticated_headers
    )
    result.raise_for_status()

    with pytest.raises(Exception):
        db_session.refresh(version)
    mocked_send_to_elasticsearch.assert_called()


def test_atbd_versions_ordering(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_elasticsearch,
    mocked_validate_cognito_token,
):

    atbd1 = atbds_factory.create()
    atbd2 = atbds_factory.create()

    # Create a bunch of versions with a 0.2 second delay in order to test that
    # versions get returned in order of creation
    for _ in range(10):

        atbd_versions_factory.create(
            atbd_id=random.choice([atbd1.id, atbd2.id]),
        )

        time.sleep(0.2)

    result = test_client.get("/v2/atbds", headers=authenticated_headers)
    result.raise_for_status()
    result = json.loads(result.content)
    dt_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    for atbd in result:
        for i in range(len(atbd["versions"]) - 2):
            c1 = atbd["versions"][i]["created_at"]
            c2 = atbd["versions"][i + 1]["created_at"]
            assert datetime.strptime(c1, dt_format) < datetime.strptime(c2, dt_format)

    result = test_client.get("/v2/atbds")
    result.raise_for_status()
    result = json.loads(result.content)
    dt_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    for atbd in result:
        for i in range(len(atbd["versions"]) - 2):
            c1 = atbd["versions"][i]["created_at"]
            c2 = atbd["versions"][i + 1]["created_at"]
            assert datetime.strptime(c1, dt_format) < datetime.strptime(c2, dt_format)
