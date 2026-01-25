"""Pydantic models for Coinbase Advanced Trade API responses.

This module provides type-safe models for API request and response data,
ensuring proper validation and serialization.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ============================================================================
# Enums
# ============================================================================


class OrderSide(str, Enum):
    """Order side (buy or sell)."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    """Order status."""

    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN_ORDER_STATUS"


class TimeInForce(str, Enum):
    """Time in force for orders."""

    GTC = "GOOD_UNTIL_CANCELLED"
    GTD = "GOOD_UNTIL_DATE"
    IOC = "IMMEDIATE_OR_CANCEL"
    FOK = "FILL_OR_KILL"


class Granularity(str, Enum):
    """Candle granularity options."""

    ONE_MINUTE = "ONE_MINUTE"
    FIVE_MINUTE = "FIVE_MINUTE"
    FIFTEEN_MINUTE = "FIFTEEN_MINUTE"
    THIRTY_MINUTE = "THIRTY_MINUTE"
    ONE_HOUR = "ONE_HOUR"
    TWO_HOUR = "TWO_HOUR"
    SIX_HOUR = "SIX_HOUR"
    ONE_DAY = "ONE_DAY"


class ProductType(str, Enum):
    """Product type."""

    SPOT = "SPOT"
    FUTURE = "FUTURE"


# ============================================================================
# Base Models
# ============================================================================


class CoinbaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        extra="allow",  # Allow extra fields from API
    )


# ============================================================================
# Account Models
# ============================================================================


class Account(CoinbaseModel):
    """Represents a Coinbase account."""

    uuid: str
    name: str
    currency: str
    available_balance: Balance
    default: bool = False
    active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None
    type: str | None = None
    ready: bool = True
    hold: Balance | None = None


class Balance(CoinbaseModel):
    """Represents a balance amount."""

    value: str
    currency: str

    @property
    def decimal_value(self) -> Decimal:
        """Get the balance as a Decimal."""
        return Decimal(self.value)


class AccountsResponse(CoinbaseModel):
    """Response for list accounts endpoint."""

    accounts: list[Account]
    has_next: bool = False
    cursor: str | None = None
    size: int | None = None


# ============================================================================
# Product Models
# ============================================================================


class Product(CoinbaseModel):
    """Represents a tradeable product."""

    product_id: str
    price: str | None = None
    price_percentage_change_24h: str | None = None
    volume_24h: str | None = None
    volume_percentage_change_24h: str | None = None
    base_increment: str | None = None
    quote_increment: str | None = None
    quote_min_size: str | None = None
    quote_max_size: str | None = None
    base_min_size: str | None = None
    base_max_size: str | None = None
    base_name: str | None = None
    quote_name: str | None = None
    watched: bool = False
    is_disabled: bool = False
    new: bool = False
    status: str | None = None
    cancel_only: bool = False
    limit_only: bool = False
    post_only: bool = False
    trading_disabled: bool = False
    auction_mode: bool = False
    product_type: str | None = None
    quote_currency_id: str | None = None
    base_currency_id: str | None = None
    base_display_symbol: str | None = None
    quote_display_symbol: str | None = None


class ProductsResponse(CoinbaseModel):
    """Response for list products endpoint."""

    products: list[Product]
    num_products: int | None = None


# ============================================================================
# Candle Models
# ============================================================================


class Candle(CoinbaseModel):
    """Represents a price candle (OHLCV)."""

    start: str
    low: str
    high: str
    open: str = Field(alias="open")
    close: str
    volume: str

    @property
    def start_timestamp(self) -> int:
        """Get the start time as a Unix timestamp."""
        return int(self.start)

    @property
    def start_datetime(self) -> datetime:
        """Get the start time as a UTC datetime."""
        from datetime import timezone

        return datetime.fromtimestamp(int(self.start), tz=timezone.utc)


class CandlesResponse(CoinbaseModel):
    """Response for get candles endpoint."""

    candles: list[Candle]


# ============================================================================
# Order Models
# ============================================================================


class OrderConfiguration(CoinbaseModel):
    """Order configuration details."""

    market_market_ioc: dict[str, Any] | None = None
    limit_limit_gtc: dict[str, Any] | None = None
    limit_limit_gtd: dict[str, Any] | None = None
    stop_limit_stop_limit_gtc: dict[str, Any] | None = None
    stop_limit_stop_limit_gtd: dict[str, Any] | None = None


class Order(CoinbaseModel):
    """Represents an order."""

    order_id: str
    product_id: str
    side: str
    client_order_id: str | None = None
    status: str | None = None
    time_in_force: str | None = None
    created_time: datetime | None = None
    completion_percentage: str | None = None
    filled_size: str | None = None
    average_filled_price: str | None = None
    fee: str | None = None
    number_of_fills: str | None = None
    filled_value: str | None = None
    pending_cancel: bool = False
    size_in_quote: bool = False
    total_fees: str | None = None
    size_inclusive_of_fees: bool = False
    total_value_after_fees: str | None = None
    trigger_status: str | None = None
    order_type: str | None = None
    reject_reason: str | None = None
    settled: bool = False
    product_type: str | None = None
    reject_message: str | None = None
    cancel_message: str | None = None
    order_configuration: OrderConfiguration | None = None


class CreateOrderResponse(CoinbaseModel):
    """Response for create order endpoint."""

    success: bool
    order_id: str | None = None
    success_response: dict[str, Any] | None = None
    failure_reason: str | None = None
    error_response: dict[str, Any] | None = None
    order_configuration: OrderConfiguration | None = None


class OrdersResponse(CoinbaseModel):
    """Response for list orders endpoint."""

    orders: list[Order]
    has_next: bool = False
    cursor: str | None = None
    sequence: str | None = None


class CancelOrderResult(CoinbaseModel):
    """Result of cancelling a single order."""

    success: bool
    order_id: str
    failure_reason: str | None = None


class CancelOrdersResponse(CoinbaseModel):
    """Response for cancel orders endpoint."""

    results: list[CancelOrderResult]


# ============================================================================
# Fill Models
# ============================================================================


class Fill(CoinbaseModel):
    """Represents a trade fill."""

    entry_id: str
    trade_id: str
    order_id: str
    trade_time: datetime | None = None
    trade_type: str | None = None
    price: str
    size: str
    commission: str | None = None
    product_id: str
    sequence_timestamp: datetime | None = None
    liquidity_indicator: str | None = None
    size_in_quote: bool = False
    user_id: str | None = None
    side: str | None = None


class FillsResponse(CoinbaseModel):
    """Response for list fills endpoint."""

    fills: list[Fill]
    cursor: str | None = None


# ============================================================================
# Market Trades Models
# ============================================================================


class Trade(CoinbaseModel):
    """Represents a market trade."""

    trade_id: str
    product_id: str
    price: str
    size: str
    time: datetime | None = None
    side: str | None = None
    bid: str | None = None
    ask: str | None = None


class MarketTradesResponse(CoinbaseModel):
    """Response for get market trades endpoint."""

    trades: list[Trade]
    best_bid: str | None = None
    best_ask: str | None = None
