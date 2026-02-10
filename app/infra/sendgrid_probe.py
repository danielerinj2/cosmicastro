from __future__ import annotations

from dataclasses import dataclass
from typing import List

import requests


@dataclass(frozen=True)
class SendGridProbeResult:
    ok: bool
    message: str
    scopes: List[str]


def _base_url(region: str) -> str:
    if region.strip().lower() == "eu":
        return "https://api.eu.sendgrid.com"
    return "https://api.sendgrid.com"


def probe_sendgrid_key(api_key: str, region: str = "global") -> SendGridProbeResult:
    if not api_key.strip():
        return SendGridProbeResult(ok=False, message="SENDGRID_API_KEY is empty.", scopes=[])

    url = f"{_base_url(region)}/v3/scopes"
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(url, headers=headers, timeout=20)
    except Exception as exc:  # pragma: no cover - network/requests variance
        return SendGridProbeResult(ok=False, message=str(exc), scopes=[])

    if response.status_code != 200:
        return SendGridProbeResult(
            ok=False,
            message=f"HTTP {response.status_code}: {response.text[:300]}",
            scopes=[],
        )

    payload = response.json()
    scopes = sorted(payload.get("scopes", []))
    return SendGridProbeResult(ok=True, message="SendGrid API key is valid.", scopes=scopes)

