import base64
import hashlib
import hmac
import json
from typing import Any


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def sign_payload(secret: str, payload: dict[str, Any]) -> tuple[str, str]:
    body = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return b64url(body), b64url(sig)

