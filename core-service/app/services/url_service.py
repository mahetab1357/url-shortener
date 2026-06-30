from datetime import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.models.url import ShortUrl
from app.services.shortcode import generate_short_code


class AliasTakenError(Exception):
    """Raised when a requested custom alias is already in use."""


class CollisionRetriesExhaustedError(Exception):
    """Raised if we can't find a free random short code after max attempts.
    With 62^7 ≈ 3.5 trillion combinations this should never realistically
    happen; it exists as a safety net rather than a code path we expect
    to hit in production."""


def create_short_url(
    db: Session,
    original_url: str,
    custom_alias: str | None = None,
    expires_at: datetime | None = None,
) -> ShortUrl:
    if custom_alias:
        return _insert_with_code(db, custom_alias, original_url, expires_at, is_custom=True)

    last_error: IntegrityError | None = None
    for _ in range(settings.short_code_max_attempts):
        code = generate_short_code(settings.short_code_length)
        try:
            return _insert_with_code(db, code, original_url, expires_at, is_custom=False)
        except IntegrityError as exc:
            db.rollback()
            last_error = exc
            continue

    raise CollisionRetriesExhaustedError(
        f"Could not generate a unique short code after "
        f"{settings.short_code_max_attempts} attempts"
    ) from last_error


def _insert_with_code(
    db: Session,
    code: str,
    original_url: str,
    expires_at: datetime | None,
    is_custom: bool,
) -> ShortUrl:
    row = ShortUrl(short_code=code, original_url=original_url, expires_at=expires_at)
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if is_custom:
            raise AliasTakenError(f"Alias '{code}' is already taken") from exc
        raise
    db.refresh(row)
    return row


def get_short_url(db: Session, short_code: str) -> ShortUrl | None:
    return db.query(ShortUrl).filter(ShortUrl.short_code == short_code).first()
