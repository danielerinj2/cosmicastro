from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List

from dotenv import load_dotenv

load_dotenv()


DEFAULT_REQUIRED_TABLE_COLUMNS: Dict[str, List[str]] = {
    "users": [
        "id",
        "email",
        "hashed_password",
        "first_name",
        "dob",
        "birth_time",
        "birth_location",
        "lat",
        "lng",
        "timezone",
        "sun_sign",
        "email_verified",
        "subscription_tier",
        "stripe_customer_id",
        "subscription_expires_at",
        "theme_preference",
        "language_preference",
        "notify_daily_reading",
        "daily_reading_hour",
        "notify_transit_alerts",
        "country_code",
        "created_at",
        "updated_at",
    ],
    "readings": [
        "id",
        "user_id",
        "type",
        "mode",
        "partner_profile_id",
        "profection_age",
        "source_data",
        "content",
        "created_at",
    ],
    "tokens": [
        "id",
        "user_id",
        "token",
        "type",
        "expires_at",
        "used",
        "created_at",
    ],
    "daily_horoscopes_cache": [
        "id",
        "sign",
        "date",
        "content",
        "created_at",
    ],
    "moon_phase_cache": [
        "id",
        "phase",
        "start_date",
        "end_date",
        "content",
        "created_at",
    ],
    "partner_profiles": [
        "id",
        "user_id",
        "name",
        "dob",
        "birth_time",
        "birth_location",
        "lat",
        "lng",
        "timezone",
        "sun_sign",
        "relationship_type",
        "created_at",
        "updated_at",
    ],
    "reading_reactions": [
        "id",
        "user_id",
        "reading_id",
        "daily_horoscope_id",
        "moon_phase_id",
        "reaction",
        "journal_text",
        "created_at",
    ],
}


def _normalize_supabase_url(raw_url: str) -> str:
    raw = raw_url.strip()
    if not raw:
        return raw

    if raw.startswith("http://") or raw.startswith("https://"):
        return raw

    # Allow a Postgres DSN from Supabase and derive the project REST URL.
    # Example host pattern inside DSN: db.<project_ref>.supabase.co
    match = re.search(r"db\.([a-z0-9]+)\.supabase\.co", raw, flags=re.IGNORECASE)
    if match:
        project_ref = match.group(1)
        return f"https://{project_ref}.supabase.co"

    return raw


def _get_config_value(key: str, default: str = "") -> str:
    """
    Resolve config values in this order:
    1) OS environment variables
    2) Streamlit Cloud secrets (st.secrets)
    3) provided default
    """
    env_value = os.getenv(key)
    if env_value is not None and str(env_value).strip():
        return str(env_value).strip()

    try:
        import streamlit as st

        if key in st.secrets:
            secret_value = st.secrets[key]
            if secret_value is not None and str(secret_value).strip():
                return str(secret_value).strip()
    except Exception:
        # Streamlit may be unavailable (e.g., CLI scripts) or secrets may not exist.
        pass

    return default


@dataclass(frozen=True)
class AppConfig:
    supabase_url: str
    supabase_service_role_key: str
    required_tables: List[str]
    llm_provider: str
    groq_api_key: str
    groq_model: str
    email_provider: str
    sendgrid_api_key: str
    sendgrid_from_email: str
    sendgrid_region: str
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_price_monthly: str
    stripe_price_yearly: str
    app_base_url: str

    @staticmethod
    def from_env() -> "AppConfig":
        supabase_url = _normalize_supabase_url(_get_config_value("SUPABASE_URL", ""))
        supabase_service_role_key = _get_config_value("SUPABASE_SERVICE_ROLE_KEY", "")

        required_tables_raw = _get_config_value("SUPABASE_REQUIRED_TABLES", "")
        if required_tables_raw:
            required_tables = [item.strip() for item in required_tables_raw.split(",") if item.strip()]
        else:
            required_tables = list(DEFAULT_REQUIRED_TABLE_COLUMNS.keys())

        llm_provider = _get_config_value("LLM_PROVIDER", "groq").lower()
        groq_api_key = _get_config_value("GROQ_API_KEY", "")
        groq_model = _get_config_value("GROQ_MODEL", "llama-3.3-70b-versatile")

        email_provider = _get_config_value("EMAIL_PROVIDER", "sendgrid").lower()
        sendgrid_api_key = _get_config_value("SENDGRID_API_KEY", "")
        sendgrid_from_email = _get_config_value("SENDGRID_FROM_EMAIL", "")
        sendgrid_region = _get_config_value("SENDGRID_REGION", "global").lower()

        stripe_secret_key = _get_config_value("STRIPE_SECRET_KEY", "")
        stripe_publishable_key = _get_config_value("STRIPE_PUBLISHABLE_KEY", "")
        stripe_price_monthly = _get_config_value("STRIPE_PRICE_MONTHLY", "")
        stripe_price_yearly = _get_config_value("STRIPE_PRICE_YEARLY", "")
        app_base_url = _get_config_value("APP_BASE_URL", "http://localhost:8501")

        return AppConfig(
            supabase_url=supabase_url,
            supabase_service_role_key=supabase_service_role_key,
            required_tables=required_tables,
            llm_provider=llm_provider,
            groq_api_key=groq_api_key,
            groq_model=groq_model,
            email_provider=email_provider,
            sendgrid_api_key=sendgrid_api_key,
            sendgrid_from_email=sendgrid_from_email,
            sendgrid_region=sendgrid_region,
            stripe_secret_key=stripe_secret_key,
            stripe_publishable_key=stripe_publishable_key,
            stripe_price_monthly=stripe_price_monthly,
            stripe_price_yearly=stripe_price_yearly,
            app_base_url=app_base_url,
        )

    def missing_required_env(self) -> List[str]:
        missing: List[str] = []
        if not self.supabase_url:
            missing.append("SUPABASE_URL")
        if not self.supabase_service_role_key:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        return missing

    def missing_groq_env(self) -> List[str]:
        missing: List[str] = []
        if self.llm_provider == "groq" and not self.groq_api_key:
            missing.append("GROQ_API_KEY")
        return missing

    def missing_sendgrid_env(self) -> List[str]:
        missing: List[str] = []
        if self.email_provider == "sendgrid":
            if not self.sendgrid_api_key:
                missing.append("SENDGRID_API_KEY")
            if not self.sendgrid_from_email:
                missing.append("SENDGRID_FROM_EMAIL")
        return missing

    def missing_stripe_env(self) -> List[str]:
        missing: List[str] = []
        if not self.stripe_secret_key:
            missing.append("STRIPE_SECRET_KEY")
        if not self.stripe_price_monthly:
            missing.append("STRIPE_PRICE_MONTHLY")
        if not self.stripe_price_yearly:
            missing.append("STRIPE_PRICE_YEARLY")
        return missing
