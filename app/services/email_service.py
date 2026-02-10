from __future__ import annotations

import os
from dataclasses import dataclass

import requests

from app.config import AppConfig


@dataclass
class EmailResult:
    ok: bool
    message: str


class EmailService:
    def __init__(self) -> None:
        self.config = AppConfig.from_env()
        self.base_app_url = os.getenv("APP_BASE_URL", "http://localhost:8501").rstrip("/")

    def _send(self, to_email: str, subject: str, body_text: str) -> EmailResult:
        if self.config.email_provider != "sendgrid":
            return EmailResult(ok=False, message=f"Unsupported email provider: {self.config.email_provider}")

        base_url = "https://api.eu.sendgrid.com" if self.config.sendgrid_region == "eu" else "https://api.sendgrid.com"
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.config.sendgrid_from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body_text}],
        }
        headers = {
            "Authorization": f"Bearer {self.config.sendgrid_api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(f"{base_url}/v3/mail/send", headers=headers, json=payload, timeout=20)
        except Exception as exc:  # pragma: no cover - network/requests variance
            return EmailResult(ok=False, message=str(exc))

        if response.status_code not in {200, 202}:
            return EmailResult(ok=False, message=f"HTTP {response.status_code}: {response.text[:300]}")

        return EmailResult(ok=True, message="Email queued.")

    def send_welcome_email(self, *, to_email: str, first_name: str) -> EmailResult:
        subject = f"Your chart is waiting, {first_name}"
        body = (
            f"Hi {first_name},\n\n"
            "Your account is live.\n"
            f"Generate your Origin Chart here: {self.base_app_url}\n\n"
            "We just launched. You're early. But your chart is still accurate."
        )
        return self._send(to_email, subject, body)

    def send_password_reset_email(self, *, to_email: str, first_name: str, token: str) -> EmailResult:
        reset_link = f"{self.base_app_url}/?reset_token={token}"
        subject = f"Reset your password, {first_name}"
        body = (
            f"Hi {first_name},\n\n"
            f"Use this link to reset your password (valid for 1 hour): {reset_link}\n\n"
            "If you did not request this, you can ignore this email."
        )
        return self._send(to_email, subject, body)

    def send_email_verification_email(self, *, to_email: str, first_name: str, token: str) -> EmailResult:
        verify_link = f"{self.base_app_url}/?verify_token={token}"
        subject = f"Verify your email, {first_name}"
        body = (
            f"Hi {first_name},\n\n"
            f"Use this link to verify your email (valid for 24 hours): {verify_link}"
        )
        return self._send(to_email, subject, body)

