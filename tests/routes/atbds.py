import pytest
import json
from typing import List
from datetime import datetime
from fastapi import HTTPException

# TODO: add test that elasticsearch indexing get's added to background tasks


def test_list_atbds_unauthenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, mocked_event_listener
):
    assert json.loads(test_client.get("/atbds").content) == []

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")
        db_session.add(atbd)
        db_session.add(version)
    db_session.commit()
    db_session.flush()

    result = json.loads(test_client.get("/atbds").content)
    assert result == []

    for atbd in atbds:
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
    db_session.commit()
    db_session.flush()

    result = json.loads(test_client.get("/atbds").content)

    assert len(result) == 2
    result = result[0]
    assert result["title"] == atbds[0].title
    assert len(result["versions"]) == 1
    assert result["versions"][0]["status"] == "Published"
    assert result["versions"][0]["version"] == "v1.0"


def test_list_atbds_returns_all_versions_when_user_is_authenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    load_db_session,
):

    result = json.loads(
        test_client.get("/atbds", headers=authenticated_headers).content
    )
    assert len(result) == 2
    result = result[0]
    assert result["title"] == load_db_session[0].title
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


def test_index_atbd_is_called():
    pass
