"""Token encryption for at-rest protection of Wargaming access tokens.

Uses Fernet symmetric encryption. The encryption key is derived from
the ENCRYPTION_KEY environment variable. If not set, a key is auto-generated
and stored in a local file (encryption.key) — but for production you should
always set ENCRYPTION_KEY explicitly.
"""

import base64
import hashlib
import logging
import os

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)

_fernet: Fernet | None = None


def _get_fernet() -> Fernet:
    global _fernet
    if _fernet is not None:
        return _fernet

    key_source = os.environ.get("ENCRYPTION_KEY")

    if key_source:
        # Derive a valid 32-byte Fernet key from any string
        derived = hashlib.sha256(key_source.encode()).digest()
        key = base64.urlsafe_b64encode(derived)
    else:
        # Fallback: generate and persist a key file (not ideal for production)
        key_file = "encryption.key"
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key = f.read().strip()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            logger.warning(
                "Generated new encryption key at %s. "
                "Set ENCRYPTION_KEY env var for production deployments.",
                key_file,
            )

    _fernet = Fernet(key)
    return _fernet


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token. Returns a base64-encoded encrypted string."""
    f = _get_fernet()
    return f.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str | None:
    """Decrypt a token. Returns None if decryption fails."""
    f = _get_fernet()
    try:
        return f.decrypt(ciphertext.encode()).decode()
    except (InvalidToken, Exception) as e:
        logger.error("Failed to decrypt token: %s", e)
        return None
