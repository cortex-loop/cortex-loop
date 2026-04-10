"""Deterministic verified-work fixture payloads for unit tests."""

from __future__ import annotations


VALID_MODELS_PY = """from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


def _normalize_tags(raw_tags: list[str] | None) -> list[str]:
    if raw_tags is None:
        return []
    normalized: list[str] = []
    for raw_tag in raw_tags:
        tag = raw_tag.strip().lower()
        if not tag:
            continue
        if tag not in normalized:
            normalized.append(tag)
    return normalized


class BookmarkCreate(BaseModel):
    url: HttpUrl
    title: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must be non-empty")
        return stripped

    @field_validator("tags", mode="before")
    @classmethod
    def _validate_tags(cls, value: list[str] | None) -> list[str]:
        return _normalize_tags(value)

    @field_validator("notes")
    @classmethod
    def _validate_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class BookmarkUpdate(BaseModel):
    url: HttpUrl | None = None
    title: str | None = None
    tags: list[str] | None = None
    notes: str | None = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("title must be non-empty")
        return stripped

    @field_validator("tags", mode="before")
    @classmethod
    def _validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return _normalize_tags(value)

    @field_validator("notes")
    @classmethod
    def _validate_notes(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class ArchiveRequest(BaseModel):
    archived: bool


class BookmarkOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    title: str
    tags: list[str]
    notes: str | None
    archived: bool
    created_at: datetime
    updated_at: datetime


class BookmarkListResponse(BaseModel):
    items: list[BookmarkOut]
    page: int
    page_size: int
    total: int


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
"""

VALID_STORE_PY = """from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class BookmarkRecord:
    id: str
    url: str
    title: str
    tags: list[str]
    notes: str | None
    archived: bool
    created_at: datetime
    updated_at: datetime


class BookmarkStore:
    def __init__(self) -> None:
        self._items: dict[str, BookmarkRecord] = {}

    def create(
        self,
        *,
        url: str,
        title: str,
        tags: list[str],
        notes: str | None,
    ) -> BookmarkRecord:
        now = datetime.now(timezone.utc)
        record = BookmarkRecord(
            id=uuid4().hex,
            url=url,
            title=title,
            tags=list(tags),
            notes=notes,
            archived=False,
            created_at=now,
            updated_at=now,
        )
        self._items[record.id] = record
        return record

    def get(self, bookmark_id: str) -> BookmarkRecord | None:
        return self._items.get(bookmark_id)

    def list(
        self,
        *,
        tag: str | None,
        query: str | None,
        sort_by: str,
        order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[BookmarkRecord], int]:
        items = list(self._items.values())
        if tag is not None:
            items = [item for item in items if tag in item.tags]
        if query is not None:
            lowered = query.lower()
            items = [
                item
                for item in items
                if lowered in item.title.lower()
                or lowered in item.url.lower()
                or lowered in (item.notes or "").lower()
                or any(lowered in tag_value.lower() for tag_value in item.tags)
            ]
        reverse = order == "desc"
        items.sort(key=lambda item: getattr(item, sort_by), reverse=reverse)
        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return items[start:end], total

    def update(
        self,
        bookmark_id: str,
        *,
        url: str | None,
        title: str | None,
        tags: list[str] | None,
        notes: str | None,
    ) -> BookmarkRecord | None:
        item = self._items.get(bookmark_id)
        if item is None:
            return None
        if url is not None:
            item.url = url
        if title is not None:
            item.title = title
        if tags is not None:
            item.tags = list(tags)
        if notes is not None or notes is None:
            item.notes = notes
        item.updated_at = datetime.now(timezone.utc)
        return item

    def set_archived(self, bookmark_id: str, archived: bool) -> BookmarkRecord | None:
        item = self._items.get(bookmark_id)
        if item is None:
            return None
        item.archived = archived
        item.updated_at = datetime.now(timezone.utc)
        return item

    def delete(self, bookmark_id: str) -> bool:
        return self._items.pop(bookmark_id, None) is not None
"""

VALID_MAIN_PY = """from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .models import (
    ArchiveRequest,
    BookmarkCreate,
    BookmarkListResponse,
    BookmarkOut,
    BookmarkUpdate,
)
from .store import BookmarkStore


app = FastAPI(title="Bookmarks API")
store = BookmarkStore()


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


@app.exception_handler(RequestValidationError)
async def _validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    del request
    detail = exc.errors()[0] if exc.errors() else {}
    message = str(detail.get("msg") or "Request validation failed.")
    return _error_response(422, "validation_error", message)


@app.exception_handler(HTTPException)
async def _http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    del request
    if exc.status_code == 404:
        return _error_response(404, "not_found", str(exc.detail or "Bookmark not found."))
    return _error_response(exc.status_code, "http_error", str(exc.detail or "Request failed."))


def _require_bookmark(bookmark_id: str):
    bookmark = store.get(bookmark_id)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found.")
    return bookmark


@app.post("/bookmarks", response_model=BookmarkOut, status_code=201)
def create_bookmark(payload: BookmarkCreate) -> BookmarkOut:
    bookmark = store.create(
        url=str(payload.url),
        title=payload.title,
        tags=payload.tags,
        notes=payload.notes,
    )
    return BookmarkOut.model_validate(bookmark)


@app.get("/bookmarks/{bookmark_id}", response_model=BookmarkOut)
def get_bookmark(bookmark_id: str) -> BookmarkOut:
    return BookmarkOut.model_validate(_require_bookmark(bookmark_id))


@app.get("/bookmarks", response_model=BookmarkListResponse)
def list_bookmarks(
    tag: str | None = None,
    query: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort_by: str = Query(default="created_at", pattern="^(created_at|updated_at|title|url)$"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> BookmarkListResponse:
    normalized_tag = tag.strip().lower() if isinstance(tag, str) and tag.strip() else None
    normalized_query = query.strip() if isinstance(query, str) and query.strip() else None
    items, total = store.list(
        tag=normalized_tag,
        query=normalized_query,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )
    return BookmarkListResponse(
        items=[BookmarkOut.model_validate(item) for item in items],
        page=page,
        page_size=page_size,
        total=total,
    )


@app.patch("/bookmarks/{bookmark_id}", response_model=BookmarkOut)
def update_bookmark(bookmark_id: str, payload: BookmarkUpdate) -> BookmarkOut:
    bookmark = store.update(
        bookmark_id,
        url=str(payload.url) if payload.url is not None else None,
        title=payload.title,
        tags=payload.tags,
        notes=payload.notes,
    )
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found.")
    return BookmarkOut.model_validate(bookmark)


@app.post("/bookmarks/{bookmark_id}/archive", response_model=BookmarkOut)
def archive_bookmark(bookmark_id: str, payload: ArchiveRequest) -> BookmarkOut:
    bookmark = store.set_archived(bookmark_id, payload.archived)
    if bookmark is None:
        raise HTTPException(status_code=404, detail="Bookmark not found.")
    return BookmarkOut.model_validate(bookmark)


@app.delete("/bookmarks/{bookmark_id}")
def delete_bookmark(bookmark_id: str) -> dict[str, object]:
    if not store.delete(bookmark_id):
        raise HTTPException(status_code=404, detail="Bookmark not found.")
    return {"id": bookmark_id, "deleted": True}
"""


VALID_FILE_MAP = {
    "src/bookmarks_api/main.py": VALID_MAIN_PY,
    "src/bookmarks_api/models.py": VALID_MODELS_PY,
    "src/bookmarks_api/store.py": VALID_STORE_PY,
}

VALID_NORMALIZE_PORT_PY = """from __future__ import annotations


def normalize_port(value: int | str) -> int:
    port = int(value)
    if port < 0:
        raise ValueError("port must be non-negative")
    if port > 65535:
        raise ValueError("port must be <= 65535")
    return port
"""

VALID_NORMALIZE_PORT_FILE_MAP = {
    "src/normalize_port.py": VALID_NORMALIZE_PORT_PY,
}

VALID_FEATURE_FLAG_MODELS_PY = """from __future__ import annotations

from dataclasses import dataclass


def _normalize_country_codes(values: tuple[str, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for raw_value in values:
        code = raw_value.strip().upper()
        if not code:
            raise ValueError("country codes must be non-empty")
        if code not in normalized:
            normalized.append(code)
    return tuple(normalized)


@dataclass(frozen=True, slots=True)
class FeatureFlag:
    name: str
    enabled: bool = True
    rollout_percentage: int = 100
    allow_countries: tuple[str, ...] = ()
    deny_countries: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not name:
            raise ValueError("name must be non-empty")
        if self.rollout_percentage < 0 or self.rollout_percentage > 100:
            raise ValueError("rollout_percentage must be between 0 and 100")
        object.__setattr__(self, "name", name)
        object.__setattr__(
            self,
            "allow_countries",
            _normalize_country_codes(self.allow_countries),
        )
        object.__setattr__(
            self,
            "deny_countries",
            _normalize_country_codes(self.deny_countries),
        )
"""

VALID_FEATURE_FLAG_EVALUATOR_PY = """from __future__ import annotations

from hashlib import sha256

from .models import FeatureFlag


def is_flag_active(flag: FeatureFlag, *, user_key: str, country: str) -> bool:
    normalized_country = country.strip().upper()
    if not flag.enabled:
        return False
    if normalized_country in flag.deny_countries:
        return False
    if flag.allow_countries and normalized_country not in flag.allow_countries:
        return False
    if flag.rollout_percentage == 0:
        return False
    if flag.rollout_percentage == 100:
        return True
    digest = sha256(f"{flag.name}:{user_key}".encode("utf-8")).hexdigest()[:8]
    bucket = int(digest, 16) % 100
    return bucket < flag.rollout_percentage
"""

VALID_FEATURE_FLAG_FILE_MAP = {
    "src/feature_flags/models.py": VALID_FEATURE_FLAG_MODELS_PY,
    "src/feature_flags/evaluator.py": VALID_FEATURE_FLAG_EVALUATOR_PY,
}


def render_full_files_result(file_map: dict[str, str]) -> str:
    blocks: list[str] = []
    for path, content in file_map.items():
        blocks.append(f"=== FILE: {path} ===")
        blocks.append(content)
        blocks.append("=== END FILE ===")
    return "\n".join(blocks)
