"""Pytest fixtures for cbadvanced tests."""

from __future__ import annotations

import pytest

# Sample EC private key for testing (DO NOT use in production)
# This is a P-256 test key generated specifically for unit tests (ES256 algorithm)
TEST_PRIVATE_KEY = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIB7jXcGrFVewaEAZZQwsYylqT2Gdr9YBjFPNrdu4lC9DoAoGCCqGSM49
AwEHoUQDQgAECjGEMQ8Be+9SYWWlauWpG/o66E67OiFnvxeyY31ZED5fUE6GLWpe
UNpYLCUuTLGl2DDjRdvdY85W3utjiDna3w==
-----END EC PRIVATE KEY-----"""

TEST_KEY_NAME = "organizations/test-org/apiKeys/test-key"


@pytest.fixture
def test_credentials() -> tuple[str, str]:
    """Return test API credentials."""
    return TEST_KEY_NAME, TEST_PRIVATE_KEY


@pytest.fixture
def sample_accounts_response() -> dict:
    """Return a sample accounts API response."""
    return {
        "accounts": [
            {
                "uuid": "8bfc20d7-f7c6-4422-bf07-8243ca4169fe",
                "name": "BTC Wallet",
                "currency": "BTC",
                "available_balance": {"value": "1.23", "currency": "BTC"},
                "default": True,
                "active": True,
                "type": "ACCOUNT_TYPE_CRYPTO",
                "ready": True,
            },
            {
                "uuid": "9cfd31e8-g8d7-5533-cg18-9354db5270gf",
                "name": "USD Wallet",
                "currency": "USD",
                "available_balance": {"value": "1000.00", "currency": "USD"},
                "default": False,
                "active": True,
                "type": "ACCOUNT_TYPE_FIAT",
                "ready": True,
            },
        ],
        "has_next": False,
        "cursor": "",
        "size": 2,
    }


@pytest.fixture
def sample_products_response() -> dict:
    """Return a sample products API response."""
    return {
        "products": [
            {
                "product_id": "BTC-USD",
                "price": "50000.00",
                "price_percentage_change_24h": "2.5",
                "volume_24h": "1000000.00",
                "base_increment": "0.00000001",
                "quote_increment": "0.01",
                "quote_min_size": "1",
                "quote_max_size": "10000000",
                "base_min_size": "0.0001",
                "base_max_size": "1000",
                "base_name": "Bitcoin",
                "quote_name": "US Dollar",
                "status": "online",
                "product_type": "SPOT",
            },
            {
                "product_id": "ETH-USD",
                "price": "3000.00",
                "price_percentage_change_24h": "1.2",
                "volume_24h": "500000.00",
                "base_increment": "0.00000001",
                "quote_increment": "0.01",
                "quote_min_size": "1",
                "quote_max_size": "10000000",
                "base_min_size": "0.001",
                "base_max_size": "10000",
                "base_name": "Ethereum",
                "quote_name": "US Dollar",
                "status": "online",
                "product_type": "SPOT",
            },
        ],
        "num_products": 2,
    }


@pytest.fixture
def sample_candles_response() -> dict:
    """Return a sample candles API response."""
    return {
        "candles": [
            {
                "start": "1704067200",
                "low": "49500.00",
                "high": "50500.00",
                "open": "50000.00",
                "close": "50200.00",
                "volume": "100.5",
            },
            {
                "start": "1704070800",
                "low": "50100.00",
                "high": "51000.00",
                "open": "50200.00",
                "close": "50800.00",
                "volume": "150.2",
            },
        ]
    }


@pytest.fixture
def sample_order_response() -> dict:
    """Return a sample create order API response."""
    return {
        "success": True,
        "order_id": "order-123-456",
        "success_response": {
            "order_id": "order-123-456",
            "product_id": "BTC-USD",
            "side": "BUY",
            "client_order_id": "client-order-123",
        },
    }


@pytest.fixture
def sample_orders_response() -> dict:
    """Return a sample list orders API response."""
    return {
        "orders": [
            {
                "order_id": "order-123-456",
                "product_id": "BTC-USD",
                "side": "BUY",
                "client_order_id": "client-order-123",
                "status": "FILLED",
                "filled_size": "0.001",
                "average_filled_price": "50000.00",
                "fee": "0.50",
            }
        ],
        "has_next": False,
        "cursor": "",
    }


@pytest.fixture
def sample_fills_response() -> dict:
    """Return a sample fills API response."""
    return {
        "fills": [
            {
                "entry_id": "entry-123",
                "trade_id": "trade-456",
                "order_id": "order-123-456",
                "price": "50000.00",
                "size": "0.001",
                "commission": "0.50",
                "product_id": "BTC-USD",
                "side": "BUY",
            }
        ],
        "cursor": "",
    }


@pytest.fixture
def sample_error_response() -> dict:
    """Return a sample API error response."""
    return {
        "error": "INVALID_REQUEST",
        "message": "Invalid product ID",
        "error_details": "Product 'INVALID-USD' not found",
        "code": "400",
    }
