from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig
from app.infra.sendgrid_probe import probe_sendgrid_key


def main() -> int:
    config = AppConfig.from_env()
    missing = config.missing_sendgrid_env()
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    result = probe_sendgrid_key(
        api_key=config.sendgrid_api_key,
        region=config.sendgrid_region,
    )
    print(f"[sendgrid] {'OK' if result.ok else 'FAIL'} - {result.message}")
    if not result.ok:
        return 1

    has_mail_send = "mail.send" in result.scopes
    print(f"[sendgrid] mail.send scope: {'YES' if has_mail_send else 'NO'}")
    if result.scopes:
        print("[sendgrid] scopes:")
        for scope in result.scopes:
            print(f"  - {scope}")

    if not has_mail_send:
        print("API key is valid but missing `mail.send`. Create/update key with Mail Send permission.")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

