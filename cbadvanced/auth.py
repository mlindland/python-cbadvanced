"""Coinbase Advanced Trade API authentication module.

This module provides JWT-based authentication for the Coinbase Advanced Trade API
using ES256 (ECDSA with SHA-256) signing.
"""

from __future__ import annotations

import secrets
import time
from typing import TYPE_CHECKING

import jwt
from cryptography.hazmat.primitives import serialization

if TYPE_CHECKING:
    from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


class CoinbaseAuth:
    """Handles JWT-based authentication for Coinbase Advanced Trade API.

    This class generates signed JWT tokens required for authenticating
    requests to the Coinbase Advanced Trade API.

    Attributes:
        key_name: The API key name (used as 'sub' and 'kid' in JWT).
        _private_key: The loaded EC private key for signing.

    Example:
        >>> auth = CoinbaseAuth(key_name="your-key-name", key_secret="-----BEGIN EC PRIVATE KEY-----...")
        >>> token = auth.build_jwt("GET", "/api/v3/brokerage/accounts")
    """

    # JWT token expiration time in seconds
    TOKEN_EXPIRY_SECONDS: int = 120

    # JWT issuer claim
    JWT_ISSUER: str = "cdp"

    def __init__(self, key_name: str, key_secret: str) -> None:
        """Initialize the authentication handler.

        Args:
            key_name: Your Coinbase API key name.
            key_secret: Your Coinbase API secret (PEM-encoded EC private key).

        Raises:
            ValueError: If the key_secret is not a valid PEM-encoded private key.
        """
        self.key_name = key_name
        self._private_key = self._load_private_key(key_secret)

    @staticmethod
    def _load_private_key(key_secret: str) -> EllipticCurvePrivateKey:
        """Load and validate the PEM-encoded private key.

        Args:
            key_secret: PEM-encoded EC private key string.

        Returns:
            The loaded private key object.

        Raises:
            ValueError: If the key cannot be loaded or is invalid.
        """
        try:
            private_key_bytes = key_secret.encode("utf-8")
            private_key = serialization.load_pem_private_key(
                private_key_bytes,
                password=None,
            )
            return private_key  # type: ignore[return-value]
        except Exception as e:
            raise ValueError(f"Invalid private key: {e}") from e

    def build_jwt(self, method: str, path: str, host: str = "api.coinbase.com") -> str:
        """Build a signed JWT token for API authentication.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path (e.g., "/api/v3/brokerage/accounts").
            host: API host (defaults to api.coinbase.com).

        Returns:
            The signed JWT token string.
        """
        uri = f"{method} {host}{path}"
        current_time = int(time.time())

        jwt_payload = {
            "sub": self.key_name,
            "iss": self.JWT_ISSUER,
            "nbf": current_time,
            "exp": current_time + self.TOKEN_EXPIRY_SECONDS,
            "uri": uri,
        }

        jwt_token: str = jwt.encode(
            jwt_payload,
            self._private_key,
            algorithm="ES256",
            headers={
                "kid": self.key_name,
                "nonce": secrets.token_hex(16),
            },
        )

        return jwt_token

    def get_auth_headers(self, method: str, path: str) -> dict[str, str]:
        """Get authentication headers for an API request.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.

        Returns:
            Dictionary containing the Authorization header.
        """
        token = self.build_jwt(method, path)
        return {"Authorization": f"Bearer {token}"}
