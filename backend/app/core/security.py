"""
Security utilities: Password hashing, JWT token handling, CSRF protection, and session management.
Uses Python hashlib pbkdf2_hmac for guaranteed compatibility across Python 3.11-3.13.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta, timezone
import secrets
import hashlib
from jose import jwt, JWTError

from app.config import settings

ALGORITHM = "HS256"
ISSUER = "samarath-auth-service"
AUDIENCE = "samarath-api"


def hash_password(password: str) -> str:
    """
    PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations and 16-byte random salt.
    Format: pbkdf2_sha256$100000$hex_salt$hex_digest
    """
    salt = secrets.token_hex(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    )
    return f"pbkdf2_sha256${iterations}${salt}${derived.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        scheme, iterations_str, salt, digest_hex = hashed_password.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iterations_str)
        derived = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        return secrets.compare_digest(derived.hex(), digest_hex)
    except Exception:
        return False


def create_access_token(
    subject: str,
    roles: List[str],
    permissions: List[str],
    department: Optional[str] = None,
    territory: str = "VKC",
    expires_delta: Optional[timedelta] = None,
) -> str:
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": subject,
        "iss": ISSUER,
        "aud": AUDIENCE,
        "roles": roles,
        "permissions": permissions,
        "department": department,
        "territory": territory,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": secrets.token_hex(16),
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates token against ISSUER, AUDIENCE, and EXPIRY.
    """
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[ALGORITHM],
        issuer=ISSUER,
        audience=AUDIENCE,
    )
    return payload


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def verify_csrf_token(header_token: Optional[str], cookie_token: Optional[str]) -> bool:
    if not header_token or not cookie_token:
        return False
    return secrets.compare_digest(header_token, cookie_token)
