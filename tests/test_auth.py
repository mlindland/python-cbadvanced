"""Tests for the authentication module."""

from __future__ import annotations

import time

import jwt
import pytest

from cbadvanced.auth import CoinbaseAuth


class TestCoinbaseAuth:
    """Tests for CoinbaseAuth class."""

    def test_init_valid_key(self, test_credentials: tuple[str, str]) -> None:
        """Test initialization with valid credentials."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        assert auth.key_name == key_name

    def test_init_invalid_key(self) -> None:
        """Test initialization with invalid private key."""
        with pytest.raises(ValueError, match="Invalid private key"):
            CoinbaseAuth("test-key", "invalid-key-data")

    def test_build_jwt_structure(self, test_credentials: tuple[str, str]) -> None:
        """Test that JWT has correct structure."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        token = auth.build_jwt("GET", "/api/v3/brokerage/accounts")

        # Decode without verification to inspect structure
        decoded = jwt.decode(token, options={"verify_signature": False})

        assert decoded["sub"] == key_name
        assert decoded["iss"] == "cdp"
        assert "nbf" in decoded
        assert "exp" in decoded
        assert "uri" in decoded

    def test_build_jwt_expiry(self, test_credentials: tuple[str, str]) -> None:
        """Test that JWT has correct expiry time."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        before = int(time.time())
        token = auth.build_jwt("GET", "/api/v3/brokerage/accounts")
        after = int(time.time())

        decoded = jwt.decode(token, options={"verify_signature": False})

        # Expiry should be ~120 seconds from now
        assert decoded["exp"] >= before + 120
        assert decoded["exp"] <= after + 120

    def test_build_jwt_uri_format(self, test_credentials: tuple[str, str]) -> None:
        """Test that JWT uri claim is formatted correctly."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        token = auth.build_jwt("POST", "/api/v3/brokerage/orders")

        decoded = jwt.decode(token, options={"verify_signature": False})

        assert decoded["uri"] == "POST api.coinbase.com/api/v3/brokerage/orders"

    def test_build_jwt_headers(self, test_credentials: tuple[str, str]) -> None:
        """Test that JWT has correct headers."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        token = auth.build_jwt("GET", "/api/v3/brokerage/accounts")

        # Get headers
        header = jwt.get_unverified_header(token)

        assert header["alg"] == "ES256"
        assert header["kid"] == key_name
        assert "nonce" in header

    def test_get_auth_headers(self, test_credentials: tuple[str, str]) -> None:
        """Test that auth headers are correctly formatted."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        headers = auth.get_auth_headers("GET", "/api/v3/brokerage/accounts")

        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")

        # Extract and validate token
        token = headers["Authorization"].replace("Bearer ", "")
        decoded = jwt.decode(token, options={"verify_signature": False})
        assert decoded["sub"] == key_name

    def test_unique_nonce_per_request(self, test_credentials: tuple[str, str]) -> None:
        """Test that each JWT has a unique nonce."""
        key_name, key_secret = test_credentials
        auth = CoinbaseAuth(key_name, key_secret)

        token1 = auth.build_jwt("GET", "/api/v3/brokerage/accounts")
        token2 = auth.build_jwt("GET", "/api/v3/brokerage/accounts")

        header1 = jwt.get_unverified_header(token1)
        header2 = jwt.get_unverified_header(token2)

        assert header1["nonce"] != header2["nonce"]
