from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig, DEFAULT_REQUIRED_TABLE_COLUMNS
from app.infra.supabase_client import get_supabase_client
from app.infra.supabase_probe import probe_connection, probe_required_columns, probe_tables


def main() -> int:
    config = AppConfig.from_env()
    missing = config.missing_required_env()
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    try:
        client = get_supabase_client()
    except Exception as exc:
        print(f"Failed to initialize Supabase client: {exc}")
        return 1

    connection_result = probe_connection(client)
    print(f"[connection] {'OK' if connection_result.ok else 'FAIL'} - {connection_result.message}")
    if not connection_result.ok:
        return 1

    any_failures = False
    for result in probe_tables(client, config.required_tables):
        print(f"[table:{result.target}] {'OK' if result.ok else 'FAIL'} - {result.message}")
        any_failures = any_failures or (not result.ok)

    filtered_column_checks = {
        table_name: columns
        for table_name, columns in DEFAULT_REQUIRED_TABLE_COLUMNS.items()
        if table_name in config.required_tables
    }
    for result in probe_required_columns(client, filtered_column_checks):
        print(f"[columns:{result.target}] {'OK' if result.ok else 'FAIL'} - {result.message}")
        any_failures = any_failures or (not result.ok)

    return 1 if any_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
