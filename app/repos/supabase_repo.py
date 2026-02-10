from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any
from uuid import uuid4

from postgrest.exceptions import APIError

from app.constants import DEFAULT_DAILY_READING_HOUR
from app.domain.models import PartnerProfile, Reading, TokenRecord, User
from app.infra.supabase_client import get_supabase_client
from app.utils.time import iso_utc_now, parse_date, parse_time, utc_now


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _row_to_user(row: dict[str, Any]) -> User:
    dob = parse_date(row.get("dob"))
    if dob is None:
        raise ValueError("User row missing dob.")

    created_at = _parse_datetime(row.get("created_at"))
    updated_at = _parse_datetime(row.get("updated_at"))
    if created_at is None or updated_at is None:
        now = utc_now()
        created_at = created_at or now
        updated_at = updated_at or now

    return User(
        id=row["id"],
        email=row["email"],
        hashed_password=row["hashed_password"],
        first_name=row["first_name"],
        dob=dob,
        birth_time=parse_time(row.get("birth_time")),
        birth_location=row.get("birth_location"),
        lat=row.get("lat"),
        lng=row.get("lng"),
        timezone=row.get("timezone"),
        sun_sign=row.get("sun_sign"),
        email_verified=bool(row.get("email_verified")),
        subscription_tier=row.get("subscription_tier", "free"),
        stripe_customer_id=row.get("stripe_customer_id"),
        subscription_expires_at=_parse_datetime(row.get("subscription_expires_at")),
        theme_preference=row.get("theme_preference", "dark"),
        language_preference=row.get("language_preference", "en"),
        notify_daily_reading=bool(row.get("notify_daily_reading", True)),
        daily_reading_hour=row.get("daily_reading_hour", DEFAULT_DAILY_READING_HOUR),
        notify_transit_alerts=bool(row.get("notify_transit_alerts", False)),
        country_code=row.get("country_code"),
        created_at=created_at,
        updated_at=updated_at,
    )


def _row_to_token(row: dict[str, Any]) -> TokenRecord:
    expires_at = _parse_datetime(row.get("expires_at"))
    created_at = _parse_datetime(row.get("created_at"))
    if expires_at is None or created_at is None:
        raise ValueError("Token row missing timestamp values.")

    return TokenRecord(
        id=row["id"],
        user_id=row["user_id"],
        token=row["token"],
        type=row["type"],
        expires_at=expires_at,
        used=bool(row["used"]),
        created_at=created_at,
    )


def _row_to_reading(row: dict[str, Any]) -> Reading:
    created_at = _parse_datetime(row.get("created_at"))
    if created_at is None:
        created_at = utc_now()
    return Reading(
        id=row["id"],
        user_id=row["user_id"],
        type=row["type"],
        mode=row["mode"],
        partner_profile_id=row.get("partner_profile_id"),
        profection_age=row.get("profection_age"),
        source_data=row.get("source_data") or {},
        content=row.get("content") or {},
        created_at=created_at,
    )


def _row_to_partner(row: dict[str, Any]) -> PartnerProfile:
    created_at = _parse_datetime(row.get("created_at"))
    updated_at = _parse_datetime(row.get("updated_at"))
    now = utc_now()
    return PartnerProfile(
        id=row["id"],
        user_id=row["user_id"],
        name=row["name"],
        dob=parse_date(row.get("dob")),
        birth_time=parse_time(row.get("birth_time")),
        birth_location=row.get("birth_location"),
        lat=row.get("lat"),
        lng=row.get("lng"),
        timezone=row.get("timezone"),
        sun_sign=row.get("sun_sign"),
        relationship_type=row.get("relationship_type"),
        created_at=created_at or now,
        updated_at=updated_at or now,
    )


class SupabaseRepository:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    # Users
    def get_user_by_email(self, email: str) -> User | None:
        response = (
            self.client.table("users")
            .select("*")
            .eq("email", email.lower().strip())
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _row_to_user(response.data[0])

    def get_user_by_id(self, user_id: str) -> User | None:
        response = self.client.table("users").select("*").eq("id", user_id).limit(1).execute()
        if not response.data:
            return None
        return _row_to_user(response.data[0])

    def create_user(
        self,
        *,
        email: str,
        hashed_password: str,
        first_name: str,
        dob: date,
        birth_time: str | None,
        birth_location: str | None,
        lat: float | None,
        lng: float | None,
        timezone: str | None,
        sun_sign: str | None,
    ) -> User:
        now = iso_utc_now()
        payload = {
            "id": str(uuid4()),
            "email": email.lower().strip(),
            "hashed_password": hashed_password,
            "first_name": first_name.strip(),
            "dob": dob.isoformat(),
            "birth_time": birth_time,
            "birth_location": birth_location,
            "lat": lat,
            "lng": lng,
            "timezone": timezone,
            "sun_sign": sun_sign,
            "email_verified": False,
            "subscription_tier": "free",
            "theme_preference": "dark",
            "language_preference": "en",
            "notify_daily_reading": True,
            "daily_reading_hour": DEFAULT_DAILY_READING_HOUR,
            "notify_transit_alerts": False,
            "country_code": "US",
            "created_at": now,
            "updated_at": now,
        }
        response = self.client.table("users").insert(payload).execute()
        return _row_to_user(response.data[0])

    def update_user(self, user_id: str, updates: dict[str, Any]) -> User:
        updates = {**updates, "updated_at": iso_utc_now()}
        response = (
            self.client.table("users")
            .update(updates)
            .eq("id", user_id)
            .select("*")
            .limit(1)
            .execute()
        )
        return _row_to_user(response.data[0])

    def delete_user_full(self, user_id: str) -> None:
        # Explicit child cleanup for schemas without ON DELETE CASCADE.
        self.client.table("reading_reactions").delete().eq("user_id", user_id).execute()
        self.client.table("tokens").delete().eq("user_id", user_id).execute()

        partner_ids = (
            self.client.table("partner_profiles").select("id").eq("user_id", user_id).execute().data or []
        )
        for row in partner_ids:
            self.client.table("readings").delete().eq("partner_profile_id", row["id"]).execute()

        self.client.table("readings").delete().eq("user_id", user_id).execute()
        self.client.table("partner_profiles").delete().eq("user_id", user_id).execute()
        self.client.table("users").delete().eq("id", user_id).execute()

    # Tokens
    def create_token(self, user_id: str, token_value: str, token_type: str, expires_hours: int) -> TokenRecord:
        now = utc_now()
        expires_at = (now + timedelta(hours=expires_hours)).isoformat()
        payload = {
            "id": str(uuid4()),
            "user_id": user_id,
            "token": token_value,
            "type": token_type,
            "expires_at": expires_at,
            "used": False,
            "created_at": now.isoformat(),
        }
        try:
            response = self.client.table("tokens").insert(payload).execute()
        except APIError as exc:
            message = str(getattr(exc, "message", "")) or str(exc)
            if getattr(exc, "code", "") != "23505" or "uniq_tokens_user_type_active" not in message:
                raise

            # Schema enforces one active token per (user_id, type). Rotate existing active token.
            self.client.table("tokens").update(
                {
                    "token": token_value,
                    "expires_at": expires_at,
                    "used": False,
                    "created_at": now.isoformat(),
                }
            ).eq("user_id", user_id).eq("type", token_type).eq("used", False).execute()
            response = (
                self.client.table("tokens")
                .select("*")
                .eq("user_id", user_id)
                .eq("type", token_type)
                .eq("used", False)
                .limit(1)
                .execute()
            )
        return _row_to_token(response.data[0])

    def get_token(self, token_value: str, token_type: str) -> TokenRecord | None:
        response = (
            self.client.table("tokens")
            .select("*")
            .eq("token", token_value)
            .eq("type", token_type)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _row_to_token(response.data[0])

    def mark_token_used(self, token_id: str) -> None:
        self.client.table("tokens").update({"used": True}).eq("id", token_id).execute()

    # Readings
    def get_latest_reading(
        self,
        *,
        user_id: str,
        reading_type: str,
        mode: str | None = None,
        partner_profile_id: str | None = None,
        profection_age: int | None = None,
    ) -> Reading | None:
        query = self.client.table("readings").select("*").eq("user_id", user_id).eq("type", reading_type)
        if mode is not None:
            query = query.eq("mode", mode)
        if partner_profile_id is not None:
            query = query.eq("partner_profile_id", partner_profile_id)
        if profection_age is not None:
            query = query.eq("profection_age", profection_age)

        response = query.order("created_at", desc=True).limit(1).execute()
        if not response.data:
            return None
        return _row_to_reading(response.data[0])

    def create_reading(
        self,
        *,
        user_id: str,
        reading_type: str,
        mode: str,
        source_data: dict[str, Any],
        content: dict[str, Any],
        partner_profile_id: str | None = None,
        profection_age: int | None = None,
    ) -> Reading:
        payload = {
            "id": str(uuid4()),
            "user_id": user_id,
            "type": reading_type,
            "mode": mode,
            "partner_profile_id": partner_profile_id,
            "profection_age": profection_age,
            "source_data": source_data,
            "content": content,
            "created_at": iso_utc_now(),
        }
        response = self.client.table("readings").insert(payload).execute()
        return _row_to_reading(response.data[0])

    def list_readings(self, user_id: str, limit: int = 100) -> list[Reading]:
        response = (
            self.client.table("readings")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [_row_to_reading(row) for row in (response.data or [])]

    # Daily cache
    def get_daily_horoscope(self, sign: str, day: date) -> dict[str, Any] | None:
        response = (
            self.client.table("daily_horoscopes_cache")
            .select("*")
            .eq("sign", sign)
            .eq("date", day.isoformat())
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return response.data[0]

    def upsert_daily_horoscope(self, sign: str, day: date, content: dict[str, Any]) -> dict[str, Any]:
        existing = self.get_daily_horoscope(sign, day)
        if existing:
            response = (
                self.client.table("daily_horoscopes_cache")
                .update({"content": content, "created_at": iso_utc_now()})
                .eq("id", existing["id"])
                .select("*")
                .limit(1)
                .execute()
            )
            return response.data[0]

        payload = {
            "id": str(uuid4()),
            "sign": sign,
            "date": day.isoformat(),
            "content": content,
            "created_at": iso_utc_now(),
        }
        response = self.client.table("daily_horoscopes_cache").insert(payload).execute()
        return response.data[0]

    # Moon cache
    def get_moon_phase_for_day(self, day: date) -> dict[str, Any] | None:
        response = (
            self.client.table("moon_phase_cache")
            .select("*")
            .lte("start_date", day.isoformat())
            .gte("end_date", day.isoformat())
            .order("start_date", desc=True)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return response.data[0]

    def upsert_moon_phase(
        self,
        *,
        phase: str,
        start_date: date,
        end_date: date,
        content: dict[str, Any],
    ) -> dict[str, Any]:
        existing = (
            self.client.table("moon_phase_cache")
            .select("*")
            .eq("phase", phase)
            .eq("start_date", start_date.isoformat())
            .eq("end_date", end_date.isoformat())
            .limit(1)
            .execute()
        )
        if existing.data:
            response = (
                self.client.table("moon_phase_cache")
                .update({"content": content, "created_at": iso_utc_now()})
                .eq("id", existing.data[0]["id"])
                .select("*")
                .limit(1)
                .execute()
            )
            return response.data[0]

        payload = {
            "id": str(uuid4()),
            "phase": phase,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "content": content,
            "created_at": iso_utc_now(),
        }
        response = self.client.table("moon_phase_cache").insert(payload).execute()
        return response.data[0]

    # Partner profiles
    def list_partner_profiles(self, user_id: str) -> list[PartnerProfile]:
        response = (
            self.client.table("partner_profiles")
            .select("*")
            .eq("user_id", user_id)
            .order("updated_at", desc=True)
            .execute()
        )
        return [_row_to_partner(item) for item in response.data or []]

    def get_partner_profile(self, partner_profile_id: str) -> PartnerProfile | None:
        response = (
            self.client.table("partner_profiles")
            .select("*")
            .eq("id", partner_profile_id)
            .limit(1)
            .execute()
        )
        if not response.data:
            return None
        return _row_to_partner(response.data[0])

    def create_partner_profile(
        self,
        *,
        user_id: str,
        name: str,
        dob: date | None,
        birth_time: str | None,
        birth_location: str | None,
        lat: float | None,
        lng: float | None,
        timezone: str | None,
        sun_sign: str | None,
        relationship_type: str | None,
    ) -> PartnerProfile:
        now = iso_utc_now()
        payload = {
            "id": str(uuid4()),
            "user_id": user_id,
            "name": name,
            "dob": dob.isoformat() if dob else None,
            "birth_time": birth_time,
            "birth_location": birth_location,
            "lat": lat,
            "lng": lng,
            "timezone": timezone,
            "sun_sign": sun_sign,
            "relationship_type": relationship_type,
            "created_at": now,
            "updated_at": now,
        }
        response = self.client.table("partner_profiles").insert(payload).execute()
        return _row_to_partner(response.data[0])

    # Reactions
    def add_reaction(
        self,
        *,
        user_id: str,
        reaction: str,
        journal_text: str | None = None,
        reading_id: str | None = None,
        daily_horoscope_id: str | None = None,
        moon_phase_id: str | None = None,
    ) -> dict[str, Any]:
        payload = {
            "id": str(uuid4()),
            "user_id": user_id,
            "reading_id": reading_id,
            "daily_horoscope_id": daily_horoscope_id,
            "moon_phase_id": moon_phase_id,
            "reaction": reaction,
            "journal_text": journal_text,
            "created_at": iso_utc_now(),
        }
        response = self.client.table("reading_reactions").insert(payload).execute()
        return response.data[0]

    def list_reactions(self, user_id: str, limit: int = 200) -> list[dict[str, Any]]:
        response = (
            self.client.table("reading_reactions")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
