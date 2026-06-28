"""OIDC authentication and RBAC authorization for Nunneri.

Set AUTH_ENABLED=false to bypass all auth (dev mode).
Configure via environment variables:
  OIDC_ISSUER_URL     — e.g. https://keycloak.example.com/realms/nunneri
  OIDC_CLIENT_ID
  OIDC_CLIENT_SECRET
  OIDC_REDIRECT_URI   — defaults to http://localhost:8000/auth/callback
  SESSION_SECRET      — used to sign internal session JWTs (change in prod)
  SESSION_TTL_S       — session lifetime in seconds (default 86400 = 24h)
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from functools import lru_cache
from typing import Any
from urllib.parse import urlencode

import httpx
import jwt as pyjwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

import db as _db
from models import Membership, ROLE_RANK, RbacRole, User

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

AUTH_ENABLED: bool = os.environ.get("AUTH_ENABLED", "true").lower() not in (
    "false", "0", "no"
)
OIDC_ISSUER: str = os.environ.get("OIDC_ISSUER_URL", "")
OIDC_CLIENT_ID: str = os.environ.get("OIDC_CLIENT_ID", "nunneri")
OIDC_CLIENT_SECRET: str = os.environ.get("OIDC_CLIENT_SECRET", "")
OIDC_REDIRECT_URI: str = os.environ.get(
    "OIDC_REDIRECT_URI", "http://localhost:8000/auth/callback"
)
SESSION_SECRET: str = os.environ.get("SESSION_SECRET", "change-me-in-production")
SESSION_TTL_S: int = int(os.environ.get("SESSION_TTL_S", "86400"))

# Pending OAuth states: state_token -> {"nonce": str, "created_at": float}
_pending_states: dict[str, dict] = {}

_bearer = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# OIDC discovery
# ---------------------------------------------------------------------------

_oidc_meta: dict[str, Any] | None = None


async def _get_oidc_meta() -> dict[str, Any]:
    global _oidc_meta
    if _oidc_meta:
        return _oidc_meta
    if not OIDC_ISSUER:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OIDC_ISSUER_URL not configured",
        )
    url = OIDC_ISSUER.rstrip("/") + "/.well-known/openid-configuration"
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        r.raise_for_status()
        _oidc_meta = r.json()
    return _oidc_meta


# ---------------------------------------------------------------------------
# JWKS-based ID-token validation
# ---------------------------------------------------------------------------

_jwks_client: pyjwt.PyJWKClient | None = None


async def _get_jwks_client() -> pyjwt.PyJWKClient:
    global _jwks_client
    if _jwks_client:
        return _jwks_client
    meta = await _get_oidc_meta()
    _jwks_client = pyjwt.PyJWKClient(meta["jwks_uri"])
    return _jwks_client


async def _validate_id_token(id_token: str) -> dict:
    """Validate OIDC ID token and return claims."""
    jwks = await _get_jwks_client()
    signing_key = jwks.get_signing_key_from_jwt(id_token)
    return pyjwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256", "ES256"],
        audience=OIDC_CLIENT_ID,
    )


# ---------------------------------------------------------------------------
# Session JWT (internal, signed with SESSION_SECRET)
# ---------------------------------------------------------------------------

def _issue_session(user: User) -> str:
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "iat": int(time.time()),
        "exp": int(time.time()) + SESSION_TTL_S,
    }
    return pyjwt.encode(payload, SESSION_SECRET, algorithm="HS256")


def _decode_session(token: str) -> dict:
    try:
        return pyjwt.decode(token, SESSION_SECRET, algorithms=["HS256"])
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid session token: {exc}")


# ---------------------------------------------------------------------------
# Anonymous fallback user (AUTH_ENABLED=false)
# ---------------------------------------------------------------------------

_ANON_USER = User(
    id="00000000-0000-0000-0000-000000000000",
    sub="anonymous",
    email="anonymous@localhost",
    name="Anonymous Admin",
)


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> User:
    """Resolve the current user from the Bearer session JWT.

    When AUTH_ENABLED=false, returns the anonymous admin user.
    """
    if not AUTH_ENABLED:
        return _ANON_USER

    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header required")

    claims = _decode_session(credentials.credentials)
    user = await _db.get_user(claims["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found — please log in again")
    return user


async def require_org_role(
    org_id: str,
    min_role: RbacRole,
    user: User,
) -> None:
    if not AUTH_ENABLED:
        return
    role = await _db.get_role("org", org_id, user.id)
    if role is None or ROLE_RANK.get(role, -1) < ROLE_RANK[min_role]:
        raise HTTPException(status_code=403, detail="Insufficient org permissions")


async def require_team_role(
    team_id: str,
    min_role: RbacRole,
    user: User,
) -> None:
    if not AUTH_ENABLED:
        return
    # Team role OR org-admin satisfies the check.
    team = await _db.get_team(team_id)
    if team:
        org_role = await _db.get_role("org", team.org_id, user.id)
        if org_role == "admin":
            return
    role = await _db.get_role("team", team_id, user.id)
    if role is None or ROLE_RANK.get(role, -1) < ROLE_RANK[min_role]:
        raise HTTPException(status_code=403, detail="Insufficient team permissions")


async def require_project_role(
    project_id: str,
    min_role: RbacRole,
    user: User,
) -> None:
    if not AUTH_ENABLED:
        return
    project = await _db.get_project(project_id)
    if project:
        # Org admin always passes.
        org_role = await _db.get_role("org", project.org_id, user.id)
        if org_role == "admin":
            return
        # Team admin passes.
        team_role = await _db.get_role("team", project.team_id, user.id)
        if team_role == "admin":
            return
    role = await _db.get_role("project", project_id, user.id)
    if role is None or ROLE_RANK.get(role, -1) < ROLE_RANK[min_role]:
        raise HTTPException(status_code=403, detail="Insufficient project permissions")


# ---------------------------------------------------------------------------
# OAuth Authorization Code flow helpers
# ---------------------------------------------------------------------------

def build_auth_url(state: str) -> str:
    meta = _oidc_meta or {}
    auth_ep = meta.get("authorization_endpoint", "")
    params = {
        "response_type": "code",
        "client_id": OIDC_CLIENT_ID,
        "redirect_uri": OIDC_REDIRECT_URI,
        "scope": "openid email profile",
        "state": state,
    }
    return f"{auth_ep}?{urlencode(params)}"


async def exchange_code(code: str) -> tuple[str, str]:
    """Exchange authorization code for (access_token, id_token)."""
    meta = await _get_oidc_meta()
    async with httpx.AsyncClient(timeout=15.0) as client:
        r = await client.post(
            meta["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": OIDC_REDIRECT_URI,
                "client_id": OIDC_CLIENT_ID,
                "client_secret": OIDC_CLIENT_SECRET,
            },
        )
        r.raise_for_status()
        body = r.json()
    return body.get("access_token", ""), body.get("id_token", "")


async def oidc_login_url() -> str:
    """Generate OIDC authorization URL and register the state token."""
    state = secrets.token_urlsafe(24)
    _pending_states[state] = {"created_at": time.time()}
    await _get_oidc_meta()   # warm the cache; raises if misconfigured
    return build_auth_url(state)


async def oidc_callback(code: str, state: str) -> tuple[User, str]:
    """Handle OIDC callback: validate state, exchange code, upsert user, return (user, session_jwt)."""
    entry = _pending_states.pop(state, None)
    if not entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OAuth state")
    if time.time() - entry["created_at"] > 600:
        raise HTTPException(status_code=400, detail="OAuth state expired")

    _access, id_token = await exchange_code(code)
    claims = await _validate_id_token(id_token)

    user = await _db.upsert_user(User(
        sub=claims["sub"],
        email=claims.get("email", ""),
        name=claims.get("name"),
        picture=claims.get("picture"),
    ))
    session = _issue_session(user)
    return user, session
