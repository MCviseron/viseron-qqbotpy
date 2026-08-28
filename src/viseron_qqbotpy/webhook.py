"""Webhook signature verification helpers (optional).

Install the optional dependency first:

    pip install viseron-qqbotpy[webhook]

The signature algorithm uses Ed25519.  The bot secret is repeated until it is
at least 32 bytes long and then used as the Ed25519 seed.
"""

from __future__ import annotations

import binascii
from typing import Tuple

__all__ = ["verify_signature", "sign_validation"]


def _seed_from_secret(secret: str) -> bytes:
    seed = secret.encode("utf-8")
    while len(seed) < 32:
        seed = seed * 2
    return seed[:32]


def _load_crypto():
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.exceptions import InvalidSignature
    except ImportError as exc:  # pragma: no cover - depends on optional extra
        raise ImportError(
            "webhook support requires the 'cryptography' package; "
            "install it with: pip install viseron-qqbotpy[webhook]"
        ) from exc
    return Ed25519PrivateKey, InvalidSignature


def verify_signature(secret: str, timestamp: str, body: str, signature_hex: str) -> bool:
    """Verify an incoming webhook request.

    Parameters:
        secret:
            Bot AppSecret.
        timestamp:
            Value of the X-Signature-Timestamp header.
        body:
            Raw HTTP request body string.
        signature_hex:
            Value of the X-Signature-Ed25519 header.
    """
    Ed25519PrivateKey, InvalidSignature = _load_crypto()
    try:
        signature = binascii.unhexlify(signature_hex)
    except (binascii.Error, ValueError):
        return False
    if len(signature) != 64 or (signature[63] & 224) != 0:
        return False

    private_key = Ed25519PrivateKey.from_private_bytes(_seed_from_secret(secret))
    message = f"{timestamp}{body}".encode("utf-8")
    try:
        private_key.public_key().verify(signature, message)
    except InvalidSignature:
        return False
    return True


def sign_validation(secret: str, event_ts: str, plain_token: str) -> Tuple[str, str]:
    """Return (plain_token, signature) for the webhook URL verification flow."""
    Ed25519PrivateKey, _ = _load_crypto()
    private_key = Ed25519PrivateKey.from_private_bytes(_seed_from_secret(secret))
    message = f"{event_ts}{plain_token}".encode("utf-8")
    signature = private_key.sign(message)
    return plain_token, signature.hex()
