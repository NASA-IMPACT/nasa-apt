import pytest
import json
from typing import List


def _create_atbd_with_versions(
    db_session, atbds_factory, atbd_versions_factory, version_statuses: List[str] = []
):
    atbd = atbds_factory.create()
    atbd.alias = atbd.alias.lower()
    db_session.add(atbd)
    db_session.commit()
    db_session.refresh(atbd)
    atbd_versions = []
    for version_status in version_statuses:
        atbd_version = atbd_versions_factory(atbd_id=atbd.id, status=version_status)
        db_session.add(atbd_version)
        db_session.commit()
        db_session.refresh(atbd_version)
        atbd_versions.append(atbd_version)
    return atbd, atbd_versions


def test_list_atbds_returns_empty_when_db_is_empty(test_client):
    assert json.loads(test_client.get("/atbds").content) == []


def test_list_atbds_returns_empty_user_is_not_autenticated_and_no_atbds_have_published_versions(
    test_client, db_session, atbds_factory, atbd_versions_factory
):

    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Review"],
    )
    _, _ = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Review"],
    )
    result = json.loads(test_client.get("/atbds").content)
    assert result == []


def test_list_atbds_returns_only_published_versions_when_user_is_not_autenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory
):

    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    _, _ = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    result = json.loads(test_client.get("/atbds").content)
    assert len(result) == 2
    result = result[0]
    assert result["title"] == atbd.title
    assert len(result["versions"]) == 1
    assert result["versions"][0]["status"] == "Published"


def test_list_atbds_returns_all_versions_when_user_is_authenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, authenticated_headers
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    _, _ = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    result = json.loads(
        test_client.get("/atbds", headers=authenticated_headers).content
    )
    assert len(result) == 2
    result = result[0]
    assert result["title"] == atbd.title
    assert len(result["versions"]) == 2
    assert set(map(lambda d: d["status"], result["versions"])) == {
        "Published",
        "Draft",
    }


def test_get_atbd_by_alias_fails_when_no_versions_are_published_and_user_is_unathenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Review"],
    )
    with pytest.raises(Exception) as e:
        req = test_client.get(f"/atbds/{atbd.alias}")
        req.raise_for_status()
    assert str(e.value).startswith("404")


def test_get_atbd_by_alias_returns_only_published_versions_and_user_is_unathenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, authenticated_headers
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    result = json.loads(test_client.get(f"/atbds/{atbd.alias}").content)

    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 1
    assert result["versions"][0]["status"] == "Published"


def test_get_atbd_by_alias_returns_all_versions_when_user_is_authenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, authenticated_headers
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    result = json.loads(
        test_client.get(f"/atbds/{atbd.alias}", headers=authenticated_headers).content
    )

    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 2

    assert set(map(lambda d: d["status"], result["versions"])) == {
        "Published",
        "Draft",
    }


def test_get_atbd_by_id_fails_when_no_versions_are_published_and_user_is_unathenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Review"],
    )
    with pytest.raises(Exception) as e:
        req = test_client.get(f"/atbds/{atbd.id}")
        req.raise_for_status()
    assert str(e.value).startswith("404")


def test_get_atbd_by_id_returns_only_published_versions_and_user_is_unathenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, authenticated_headers
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    result = json.loads(test_client.get(f"/atbds/{atbd.id}").content)

    assert result["id"] == atbd.id
    assert len(result["versions"]) == 1
    assert result["versions"][0]["status"] == "Published"


def test_get_atbd_by_id_returns_all_versions_when_user_is_authenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, authenticated_headers
):
    atbd, versions = _create_atbd_with_versions(
        db_session,
        atbds_factory,
        atbd_versions_factory,
        version_statuses=["Draft", "Published"],
    )
    result = json.loads(
        test_client.get(f"/atbds/{atbd.id}", headers=authenticated_headers).content
    )

    assert result["id"] == atbd.id
    assert len(result["versions"]) == 2
    assert set(map(lambda d: d["status"], result["versions"])) == {
        "Published",
        "Draft",
    }


def test_get_atbd_fails_when_atbd_alias_does_not_exist(test_client):
    with pytest.raises(Exception) as e:
        req = test_client.get("/atbds/non-existent-alias")
        req.raise_for_status()
    assert str(e.value).startswith("404")


def test_that_atbd_creation_fails_if_user_is_unauthenticated(
    test_client, atbd_creation_input
):
    with pytest.raises(Exception) as e:
        req = test_client.post("/atbds", json=atbd_creation_input)
        req.raise_for_status()
    assert str(e.value).startswith("401")


def test_atbd_creation_without_alias(
    test_client, db_session, atbd_creation_input, authenticated_headers
):
    del atbd_creation_input["alias"]
    created_item = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    [dbobj] = db_session.execute(
        f"SELECT * FROM atbds WHERE atbds.id = '{created_item['id']}'"
    )
    assert created_item["title"] == dbobj.title
    assert dbobj.alias is None


def test_atbd_creation_with_alias(
    test_client, db_session, atbd_creation_input, authenticated_headers
):
    created_item = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    [dbobj] = db_session.execute(
        f"SELECT * FROM atbds WHERE atbds.id = '{created_item['id']}'"
    )
    assert created_item["title"] == dbobj.title
    assert created_item["alias"] == dbobj.alias


def test_create_atbd_with_non_unique_alias_fail(
    test_client, db_session, atbd_creation_input, authenticated_headers
):
    _ = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    with pytest.raises(Exception) as e:
        duplicated_item_request = test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        )
        duplicated_item_request.raise_for_status()
    assert str(e.value).startswith("400")


def test_create_atbd_fails_if_missing_title(test_client, atbd_creation_input):
    del atbd_creation_input["title"]
    with pytest.raises(Exception) as e:
        unauthenticated_request = test_client.post("/atbds", json=atbd_creation_input)
        unauthenticated_request.raise_for_status()

    assert str(e.value).startswith("401")


def test_update_atbd_by_id(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
):

    created = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )
    updated = json.loads(
        test_client.post(
            f"/atbds/{created['id']}",
            json={"title": "New and improved!"},
            headers=authenticated_headers,
        ).content
    )
    print("UPDATED: ", updated)

    [dbobj] = db_session.execute(
        f"SELECT * FROM atbds WHERE atbds.id = '{updated['id']}'"
    )
    assert created["title"] != dbobj.title
    assert dbobj.title == "New and improved!"
    assert created["alias"] == dbobj.alias


def test_update_atbd_by_alias(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
):

    created = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )
    updated = json.loads(
        test_client.post(
            f"/atbds/{created['alias']}",
            json={"title": "New and improved!"},
            headers=authenticated_headers,
        ).content
    )

    [dbobj] = db_session.execute(
        f"SELECT * FROM atbds WHERE atbds.id = '{updated['id']}'"
    )
    assert created["title"] != dbobj.title
    assert dbobj.title == "New and improved!"
    assert created["alias"] == dbobj.alias


def test_update_atbd_fails_if_updated_alias_already_exists_in_database(
    test_client,
    db_session,
    atbd_creation_input,
    authenticated_headers,
    mocked_event_listener,
):
    atbd1 = json.loads(
        test_client.post(
            "/atbds", json=atbd_creation_input, headers=authenticated_headers
        ).content
    )

    # Create another ATBD whose alias will conflict with the
    # alias we try to set for atbd1
    atbd_creation_input["alias"] = "atbd-alias-2"
    test_client.post("/atbds", json=atbd_creation_input, headers=authenticated_headers)

    with pytest.raises(Exception) as e:
        # update atbd1 with an alias that already belongs to atbd2
        req = test_client.post(
            f"/atbds/{atbd1['id']}",
            json={"alias": "atbd-alias-2"},
            headers=authenticated_headers,
        )
        req.raise_for_status()

    assert str(e.value).startswith("401")


def test_update_atbd_fails_if_user_is_not_authenticated(
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
    with pytest.raises(Exception) as e:
        req = test_client.post(f"/atbds/{atbd['id']}", json={"alias": "atbd-alias-2"},)
        req.raise_for_status()

    assert str(e.value).startswith("401")


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


def test_update_document_by_key(
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
            f"/atbds/{atbd['id']}/versions/latest/document",
            json={
                "key": "new_top_level_key",
                "value": {"new_sub_level_key_1": "abc", "new_sub_level_key_2": "def"},
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.document is not None
    assert "new_top_level_key" in req.document
    assert req.document["new_top_level_key"] == {
        "new_sub_level_key_1": "abc",
        "new_sub_level_key_2": "def",
    }
    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest/document",
            json={"key": "new_top_level_key", "value": "Just a single string"},
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.document is not None
    assert "new_top_level_key" in req.document
    assert req.document["new_top_level_key"] == "Just a single string"


def test_update_sections_completed_by_key(
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
            f"/atbds/{atbd['id']}/versions/latest/sections_completed",
            json={
                "key": "new_top_level_key",
                "value": {"new_sub_level_key_1": "abc", "new_sub_level_key_2": "def"},
            },
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.sections_completed is not None
    assert "new_top_level_key" in req.sections_completed
    assert req.sections_completed["new_top_level_key"] == {
        "new_sub_level_key_1": "abc",
        "new_sub_level_key_2": "def",
    }
    updated_atbd = json.loads(
        test_client.post(
            f"/atbds/{atbd['id']}/versions/latest/sections_completed",
            json={"key": "new_top_level_key", "value": "Just a single string"},
            headers=authenticated_headers,
        ).content
    )
    [req] = db_session.execute(
        f"SELECT * FROM atbd_versions WHERE atbd_id='{atbd['id']}' AND major={updated_atbd['versions'][-1]['major']}"
    )
    assert req.sections_completed is not None
    assert "new_top_level_key" in req.sections_completed
    assert req.sections_completed["new_top_level_key"] == "Just a single string"


def test_update_atbd_version_fails_if_user_is_unauthenticated(test_client, db_session):
    pass


def get_atbd_version(test_client, db_session):
    pass

