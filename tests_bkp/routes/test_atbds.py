import json

import pytest
from sqlalchemy.exc import InvalidRequestError

from app.db.models import Atbds


def test_list_atbds_unauthenticated(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    assert json.loads(test_client.get("/v2/atbds").content) == []

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft")

    result = json.loads(test_client.get("/v2/atbds").content)
    assert result == []

    for atbd in atbds:

        atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft", major=2, minor=0)

    result = json.loads(test_client.get("/v2/atbds").content)

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
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    assert (
        json.loads(test_client.get("/v2/atbds", headers=authenticated_headers).content)
        == []
    )
    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:

        atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft", major=2, minor=0)

    result = json.loads(
        test_client.get("/v2/atbds", headers=authenticated_headers).content
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
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    with pytest.raises(Exception):
        result = test_client.get("/v2/atbds/1")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:

        atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft", major=2, minor=0)

    atbd = atbds[0]

    result = test_client.get(f"/v2/atbds/{atbd.id}")
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
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    with pytest.raises(Exception):
        result = test_client.get("/v2/atbds/1")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:
        atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft", major=2, minor=0)

    atbd = atbds[0]

    result = test_client.get(f"/v2/atbds/{atbd.id}", headers=authenticated_headers)
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
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    with pytest.raises(Exception):
        result = test_client.get("/v2/atbds/non-existent-alias")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]

    for atbd in atbds:
        atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft", major=2, minor=0)

    atbd = atbds[0]

    result = test_client.get(f"/v2/atbds/{atbd.alias}")
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
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    with pytest.raises(Exception):
        result = test_client.get("/v2/atbds/non-existent-alias")
        result.raise_for_status()

    atbds = [atbds_factory.create(), atbds_factory.create()]
    for atbd in atbds:

        atbd_versions_factory.create(
            atbd_id=atbd.id, status="Published", major=1, minor=0
        )
        atbd_versions_factory.create(atbd_id=atbd.id, status="Draft", major=2, minor=0)

    atbd = atbds[0]

    result = test_client.get(f"/v2/atbds/{atbd.alias}", headers=authenticated_headers)
    result.raise_for_status()
    result = json.loads(result.content)
    assert result["title"] == atbd.title
    assert result["alias"] == atbd.alias
    assert len(result["versions"]) == 2
    assert set(v["status"] for v in result["versions"]) == {"Draft", "Published"}
    assert set(v["version"] for v in result["versions"]) == {"v1.0", "v2.0"}


def test_create_atbd_without_alias(
    test_client, db_session, authenticated_headers, mocked_validate_cognito_token
):

    with pytest.raises(Exception):
        result = test_client.post(
            "/v2/atbds", data=json.dumps({"title": "New Test ATBD"})
        )
        result.raise_for_status()

    result = test_client.post(
        "/v2/atbds",
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


def test_create_atbd_with_alias(
    test_client, db_session, authenticated_headers, mocked_validate_cognito_token
):
    with pytest.raises(Exception):
        result = test_client.post(
            "/v2/atbds",
            data=json.dumps(
                {"title": "New Test ATBD", "alias": "Non Conforming Alias"}
            ),
            headers=authenticated_headers,
        )
        result.raise_for_status()

    result = test_client.post(
        "/v2/atbds",
        data=json.dumps({"title": "New Test ATBD", "alias": "new-test-atbd-alias"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    with pytest.raises(Exception):
        # Test that duplicate alias fails
        failed_result = test_client.post(
            "/v2/atbds",
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
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):

    with pytest.raises(Exception):
        result = test_client.post(
            "/v2/atbds/1", data=json.dumps({"title": "New Test ATBD"})
        )
        result.raise_for_status()

    atbd = atbds_factory.create()
    atbd_versions_factory.create(atbd_id=atbd.id)

    assert atbd.title == atbd.title

    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.id}",
            data=json.dumps(
                {"title": "New Test ATBD", "alias": "Non conforming alias"}
            ),
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        atbd2 = atbds_factory.create()

        atbd_versions_factory.create(atbd_id=atbd.id)

        # ensure that updating alias to an already existing alias
        # fails
        result = test_client.post(
            f"/v2/atbds/{atbd.id}",
            data=json.dumps({"title": "New Test ATBD", "alias": atbd2.alias}),
        )
        result.raise_for_status()

    result = test_client.post(
        f"/v2/atbds/{atbd.id}",
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


def test_update_atbd_by_alias(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):

    with pytest.raises(Exception):
        result = test_client.post(
            "/v2/atbds/non-existent-alias", data=json.dumps({"title": "New Test ATBD"})
        )
        result.raise_for_status()

    atbd = atbds_factory.create()
    atbd_versions_factory.create(atbd_id=atbd.id)

    with pytest.raises(Exception):
        result = test_client.post(
            f"/v2/atbds/{atbd.alias}",
            data=json.dumps(
                {"title": "New Test ATBD", "alias": "Non conforming alias"}
            ),
        )
        result.raise_for_status()

    with pytest.raises(Exception):
        atbd2 = atbds_factory.create()

        atbd_versions_factory.create(atbd_id=atbd.id)

        # ensure that updating alias to an already existing alias
        # fails
        result = test_client.post(
            f"/v2/atbds/{atbd.alias}",
            data=json.dumps({"title": "New Test ATBD", "alias": atbd2.alias}),
        )
        result.raise_for_status()

    result = test_client.post(
        f"/v2/atbds/{atbd.alias}",
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

    result = test_client.get("/v2/atbds/new-alias", headers=authenticated_headers)
    result.raise_for_status()


def test_delete_atbd_by_id(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    with pytest.raises(Exception):
        result = test_client.delete("/v2/atbds/1", headers=authenticated_headers)
        result.raise_for_status()

    atbd = atbds_factory.create(alias=None)

    atbd_versions_factory.create(atbd_id=atbd.id)

    with pytest.raises(Exception):
        result = test_client.delete(f"/v2/atbds/{atbd.id}")
        result.raise_for_status()

    result = test_client.delete(f"/v2/atbds/{atbd.id}", headers=authenticated_headers)
    result.raise_for_status()
    with pytest.raises(InvalidRequestError):
        db_session.refresh(atbd)
        assert atbd is None


def test_delete_atbd_by_alias(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):
    with pytest.raises(Exception):
        result = test_client.delete(
            "/v2/atbds/non-existent-alias", headers=authenticated_headers
        )
        result.raise_for_status()

    atbd = atbds_factory.create()
    atbd_versions_factory.create(atbd_id=atbd.id)

    with pytest.raises(Exception):
        result = test_client.delete(f"/v2/atbds/{atbd.alias}")
        result.raise_for_status()

    result = test_client.delete(
        f"/v2/atbds/{atbd.alias}", headers=authenticated_headers
    )
    result.raise_for_status()
    with pytest.raises(InvalidRequestError):
        db_session.refresh(atbd)
        assert atbd is None


def test_atbd_existence_check_by_id(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):

    with pytest.raises(Exception):
        result = test_client.head("/v2/atbds/1", headers=authenticated_headers)
        result.raise_for_status()

    atbd = atbds_factory.create()

    # create a version to go along with the atbd
    # otherwise the atbd will fail to retrieve since
    # it mandatorily joins versions on ATBDSs
    atbd_versions_factory.create(atbd_id=atbd.id)

    with pytest.raises(Exception):
        result = test_client.delete(f"/v2/atbds/{atbd.id}")
        result.raise_for_status()

    result = test_client.delete(f"/v2/atbds/{atbd.id}", headers=authenticated_headers)
    result.raise_for_status()


def test_atbd_existence_check_by_alias(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):

    with pytest.raises(Exception):
        result = test_client.head(
            "/v2/atbds/non-existent-alias", headers=authenticated_headers
        )
        result.raise_for_status()

    atbd = atbds_factory.create()

    # create a version to go along with the atbd
    # otherwise the atbd will fail to retrieve since
    # it mandatorily joins versions on ATBDSs
    atbd_versions_factory.create(atbd_id=atbd.id)

    with pytest.raises(Exception):
        result = test_client.delete(f"/v2/atbds/{atbd.alias}")
        result.raise_for_status()

    result = test_client.delete(
        f"/v2/atbds/{atbd.alias}", headers=authenticated_headers
    )
    result.raise_for_status()


def test_publish_atbd_by_id(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
    s3_bucket,
):

    with pytest.raises(Exception):
        result = test_client.post("/v2/atbds/1/publish", headers=authenticated_headers)
        result.raise_for_status()

    atbd = atbds_factory.create()

    with open("./tests/fullmoon.jpg", "rb") as f:
        s3_bucket.put_object(Key=f"{atbd.id}/images/fullmoon.jpg", Body=f.read())

    # create a version to go along with the atbd
    # otherwise the atbd will fail to retrieve since
    # it mandatorily joins versions on ATBDSs
    version = atbd_versions_factory.create(atbd_id=atbd.id, status="Published")

    with pytest.raises(Exception):
        result = test_client.post(f"/v2/atbds/{atbd.id}/publish")
        result.raise_for_status()

    with pytest.raises(Exception):

        result = test_client.post(
            f"/v2/atbds/{atbd.id}/publish", headers=authenticated_headers
        )
        result.raise_for_status()

    version.status = "Draft"
    db_session.add(version)
    db_session.commit()

    with pytest.raises(Exception):

        result = test_client.post(
            f"/v2/atbds/{atbd.id}/publish", headers=authenticated_headers
        )
        result.raise_for_status()

    result = test_client.post(
        f"/v2/atbds/{atbd.id}/publish",
        data=json.dumps({}),
        headers=authenticated_headers,
    )
    result.raise_for_status()

    db_session.refresh(atbd)
    db_session.refresh(version)
    assert version.status == "Published"
    assert version.published_at is not None
    assert version.published_at > version.created_at
    assert version.last_updated_at > version.created_at

    assert (
        s3_bucket.Object(
            f"{atbd.id}/pdf/{atbd.alias}-v{version.major}-{version.minor}-journal.pdf"
        ).get()["ContentLength"]
        > 100
    )
    assert (
        s3_bucket.Object(
            f"{atbd.id}/pdf/{atbd.alias}-v{version.major}-{version.minor}.pdf"
        ).get()["ContentLength"]
        > 100
    )


def test_atbd_timestamps(
    test_client,
    db_session,
    atbds_factory,
    atbd_versions_factory,
    authenticated_headers,
    mocked_send_to_opensearch,
    mocked_validate_cognito_token,
):

    result = test_client.post(
        "/v2/atbds",
        data=json.dumps({"alias": "test-alias", "title": "Test ATBD"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()
    result = json.loads(result.content)

    atbd = db_session.query(Atbds).get(result["id"])

    assert atbd.created_at is not None
    assert atbd.last_updated_at is not None
    assert atbd.created_at == atbd.last_updated_at

    prev_updated_at = atbd.last_updated_at
    prev_created_at = atbd.created_at

    result = test_client.post(
        f"/v2/atbds/{result['id']}",
        data=json.dumps({"title": "NEW Test ATBD"}),
        headers=authenticated_headers,
    )
    result.raise_for_status()
    result = json.loads(result.content)

    db_session.refresh(atbd)

    assert atbd.last_updated_at is not None
    assert atbd.last_updated_at > prev_updated_at
    assert atbd.created_at == prev_created_at
