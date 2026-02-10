from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from supabase import Client

from app.config import DEFAULT_REQUIRED_TABLE_COLUMNS


@dataclass(frozen=True)
class ProbeResult:
    target: str
    ok: bool
    message: str


def probe_connection(client: Client) -> ProbeResult:
    try:
        # A tiny metadata query that validates auth and DB connectivity.
        client.table("users").select("id").limit(1).execute()
        return ProbeResult(target="connection", ok=True, message="Connected and queryable.")
    except Exception as exc:  # pragma: no cover - upstream SDK exceptions vary
        return ProbeResult(target="connection", ok=False, message=str(exc))


def probe_tables(client: Client, table_names: Iterable[str]) -> List[ProbeResult]:
    results: List[ProbeResult] = []
    for table_name in table_names:
        try:
            client.table(table_name).select("id").limit(1).execute()
            results.append(ProbeResult(target=table_name, ok=True, message="Table is reachable."))
        except Exception as exc:  # pragma: no cover - upstream SDK exceptions vary
            results.append(ProbeResult(target=table_name, ok=False, message=str(exc)))
    return results


def probe_required_columns(client: Client, required_columns: Dict[str, List[str]] | None = None) -> List[ProbeResult]:
    checks = required_columns if required_columns is not None else DEFAULT_REQUIRED_TABLE_COLUMNS
    results: List[ProbeResult] = []

    for table_name, columns in checks.items():
        select_fields = ",".join(columns)
        try:
            client.table(table_name).select(select_fields).limit(1).execute()
            results.append(
                ProbeResult(
                    target=f"{table_name} columns",
                    ok=True,
                    message=f"Validated columns: {', '.join(columns)}",
                )
            )
        except Exception as exc:  # pragma: no cover - upstream SDK exceptions vary
            results.append(ProbeResult(target=f"{table_name} columns", ok=False, message=str(exc)))

    return results

