from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from app.security import getenv, hash_password, verify_password
from app.store import STORE


SESSION_TOKENS: dict[str, dict[str, Any]] = {}


def parse_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.strip().split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]


def actor_from_auth_header(authorization: str | None) -> dict[str, Any] | None:
    token = parse_bearer_token(authorization)
    if not token:
        return None
    data = SESSION_TOKENS.get(token)
    if not data:
        return None
    if data["expires_at"] < datetime.now(timezone.utc):
        SESSION_TOKENS.pop(token, None)
        return None
    return {"actor_id": data["actor_id"], "role": data["role"], "username": data["username"]}


def issue_session_token(username: str, actor_id: str, role: str, ttl_hours: int = 12) -> str:
    token = secrets.token_urlsafe(36)
    SESSION_TOKENS[token] = {
        "username": username,
        "actor_id": actor_id,
        "role": role,
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
    }
    return token


def get_user_by_username(username: str) -> dict[str, Any] | None:
    users = STORE.list("users")
    for row in users:
        if row.get("username") == username:
            return row
    return None


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    user = get_user_by_username(username)
    if not user:
        return None
    if not user.get("is_active", True):
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


def ensure_default_users() -> None:
    defaults = [
        {
            "username": getenv("NA_ADMIN_USERNAME", "admin"),
            "password": getenv("NA_ADMIN_PASSWORD", "admin123"),
            "role": "admin",
            "actor_id": "admin_1",
        },
        {
            "username": getenv("NA_SALES_USERNAME", "sales"),
            "password": getenv("NA_SALES_PASSWORD", "sales123"),
            "role": "sales",
            "actor_id": "rep_1",
        },
    ]

    for item in defaults:
        exists = get_user_by_username(item["username"])
        if exists:
            continue
        user_id = STORE.new_id("usr")
        payload = {
            "id": user_id,
            "username": item["username"],
            "role": item["role"],
            "actor_id": item["actor_id"],
            "is_active": True,
            "password_hash": hash_password(item["password"]),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        STORE.upsert("users", user_id, payload)
        STORE.audit("system", "create", "user", user_id, "seed_default_user", payload)
