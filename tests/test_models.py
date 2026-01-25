"""Tests for Pydantic models."""

from __future__ import annotations

from decimal import Decimal

from cbadvanced.models import (
    Account,
    AccountsResponse,
    Balance,
    Candle,
    CandlesResponse,
    Granularity,
    Order,
    OrderSide,
    OrderStatus,
    Product,
    ProductsResponse,
)


class TestEnums:
    """Tests for enum types."""

    def test_order_side_values(self) -> None:
        """Test OrderSide enum values."""
        assert OrderSide.BUY.value == "BUY"
        assert OrderSide.SELL.value == "SELL"

    def test_order_status_values(self) -> None:
        """Test OrderStatus enum values."""
        assert OrderStatus.OPEN.value == "OPEN"
        assert OrderStatus.FILLED.value == "FILLED"
        assert OrderStatus.CANCELLED.value == "CANCELLED"

    def test_granularity_values(self) -> None:
        """Test Granularity enum values."""
        assert Granularity.ONE_MINUTE.value == "ONE_MINUTE"
        assert Granularity.FIFTEEN_MINUTE.value == "FIFTEEN_MINUTE"
        assert Granularity.ONE_HOUR.value == "ONE_HOUR"
        assert Granularity.ONE_DAY.value == "ONE_DAY"


class TestBalance:
    """Tests for Balance model."""

    def test_balance_creation(self) -> None:
        """Test Balance model creation."""
        balance = Balance(value="123.456", currency="BTC")

        assert balance.value == "123.456"
        assert balance.currency == "BTC"

    def test_balance_decimal_value(self) -> None:
        """Test Balance decimal_value property."""
        balance = Balance(value="123.456789", currency="BTC")

        assert balance.decimal_value == Decimal("123.456789")

    def test_balance_from_dict(self) -> None:
        """Test Balance creation from dict."""
        data = {"value": "1000.00", "currency": "USD"}
        balance = Balance.model_validate(data)

        assert balance.value == "1000.00"
        assert balance.currency == "USD"


class TestAccount:
    """Tests for Account model."""

    def test_account_creation(self) -> None:
        """Test Account model creation."""
        account = Account(
            uuid="test-uuid-123",
            name="BTC Wallet",
            currency="BTC",
            available_balance=Balance(value="1.5", currency="BTC"),
            default=True,
            active=True,
        )

        assert account.uuid == "test-uuid-123"
        assert account.currency == "BTC"
        assert account.available_balance.value == "1.5"

    def test_account_from_api_response(self, sample_accounts_response: dict) -> None:
        """Test Account parsing from API response."""
        response = AccountsResponse.model_validate(sample_accounts_response)

        assert len(response.accounts) == 2
        assert response.accounts[0].currency == "BTC"
        assert response.accounts[0].available_balance.decimal_value == Decimal("1.23")


class TestProduct:
    """Tests for Product model."""

    def test_product_creation(self) -> None:
        """Test Product model creation."""
        product = Product(
            product_id="BTC-USD",
            price="50000.00",
            base_name="Bitcoin",
            quote_name="US Dollar",
        )

        assert product.product_id == "BTC-USD"
        assert product.price == "50000.00"

    def test_product_from_api_response(self, sample_products_response: dict) -> None:
        """Test Product parsing from API response."""
        response = ProductsResponse.model_validate(sample_products_response)

        assert len(response.products) == 2
        assert response.products[0].product_id == "BTC-USD"
        assert response.products[0].base_name == "Bitcoin"

    def test_product_allows_extra_fields(self) -> None:
        """Test that Product allows extra fields from API."""
        data = {
            "product_id": "BTC-USD",
            "price": "50000.00",
            "some_new_field": "new_value",  # API might add new fields
        }
        product = Product.model_validate(data)

        assert product.product_id == "BTC-USD"


class TestCandle:
    """Tests for Candle model."""

    def test_candle_creation(self) -> None:
        """Test Candle model creation."""
        candle = Candle(
            start="1704067200",
            low="49500.00",
            high="50500.00",
            open="50000.00",
            close="50200.00",
            volume="100.5",
        )

        assert candle.start == "1704067200"
        assert candle.open == "50000.00"

    def test_candle_start_timestamp(self) -> None:
        """Test Candle start_timestamp property."""
        candle = Candle(
            start="1704067200",
            low="49500.00",
            high="50500.00",
            open="50000.00",
            close="50200.00",
            volume="100.5",
        )

        assert candle.start_timestamp == 1704067200

    def test_candle_start_datetime(self) -> None:
        """Test Candle start_datetime property."""
        candle = Candle(
            start="1704067200",
            low="49500.00",
            high="50500.00",
            open="50000.00",
            close="50200.00",
            volume="100.5",
        )

        dt = candle.start_datetime
        assert dt.year == 2024
        assert dt.month == 1

    def test_candles_from_api_response(self, sample_candles_response: dict) -> None:
        """Test Candles parsing from API response."""
        response = CandlesResponse.model_validate(sample_candles_response)

        assert len(response.candles) == 2
        assert response.candles[0].open == "50000.00"


class TestOrder:
    """Tests for Order model."""

    def test_order_creation(self) -> None:
        """Test Order model creation."""
        order = Order(
            order_id="order-123",
            product_id="BTC-USD",
            side="BUY",
            status="FILLED",
            filled_size="0.001",
        )

        assert order.order_id == "order-123"
        assert order.side == "BUY"
        assert order.status == "FILLED"

    def test_order_from_api_response(self, sample_orders_response: dict) -> None:
        """Test Order parsing from API response."""
        from cbadvanced.models import OrdersResponse

        response = OrdersResponse.model_validate(sample_orders_response)

        assert len(response.orders) == 1
        assert response.orders[0].order_id == "order-123-456"
        assert response.orders[0].status == "FILLED"
