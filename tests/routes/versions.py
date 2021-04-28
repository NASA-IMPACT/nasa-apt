import pytest
import json
from typing import List
from datetime import datetime


def test_update_atbd_latest_version(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    assert len(atbd["versions"]) == 1
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={atbd['versions'][0]['major']}"
    )
    assert req.doi is None
    assert req.citation == {}
    assert req.changelog is None

    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "doi": "http://doi.org",
                "changelog": "This is a changelog",
                "citation": {"ping": "pong"},
            },
            headers=authenticated_headers,
        ).content
    )
    assert len(updated_atbd["versions"]) == 1
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][0]['major']}"
    )
    assert req.doi == updated_atbd["versions"][0]["doi"]
    assert req.changelog == updated_atbd["versions"][0]["changelog"]
    assert req.citation == updated_atbd["versions"][0]["citation"]

    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "doi": "http://new-doi.org",
                "changelog": "This is a NEW and IMPROVED changelog!",
                "citation": {"pong ping": "ping pong"},
            },
            headers=authenticated_headers,
        ).content
    )
    assert len(updated_atbd["versions"]) == 1

    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][0]['major']}"
    )
    assert req.doi == updated_atbd["versions"][0]["doi"]
    assert req.citation == updated_atbd["versions"][0]["citation"]
    assert req.changelog == updated_atbd["versions"][0]["changelog"]


def test_update_atbd_versions_fails_if_user_is_unauthenticated(
    test_client, db_session, atbd_creation_input, mocked_event_listener
):
    pass


def test_publish_atbd_version(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
    s3_bucket,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    test_client.post(f"/atbds/{atbd['id']}/publish", headers=authenticated_headers)

    [req] = db_session.execute(
        f"SELECT status FROM atbd_versions where atbd_id = '{atbd['id']}'"
    )
    assert req.status == "Published"


def test_publish_atbd_version_fails_if_user_is_unauthenticated():
    pass


def test_publish_atbd_version_fails_if_latest_versions_is_already_published():
    pass


def test_create_new_atbd_version(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
    s3_bucket,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    [req] = db_session.execute(
        f"SELECT major, minor FROM atbd_versions WHERE atbd_id='{atbd['id']}'"
    )
    assert req.major == 1
    assert req.minor == 0

    test_client.post(f"/atbds/{atbd['id']}/publish", headers=authenticated_headers)

    new_version = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions", headers=authenticated_headers
        ).content
    )

    [v1, v2] = db_session.execute(
        f"SELECT major, minor, document FROM atbd_versions WHERE atbd_id='{atbd['id']}'"
    )

    assert v2.major == v1.major + 1
    assert v2.minor == 0
    assert v2.document == v1.document


def test_atbd_versions_returned_in_chronological_order(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
    s3_bucket,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    test_client.post(f"/atbds/{atbd['id']}/publish", headers=authenticated_headers)

    new_version = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions", headers=authenticated_headers
        ).content
    )
    test_client.post(f"/atbds/{atbd['id']}/publish", headers=authenticated_headers)

    new_version = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions", headers=authenticated_headers
        ).content
    )

    versions = json.loads(
        test_client.get(f"/atbds/{atbd['id']}", headers=authenticated_headers).content
    )["versions"]

    timestamps = [
        datetime.strptime(version["created_at"], "%Y-%m-%dT%H:%M:%S.%f%z")
        for version in versions
    ]
    assert sorted(timestamps) == timestamps


def test_create_new_atbd_version_fails_if_user_is_unauthenticated(
    test_client, db_session
):
    pass


def test_create_new_atbd_version_fails_if_latest_version_is_not_published(
    test_client, db_session
):
    pass


def test_update_atbd_specific_version(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
    s3_bucket,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    test_client.post(f"/atbds/{atbd['id']}/publish", headers=authenticated_headers)

    new_version = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions", headers=authenticated_headers
        ).content
    )

    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={atbd['versions'][-1]['major']}"
    )
    assert req.doi is None
    assert req.changelog is None

    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/v2.0",
            json={"doi": "http://doi.org", "changelog": "This is a changelog"},
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.doi == updated_atbd["versions"][-1]["doi"]
    assert req.changelog == updated_atbd["versions"][-1]["changelog"]

    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "doi": "http://new-doi.org",
                "changelog": "This is a NEW and IMPROVED changelog!",
            },
            headers=authenticated_headers,
        ).content
    )

    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.doi == updated_atbd["versions"][-1]["doi"]
    assert req.changelog == updated_atbd["versions"][-1]["changelog"]


def test_update_document(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )
    # TODO: test that this requests succeeded
    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "document": {
                    "algorithm_implementations": [
                        {
                            "url": "https://developmentseed.org",
                            "description": "This is our website",
                        }
                    ]
                }
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.document is not None

    assert req.document["algorithm_implementations"] == [
        {"url": "https://developmentseed.org", "description": "This is our website",}
    ]
    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "document": {
                    "mathematical_theory_assumptions": {
                        "children": [
                            {
                                "type": "p",
                                "children": [
                                    {"text": "There are no assumptions being made "},
                                    {"text": "at the moment", "italic": True},
                                    {"text": "."},
                                ],
                            }
                        ]
                    },
                }
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.document is not None
    assert req.document["algorithm_implementations"] == [
        {"url": "https://developmentseed.org", "description": "This is our website",}
    ]
    assert req.document["mathematical_theory_assumptions"] == {
        "children": [
            {
                "type": "p",
                "children": [
                    {"text": "There are no assumptions being made "},
                    {"text": "at the moment", "italic": True},
                    {"text": "."},
                ],
            }
        ]
    }

    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest?overwrite=true",
            json={
                "document": {
                    "publication_references": [
                        {
                            "id": 1,
                            "authors": "Dickens, Charles and Steinbeck, John",
                            "title": "Example Reference",
                            "series": "A",
                            "edition": "3rd",
                            "volume": "42ml",
                            "issue": "ticket",
                            "publication_place": "Boston",
                            "publisher": "PenguinBooks",
                            "pages": "189-198",
                            "isbn": 123456789,
                            "year": 1995,
                        }
                    ]
                }
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.document is not None
    assert not req.document.get("algorithm_implementations")
    assert not req.document.get("mathematical_theory_assumptions")
    assert req.document["publication_references"] == [
        {
            "id": 1,
            "authors": "Dickens, Charles and Steinbeck, John",
            "title": "Example Reference",
            "series": "A",
            "edition": "3rd",
            "volume": "42ml",
            "issue": "ticket",
            "publication_place": "Boston",
            "publisher": "PenguinBooks",
            "pages": "189-198",
            "isbn": 123456789,
            "year": 1995,
        }
    ]


def test_update_sections_completed(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
):
    atbd = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )
    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "sections_completed": {
                    "new_top_level_key": {
                        "new_sub_level_key_1": "abc",
                        "new_sub_level_key_2": "def",
                    },
                }
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.sections_completed is not None
    assert req.sections_completed["new_top_level_key"] == {
        "new_sub_level_key_1": "abc",
        "new_sub_level_key_2": "def",
    }
    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest",
            json={
                "sections_completed": {
                    "new_top_level_key": "Just a single string",
                    "even_newer_top_level_key": "Just another string",
                }
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.sections_completed is not None
    assert req.sections_completed["new_top_level_key"] == "Just a single string"
    assert req.sections_completed["even_newer_top_level_key"] == "Just another string"

    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest?overwrite=true",
            json={
                "sections_completed": {
                    "overwritten_top_level_key": "Just another string"
                }
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.sections_completed is not None
    assert not req.sections_completed.get("new_top_level_key")
    assert not req.sections_completed.get("even_newer_top_level_key")
    assert req.sections_completed["overwritten_top_level_key"] == "Just another string"


def test_update_minor_version_of_draft_atbd_fails():
    pass

