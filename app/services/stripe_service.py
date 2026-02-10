from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import requests

from app.config import AppConfig
from app.domain.models import User


@dataclass
class StripeResult:
    ok: bool
    message: str
    url: str | None = None


class StripeService:
    def __init__(self) -> None:
        self.config = AppConfig.from_env()

    def configured(self) -> bool:
        return len(self.config.missing_stripe_env()) == 0

    def user_has_active_premium(self, user: User) -> bool:
        if user.subscription_tier.lower() != "premium":
            return False
        if user.subscription_expires_at is None:
            return True
        expires = user.subscription_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        return expires >= datetime.now(UTC)

    def _post_form(self, endpoint: str, data: dict[str, Any]) -> requests.Response:
        headers = {"Authorization": f"Bearer {self.config.stripe_secret_key}"}
        return requests.post(
            f"https://api.stripe.com/v1/{endpoint}",
            headers=headers,
            data=data,
            timeout=25,
        )

    def create_checkout_session(self, user: User, plan: str = "monthly") -> StripeResult:
        if not self.configured():
            return StripeResult(ok=False, message="Stripe env vars are missing.")

        price_id = self.config.stripe_price_monthly if plan == "monthly" else self.config.stripe_price_yearly
        data: dict[str, Any] = {
            "mode": "subscription",
            "success_url": f"{self.config.app_base_url}/?checkout=success",
            "cancel_url": f"{self.config.app_base_url}/?checkout=cancel",
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "allow_promotion_codes": "true",
            "metadata[user_id]": user.id,
            "metadata[user_email]": user.email,
            "customer_email": user.email,
        }
        if user.stripe_customer_id:
            data["customer"] = user.stripe_customer_id

        try:
            response = self._post_form("checkout/sessions", data)
        except Exception as exc:  # pragma: no cover - requests/network variance
            return StripeResult(ok=False, message=str(exc))

        if response.status_code not in {200, 201}:
            return StripeResult(ok=False, message=f"Stripe HTTP {response.status_code}: {response.text[:300]}")

        payload = response.json()
        return StripeResult(ok=True, message="Checkout session created.", url=payload.get("url"))

    def create_customer_portal_session(self, user: User) -> StripeResult:
        if not self.configured():
            return StripeResult(ok=False, message="Stripe env vars are missing.")
        if not user.stripe_customer_id:
            return StripeResult(ok=False, message="No Stripe customer ID linked for this account.")

        data = {
            "customer": user.stripe_customer_id,
            "return_url": f"{self.config.app_base_url}/?portal=return",
        }
        try:
            response = self._post_form("billing_portal/sessions", data)
        except Exception as exc:  # pragma: no cover - requests/network variance
            return StripeResult(ok=False, message=str(exc))

        if response.status_code not in {200, 201}:
            return StripeResult(ok=False, message=f"Stripe HTTP {response.status_code}: {response.text[:300]}")

        payload = response.json()
        return StripeResult(ok=True, message="Customer portal session created.", url=payload.get("url"))

