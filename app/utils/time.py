from __future__ import annotations

from datetime import UTC, date, datetime, time


def utc_now() -> datetime:
    return datetime.now(UTC)


def iso_utc_now() -> str:
    return utc_now().isoformat()


def parse_date(value: str | date | None) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def parse_time(value: str | time | None) -> time | None:
    if value is None:
        return None
    if isinstance(value, time):
        return value
    return time.fromisoformat(str(value))


def to_iso_date(value: date | None) -> str | None:
    return value.isoformat() if value else None


def to_iso_time(value: time | None) -> str | None:
    return value.isoformat() if value else None


def calculate_age_on(reference: date, dob: date) -> int:
    years = reference.year - dob.year
    has_had_birthday = (reference.month, reference.day) >= (dob.month, dob.day)
    if not has_had_birthday:
        years -= 1
    return max(years, 0)


def current_profection_window(reference: date, dob: date) -> tuple[date, date]:
    this_year_birthday = date(reference.year, dob.month, dob.day)
    if reference >= this_year_birthday:
        start = this_year_birthday
        end = date(reference.year + 1, dob.month, dob.day)
    else:
        start = date(reference.year - 1, dob.month, dob.day)
        end = this_year_birthday
    return start, end
