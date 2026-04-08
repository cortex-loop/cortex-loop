from __future__ import annotations

from fastapi.testclient import TestClient

from bookmarks_api.main import app


client = TestClient(app)


def _create_bookmark(
    *,
    url: str,
    title: str,
    tags: list[str] | None = None,
    notes: str | None = None,
) -> dict[str, object]:
    response = client.post(
        "/bookmarks",
        json={
            "url": url,
            "title": title,
            "tags": tags or [],
            "notes": notes,
        },
    )
    assert response.status_code == 201, response.text
    payload = response.json()
    assert isinstance(payload["id"], str)
    return payload


def _assert_error(response, *, status_code: int, code: str) -> None:
    assert response.status_code == status_code, response.text
    payload = response.json()
    assert payload["error"]["code"] == code
    assert isinstance(payload["error"]["message"], str)
    assert payload["error"]["message"]


def test_create_and_get_bookmark_by_id() -> None:
    created = _create_bookmark(
        url="https://example.com/docs",
        title="Example Docs",
        tags=["docs", "reference"],
        notes="starter note",
    )

    fetched = client.get(f"/bookmarks/{created['id']}")
    assert fetched.status_code == 200, fetched.text
    payload = fetched.json()
    assert payload["id"] == created["id"]
    assert payload["url"] == "https://example.com/docs"
    assert payload["title"] == "Example Docs"
    assert payload["tags"] == ["docs", "reference"]
    assert payload["archived"] is False


def test_list_bookmarks_returns_pagination_metadata() -> None:
    _create_bookmark(
        url="https://example.com/a",
        title="Alpha",
        tags=["list-meta"],
    )
    _create_bookmark(
        url="https://example.com/b",
        title="Beta",
        tags=["list-meta"],
    )

    response = client.get("/bookmarks?tag=list-meta&page=1&page_size=2")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 2
    assert payload["total"] >= 2
    assert len(payload["items"]) <= 2


def test_list_bookmarks_filters_by_tag() -> None:
    _create_bookmark(
        url="https://example.com/python",
        title="Python",
        tags=["python", "backend"],
    )
    _create_bookmark(
        url="https://example.com/design",
        title="Design",
        tags=["design"],
    )

    response = client.get("/bookmarks?tag=python")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["items"]
    assert all("python" in item["tags"] for item in payload["items"])


def test_list_bookmarks_searches_by_query() -> None:
    _create_bookmark(
        url="https://example.com/fastapi-guide",
        title="FastAPI Guide",
        notes="great walkthrough",
    )

    response = client.get("/bookmarks?query=fastapi")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["items"]
    assert any("FastAPI Guide" == item["title"] for item in payload["items"])


def test_list_bookmarks_supports_pagination_and_sorting() -> None:
    _create_bookmark(url="https://example.com/delta", title="Delta", tags=["sorting-case"])
    _create_bookmark(url="https://example.com/bravo", title="Bravo", tags=["sorting-case"])
    _create_bookmark(url="https://example.com/charlie", title="Charlie", tags=["sorting-case"])
    _create_bookmark(url="https://example.com/alpha", title="Alpha", tags=["sorting-case"])

    response = client.get(
        "/bookmarks?tag=sorting-case&sort_by=title&order=asc&page=2&page_size=2"
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    titles = [item["title"] for item in payload["items"]]
    assert titles == sorted(titles)
    assert payload["page"] == 2
    assert payload["page_size"] == 2


def test_update_bookmark() -> None:
    created = _create_bookmark(url="https://example.com/start", title="Starter")

    response = client.patch(
        f"/bookmarks/{created['id']}",
        json={
            "title": "Updated Starter",
            "tags": ["updated"],
            "notes": "new note",
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["title"] == "Updated Starter"
    assert payload["tags"] == ["updated"]
    assert payload["notes"] == "new note"


def test_archive_and_unarchive_bookmark() -> None:
    created = _create_bookmark(url="https://example.com/archive", title="Archive Me")

    archive_response = client.post(
        f"/bookmarks/{created['id']}/archive",
        json={"archived": True},
    )
    assert archive_response.status_code == 200, archive_response.text
    assert archive_response.json()["archived"] is True

    unarchive_response = client.post(
        f"/bookmarks/{created['id']}/archive",
        json={"archived": False},
    )
    assert unarchive_response.status_code == 200, unarchive_response.text
    assert unarchive_response.json()["archived"] is False


def test_delete_bookmark() -> None:
    created = _create_bookmark(url="https://example.com/delete", title="Delete Me")

    delete_response = client.delete(f"/bookmarks/{created['id']}")
    assert delete_response.status_code == 200, delete_response.text
    assert delete_response.json() == {"id": created["id"], "deleted": True}

    _assert_error(
        client.get(f"/bookmarks/{created['id']}"),
        status_code=404,
        code="not_found",
    )


def test_validation_rejects_invalid_url_and_blank_title() -> None:
    invalid_url = client.post(
        "/bookmarks",
        json={"url": "not-a-url", "title": "Bad URL", "tags": []},
    )
    _assert_error(invalid_url, status_code=422, code="validation_error")

    blank_title = client.post(
        "/bookmarks",
        json={"url": "https://example.com/blank", "title": "   ", "tags": []},
    )
    _assert_error(blank_title, status_code=422, code="validation_error")


def test_not_found_errors_use_consistent_payload() -> None:
    _assert_error(
        client.get("/bookmarks/does-not-exist"),
        status_code=404,
        code="not_found",
    )
    _assert_error(
        client.patch(
            "/bookmarks/does-not-exist",
            json={"title": "Nope"},
        ),
        status_code=404,
        code="not_found",
    )


def test_validation_errors_use_consistent_payload_shape() -> None:
    response = client.post(
        "/bookmarks",
        json={"url": "ftp://example.com", "title": "", "tags": ["bad"]},
    )

    assert response.status_code == 422, response.text
    payload = response.json()
    assert tuple(payload) == ("error",)
    assert payload["error"]["code"] == "validation_error"
    assert isinstance(payload["error"]["message"], str)
