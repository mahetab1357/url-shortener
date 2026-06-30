import re
from datetime import datetime

from pydantic import BaseModel, HttpUrl, field_validator

CUSTOM_ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,30}$")


class ShortenRequest(BaseModel):
    url: HttpUrl
    custom_alias: str | None = None
    expires_at: datetime | None = None

    @field_validator("custom_alias")
    @classmethod
    def validate_alias(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not CUSTOM_ALIAS_PATTERN.match(v):
            raise ValueError(
                "custom_alias must be 3-30 characters, using only letters, digits, '_' or '-'"
            )
        return v

    @field_validator("expires_at")
    @classmethod
    def validate_expiry(cls, v: datetime | None) -> datetime | None:
        if v is None:
            return v
        # Pydantic parses naive datetimes as-is; require it be timezone-aware
        # so "in the past" comparisons aren't ambiguous across server timezones.
        if v.tzinfo is None:
            raise ValueError("expires_at must include a timezone offset")
        return v


class ShortenResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None = None


class ErrorResponse(BaseModel):
    detail: str


class HourlyBucket(BaseModel):
    hour_start: datetime
    count: int


class DailyBucket(BaseModel):
    date: str
    count: int


class DeviceBreakdownItem(BaseModel):
    device_type: str
    browser: str
    count: int


class ReferrerBreakdownItem(BaseModel):
    referrer_domain: str
    count: int


class UrlStatsResponse(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None
    total_clicks: int
    last_clicked_at: datetime | None
    hourly_clicks: list[HourlyBucket]
    daily_clicks: list[DailyBucket]
    device_breakdown: list[DeviceBreakdownItem]
    referrer_breakdown: list[ReferrerBreakdownItem]
    analytics_available: bool
