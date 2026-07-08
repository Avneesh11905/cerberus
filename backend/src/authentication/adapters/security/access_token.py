"""
Generates and validates stateless JSON Web Tokens (JWT).
Access Tokens are short-lived (e.g. 15 minutes) and signed using RS256 with asymmetric key pairs to prevent tampering.
They contain the minimal user claims needed by the API to identify the caller without querying the database.
"""
from datetime import datetime, timezone
from uuid import UUID

import jwt
from uuid6 import uuid7

from src.authentication.core.domain import UserIdentity


class JWTAccessTokenAdapter:
    """Implements AccessTokenPort using PyJWT for stateless token signing with RS256."""

    def __init__(self, private_key: str, public_key: str, lifetime_minutes: int):
        self._private_key = private_key
        self._public_key = public_key
        self._algorithm = "RS256"

        self._lifetime_seconds = lifetime_minutes * 60

    def create(self, user: UserIdentity, extra_claims: dict[str, object] | None = None, private_key_override: str | None = None) -> str:
        now = int(datetime.now(timezone.utc).timestamp())
        expires = now + self._lifetime_seconds
        payload = {
            "jti": str(uuid7()),
            "sub": str(user.id),
            "email": str(user.email),
            "role": user.role,
            "project_id": str(user.project_id) if user.project_id else None,
            "is_verified": user.is_verified,
            "exp": expires,
            "iat": now,
        }
        if extra_claims:
            # We don't want extra claims to overwrite critical JWT fields
            safe_claims = {k: v for k, v in extra_claims.items() if k not in payload}
            payload.update(safe_claims) # type: ignore
            
        key = private_key_override if private_key_override else self._private_key
        return jwt.encode(payload, key, algorithm=self._algorithm)
            
    def verify(self, token: str, public_key_override: str | None = None) -> tuple[UserIdentity | None, dict[str, object] | None]:
        key = public_key_override if public_key_override else self._public_key
        try:
            payload = jwt.decode(token, key, algorithms=[self._algorithm])
            user = UserIdentity(
                id=UUID(payload["sub"]),   # str → UUID at JWT boundary
                email=payload["email"],
                role=payload.get("role", "user"),
                project_id=UUID(payload["project_id"]) if payload.get("project_id") else None,
                is_verified=payload.get("is_verified", True),
            )
            return user, payload
        except jwt.ExpiredSignatureError:
            return None, None
        except jwt.InvalidTokenError:
            return None, None
