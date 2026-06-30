from unittest.mock import patch

import pytest

from app.services.url_service import (
    AliasTakenError,
    CollisionRetriesExhaustedError,
    create_short_url,
    get_short_url,
)


def test_create_short_url_persists_row(db_session):
    row = create_short_url(db_session, original_url="https://example.com/page")
    assert row.id is not None
    assert len(row.short_code) == 7
    assert row.original_url == "https://example.com/page"


def test_get_short_url_returns_none_when_missing(db_session):
    assert get_short_url(db_session, "doesnotexist") is None


def test_get_short_url_returns_existing_row(db_session):
    created = create_short_url(db_session, original_url="https://example.com")
    fetched = get_short_url(db_session, created.short_code)
    assert fetched is not None
    assert fetched.id == created.id


def test_custom_alias_is_used_verbatim(db_session):
    row = create_short_url(db_session, original_url="https://example.com", custom_alias="my-link")
    assert row.short_code == "my-link"


def test_custom_alias_conflict_raises(db_session):
    create_short_url(db_session, original_url="https://example.com", custom_alias="taken")
    with pytest.raises(AliasTakenError):
        create_short_url(db_session, original_url="https://other.com", custom_alias="taken")


def test_collision_on_random_code_triggers_retry(db_session):
    """Simulate a collision: force the first generated code to already exist,
    then verify a second (different) code is generated and the insert
    succeeds instead of raising."""
    existing = create_short_url(db_session, original_url="https://example.com/first")

    codes = iter([existing.short_code, "freshcd"])
    with patch("app.services.url_service.generate_short_code", side_effect=lambda length: next(codes)):
        row = create_short_url(db_session, original_url="https://example.com/second")

    assert row.short_code == "freshcd"
    assert row.short_code != existing.short_code


def test_collision_retries_exhausted_raises(db_session):
    existing = create_short_url(db_session, original_url="https://example.com/first")

    with patch(
        "app.services.url_service.generate_short_code",
        return_value=existing.short_code,
    ):
        with pytest.raises(CollisionRetriesExhaustedError):
            create_short_url(db_session, original_url="https://example.com/second")
