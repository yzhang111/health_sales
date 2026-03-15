from __future__ import annotations

import hashlib
import os
import secrets


def hash_password(password: str, salt: str | None = None, iterations: int = 120_000) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations).hex()
    return f"pbkdf2_sha256${iterations}${salt}${digest}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iter_s, salt, digest = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        check = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iter_s)).hex()
        return secrets.compare_digest(check, digest)
    except Exception:
        return False


def getenv(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value if value else default
