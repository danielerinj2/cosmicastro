from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from app.config import AppConfig


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    config = AppConfig.from_env()
    missing = config.missing_required_env()
    if missing:
        raise ValueError(f"Missing required env vars: {', '.join(missing)}")

    return create_client(config.supabase_url, config.supabase_service_role_key)

