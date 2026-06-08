"""
crypto.py - Symmetric encryption utilities for sensitive configuration values.

Uses Fernet (AES-128-CBC + HMAC-SHA256) from the `cryptography` package.

Encrypted values are stored with a "fernet:" prefix so that plaintext values
already in the database remain usable without migration (backward-compatible).

Usage:
    from ina_ground_control.utils.crypto import get_secret_cipher

    cipher = get_secret_cipher()
    encrypted = cipher.encrypt("my-plain-secret")   # "fernet:gAAAAA..."
    plain     = cipher.decrypt(encrypted)           # "my-plain-secret"
    plain     = cipher.decrypt("legacy-plain")      # "legacy-plain" (passthrough)

Testing:
    from cryptography.fernet import Fernet
    from ina_ground_control.utils.crypto import SecretCipher

    key = Fernet.generate_key().decode()
    cipher = SecretCipher(key)
    assert cipher.decrypt(cipher.encrypt("secret")) == "secret"
"""

from cryptography.fernet import Fernet, InvalidToken

from ina_ground_control import logger
from ina_ground_control.exception.exceptions import ErrorCode, GroundControlException

_PREFIX = "fernet:"


class SecretCipher:
    """
    Fernet-based symmetric cipher for plugin client secrets.

    The key must be a 32-byte URL-safe base64-encoded string as produced by
    ``Fernet.generate_key()``.  Pass it explicitly in tests; the
    :func:`get_secret_cipher` factory reads it from application settings.
    """

    def __init__(self, key: str) -> None:
        if not key:
            raise ValueError(
                "GC_SECRET_ENCRYPTION_KEY is not set. "
                "Generate one with: "
                'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            )
        try:
            self._fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except (ValueError, Exception) as exc:
            raise ValueError(
                f"GC_SECRET_ENCRYPTION_KEY is invalid ({exc}). "
                "It must be a 32-byte URL-safe base64 string. "
                "Regenerate it with: "
                'python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
            ) from exc

    def encrypt(self, plain: str) -> str:
        """
        Encrypt *plain* and return a prefixed ciphertext string.

        Returns *plain* unchanged when it is empty.

        Args:
            plain: Plaintext secret to encrypt.

        Returns:
            ``"fernet:<base64-ciphertext>"`` or the original value if empty.
        """
        if not plain:
            return plain
        token = self._fernet.encrypt(plain.encode()).decode()
        return f"{_PREFIX}{token}"

    def decrypt(self, value: str) -> str:
        """
        Decrypt a value previously produced by :meth:`encrypt`.

        Values that do **not** start with the ``"fernet:"`` prefix are returned
        as-is, allowing backward-compatible handling of secrets stored in
        plaintext before encryption was introduced.

        Args:
            value: Encrypted (prefixed) string or a legacy plaintext value.

        Returns:
            The decrypted plaintext.

        Raises:
            GroundControlException: If decryption fails (tampered data or wrong key).
        """
        if not value or not value.startswith(_PREFIX):
            return value

        try:
            token = value[len(_PREFIX) :].encode()
            return self._fernet.decrypt(token).decode()
        except InvalidToken as exc:
            logger.error("Failed to decrypt secret: invalid token or wrong key.")
            raise GroundControlException(
                ErrorCode.GENERIC_CLIENT_ERROR,
                details="Failed to decrypt plugin client secret. Check GC_SECRET_ENCRYPTION_KEY.",
            ) from exc

    @staticmethod
    def is_encrypted(value: str) -> bool:
        """Return True if *value* looks like a Fernet-encrypted secret."""
        return bool(value and value.startswith(_PREFIX))


def get_secret_cipher() -> SecretCipher:
    """
    Application-level factory that builds a :class:`SecretCipher` from settings.

    Reads ``settings.secret_encryption_key`` (env var ``GC_SECRET_ENCRYPTION_KEY``).
    Call this at use-time, not at import-time, to keep the module testable.
    """
    # pylint: disable=import-outside-toplevel
    from ina_ground_control import settings

    return SecretCipher(settings.secret_encryption_key)
