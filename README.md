# cbadvanced

[![PyPI version](https://badge.fury.io/py/cbadvanced.svg)](https://badge.fury.io/py/cbadvanced)
[![Python versions](https://img.shields.io/pypi/pyversions/cbadvanced.svg)](https://pypi.org/project/cbadvanced/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, async-first Python client for the [Coinbase Advanced Trade API](https://docs.cdp.coinbase.com/advanced-trade/docs/welcome).

## Features

- **Async & Sync Support** - Both asynchronous and synchronous clients
- **Type Hints** - Full type annotations with Pydantic models
- **Modern Python** - Requires Python 3.10+, uses `httpx` for HTTP
- **Validated Responses** - All API responses are validated with Pydantic
- **Context Manager Support** - Proper resource management with `with`/`async with`

## Disclaimer

This is an **unofficial** library. I am in no way affiliated with Coinbase. Use at your own risk.

## Installation

```bash
pip install cbadvanced
```

Or with your preferred package manager:

```bash
# Using uv
uv add cbadvanced

# Using poetry
poetry add cbadvanced
```

## Quick Start

### Getting API Credentials

1. Go to [Coinbase Developer Platform](https://portal.cdp.coinbase.com/)
2. Create a new API key with "Advanced Trade" permissions
3. Save your API key name and private key (PEM format)

### Synchronous Usage

```python
from cbadvanced import Client

# Your API credentials
API_KEY = "organizations/your-org/apiKeys/your-key"
API_SECRET = """-----BEGIN EC PRIVATE KEY-----
YOUR PRIVATE KEY HERE
-----END EC PRIVATE KEY-----"""

with Client(key=API_KEY, secret=API_SECRET) as client:
    # Get all products
    products = client.get_products()
    for product in products:
        print(f"{product.product_id}: ${product.price}")

    # Get account balances
    accounts = client.get_accounts()
    for account in accounts:
        if float(account.available_balance.value) > 0:
            print(f"{account.currency}: {account.available_balance.value}")
```

### Asynchronous Usage

```python
import asyncio
from cbadvanced import AsyncClient

async def main():
    async with AsyncClient(key=API_KEY, secret=API_SECRET) as client:
        # Get BTC-USD price
        product = await client.get_product("BTC-USD")
        print(f"BTC-USD: ${product.price}")

        # Get recent candles
        candles = await client.get_candles("BTC-USD")
        for candle in candles[:5]:
            print(f"Open: {candle['open']}, Close: {candle['close']}")

asyncio.run(main())
```

## API Reference

### Client Initialization

Both `Client` and `AsyncClient` accept the same parameters:

```python
Client(
    key: str,           # API key name
    secret: str,        # PEM-encoded private key
    timeout: float = 30.0  # Request timeout in seconds
)
```

### Account Methods

```python
# Get all accounts (wallets)
accounts = client.get_accounts(limit=250, cursor=None)

# Get a specific account
account = client.get_account(account_id="your-account-uuid")
```

### Product Methods

```python
# Get all tradeable products
products = client.get_products(product_type="SPOT", limit=None)

# Get a specific product
product = client.get_product("BTC-USD")

# Get historical candles (OHLCV data)
from cbadvanced import Granularity
from datetime import datetime, timedelta

candles = client.get_candles(
    "BTC-USD",
    start=datetime.now() - timedelta(days=7),  # or Unix timestamp
    end=datetime.now(),                         # or Unix timestamp
    granularity=Granularity.ONE_HOUR
)

# Get recent market trades
trades = client.get_market_trades("BTC-USD", limit=100)
print(f"Best bid: {trades.best_bid}, Best ask: {trades.best_ask}")
```

### Order Methods

```python
from cbadvanced import OrderSide

# Create a limit order
response = client.create_order(
    product_id="BTC-USD",
    side=OrderSide.BUY,  # or "BUY"
    order_type="limit",
    size="0.001",        # Amount in base currency (BTC)
    price="50000.00"     # Limit price in quote currency (USD)
)

if response.success:
    print(f"Order created: {response.order_id}")

# Create a market order
response = client.create_order(
    product_id="BTC-USD",
    side=OrderSide.BUY,
    order_type="market",
    size="100.00"  # Amount in quote currency (USD) for market orders
)

# Get historical orders
orders = client.get_orders(
    product_id="BTC-USD",      # Optional: filter by product
    order_status=["FILLED"],   # Optional: filter by status
    limit=100
)

# Get a specific order
order = client.get_order("order-id-here")

# Cancel orders
result = client.cancel_orders(["order-id-1", "order-id-2"])
for r in result.results:
    print(f"Order {r.order_id}: {'Cancelled' if r.success else r.failure_reason}")
```

### Fill Methods

```python
# Get trade fills (executed orders)
fills = client.get_fills(
    product_id="BTC-USD",  # Optional
    order_id="order-123",  # Optional
    limit=100
)

for fill in fills:
    print(f"Trade {fill.trade_id}: {fill.size} @ ${fill.price}")
```

## Models & Enums

All API responses are validated and returned as Pydantic models:

```python
from cbadvanced import (
    # Enums
    OrderSide,      # BUY, SELL
    OrderStatus,    # PENDING, OPEN, FILLED, CANCELLED, EXPIRED, FAILED
    OrderType,      # MARKET, LIMIT, STOP, STOP_LIMIT
    Granularity,    # ONE_MINUTE, FIVE_MINUTE, FIFTEEN_MINUTE, etc.
    TimeInForce,    # GTC, GTD, IOC, FOK

    # Account models
    Account,
    Balance,

    # Product models
    Product,
    Candle,
    Trade,

    # Order models
    Order,
    CreateOrderResponse,
    CancelOrdersResponse,

    # Fill models
    Fill,
)
```

## Error Handling

The library provides specific exception types:

```python
from cbadvanced import (
    CoinbaseError,        # Base exception
    CoinbaseAPIError,     # API returned an error (4xx, 5xx)
    CoinbaseAuthError,    # Authentication failed
    CoinbaseRequestError, # Request/network error
)

try:
    product = client.get_product("INVALID-PRODUCT")
except CoinbaseAPIError as e:
    print(f"API Error {e.status_code}: {e.message}")
    print(f"Error code: {e.error_code}")
    print(f"Details: {e.details}")
except CoinbaseRequestError as e:
    print(f"Request failed: {e.message}")
```

## Configuration

### Environment Variables

Store your credentials securely using environment variables:

```python
import os
from cbadvanced import Client

with Client(
    key=os.environ["COINBASE_API_KEY"],
    secret=os.environ["COINBASE_API_SECRET"]
) as client:
    ...
```

### Timeout Configuration

```python
# Set a custom timeout (in seconds)
with Client(key=API_KEY, secret=API_SECRET, timeout=60.0) as client:
    ...
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mlindland/python-cbadvanced.git
cd python-cbadvanced

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cbadvanced

# Run specific test file
pytest tests/test_client.py
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy cbadvanced
```

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE.md) file for details.

## Links

- [PyPI Package](https://pypi.org/project/cbadvanced/)
- [GitHub Repository](https://github.com/mlindland/python-cbadvanced)
- [Coinbase Advanced Trade API Docs](https://docs.cdp.coinbase.com/advanced-trade/docs/welcome)
