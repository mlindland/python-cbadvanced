# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-01-25

### Changed

- **BREAKING**: Complete rewrite with modern Python patterns
- **BREAKING**: Switched from `requests` to `httpx` for HTTP client
- **BREAKING**: All API methods now require context manager usage (`with`/`async with`)
- **BREAKING**: Renamed exception classes:
  - `AdvancedTradeAPIExceptions` → `CoinbaseAPIError`
  - `AdvancedTradeRequestException` → `CoinbaseRequestError`
- **BREAKING**: Method renames for consistency:
  - `list_products()` → `get_products()`
  - `list_orders()` → `get_orders()`
  - `list_fills()` → `get_fills()`
  - `get_product_candles()` → `get_candles()`
- Migrated from `setup.py` to `pyproject.toml` (PEP 517/518)
- Updated minimum Python version to 3.10

### Added

- Full async support with `AsyncClient`
- Complete type hints throughout the codebase
- Pydantic models for all API responses with validation
- `py.typed` marker for PEP 561 compliance
- New exception types: `CoinbaseError` (base), `CoinbaseAuthError`
- Enums for type-safe parameters: `OrderSide`, `OrderStatus`, `Granularity`, etc.
- Context manager support for proper resource cleanup
- Comprehensive test suite with pytest and pytest-httpx
- GitLab CI configuration

### Fixed

- Fixed bug where default timestamps in `get_candles()` were evaluated at import time
- Fixed bug in exception handling (`if 'error_details':` → `if 'error_details' in json_res:`)
- Fixed incorrect dependency: `jwt` → `PyJWT`
- Added missing runtime dependencies to package metadata

### Removed

- Removed `setup.py` (replaced by `pyproject.toml`)
- Removed `requirements.txt` (dependencies now in `pyproject.toml`)
- Removed old `cb_auth.py` (replaced by `auth.py`)

## [2.0.0] - 2023-XX-XX

### Changed

- Updated to Coinbase Advanced Trade API v3
- Switched to JWT-based authentication (ES256)

## [1.0.0] - Initial Release

- Initial release with basic Coinbase Pro API support
