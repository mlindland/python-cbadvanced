"""Coinbase Advanced Trade API client.

This module provides both synchronous and asynchronous clients for interacting
with the Coinbase Advanced Trade API.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any

import httpx

from cbadvanced.auth import CoinbaseAuth
from cbadvanced.exceptions import CoinbaseAPIError, CoinbaseRequestError
from cbadvanced.models import (
    Account,
    AccountsResponse,
    CancelOrdersResponse,
    CandlesResponse,
    CreateOrderResponse,
    Fill,
    FillsResponse,
    Granularity,
    MarketTradesResponse,
    Order,
    OrderSide,
    OrdersResponse,
    Product,
    ProductsResponse,
)

if TYPE_CHECKING:
    pass


# ============================================================================
# Base Client
# ============================================================================


class BaseClient:
    """Base class with shared functionality for sync and async clients."""

    BASE_URL: str = "https://api.coinbase.com"
    API_VERSION: str = "/api/v3"
    DEFAULT_TIMEOUT: float = 30.0

    def __init__(self, key: str, secret: str, *, timeout: float | None = None) -> None:
        """Initialize the client.

        Args:
            key: Your Coinbase API key name.
            secret: Your Coinbase API secret (PEM-encoded private key).
            timeout: Request timeout in seconds (default: 30).
        """
        self._auth = CoinbaseAuth(key, secret)
        self._timeout = timeout or self.DEFAULT_TIMEOUT

    def _build_url(self, endpoint: str) -> str:
        """Build full URL for an endpoint."""
        return f"{self.BASE_URL}{self.API_VERSION}{endpoint}"

    def _get_headers(self, method: str, endpoint: str) -> dict[str, str]:
        """Get headers for a request, including auth."""
        path = f"{self.API_VERSION}{endpoint}"
        headers = self._auth.get_auth_headers(method, path)
        headers["Content-Type"] = "application/json"
        return headers

    @staticmethod
    def _handle_response(response: httpx.Response) -> dict[str, Any]:
        """Handle API response and raise appropriate exceptions.

        Args:
            response: The HTTP response object.

        Returns:
            Parsed JSON response data.

        Raises:
            CoinbaseAPIError: If the API returns an error response.
            CoinbaseRequestError: If the response cannot be parsed.
        """
        if not response.is_success:
            try:
                data = response.json()
            except Exception:
                data = None
            raise CoinbaseAPIError(
                status_code=response.status_code,
                response_data=data,
                message=response.text if not data else None,
            )

        try:
            return response.json()  # type: ignore[no-any-return]
        except Exception as e:
            raise CoinbaseRequestError(
                f"Invalid JSON response: {response.text[:200]}",
                original_error=e,
            ) from e


# ============================================================================
# Async Client
# ============================================================================


class AsyncClient(BaseClient):
    """Asynchronous client for the Coinbase Advanced Trade API.

    This client uses httpx for async HTTP requests and provides full
    type hints and Pydantic model responses.

    Example:
        >>> async with AsyncClient(key="...", secret="...") as client:
        ...     accounts = await client.get_accounts()
        ...     for account in accounts:
        ...         print(f"{account.currency}: {account.available_balance.value}")
    """

    def __init__(self, key: str, secret: str, *, timeout: float | None = None) -> None:
        """Initialize the async client.

        Args:
            key: Your Coinbase API key name.
            secret: Your Coinbase API secret (PEM-encoded private key).
            timeout: Request timeout in seconds (default: 30).
        """
        super().__init__(key, secret, timeout=timeout)
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> AsyncClient:
        """Enter async context manager."""
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request.

        Args:
            method: HTTP method.
            endpoint: API endpoint path.
            params: Query parameters.
            json_data: JSON body data.

        Returns:
            Parsed JSON response.
        """
        if self._client is None:
            raise CoinbaseRequestError("Client not initialized. Use 'async with' context manager.")

        url = self._build_url(endpoint)
        headers = self._get_headers(method, endpoint)

        response = await self._client.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json_data,
        )
        return self._handle_response(response)

    # ========================================================================
    # Account Methods
    # ========================================================================

    async def get_accounts(self, *, limit: int = 250, cursor: str | None = None) -> list[Account]:
        """Get all accounts for the authenticated user.

        Args:
            limit: Maximum number of accounts to return (default: 250, max: 250).
            cursor: Pagination cursor for fetching next page.

        Returns:
            List of Account objects.
        """
        params: dict[str, Any] = {"limit": str(limit)}
        if cursor:
            params["cursor"] = cursor

        data = await self._request("GET", "/brokerage/accounts", params=params)
        response = AccountsResponse.model_validate(data)
        return response.accounts

    async def get_account(self, account_id: str) -> Account:
        """Get a specific account by ID.

        Args:
            account_id: The UUID of the account.

        Returns:
            Account object.
        """
        data = await self._request("GET", f"/brokerage/accounts/{account_id}")
        return Account.model_validate(data.get("account", data))

    # ========================================================================
    # Product Methods
    # ========================================================================

    async def get_products(
        self,
        *,
        product_type: str | None = None,
        limit: int | None = None,
    ) -> list[Product]:
        """Get all available products.

        Args:
            product_type: Filter by product type (e.g., "SPOT").
            limit: Maximum number of products to return.

        Returns:
            List of Product objects.
        """
        params: dict[str, Any] = {}
        if product_type:
            params["product_type"] = product_type
        if limit:
            params["limit"] = str(limit)

        data = await self._request("GET", "/brokerage/products", params=params or None)
        response = ProductsResponse.model_validate(data)
        return response.products

    async def get_product(self, product_id: str) -> Product:
        """Get a specific product by ID.

        Args:
            product_id: The product ID (e.g., "BTC-USD").

        Returns:
            Product object.
        """
        data = await self._request("GET", f"/brokerage/products/{product_id}")
        return Product.model_validate(data)

    async def get_candles(
        self,
        product_id: str,
        *,
        start: datetime | int | None = None,
        end: datetime | int | None = None,
        granularity: Granularity | str = Granularity.FIFTEEN_MINUTE,
    ) -> list[dict[str, Any]]:
        """Get historical candles for a product.

        Args:
            product_id: The product ID (e.g., "BTC-USD").
            start: Start time (datetime or Unix timestamp). Defaults to 24 hours ago.
            end: End time (datetime or Unix timestamp). Defaults to now.
            granularity: Candle granularity (default: FIFTEEN_MINUTE).

        Returns:
            List of candle data dictionaries.
        """
        now = datetime.now(timezone.utc)

        # Handle start time
        if start is None:
            start_ts = int((now - timedelta(hours=24)).timestamp())
        elif isinstance(start, datetime):
            start_ts = int(start.timestamp())
        else:
            start_ts = start

        # Handle end time
        if end is None:
            end_ts = int(now.timestamp())
        elif isinstance(end, datetime):
            end_ts = int(end.timestamp())
        else:
            end_ts = end

        # Handle granularity
        granularity_str = granularity.value if isinstance(granularity, Granularity) else granularity

        params = {
            "start": str(start_ts),
            "end": str(end_ts),
            "granularity": granularity_str,
        }

        data = await self._request(
            "GET", f"/brokerage/products/{product_id}/candles", params=params
        )
        response = CandlesResponse.model_validate(data)
        return [candle.model_dump() for candle in response.candles]

    async def get_market_trades(self, product_id: str, *, limit: int = 100) -> MarketTradesResponse:
        """Get recent market trades for a product.

        Args:
            product_id: The product ID (e.g., "BTC-USD").
            limit: Maximum number of trades to return (default: 100).

        Returns:
            MarketTradesResponse with trades and best bid/ask.
        """
        params = {"limit": str(limit)}
        data = await self._request("GET", f"/brokerage/products/{product_id}/ticker", params=params)
        return MarketTradesResponse.model_validate(data)

    # ========================================================================
    # Order Methods
    # ========================================================================

    async def create_order(
        self,
        product_id: str,
        side: OrderSide | str,
        *,
        order_type: str = "limit",
        size: str | None = None,
        price: str | None = None,
        client_order_id: str | None = None,
        **kwargs: Any,
    ) -> CreateOrderResponse:
        """Create a new order.

        Args:
            product_id: The product ID (e.g., "BTC-USD").
            side: Order side (BUY or SELL).
            order_type: Order type ("market" or "limit", default: "limit").
            size: Order size (base currency for limit, quote currency for market).
            price: Limit price (required for limit orders).
            client_order_id: Optional client-specified order ID.
            **kwargs: Additional order parameters.

        Returns:
            CreateOrderResponse with order details.
        """
        if client_order_id is None:
            client_order_id = str(uuid.uuid4())

        # Normalize side
        side_str = side.value if isinstance(side, OrderSide) else side.upper()

        # Build order configuration based on type
        if order_type.lower() == "market":
            order_config = {"market_market_ioc": {"quote_size": str(size)}}
        else:
            if price is None:
                raise ValueError("price is required for limit orders")
            order_config = {
                "limit_limit_gtc": {
                    "base_size": str(size),
                    "limit_price": str(price),
                }
            }

        payload = {
            "product_id": product_id,
            "side": side_str,
            "client_order_id": client_order_id,
            "order_configuration": order_config,
            **kwargs,
        }

        data = await self._request("POST", "/brokerage/orders", json_data=payload)
        return CreateOrderResponse.model_validate(data)

    async def cancel_orders(self, order_ids: str | list[str]) -> CancelOrdersResponse:
        """Cancel one or more orders.

        Args:
            order_ids: Single order ID or list of order IDs to cancel.

        Returns:
            CancelOrdersResponse with cancellation results.
        """
        if isinstance(order_ids, str):
            order_ids = [order_ids]

        payload = {"order_ids": order_ids}
        data = await self._request("POST", "/brokerage/orders/batch_cancel", json_data=payload)
        return CancelOrdersResponse.model_validate(data)

    async def get_orders(
        self,
        *,
        product_id: str | None = None,
        order_status: list[str] | None = None,
        limit: int = 100,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> list[Order]:
        """Get historical orders.

        Args:
            product_id: Filter by product ID.
            order_status: Filter by order status (e.g., ["OPEN", "FILLED"]).
            limit: Maximum number of orders to return.
            cursor: Pagination cursor.
            **kwargs: Additional filter parameters.

        Returns:
            List of Order objects.
        """
        params: dict[str, Any] = {"limit": str(limit), **kwargs}
        if product_id:
            params["product_id"] = product_id
        if order_status:
            params["order_status"] = order_status
        if cursor:
            params["cursor"] = cursor

        data = await self._request("GET", "/brokerage/orders/historical/batch", params=params)
        response = OrdersResponse.model_validate(data)
        return response.orders

    async def get_order(self, order_id: str) -> Order:
        """Get a specific order by ID.

        Args:
            order_id: The order ID.

        Returns:
            Order object.
        """
        data = await self._request("GET", f"/brokerage/orders/historical/{order_id}")
        return Order.model_validate(data.get("order", data))

    # ========================================================================
    # Fill Methods
    # ========================================================================

    async def get_fills(
        self,
        *,
        order_id: str | None = None,
        product_id: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> list[Fill]:
        """Get historical fills (executed trades).

        Args:
            order_id: Filter by order ID.
            product_id: Filter by product ID.
            limit: Maximum number of fills to return.
            cursor: Pagination cursor.
            **kwargs: Additional filter parameters.

        Returns:
            List of Fill objects.
        """
        params: dict[str, Any] = {"limit": str(limit), **kwargs}
        if order_id:
            params["order_id"] = order_id
        if product_id:
            params["product_id"] = product_id
        if cursor:
            params["cursor"] = cursor

        data = await self._request("GET", "/brokerage/orders/historical/fills", params=params)
        response = FillsResponse.model_validate(data)
        return response.fills


# ============================================================================
# Sync Client
# ============================================================================


class Client(BaseClient):
    """Synchronous client for the Coinbase Advanced Trade API.

    This client uses httpx for HTTP requests and provides full
    type hints and Pydantic model responses.

    Example:
        >>> with Client(key="...", secret="...") as client:
        ...     accounts = client.get_accounts()
        ...     for account in accounts:
        ...         print(f"{account.currency}: {account.available_balance.value}")
    """

    def __init__(self, key: str, secret: str, *, timeout: float | None = None) -> None:
        """Initialize the sync client.

        Args:
            key: Your Coinbase API key name.
            secret: Your Coinbase API secret (PEM-encoded private key).
            timeout: Request timeout in seconds (default: 30).
        """
        super().__init__(key, secret, timeout=timeout)
        self._client: httpx.Client | None = None

    def __enter__(self) -> Client:
        """Enter context manager."""
        self._client = httpx.Client(timeout=self._timeout)
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit context manager."""
        if self._client:
            self._client.close()
            self._client = None

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an authenticated API request."""
        if self._client is None:
            raise CoinbaseRequestError("Client not initialized. Use 'with' context manager.")

        url = self._build_url(endpoint)
        headers = self._get_headers(method, endpoint)

        response = self._client.request(
            method,
            url,
            headers=headers,
            params=params,
            json=json_data,
        )
        return self._handle_response(response)

    # ========================================================================
    # Account Methods
    # ========================================================================

    def get_accounts(self, *, limit: int = 250, cursor: str | None = None) -> list[Account]:
        """Get all accounts for the authenticated user."""
        params: dict[str, Any] = {"limit": str(limit)}
        if cursor:
            params["cursor"] = cursor

        data = self._request("GET", "/brokerage/accounts", params=params)
        response = AccountsResponse.model_validate(data)
        return response.accounts

    def get_account(self, account_id: str) -> Account:
        """Get a specific account by ID."""
        data = self._request("GET", f"/brokerage/accounts/{account_id}")
        return Account.model_validate(data.get("account", data))

    # ========================================================================
    # Product Methods
    # ========================================================================

    def get_products(
        self,
        *,
        product_type: str | None = None,
        limit: int | None = None,
    ) -> list[Product]:
        """Get all available products."""
        params: dict[str, Any] = {}
        if product_type:
            params["product_type"] = product_type
        if limit:
            params["limit"] = str(limit)

        data = self._request("GET", "/brokerage/products", params=params or None)
        response = ProductsResponse.model_validate(data)
        return response.products

    def get_product(self, product_id: str) -> Product:
        """Get a specific product by ID."""
        data = self._request("GET", f"/brokerage/products/{product_id}")
        return Product.model_validate(data)

    def get_candles(
        self,
        product_id: str,
        *,
        start: datetime | int | None = None,
        end: datetime | int | None = None,
        granularity: Granularity | str = Granularity.FIFTEEN_MINUTE,
    ) -> list[dict[str, Any]]:
        """Get historical candles for a product."""
        now = datetime.now(timezone.utc)

        if start is None:
            start_ts = int((now - timedelta(hours=24)).timestamp())
        elif isinstance(start, datetime):
            start_ts = int(start.timestamp())
        else:
            start_ts = start

        if end is None:
            end_ts = int(now.timestamp())
        elif isinstance(end, datetime):
            end_ts = int(end.timestamp())
        else:
            end_ts = end

        granularity_str = granularity.value if isinstance(granularity, Granularity) else granularity

        params = {
            "start": str(start_ts),
            "end": str(end_ts),
            "granularity": granularity_str,
        }

        data = self._request("GET", f"/brokerage/products/{product_id}/candles", params=params)
        response = CandlesResponse.model_validate(data)
        return [candle.model_dump() for candle in response.candles]

    def get_market_trades(self, product_id: str, *, limit: int = 100) -> MarketTradesResponse:
        """Get recent market trades for a product."""
        params = {"limit": str(limit)}
        data = self._request("GET", f"/brokerage/products/{product_id}/ticker", params=params)
        return MarketTradesResponse.model_validate(data)

    # ========================================================================
    # Order Methods
    # ========================================================================

    def create_order(
        self,
        product_id: str,
        side: OrderSide | str,
        *,
        order_type: str = "limit",
        size: str | None = None,
        price: str | None = None,
        client_order_id: str | None = None,
        **kwargs: Any,
    ) -> CreateOrderResponse:
        """Create a new order."""
        if client_order_id is None:
            client_order_id = str(uuid.uuid4())

        side_str = side.value if isinstance(side, OrderSide) else side.upper()

        if order_type.lower() == "market":
            order_config = {"market_market_ioc": {"quote_size": str(size)}}
        else:
            if price is None:
                raise ValueError("price is required for limit orders")
            order_config = {
                "limit_limit_gtc": {
                    "base_size": str(size),
                    "limit_price": str(price),
                }
            }

        payload = {
            "product_id": product_id,
            "side": side_str,
            "client_order_id": client_order_id,
            "order_configuration": order_config,
            **kwargs,
        }

        data = self._request("POST", "/brokerage/orders", json_data=payload)
        return CreateOrderResponse.model_validate(data)

    def cancel_orders(self, order_ids: str | list[str]) -> CancelOrdersResponse:
        """Cancel one or more orders."""
        if isinstance(order_ids, str):
            order_ids = [order_ids]

        payload = {"order_ids": order_ids}
        data = self._request("POST", "/brokerage/orders/batch_cancel", json_data=payload)
        return CancelOrdersResponse.model_validate(data)

    def get_orders(
        self,
        *,
        product_id: str | None = None,
        order_status: list[str] | None = None,
        limit: int = 100,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> list[Order]:
        """Get historical orders."""
        params: dict[str, Any] = {"limit": str(limit), **kwargs}
        if product_id:
            params["product_id"] = product_id
        if order_status:
            params["order_status"] = order_status
        if cursor:
            params["cursor"] = cursor

        data = self._request("GET", "/brokerage/orders/historical/batch", params=params)
        response = OrdersResponse.model_validate(data)
        return response.orders

    def get_order(self, order_id: str) -> Order:
        """Get a specific order by ID."""
        data = self._request("GET", f"/brokerage/orders/historical/{order_id}")
        return Order.model_validate(data.get("order", data))

    # ========================================================================
    # Fill Methods
    # ========================================================================

    def get_fills(
        self,
        *,
        order_id: str | None = None,
        product_id: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
        **kwargs: Any,
    ) -> list[Fill]:
        """Get historical fills (executed trades)."""
        params: dict[str, Any] = {"limit": str(limit), **kwargs}
        if order_id:
            params["order_id"] = order_id
        if product_id:
            params["product_id"] = product_id
        if cursor:
            params["cursor"] = cursor

        data = self._request("GET", "/brokerage/orders/historical/fills", params=params)
        response = FillsResponse.model_validate(data)
        return response.fills


# ============================================================================
# Convenience Functions
# ============================================================================


@asynccontextmanager
async def async_client(key: str, secret: str, **kwargs: Any) -> AsyncIterator[AsyncClient]:
    """Create an async client as a context manager.

    Example:
        >>> async with async_client(key="...", secret="...") as client:
        ...     products = await client.get_products()
    """
    client = AsyncClient(key, secret, **kwargs)
    async with client:
        yield client


@contextmanager
def sync_client(key: str, secret: str, **kwargs: Any) -> Iterator[Client]:
    """Create a sync client as a context manager.

    Example:
        >>> with sync_client(key="...", secret="...") as client:
        ...     products = client.get_products()
    """
    client = Client(key, secret, **kwargs)
    with client:
        yield client
