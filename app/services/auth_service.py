from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.models import User
from app.repos.supabase_repo import SupabaseRepository
from app.services.email_service import EmailService
from app.utils.astro import sun_sign_for_date
from app.utils.security import generate_token, hash_password, verify_password
from app.utils.time import parse_time, utc_now


@dataclass
class AuthResult:
    ok: bool
    message: str
    user: User | None = None


class AuthService:
    def __init__(self) -> None:
        self.repo = SupabaseRepository()
        self.email = EmailService()

    def sign_up(
        self,
        *,
        first_name: str,
        email: str,
        password: str,
        dob: date,
        birth_time: str | None,
        birth_location: str | None,
        lat: float | None = None,
        lng: float | None = None,
        timezone: str | None = None,
    ) -> AuthResult:
        existing = self.repo.get_user_by_email(email)
        if existing:
            return AuthResult(ok=False, message="Email already registered.")

        user = self.repo.create_user(
            email=email,
            hashed_password=hash_password(password),
            first_name=first_name,
            dob=dob,
            birth_time=birth_time if birth_time else None,
            birth_location=birth_location if birth_location else None,
            lat=lat,
            lng=lng,
            timezone=timezone,
            sun_sign=sun_sign_for_date(dob),
        )

        # 16 bytes keeps links shorter while retaining strong entropy.
        verify_token = generate_token(length=16)
        self.repo.create_token(user.id, verify_token, "email_verification", expires_hours=24)
        self.email.send_email_verification_email(
            to_email=user.email,
            first_name=user.first_name,
            token=verify_token,
        )
        self.email.send_welcome_email(to_email=user.email, first_name=user.first_name)
        return AuthResult(ok=True, message="Account created. Verification email sent.", user=user)

    def sign_in(self, *, email: str, password: str) -> AuthResult:
        user = self.repo.get_user_by_email(email)
        if user is None:
            return AuthResult(ok=False, message="Invalid email or password.")
        if not verify_password(password, user.hashed_password):
            return AuthResult(ok=False, message="Invalid email or password.")
        return AuthResult(ok=True, message="Signed in.", user=user)

    def request_password_reset(self, email: str) -> AuthResult:
        user = self.repo.get_user_by_email(email)
        if user is None:
            # Avoid user enumeration.
            return AuthResult(ok=True, message="If that email exists, a reset link has been sent.")

        # 16 bytes keeps links shorter while retaining strong entropy.
        reset_token = generate_token(length=16)
        self.repo.create_token(user.id, reset_token, "password_reset", expires_hours=1)
        self.email.send_password_reset_email(
            to_email=user.email,
            first_name=user.first_name,
            token=reset_token,
        )
        return AuthResult(ok=True, message="If that email exists, a reset link has been sent.")

    def reset_password(self, *, token_value: str, new_password: str) -> AuthResult:
        token = self.repo.get_token(token_value, "password_reset")
        if token is None or token.used:
            return AuthResult(ok=False, message="Invalid or used reset token.")
        if token.expires_at < utc_now():
            return AuthResult(ok=False, message="Reset token has expired.")

        user = self.repo.get_user_by_id(token.user_id)
        if user is None:
            return AuthResult(ok=False, message="User not found for token.")

        self.repo.update_user(user.id, {"hashed_password": hash_password(new_password)})
        self.repo.mark_token_used(token.id)
        return AuthResult(ok=True, message="Password updated.")

    def verify_email(self, token_value: str) -> AuthResult:
        token = self.repo.get_token(token_value, "email_verification")
        if token is None or token.used:
            return AuthResult(ok=False, message="Invalid or used verification token.")
        if token.expires_at < utc_now():
            return AuthResult(ok=False, message="Verification token has expired.")

        user = self.repo.get_user_by_id(token.user_id)
        if user is None:
            return AuthResult(ok=False, message="User not found for token.")

        self.repo.update_user(user.id, {"email_verified": True})
        self.repo.mark_token_used(token.id)
        user = self.repo.get_user_by_id(user.id)
        return AuthResult(ok=True, message="Email verified.", user=user)

    def update_birth_data(
        self,
        user_id: str,
        *,
        dob: date,
        birth_time: str | None,
        birth_location: str | None,
        lat: float | None,
        lng: float | None,
        timezone: str | None,
    ) -> User:
        updates = {
            "dob": dob.isoformat(),
            "birth_time": birth_time if birth_time else None,
            "birth_location": birth_location if birth_location else None,
            "lat": lat,
            "lng": lng,
            "timezone": timezone,
            "sun_sign": sun_sign_for_date(dob),
        }
        return self.repo.update_user(user_id, updates)

    def change_password(self, user_id: str, old_password: str, new_password: str) -> AuthResult:
        user = self.repo.get_user_by_id(user_id)
        if user is None:
            return AuthResult(ok=False, message="User not found.")
        if not verify_password(old_password, user.hashed_password):
            return AuthResult(ok=False, message="Current password is incorrect.")
        self.repo.update_user(user_id, {"hashed_password": hash_password(new_password)})
        return AuthResult(ok=True, message="Password updated.")

    def update_preferences(
        self,
        user_id: str,
        *,
        theme_preference: str,
        language_preference: str,
        notify_daily_reading: bool,
        daily_reading_hour: int,
        notify_transit_alerts: bool,
    ) -> User:
        return self.repo.update_user(
            user_id,
            {
                "theme_preference": theme_preference,
                "language_preference": language_preference,
                "notify_daily_reading": notify_daily_reading,
                "daily_reading_hour": daily_reading_hour,
                "notify_transit_alerts": notify_transit_alerts,
            },
        )

    def delete_account(self, user_id: str) -> AuthResult:
        user = self.repo.get_user_by_id(user_id)
        if user is None:
            return AuthResult(ok=False, message="User not found.")
        self.repo.delete_user_full(user_id)
        return AuthResult(ok=True, message="Account deleted.")
