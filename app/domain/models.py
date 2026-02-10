from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Any


@dataclass
class User:
    id: str
    email: str
    hashed_password: str
    first_name: str
    dob: date
    birth_time: time | None
    birth_location: str | None
    lat: float | None
    lng: float | None
    timezone: str | None
    sun_sign: str | None
    email_verified: bool
    subscription_tier: str
    stripe_customer_id: str | None
    subscription_expires_at: datetime | None
    theme_preference: str
    language_preference: str
    notify_daily_reading: bool
    daily_reading_hour: int | None
    notify_transit_alerts: bool
    country_code: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class TokenRecord:
    id: str
    user_id: str
    token: str
    type: str
    expires_at: datetime
    used: bool
    created_at: datetime


@dataclass
class Reading:
    id: str
    user_id: str
    type: str
    mode: str
    partner_profile_id: str | None
    profection_age: int | None
    source_data: dict[str, Any]
    content: dict[str, Any]
    created_at: datetime


@dataclass
class PartnerProfile:
    id: str
    user_id: str
    name: str
    dob: date | None
    birth_time: time | None
    birth_location: str | None
    lat: float | None
    lng: float | None
    timezone: str | None
    sun_sign: str | None
    relationship_type: str | None
    created_at: datetime
    updated_at: datetime

