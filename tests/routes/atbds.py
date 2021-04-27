import pytest
import json
from typing import List
from datetime import datetime
from fastapi import HTTPException
from app.db.models import Atbds, AtbdVersions

# TODO: add test that elasticsearch indexing get's added to background tasks
# TODO: add test to ensure that verisons are returned in the correct order (unsure if it's
# created_at, or last_updated_at. I think it's created_at)


def test_list_atbds_unauthenticated(
    test_client, db_session, atbds_factory, atbd_versions_factory, mocked_event_listener
):
    assert json.loads(test_client.get("/atbds").content) == []

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")
        db_session.add(version)
        db_session.commit()

    result = json.loads(test_client.get("/atbds").content)
    assert result == []

    for atbd in atbds:
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Draft", major=2, minor=0
        )
        db_session.add(version)
        db_session.commit()

    result = json.loads(test_client.get("/atbds").content)

    assert len(result) == 2
    for i, r in enumerate(result):
        assert r["title"] == atbds[i].title
        assert len(r["versions"]) == 1
        assert r["versions"][0]["status"] == "Published"
        assert r["versions"][0]["version"] == "v1.0"


def test_list_atbds_authenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):
    assert (
        json.loads(test_client.get("/atbds", headers=authenticated_headers).content)
        == []
    )
    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Draft", major=2, minor=0
        )
        db_session.add(version)
        db_session.commit()

    result = json.loads(
        test_client.get("/atbds", headers=authenticated_headers).content
    )
    assert len(result) == 2
    for i, r in enumerate(result):
        assert r["title"] == atbds[i].title
        assert r["alias"] == atbds[i].alias
        assert len(r["versions"]) == 2
        assert set(v["status"] for v in r["versions"]) == {"Draft", "Published"}
        assert set(v["version"] for v in r["versions"]) == {"v1.0", "v2.0"}


def test_get_atbd_by_id_unauthenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):
    with pytest.raises(Exception):
        result = test_client.get("/atbds/1")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Draft", major=2, minor=0
        )
        db_session.add(version)
        db_session.commit()

    atbd = atbds[0]
    db_session.refresh(atbd)

    result = test_client.get(f"/atbds/{atbd.id}")
    result.raise_for_status()
    result = json.loads(result.content)
    assert result["title"] == atbd.title
    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 1
    assert result["versions"][0]["status"] == "Published"
    assert result["versions"][0]["version"] == "v1.0"


def test_get_atbd_by_id_authenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):
    with pytest.raises(Exception):
        result = test_client.get("/atbds/1")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Draft", major=2, minor=0
        )
        db_session.add(version)
        db_session.commit()

    atbd = atbds[0]
    db_session.refresh(atbd)

    result = test_client.get(f"/atbds/{atbd.id}", headers=authenticated_headers)
    result.raise_for_status()
    result = json.loads(result.content)
    assert result["title"] == atbd.title
    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 2
    assert set(v["status"] for v in result["versions"]) == {"Draft", "Published"}
    assert set(v["version"] for v in result["versions"]) == {"v1.0", "v2.0"}


def test_get_atbd_by_alias_unauthenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):
    with pytest.raises(Exception):
        result = test_client.get("/atbds/non-existent-alias")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Draft", major=2, minor=0
        )
        db_session.add(version)
        db_session.commit()

    atbd = atbds[0]
    db_session.refresh(atbd)

    result = test_client.get(f"/atbds/{atbd.alias}")
    result.raise_for_status()
    result = json.loads(result.content)
    assert result["title"] == atbd.title
    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 1
    assert result["versions"][0]["status"] == "Published"
    assert result["versions"][0]["version"] == "v1.0"


def test_get_atbd_by_alias_authenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):
    with pytest.raises(Exception):
        result = test_client.get("/atbds/non-existent-alias")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd.alias = atbd.alias.lower()
        db_session.add(atbd)
        db_session.commit()

        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        db_session.add(version)
        version = atbd_versions_factory.create(
            atbd_id=atbd.id, status="Draft", major=2, minor=0
        )
        db_session.add(version)
        db_session.commit()

    atbd = atbds[0]
    db_session.refresh(atbd)

    result = test_client.get(f"/atbds/{atbd.alias}", headers=authenticated_headers)
    result.raise_for_status()
    result = json.loads(result.content)
    assert result["title"] == atbd.title
    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 2
    assert set(v["status"] for v in result["versions"]) == {"Draft", "Published"}
    assert set(v["version"] for v in result["versions"]) == {"v1.0", "v2.0"}


def test_create_atbd_without_alias(test_client, db_session, authenticated_headers):

    with pytest.raises(Exception):
        result = test_client.post("/atbds", data=json.dumps({"title": "New Test ATBD"}))
        result.raise_for_status()

    result = test_client.post(
        "/atbds",
        data=json.dumps({"title": "New Test ATBD"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    result = json.loads(result.content)
    atbd = db_session.query(Atbds).get(result["id"])
    assert atbd.title == "New Test ATBD"
    assert atbd.alias is None
    assert atbd.created_at is not None
    assert atbd.created_by is not None
    assert atbd.last_updated_at is not None
    assert atbd.last_updated_by is not None
    assert atbd.created_at == atbd.last_updated_at
    assert atbd.created_by == atbd.last_updated_by

    assert len(atbd.versions) == 1
    assert atbd.versions[0].status == "Draft"
    assert atbd.versions[0].major == 1
    assert atbd.versions[0].minor == 0
    assert atbd.versions[0].created_at is not None
    assert atbd.versions[0].created_by is not None
    assert atbd.versions[0].last_updated_at is not None
    assert atbd.versions[0].last_updated_by is not None
    assert atbd.versions[0].created_at == atbd.versions[0].last_updated_at
    assert atbd.versions[0].created_by == atbd.versions[0].last_updated_by


def test_create_atbd_with_alias(test_client, db_session, authenticated_headers):
    with pytest.raises(Exception):
        result = test_client.post(
            "/atbds",
            data=json.dumps(
                {"title": "New Test ATBD", "alias": "Non Conforming Alias"}
            ),
            headers=authenticated_headers,
        )
        result.raise_for_status()

    result = test_client.post(
        "/atbds",
        data=json.dumps({"title": "New Test ATBD", "alias": "new-test-atbd-alias"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    with pytest.raises(Exception):
        # Test that duplicate alias fails
        failed_result = test_client.post(
            "/atbds",
            data=json.dumps({"title": "New Test ATBD", "alias": "new-test-atbd-alias"}),
            headers=authenticated_headers,
        )
        failed_result.raise_for_status()

    result = json.loads(result.content)
    atbd = db_session.query(Atbds).get(result["id"])

    assert atbd.title == "New Test ATBD"
    assert atbd.alias == "new-test-atbd-alias"
    assert atbd.created_at is not None
    assert atbd.created_by is not None
    assert atbd.last_updated_at is not None
    assert atbd.last_updated_by is not None
    assert atbd.created_at == atbd.last_updated_at
    assert atbd.created_by == atbd.last_updated_by

    assert len(atbd.versions) == 1
    assert atbd.versions[0].status == "Draft"
    assert atbd.versions[0].major == 1
    assert atbd.versions[0].minor == 0
    assert atbd.versions[0].created_at is not None
    assert atbd.versions[0].created_by is not None
    assert atbd.versions[0].last_updated_at is not None
    assert atbd.versions[0].last_updated_by is not None
    assert atbd.versions[0].created_at == atbd.versions[0].last_updated_at
    assert atbd.versions[0].created_by == atbd.versions[0].last_updated_by


def test_update_atbd_by_id(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_event_listener,
):

    with pytest.raises(Exception):
        result = test_client.post(
            "/atbds/1", data=json.dumps({"title": "New Test ATBD"})
        )
        result.raise_for_status()

    atbd = atbds_factory.create()
    atbd.alias = None
    db_session.add(atbd)
    db_session.commit()

    # create a version to go along with the atbd
    # otherwise the atbd will fail to retrieve since
    # it mandatorily joins versions on ATBDSs
    version = atbd_versions_factory.create(atbd_id=atbd.id)
    db_session.add(version)
    db_session.commit()

    assert atbd.title == atbd.title
    assert atbd.alias is None

    with pytest.raises(Exception):
        result = test_client.post(
            f"/atbds/{atbd.id}",
            data=json.dumps(
                {"title": "New Test ATBD", "alias": "Non conforming alias"}
            ),
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        atbd2 = atbds_factory.create()
        atbd2.alias = atbd2.alias.lower()
        db_session.add(atbd2)
        db_session.commit()

        version = atbd_versions_factory.create(atbd_id=atbd.id)
        db_session.add(version)
        db_session.commit()

        # ensure that updating alias to an already existing alias
        # fails
        result = test_client.post(
            f"/atbds/{atbd.id}",
            data=json.dumps({"title": "New Test ATBD", "alias": atbd2.alias}),
        )
        result.raise_for_status()

    result = test_client.post(
        f"/atbds/{atbd.id}",
        data=json.dumps({"title": "New (Updated) Test ATBD", "alias": "new-alias"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    # Refresh to reload changes made by the above POST
    db_session.refresh(atbd)
    assert atbd.title == "New (Updated) Test ATBD"
    assert atbd.alias == "new-alias"
    assert atbd.last_updated_at is not None
    assert atbd.last_updated_by is not None
    assert atbd.last_updated_at > atbd.created_at


# def test_create_atbd_with_non_unique_alias_fail(
#     test_client, db_session, atbd_creation_input, authenticated_headers
# ):
#     _ = json.loads(
#         test_client.post(
#             "/atbds", json=atbd_creation_input, headers=authenticated_headers
#         ).content
#     )

#     with pytest.raises(Exception) as e:
#         duplicated_item_request = test_client.post(
#             "/atbds", json=atbd_creation_input, headers=authenticated_headers
#         )
#         duplicated_item_request.raise_for_status()
#     assert str(e.value).startswith("400")


# def test_create_atbd_fails_if_missing_title(test_client, atbd_creation_input):
#     del atbd_creation_input["title"]
#     with pytest.raises(Exception) as e:
#         unauthenticated_request = test_client.post("/atbds", json=atbd_creation_input)
#         unauthenticated_request.raise_for_status()

#     assert str(e.value).startswith("401")


# def test_update_atbd_by_id(
#     test_client,
#     db_session,
#     atbd_creation_input,
#     authenticated_headers,
#     mocked_event_listener,
# ):

#     created = json.loads(
#         test_client.post(
#             "/atbds", json=atbd_creation_input, headers=authenticated_headers
#         ).content
#     )
#     updated = json.loads(
#         test_client.post(
#             f"/atbds/{created['id']}",
#             json={"title": "New and improved!"},
#             headers=authenticated_headers,
#         ).content
#     )

#     [dbobj] = db_session.execute(
#         f"SELECT * FROM atbds WHERE atbds.id = '{updated['id']}'"
#     )
#     assert created["title"] != dbobj.title
#     assert dbobj.title == "New and improved!"
#     assert created["alias"] == dbobj.alias


# def test_update_atbd_by_alias(
#     test_client,
#     db_session,
#     atbd_creation_input,
#     authenticated_headers,
#     mocked_event_listener,
# ):

#     created = json.loads(
#         test_client.post(
#             "/atbds", json=atbd_creation_input, headers=authenticated_headers
#         ).content
#     )
#     updated = json.loads(
#         test_client.post(
#             f"/atbds/{created['alias']}",
#             json={"title": "New and improved!"},
#             headers=authenticated_headers,
#         ).content
#     )

#     [dbobj] = db_session.execute(
#         f"SELECT * FROM atbds WHERE atbds.id = '{updated['id']}'"
#     )
#     assert created["title"] != dbobj.title
#     assert dbobj.title == "New and improved!"
#     assert created["alias"] == dbobj.alias


# def test_update_atbd_fails_if_updated_alias_already_exists_in_database(
#     test_client,
#     db_session,
#     atbd_creation_input,
#     authenticated_headers,
#     mocked_event_listener,
# ):
#     atbd1 = json.loads(
#         test_client.post(
#             "/atbds", json=atbd_creation_input, headers=authenticated_headers
#         ).content
#     )

#     # Create another ATBD whose alias will conflict with the
#     # alias we try to set for atbd1
#     atbd_creation_input["alias"] = "atbd-alias-2"
#     test_client.post("/atbds", json=atbd_creation_input, headers=authenticated_headers)

#     with pytest.raises(Exception) as e:
#         # update atbd1 with an alias that already belongs to atbd2
#         req = test_client.post(
#             f"/atbds/{atbd1['id']}",
#             json={"alias": "atbd-alias-2"},
#             headers=authenticated_headers,
#         )
#         req.raise_for_status()

#     assert str(e.value).startswith("401")


# def test_update_atbd_fails_if_user_is_not_authenticated(
#     test_client,
#     db_session,
#     atbd_creation_input,
#     authenticated_headers,
#     mocked_event_listener,
# ):
#     atbd = json.loads(
#         test_client.post(
#             "/atbds", json=atbd_creation_input, headers=authenticated_headers
#         ).content
#     )
#     with pytest.raises(Exception) as e:
#         req = test_client.post(f"/atbds/{atbd['id']}", json={"alias": "atbd-alias-2"},)
#         req.raise_for_status()

#     assert str(e.value).startswith("401")


# def test_index_atbd_is_called():
#     pass
