"""Custom exceptions for the Coinbase Advanced Trade API client.

This module provides specific exception types for handling API errors
and request failures.
"""

from __future__ import annotations

from typing import Any


class CoinbaseError(Exception):
    """Base exception for all Coinbase API errors."""

    pass


class CoinbaseAPIError(CoinbaseError):
    """Exception raised when the Coinbase API returns an error response.

    This exception captures detailed error information from API responses,
    including error codes, messages, and the original response data.

    Attributes:
        status_code: HTTP status code from the response.
        error_code: Coinbase-specific error code (if provided).
        message: Human-readable error message.
        details: Additional error details (if provided).
        response_data: The full response JSON data.

    Example:
        >>> try:
        ...     await client.get_account("invalid-id")
        ... except CoinbaseAPIError as e:
        ...     print(f"Error {e.status_code}: {e.message}")
    """

    def __init__(
        self,
        status_code: int,
        response_data: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> None:
        """Initialize the API error.

        Args:
            status_code: HTTP status code from the response.
            response_data: Parsed JSON response body (if available).
            message: Override message (used when response isn't JSON).
        """
        self.status_code = status_code
        self.response_data = response_data or {}
        self.error_code: str | None = None
        self.details: str | None = None

        # Extract error information from response
        if response_data:
            self.error_code = response_data.get("code")
            self.details = response_data.get("error_details")

            # Build message from response fields
            error_msg = response_data.get("error", "")
            api_message = response_data.get("message", "")

            if error_msg and api_message and api_message != "No message available":
                self.message = f"{error_msg} - {api_message}"
            elif error_msg:
                self.message = error_msg
            elif api_message and api_message != "No message available":
                self.message = api_message
            else:
                self.message = "Unknown API error"
        else:
            self.message = message or "Unknown API error"

        super().__init__(self.message)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        base = f"CoinbaseAPIError {self.status_code}: {self.message}"
        if self.error_code:
            base = f"CoinbaseAPIError {self.status_code} [{self.error_code}]: {self.message}"
        return base

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return (
            f"CoinbaseAPIError(status_code={self.status_code}, "
            f"error_code={self.error_code!r}, message={self.message!r})"
        )


class CoinbaseRequestError(CoinbaseError):
    """Exception raised for client-side request errors.

    This exception is raised when there's an issue with the request itself,
    such as network errors, timeout, or invalid response format.

    Attributes:
        message: Description of what went wrong.
        original_error: The underlying exception (if any).
    """

    def __init__(self, message: str, original_error: Exception | None = None) -> None:
        """Initialize the request error.

        Args:
            message: Description of the error.
            original_error: The underlying exception that caused this error.
        """
        self.message = message
        self.original_error = original_error
        super().__init__(message)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.original_error:
            return f"CoinbaseRequestError: {self.message} (caused by {type(self.original_error).__name__})"
        return f"CoinbaseRequestError: {self.message}"

    def __repr__(self) -> str:
        """Return a detailed representation of the error."""
        return f"CoinbaseRequestError(message={self.message!r}, original_error={self.original_error!r})"


class CoinbaseAuthError(CoinbaseError):
    """Exception raised for authentication-related errors.

    This includes invalid API keys, expired tokens, or permission issues.
    """

    def __init__(self, message: str) -> None:
        """Initialize the authentication error.

        Args:
            message: Description of the authentication error.
        """
        self.message = message
        super().__init__(message)

    def __str__(self) -> str:
        """Return a string representation of the error."""
        return f"CoinbaseAuthError: {self.message}"
