from datetime import datetime
import time
import random
import pytest
import json
from app.db.models import Atbds
from app.schemas import versions
from sqlalchemy.exc import InvalidRequestError
from hypothesis import given, strategies as st


# TODO: add test that elasticsearch indexing get's added to background tasks
# TODO: add test to ensure that verisons are returned in the correct order (unsure if it's
# created_at, or last_updated_at. I think it's created_at)


def test_check_version_exists(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_event_listener,
    authenticated_headers,
):
    atbd = atbds_factory.create()
    atbd.alias = atbd.alias.lower()
    db_session.add(atbd)
    db_session.commit()

    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")
    db_session.add(version)
    db_session.commit()

    with pytest.raises(Exception):
        result = test_client.head(f"atbds/{atbd.id}/versions/{version.major}")
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.head(
            f"atbds/999/versions/{version.major}", headers=authenticated_headers
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.head(
            f"atbds/{atbd.id}/versions/999", headers=authenticated_headers
        )
        result.raise_for_status()

    result = test_client.head(
        f"atbds/{atbd.id}/versions/{version.major}", headers=authenticated_headers
    )

    result.raise_for_status()
    result = test_client.head(
        f"atbds/{atbd.id}/versions/v{version.major}.{version.minor}",
        headers=authenticated_headers,
    )
    result.raise_for_status()

    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Published")
    db_session.add(version)
    db_session.commit()

    result = test_client.head(f"atbds/{atbd.id}/versions/{version.major}")
    result.raise_for_status()
    result = test_client.head(
        f"atbds/{atbd.id}/versions/v{version.major}.{version.minor}"
    )
    result.raise_for_status()


def test_get_version(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_event_listener,
    authenticated_headers,
):
    atbd = atbds_factory.create()
    atbd.alias = atbd.alias.lower()
    db_session.add(atbd)
    db_session.commit()

    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")
    db_session.add(version)
    db_session.commit()

    with pytest.raises(Exception):
        result = test_client.get(f"atbds/{atbd.id}/versions/{version.major}")
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.get(
            f"atbds/999/versions/{version.major}", headers=authenticated_headers
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        result = test_client.get(
            f"atbds/{atbd.id}/versions/999", headers=authenticated_headers
        )
        result.raise_for_status()

    result = test_client.get(
        f"atbds/{atbd.id}/versions/{version.major}", headers=authenticated_headers
    )
    result.raise_for_status()
    result = json.loads(result.content)

    assert result["versions"][0]["doi"] == version.doi
    assert result["versions"][0]["changelog"] == version.changelog
    assert len(result["versions"][0]["document"].values()) > 0


# def test_list_versions():
#     raise NotImplementedError


# def test_create_version():
#     raise NotImplementedError


# def test_update_version():
#     raise NotImplementedError


# def test_update_version_contacts():
#     raise NotImplementedError


# def test_update_version_document():
#     raise NotImplementedError


# def test_update_minor_version_numer():
#     raise NotImplementedError


# def test_delete_version():
#     raise NotImplementedError


# def test_version_timestamps():
#     raise NotImplementedError


def test_atbd_versions_ordering(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):

    atbd1 = atbds_factory.create()
    atbd2 = atbds_factory.create()

    atbd1.alias = atbd1.alias.lower()
    atbd2.alias = atbd2.alias.lower()
    db_session.add(atbd1)
    db_session.add(atbd2)
    db_session.commit()

    versions = []
    for _ in range(20):

        v = atbd_versions_factory.create(
            atbd_id=random.choice([atbd1.id, atbd2.id]),
        )
        versions.append(v)
        db_session.add(v)
        db_session.commit()
        time.sleep(0.2)

    result = test_client.get("/atbds", headers=authenticated_headers)
    result.raise_for_status()
    result = json.loads(result.content)
    dt_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    for atbd in result:
        for i in range(len(atbd["versions"]) - 2):
            c1 = atbd["versions"][i]["created_at"]
            c2 = atbd["versions"][i + 1]["created_at"]
            assert datetime.strptime(c1, dt_format) < datetime.strptime(c2, dt_format)

    result = test_client.get("/atbds")
    result.raise_for_status()
    result = json.loads(result.content)
    dt_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    for atbd in result:
        for i in range(len(atbd["versions"]) - 2):
            c1 = atbd["versions"][i]["created_at"]
            c2 = atbd["versions"][i + 1]["created_at"]
            assert datetime.strptime(c1, dt_format) < datetime.strptime(c2, dt_format)

    # for version in random.choices(versions, k=10):
    #     result = test_client.post(
    #         f"/atbds/{version.atbd_id}/versions/{version.major}",
    #         data=json.dumps(
    #             {"minor": version.minor + 1, "doi": "http://www.new-doi.org"}
    #         ),
    #         headers=authenticated_headers,
    #     )
    #     result.raise_for_status()

    # result = test_client.get("/atbds", headers=authenticated_headers)
    # result.raise_for_status()
    # result = json.loads(result.content)
    # dt_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    # for atbd in result:
    #     for i in range(len(atbd["versions"]) - 2):
    #         c1 = atbd["versions"][i]["created_at"]
    #         c2 = atbd["versions"][i + 1]["created_at"]
    #         assert datetime.strptime(c1, dt_format) < datetime.strptime(c2, dt_format)

    # result = test_client.get("/atbds")
    # result.raise_for_status()
    # result = json.loads(result.content)
    # dt_format = "%Y-%m-%dT%H:%M:%S.%f%z"
    # for atbd in result:
    #     for i in range(len(atbd["versions"]) - 2):
    #         c1 = atbd["versions"][i]["created_at"]
    #         c2 = atbd["versions"][i + 1]["created_at"]
    #         assert datetime.strptime(c1, dt_format) < datetime.strptime(c2, dt_format)
