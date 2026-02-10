from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlencode

import requests

from app.config import AppConfig


@dataclass
class EmailResult:
    ok: bool
    message: str


class EmailService:
    def __init__(self) -> None:
        self.config = AppConfig.from_env()
        self.base_app_url = self.config.app_base_url.rstrip("/")

    def _build_app_link(self, params: dict[str, str]) -> str:
        query = urlencode(params)
        return f"{self.base_app_url}/?{query}"

    def _send(self, to_email: str, subject: str, body_text: str, body_html: str | None = None) -> EmailResult:
        if self.config.email_provider != "sendgrid":
            return EmailResult(ok=False, message=f"Unsupported email provider: {self.config.email_provider}")

        base_url = "https://api.eu.sendgrid.com" if self.config.sendgrid_region == "eu" else "https://api.sendgrid.com"
        content = [{"type": "text/plain", "value": body_text}]
        if body_html:
            content.append({"type": "text/html", "value": body_html})
        payload = {
            "personalizations": [{"to": [{"email": to_email}]}],
            "from": {"email": self.config.sendgrid_from_email},
            "subject": subject,
            "content": content,
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
        start_url = self.base_app_url
        body = (
            f"Hi {first_name},\n\n"
            "Your account is live.\n"
            f"Generate your Origin Chart here: {start_url}\n\n"
            "We just launched. You're early. But your chart is still accurate."
        )
        body_html = (
            f"<p>Hi {first_name},</p>"
            "<p>Your account is live.</p>"
            f'<p><a href="{start_url}">Open App</a></p>'
            "<p>We just launched. You're early. But your chart is still accurate.</p>"
        )
        return self._send(to_email, subject, body, body_html)

    def send_password_reset_email(self, *, to_email: str, first_name: str, token: str) -> EmailResult:
        # Keep reset links compact for better deliverability/readability in clients.
        reset_link = self._build_app_link({"rt": token})
        subject = f"Reset your password, {first_name}"
        body = (
            f"Hi {first_name},\n"
            "Tap this link to reset your password (valid for 1 hour):\n"
            f"{reset_link}\n\n"
            "If you didn't request this, ignore this email."
        )
        body_html = (
            f"<p>Hi {first_name},</p>"
            '<p><a href="{0}"><strong>Reset Password</strong></a> (valid for 1 hour)</p>'
            "<p>If you didn't request this, ignore this email.</p>"
        ).format(reset_link)
        return self._send(to_email, subject, body, body_html)

    def send_email_verification_email(self, *, to_email: str, first_name: str, token: str) -> EmailResult:
        verify_link = self._build_app_link({"vt": token})
        subject = f"Verify your email, {first_name}"
        body = (
            f"Hi {first_name},\n"
            "Tap this link to verify your email (valid for 24 hours):\n"
            f"{verify_link}"
        )
        body_html = (
            f"<p>Hi {first_name},</p>"
            '<p><a href="{0}"><strong>Verify Email</strong></a> (valid for 24 hours)</p>'
        ).format(verify_link)
        return self._send(to_email, subject, body, body_html)
