"""Coinbase Advanced Trade API Python Client.

A modern, async-first Python client for the Coinbase Advanced Trade API.

Example:
    Synchronous usage::

        from cbadvanced import Client

        with Client(key="your-key", secret="your-secret") as client:
            products = client.get_products()
            for product in products:
                print(f"{product.product_id}: {product.price}")

    Asynchronous usage::

        import asyncio
        from cbadvanced import AsyncClient

        async def main():
            async with AsyncClient(key="your-key", secret="your-secret") as client:
                products = await client.get_products()
                for product in products:
                    print(f"{product.product_id}: {product.price}")

        asyncio.run(main())
"""

from cbadvanced.auth import CoinbaseAuth
from cbadvanced.client import AsyncClient, Client, async_client, sync_client
from cbadvanced.exceptions import (
    CoinbaseAPIError,
    CoinbaseAuthError,
    CoinbaseError,
    CoinbaseRequestError,
)
from cbadvanced.models import (
    Account,
    AccountsResponse,
    Balance,
    CancelOrderResult,
    CancelOrdersResponse,
    Candle,
    CandlesResponse,
    CreateOrderResponse,
    Fill,
    FillsResponse,
    Granularity,
    MarketTradesResponse,
    Order,
    OrderConfiguration,
    OrderSide,
    OrdersResponse,
    OrderStatus,
    OrderType,
    Product,
    ProductsResponse,
    ProductType,
    TimeInForce,
    Trade,
)

__version__ = "3.0.0"

__all__ = [
    # Version
    "__version__",
    # Clients
    "Client",
    "AsyncClient",
    "async_client",
    "sync_client",
    # Auth
    "CoinbaseAuth",
    # Exceptions
    "CoinbaseError",
    "CoinbaseAPIError",
    "CoinbaseAuthError",
    "CoinbaseRequestError",
    # Enums
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "TimeInForce",
    "Granularity",
    "ProductType",
    # Account Models
    "Account",
    "AccountsResponse",
    "Balance",
    # Product Models
    "Product",
    "ProductsResponse",
    "Candle",
    "CandlesResponse",
    "Trade",
    "MarketTradesResponse",
    # Order Models
    "Order",
    "OrdersResponse",
    "OrderConfiguration",
    "CreateOrderResponse",
    "CancelOrderResult",
    "CancelOrdersResponse",
    # Fill Models
    "Fill",
    "FillsResponse",
]
