"""Security utilities for HMAC signing and verification."""

import base64
import hashlib
import hmac
import os
from typing import Dict, Any

import structlog

logger = structlog.get_logger(__name__)


def get_hmac_secret() -> str:
    """Get HMAC secret from environment."""
    secret = os.getenv("HMAC_SECRET")
    if not secret:
        raise ValueError("HMAC_SECRET environment variable is required")
    return secret


def sign_payload(payload: Dict[str, Any]) -> str:
    """Sign a payload with HMAC-SHA256."""
    try:
        import json
        
        secret = get_hmac_secret()
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            secret.encode('utf-8'),
            payload_json.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Return base64url encoded signature
        return base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
        
    except Exception as e:
        logger.error("Failed to sign payload", error=str(e))
        raise


def verify_signature(payload: Dict[str, Any], signature: str) -> bool:
    """Verify HMAC signature of a payload."""
    try:
        expected_signature = sign_payload(payload)
        return hmac.compare_digest(signature, expected_signature)
        
    except Exception as e:
        logger.error("Failed to verify signature", error=str(e))
        return False


def create_cursor_link(payload: Dict[str, Any]) -> str:
    """Create a Cursor deep link with signed payload."""
    try:
        import json
        
        # Convert payload to JSON and encode as base64url
        payload_json = json.dumps(payload)
        payload_b64 = base64.urlsafe_b64encode(
            payload_json.encode('utf-8')
        ).decode('utf-8').rstrip('=')
        
        # Sign the payload
        signature = sign_payload(payload)
        
        # Create the deep link
        link = f"vscode://subhrato.blueprint-snap/ingest?data={payload_b64}&sig={signature}"
        
        return link
        
    except Exception as e:
        logger.error("Failed to create cursor link", error=str(e))
        raise


def decode_cursor_payload(data: str, signature: str) -> Dict[str, Any]:
    """Decode and verify a Cursor payload."""
    try:
        import json
        
        # Add padding if needed
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        
        # Decode base64url
        payload_json = base64.urlsafe_b64decode(data).decode('utf-8')
        payload = json.loads(payload_json)
        
        # Verify signature using the same JSON format as signing
        secret = get_hmac_secret()
        normalized_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            normalized_json.encode('utf-8'),
            hashlib.sha256
        ).digest()
        expected_sig_b64 = base64.urlsafe_b64encode(expected_signature).decode('utf-8').rstrip('=')
        
        # Add padding to signature if needed
        sig_padded = signature + '=' * ((4 - len(signature) % 4) % 4)
        expected_padded = expected_sig_b64 + '=' * ((4 - len(expected_sig_b64) % 4) % 4)
        
        if not hmac.compare_digest(sig_padded, expected_padded):
            raise ValueError("Invalid signature")
        
        return payload
        
    except Exception as e:
        logger.error("Failed to decode cursor payload", error=str(e))
        raise
