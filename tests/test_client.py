"""Tests for the client module."""

from __future__ import annotations

from typing import Any

import httpx
import pytest
from pytest_httpx import HTTPXMock

from cbadvanced import AsyncClient, Client, Granularity, OrderSide
from cbadvanced.exceptions import CoinbaseAPIError, CoinbaseRequestError


class TestSyncClient:
    """Tests for synchronous Client."""

    def test_client_requires_context_manager(self, test_credentials: tuple[str, str]) -> None:
        """Test that client raises error when used without context manager."""
        key_name, key_secret = test_credentials
        client = Client(key_name, key_secret)

        with pytest.raises(CoinbaseRequestError, match="not initialized"):
            client.get_products()

    def test_get_products(
        self,
        test_credentials: tuple[str, str],
        sample_products_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting products."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products",
            json=sample_products_response,
        )

        with Client(key_name, key_secret) as client:
            products = client.get_products()

        assert len(products) == 2
        assert products[0].product_id == "BTC-USD"
        assert products[0].price == "50000.00"
        assert products[1].product_id == "ETH-USD"

    def test_get_product(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single product."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products/BTC-USD",
            json={
                "product_id": "BTC-USD",
                "price": "50000.00",
                "base_name": "Bitcoin",
                "quote_name": "US Dollar",
            },
        )

        with Client(key_name, key_secret) as client:
            product = client.get_product("BTC-USD")

        assert product.product_id == "BTC-USD"
        assert product.price == "50000.00"

    def test_get_accounts(
        self,
        test_credentials: tuple[str, str],
        sample_accounts_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting accounts."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url=httpx.URL(
                "https://api.coinbase.com/api/v3/brokerage/accounts",
                params={"limit": "250"},
            ),
            json=sample_accounts_response,
        )

        with Client(key_name, key_secret) as client:
            accounts = client.get_accounts()

        assert len(accounts) == 2
        assert accounts[0].currency == "BTC"
        assert accounts[0].available_balance.value == "1.23"

    def test_get_candles(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles."""
        key_name, key_secret = test_credentials

        # Match any candles request (timestamps vary)
        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        with Client(key_name, key_secret) as client:
            candles = client.get_candles("BTC-USD", granularity=Granularity.ONE_HOUR)

        assert len(candles) == 2
        assert candles[0]["open"] == "50000.00"

    def test_create_limit_order(
        self,
        test_credentials: tuple[str, str],
        sample_order_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test creating a limit order."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            url="https://api.coinbase.com/api/v3/brokerage/orders",
            json=sample_order_response,
        )

        with Client(key_name, key_secret) as client:
            response = client.create_order(
                product_id="BTC-USD",
                side=OrderSide.BUY,
                order_type="limit",
                size="0.001",
                price="50000.00",
            )

        assert response.success is True
        assert response.order_id == "order-123-456"

    def test_create_order_requires_price_for_limit(
        self,
        test_credentials: tuple[str, str],
    ) -> None:
        """Test that limit orders require a price."""
        key_name, key_secret = test_credentials

        with Client(key_name, key_secret) as client:
            with pytest.raises(ValueError, match="price is required"):
                client.create_order(
                    product_id="BTC-USD",
                    side="BUY",
                    order_type="limit",
                    size="0.001",
                )

    def test_api_error_handling(
        self,
        test_credentials: tuple[str, str],
        sample_error_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test API error handling."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products/INVALID-USD",
            json=sample_error_response,
            status_code=400,
        )

        with Client(key_name, key_secret) as client:
            with pytest.raises(CoinbaseAPIError) as exc_info:
                client.get_product("INVALID-USD")

        assert exc_info.value.status_code == 400
        assert "INVALID_REQUEST" in str(exc_info.value)


class TestAsyncClient:
    """Tests for asynchronous AsyncClient."""

    @pytest.mark.asyncio
    async def test_client_requires_context_manager(self, test_credentials: tuple[str, str]) -> None:
        """Test that client raises error when used without context manager."""
        key_name, key_secret = test_credentials
        client = AsyncClient(key_name, key_secret)

        with pytest.raises(CoinbaseRequestError, match="not initialized"):
            await client.get_products()

    @pytest.mark.asyncio
    async def test_get_products(
        self,
        test_credentials: tuple[str, str],
        sample_products_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting products asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products",
            json=sample_products_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            products = await client.get_products()

        assert len(products) == 2
        assert products[0].product_id == "BTC-USD"

    @pytest.mark.asyncio
    async def test_get_accounts(
        self,
        test_credentials: tuple[str, str],
        sample_accounts_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting accounts asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url=httpx.URL(
                "https://api.coinbase.com/api/v3/brokerage/accounts",
                params={"limit": "250"},
            ),
            json=sample_accounts_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            accounts = await client.get_accounts()

        assert len(accounts) == 2
        assert accounts[0].currency == "BTC"

    @pytest.mark.asyncio
    async def test_get_orders(
        self,
        test_credentials: tuple[str, str],
        sample_orders_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting orders asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_orders_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            orders = await client.get_orders()

        assert len(orders) == 1
        assert orders[0].order_id == "order-123-456"
        assert orders[0].status == "FILLED"

    @pytest.mark.asyncio
    async def test_get_fills(
        self,
        test_credentials: tuple[str, str],
        sample_fills_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting fills asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_fills_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            fills = await client.get_fills()

        assert len(fills) == 1
        assert fills[0].trade_id == "trade-456"
        assert fills[0].price == "50000.00"

    @pytest.mark.asyncio
    async def test_cancel_orders(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test cancelling orders asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            url="https://api.coinbase.com/api/v3/brokerage/orders/batch_cancel",
            json={
                "results": [
                    {"success": True, "order_id": "order-123"},
                    {"success": False, "order_id": "order-456", "failure_reason": "NOT_FOUND"},
                ]
            },
        )

        async with AsyncClient(key_name, key_secret) as client:
            response = await client.cancel_orders(["order-123", "order-456"])

        assert len(response.results) == 2
        assert response.results[0].success is True
        assert response.results[1].success is False


class TestExceptions:
    """Tests for exception classes."""

    def test_api_error_with_response_data(self) -> None:
        """Test CoinbaseAPIError with full response data."""
        error = CoinbaseAPIError(
            status_code=400,
            response_data={
                "error": "INVALID_REQUEST",
                "message": "Invalid product",
                "code": "ERR_001",
            },
        )

        assert error.status_code == 400
        assert error.error_code == "ERR_001"
        assert "INVALID_REQUEST" in error.message
        assert "Invalid product" in error.message

    def test_api_error_without_response_data(self) -> None:
        """Test CoinbaseAPIError without response data."""
        error = CoinbaseAPIError(
            status_code=500,
            message="Internal server error",
        )

        assert error.status_code == 500
        assert error.message == "Internal server error"

    def test_request_error(self) -> None:
        """Test CoinbaseRequestError."""
        original = ValueError("Bad value")
        error = CoinbaseRequestError("Request failed", original_error=original)

        assert "Request failed" in str(error)
        assert error.original_error is original
