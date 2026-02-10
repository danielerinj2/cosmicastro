from __future__ import annotations

import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig


def main() -> int:
    config = AppConfig.from_env()
    missing = config.missing_stripe_env()
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    headers = {"Authorization": f"Bearer {config.stripe_secret_key}"}
    try:
        response = requests.get("https://api.stripe.com/v1/prices?limit=1", headers=headers, timeout=20)
    except Exception as exc:
        print(f"[stripe] FAIL - {exc}")
        return 1

    if response.status_code != 200:
        print(f"[stripe] FAIL - HTTP {response.status_code}: {response.text[:300]}")
        return 1

    print("[stripe] OK - Stripe key is valid.")
    print(f"[stripe] configured monthly price: {config.stripe_price_monthly}")
    print(f"[stripe] configured yearly price: {config.stripe_price_yearly}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

