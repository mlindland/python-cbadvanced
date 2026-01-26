"""Tests for the client module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
import pytest
from pytest_httpx import HTTPXMock

from cbadvanced import AsyncClient, Client, Granularity, OrderSide
from cbadvanced.client import async_client, sync_client
from cbadvanced.exceptions import CoinbaseAPIError, CoinbaseAuthError, CoinbaseRequestError


class TestSyncClient:
    """Tests for synchronous Client."""

    def test_client_requires_context_manager(self, test_credentials: tuple[str, str]) -> None:
        """Test that client raises error when used without context manager."""
        key_name, key_secret = test_credentials
        client = Client(key_name, key_secret)

        with pytest.raises(CoinbaseRequestError, match="not initialized"):
            client.get_products()

    def test_client_custom_timeout(self, test_credentials: tuple[str, str]) -> None:
        """Test client with custom timeout."""
        key_name, key_secret = test_credentials
        client = Client(key_name, key_secret, timeout=60.0)
        assert client._timeout == 60.0

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

    def test_get_products_with_filters(
        self,
        test_credentials: tuple[str, str],
        sample_products_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting products with filters."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_products_response,
        )

        with Client(key_name, key_secret) as client:
            products = client.get_products(product_type="SPOT", limit=10)

        assert len(products) == 2

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

    def test_get_accounts_with_cursor(
        self,
        test_credentials: tuple[str, str],
        sample_accounts_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting accounts with pagination cursor."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_accounts_response,
        )

        with Client(key_name, key_secret) as client:
            accounts = client.get_accounts(limit=50, cursor="next_page_token")

        assert len(accounts) == 2

    def test_get_account(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single account."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/accounts/test-uuid",
            json={
                "account": {
                    "uuid": "test-uuid",
                    "name": "BTC Wallet",
                    "currency": "BTC",
                    "available_balance": {"value": "1.5", "currency": "BTC"},
                }
            },
        )

        with Client(key_name, key_secret) as client:
            account = client.get_account("test-uuid")

        assert account.uuid == "test-uuid"
        assert account.currency == "BTC"

    def test_get_candles(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        with Client(key_name, key_secret) as client:
            candles = client.get_candles("BTC-USD", granularity=Granularity.ONE_HOUR)

        assert len(candles) == 2
        assert candles[0]["open"] == "50000.00"

    def test_get_candles_with_datetime(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles with datetime objects."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        now = datetime.now(timezone.utc)
        start = now - timedelta(days=7)

        with Client(key_name, key_secret) as client:
            candles = client.get_candles("BTC-USD", start=start, end=now)

        assert len(candles) == 2

    def test_get_candles_with_timestamps(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles with Unix timestamps."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        with Client(key_name, key_secret) as client:
            candles = client.get_candles(
                "BTC-USD",
                start=1704067200,
                end=1704153600,
                granularity="ONE_HOUR",
            )

        assert len(candles) == 2

    def test_get_market_trades(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting market trades."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json={
                "trades": [
                    {"trade_id": "t1", "product_id": "BTC-USD", "price": "50000", "size": "0.1"}
                ],
                "best_bid": "49999",
                "best_ask": "50001",
            },
        )

        with Client(key_name, key_secret) as client:
            response = client.get_market_trades("BTC-USD", limit=50)

        assert response.best_bid == "49999"
        assert response.best_ask == "50001"
        assert len(response.trades) == 1

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

    def test_create_market_order(
        self,
        test_credentials: tuple[str, str],
        sample_order_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test creating a market order."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            url="https://api.coinbase.com/api/v3/brokerage/orders",
            json=sample_order_response,
        )

        with Client(key_name, key_secret) as client:
            response = client.create_order(
                product_id="BTC-USD",
                side="BUY",
                order_type="market",
                size="100.00",
            )

        assert response.success is True

    def test_create_order_with_string_side(
        self,
        test_credentials: tuple[str, str],
        sample_order_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test creating order with string side."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            json=sample_order_response,
        )

        with Client(key_name, key_secret) as client:
            response = client.create_order(
                product_id="BTC-USD",
                side="sell",
                order_type="limit",
                size="0.001",
                price="60000.00",
                client_order_id="my-custom-id",
            )

        assert response.success is True

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

    def test_get_orders(
        self,
        test_credentials: tuple[str, str],
        sample_orders_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting orders."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_orders_response,
        )

        with Client(key_name, key_secret) as client:
            orders = client.get_orders()

        assert len(orders) == 1
        assert orders[0].order_id == "order-123-456"

    def test_get_orders_with_filters(
        self,
        test_credentials: tuple[str, str],
        sample_orders_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting orders with filters."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_orders_response,
        )

        with Client(key_name, key_secret) as client:
            orders = client.get_orders(
                product_id="BTC-USD",
                order_status=["FILLED", "CANCELLED"],
                limit=50,
                cursor="page_cursor",
            )

        assert len(orders) == 1

    def test_get_order(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single order."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/orders/historical/order-123",
            json={
                "order": {
                    "order_id": "order-123",
                    "product_id": "BTC-USD",
                    "side": "BUY",
                    "status": "FILLED",
                }
            },
        )

        with Client(key_name, key_secret) as client:
            order = client.get_order("order-123")

        assert order.order_id == "order-123"
        assert order.status == "FILLED"

    def test_cancel_orders(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test cancelling orders."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            url="https://api.coinbase.com/api/v3/brokerage/orders/batch_cancel",
            json={
                "results": [
                    {"success": True, "order_id": "order-123"},
                ]
            },
        )

        with Client(key_name, key_secret) as client:
            response = client.cancel_orders(["order-123"])

        assert len(response.results) == 1
        assert response.results[0].success is True

    def test_cancel_single_order(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test cancelling a single order (string instead of list)."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            json={"results": [{"success": True, "order_id": "order-123"}]},
        )

        with Client(key_name, key_secret) as client:
            response = client.cancel_orders("order-123")

        assert response.results[0].success is True

    def test_get_fills(
        self,
        test_credentials: tuple[str, str],
        sample_fills_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting fills."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_fills_response,
        )

        with Client(key_name, key_secret) as client:
            fills = client.get_fills()

        assert len(fills) == 1
        assert fills[0].trade_id == "trade-456"

    def test_get_fills_with_filters(
        self,
        test_credentials: tuple[str, str],
        sample_fills_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting fills with filters."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_fills_response,
        )

        with Client(key_name, key_secret) as client:
            fills = client.get_fills(
                order_id="order-123",
                product_id="BTC-USD",
                limit=50,
                cursor="page_cursor",
            )

        assert len(fills) == 1

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

    def test_api_error_without_json(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test API error when response is not JSON."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products/BTC-USD",
            content=b"Internal Server Error",
            status_code=500,
        )

        with Client(key_name, key_secret) as client:
            with pytest.raises(CoinbaseAPIError) as exc_info:
                client.get_product("BTC-USD")

        assert exc_info.value.status_code == 500
        assert "Internal Server Error" in exc_info.value.message

    def test_invalid_json_response(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test handling of invalid JSON in successful response."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products/BTC-USD",
            content=b"not valid json",
            status_code=200,
        )

        with Client(key_name, key_secret) as client:
            with pytest.raises(CoinbaseRequestError, match="Invalid JSON"):
                client.get_product("BTC-USD")


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
    async def test_get_products_with_filters(
        self,
        test_credentials: tuple[str, str],
        sample_products_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting products with filters asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_products_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            products = await client.get_products(product_type="SPOT", limit=10)

        assert len(products) == 2

    @pytest.mark.asyncio
    async def test_get_product(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single product asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            url="https://api.coinbase.com/api/v3/brokerage/products/ETH-USD",
            json={"product_id": "ETH-USD", "price": "3000.00"},
        )

        async with AsyncClient(key_name, key_secret) as client:
            product = await client.get_product("ETH-USD")

        assert product.product_id == "ETH-USD"
        assert product.price == "3000.00"

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
    async def test_get_accounts_with_cursor(
        self,
        test_credentials: tuple[str, str],
        sample_accounts_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting accounts with pagination cursor asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_accounts_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            accounts = await client.get_accounts(limit=50, cursor="next_page")

        assert len(accounts) == 2

    @pytest.mark.asyncio
    async def test_get_account(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single account asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json={
                "account": {
                    "uuid": "acc-123",
                    "name": "ETH Wallet",
                    "currency": "ETH",
                    "available_balance": {"value": "10.0", "currency": "ETH"},
                }
            },
        )

        async with AsyncClient(key_name, key_secret) as client:
            account = await client.get_account("acc-123")

        assert account.uuid == "acc-123"
        assert account.currency == "ETH"

    @pytest.mark.asyncio
    async def test_get_candles(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            candles = await client.get_candles("BTC-USD")

        assert len(candles) == 2

    @pytest.mark.asyncio
    async def test_get_candles_with_datetime(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles with datetime objects asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        now = datetime.now(timezone.utc)
        start = now - timedelta(days=1)

        async with AsyncClient(key_name, key_secret) as client:
            candles = await client.get_candles("BTC-USD", start=start, end=now)

        assert len(candles) == 2

    @pytest.mark.asyncio
    async def test_get_candles_with_timestamps(
        self,
        test_credentials: tuple[str, str],
        sample_candles_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting candles with Unix timestamps asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_candles_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            candles = await client.get_candles(
                "BTC-USD",
                start=1704067200,
                end=1704153600,
                granularity="FIFTEEN_MINUTE",
            )

        assert len(candles) == 2

    @pytest.mark.asyncio
    async def test_get_market_trades(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting market trades asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json={
                "trades": [],
                "best_bid": "49000",
                "best_ask": "50000",
            },
        )

        async with AsyncClient(key_name, key_secret) as client:
            response = await client.get_market_trades("BTC-USD")

        assert response.best_bid == "49000"
        assert response.best_ask == "50000"

    @pytest.mark.asyncio
    async def test_create_order(
        self,
        test_credentials: tuple[str, str],
        sample_order_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test creating an order asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            json=sample_order_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            response = await client.create_order(
                product_id="BTC-USD",
                side=OrderSide.SELL,
                order_type="limit",
                size="0.01",
                price="55000.00",
            )

        assert response.success is True

    @pytest.mark.asyncio
    async def test_create_market_order(
        self,
        test_credentials: tuple[str, str],
        sample_order_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test creating a market order asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            json=sample_order_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            response = await client.create_order(
                product_id="BTC-USD",
                side="buy",
                order_type="market",
                size="50.00",
            )

        assert response.success is True

    @pytest.mark.asyncio
    async def test_create_order_requires_price_for_limit(
        self,
        test_credentials: tuple[str, str],
    ) -> None:
        """Test that limit orders require a price asynchronously."""
        key_name, key_secret = test_credentials

        async with AsyncClient(key_name, key_secret) as client:
            with pytest.raises(ValueError, match="price is required"):
                await client.create_order(
                    product_id="BTC-USD",
                    side="BUY",
                    order_type="limit",
                    size="0.001",
                )

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
    async def test_get_orders_with_filters(
        self,
        test_credentials: tuple[str, str],
        sample_orders_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting orders with filters asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_orders_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            orders = await client.get_orders(
                product_id="BTC-USD",
                order_status=["OPEN"],
                cursor="page_token",
            )

        assert len(orders) == 1

    @pytest.mark.asyncio
    async def test_get_order(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting a single order asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json={
                "order": {
                    "order_id": "order-abc",
                    "product_id": "ETH-USD",
                    "side": "SELL",
                    "status": "OPEN",
                }
            },
        )

        async with AsyncClient(key_name, key_secret) as client:
            order = await client.get_order("order-abc")

        assert order.order_id == "order-abc"
        assert order.status == "OPEN"

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
    async def test_get_fills_with_filters(
        self,
        test_credentials: tuple[str, str],
        sample_fills_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test getting fills with filters asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_fills_response,
        )

        async with AsyncClient(key_name, key_secret) as client:
            fills = await client.get_fills(
                order_id="order-123",
                product_id="BTC-USD",
                cursor="page",
            )

        assert len(fills) == 1

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

    @pytest.mark.asyncio
    async def test_cancel_single_order(
        self,
        test_credentials: tuple[str, str],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test cancelling a single order (string) asynchronously."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="POST",
            json={"results": [{"success": True, "order_id": "order-123"}]},
        )

        async with AsyncClient(key_name, key_secret) as client:
            response = await client.cancel_orders("order-123")

        assert response.results[0].success is True


class TestConvenienceFunctions:
    """Tests for convenience context manager functions."""

    def test_sync_client_function(
        self,
        test_credentials: tuple[str, str],
        sample_products_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test sync_client convenience function."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_products_response,
        )

        with sync_client(key_name, key_secret) as client:
            products = client.get_products()

        assert len(products) == 2

    @pytest.mark.asyncio
    async def test_async_client_function(
        self,
        test_credentials: tuple[str, str],
        sample_products_response: dict[str, Any],
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test async_client convenience function."""
        key_name, key_secret = test_credentials

        httpx_mock.add_response(
            method="GET",
            json=sample_products_response,
        )

        async with async_client(key_name, key_secret) as client:
            products = await client.get_products()

        assert len(products) == 2


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
                "error_details": "Product not found",
            },
        )

        assert error.status_code == 400
        assert error.error_code == "ERR_001"
        assert error.details == "Product not found"
        assert "INVALID_REQUEST" in error.message
        assert "Invalid product" in error.message

    def test_api_error_with_error_only(self) -> None:
        """Test CoinbaseAPIError with only error field."""
        error = CoinbaseAPIError(
            status_code=400,
            response_data={"error": "BAD_REQUEST"},
        )

        assert error.message == "BAD_REQUEST"

    def test_api_error_with_message_only(self) -> None:
        """Test CoinbaseAPIError with only message field."""
        error = CoinbaseAPIError(
            status_code=400,
            response_data={"message": "Something went wrong"},
        )

        assert error.message == "Something went wrong"

    def test_api_error_ignores_no_message_available(self) -> None:
        """Test that 'No message available' is ignored."""
        error = CoinbaseAPIError(
            status_code=400,
            response_data={"error": "ERROR", "message": "No message available"},
        )

        assert error.message == "ERROR"
        assert "No message available" not in error.message

    def test_api_error_without_response_data(self) -> None:
        """Test CoinbaseAPIError without response data."""
        error = CoinbaseAPIError(
            status_code=500,
            message="Internal server error",
        )

        assert error.status_code == 500
        assert error.message == "Internal server error"
        assert error.error_code is None

    def test_api_error_unknown(self) -> None:
        """Test CoinbaseAPIError with no error info."""
        error = CoinbaseAPIError(status_code=500, response_data={})

        assert error.message == "Unknown API error"

    def test_api_error_with_irrelevant_fields(self) -> None:
        """Test CoinbaseAPIError with response data but no error/message fields."""
        error = CoinbaseAPIError(
            status_code=500,
            response_data={"code": "ERR001", "error_details": "Some details"},
        )

        assert error.message == "Unknown API error"
        assert error.error_code == "ERR001"
        assert error.details == "Some details"

    def test_api_error_str(self) -> None:
        """Test CoinbaseAPIError string representation."""
        error = CoinbaseAPIError(
            status_code=400,
            response_data={"error": "BAD", "code": "ERR001"},
        )

        assert "400" in str(error)
        assert "ERR001" in str(error)
        assert "BAD" in str(error)

    def test_api_error_repr(self) -> None:
        """Test CoinbaseAPIError repr."""
        error = CoinbaseAPIError(
            status_code=400,
            response_data={"error": "BAD", "code": "ERR001"},
        )

        repr_str = repr(error)
        assert "CoinbaseAPIError" in repr_str
        assert "400" in repr_str

    def test_request_error(self) -> None:
        """Test CoinbaseRequestError."""
        original = ValueError("Bad value")
        error = CoinbaseRequestError("Request failed", original_error=original)

        assert "Request failed" in str(error)
        assert error.original_error is original
        assert "ValueError" in str(error)

    def test_request_error_without_original(self) -> None:
        """Test CoinbaseRequestError without original error."""
        error = CoinbaseRequestError("Something failed")

        assert "Something failed" in str(error)
        assert error.original_error is None

    def test_request_error_repr(self) -> None:
        """Test CoinbaseRequestError repr."""
        error = CoinbaseRequestError("Failed", original_error=ValueError("oops"))

        repr_str = repr(error)
        assert "CoinbaseRequestError" in repr_str
        assert "Failed" in repr_str

    def test_auth_error(self) -> None:
        """Test CoinbaseAuthError."""
        error = CoinbaseAuthError("Invalid API key")

        assert "Invalid API key" in str(error)
        assert error.message == "Invalid API key"
