from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 390000


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    encoded_salt = base64.urlsafe_b64encode(salt).decode("ascii")
    encoded_hash = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"{PBKDF2_ALGO}${PBKDF2_ITERATIONS}${encoded_salt}${encoded_hash}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, iterations, encoded_salt, encoded_hash = encoded.split("$", 3)
        if algo != PBKDF2_ALGO:
            return False
        salt = base64.urlsafe_b64decode(encoded_salt.encode("ascii"))
        original = base64.urlsafe_b64decode(encoded_hash.encode("ascii"))
        new_digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return hmac.compare_digest(new_digest, original)
    except Exception:
        return False


def generate_token(length: int = 32) -> str:
    return secrets.token_urlsafe(length)
