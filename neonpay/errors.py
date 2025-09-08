"""
NEONPAY Error Classes
Comprehensive error handling for payment processing
"""

from typing import Any, Dict, Optional, Type
from enum import Enum


# допустимые номиналы для Telegram Stars
ALLOWED_STAR_AMOUNTS = [1, 5, 10, 50, 100, 200, 500]


class ErrorCode(str, Enum):
    """standardized error codes for neonpay"""

    unknown_error = "unknown_error"
    payment_error = "payment_error"
    config_error = "config_error"
    adapter_error = "adapter_error"
    validation_error = "validation_error"
    payment_validation_error = "payment_validation_error"


class NeonPayError(Exception):
    """base exception class for neonpay library"""

    def __init__(
        self,
        message: str = "an unknown neonpay error occurred",
        code: ErrorCode = ErrorCode.unknown_error,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        base = f"[{self.__class__.__name__}] {self.message}"
        if self.code:
            base += f" (code={self.code.value})"
        if self.details:
            base += f" | details={self.details}"
        return base


class PaymentError(NeonPayError):
    """payment processing error"""

    def __init__(
        self,
        message: str,
        transaction_id: Optional[str] = None,
        amount: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        # запрещаем дробные суммы
        if amount is not None and not isinstance(amount, int):
            raise PaymentValidationError(
                field="amount",
                message=f"invalid amount {amount}, must be integer (valid examples: {ALLOWED_STAR_AMOUNTS})",
                amount=amount,
            )

        details = {"transaction_id": transaction_id, "amount": amount, **kwargs}
        super().__init__(message, code=ErrorCode.payment_error, details=details)
        self.transaction_id = transaction_id
        self.amount = amount


class ConfigurationError(NeonPayError):
    """configuration or setup error"""

    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, code=ErrorCode.config_error, details=kwargs)


class AdapterError(NeonPayError):
    """bot library adapter error"""

    def __init__(self, message: str, adapter: Optional[str] = None, **kwargs: Any) -> None:
        details = {"adapter": adapter, **kwargs}
        super().__init__(message, code=ErrorCode.adapter_error, details=details)
        self.adapter = adapter


class ValidationError(NeonPayError):
    """general data validation error"""

    def __init__(self, field: Optional[str], message: str, **kwargs: Any) -> None:
        details = {"field": field, **kwargs}
        super().__init__(message, code=ErrorCode.validation_error, details=details)
        self.field = field


class PaymentValidationError(ValidationError):
    """raised when payment-specific validation fails"""

    def __init__(self, field: Optional[str] = None, message: Optional[str] = None, **kwargs: Any) -> None:
        # поддержка короткого вызова: только message
        if message is None and isinstance(field, str) and not kwargs:
            message = field
            field = None

        super().__init__(field, message or "invalid payment data", **kwargs)
        self.code = ErrorCode.payment_validation_error


# mapping codes to classes (for raise_error)
_ERROR_MAP: Dict[ErrorCode, Type[NeonPayError]] = {
    ErrorCode.payment_error: PaymentError,
    ErrorCode.config_error: ConfigurationError,
    ErrorCode.adapter_error: AdapterError,
    ErrorCode.validation_error: ValidationError,
    ErrorCode.payment_validation_error: PaymentValidationError,
    ErrorCode.unknown_error: NeonPayError,
}


def raise_error(code: ErrorCode, message: str, **kwargs: Any) -> None:
    """
    helper to raise the appropriate error by code.

    example:
        raise_error(ErrorCode.payment_error, "insufficient funds", transaction_id="TX123", amount=50)
    """
    error_class = _ERROR_MAP.get(code, NeonPayError)

    # доп. проверка для суммы, чтобы не пропустить float
    if code == ErrorCode.payment_error and "amount" in kwargs:
        amount = kwargs["amount"]
        if amount is not None and not isinstance(amount, int):
            raise PaymentValidationError(
                field="amount",
                message=f"invalid amount {amount}, must be integer (valid examples: {ALLOWED_STAR_AMOUNTS})",
                amount=amount,
            )

    raise error_class(message, **kwargs)


# legacy compatibility
StarsPaymentError = PaymentError


__all__ = [
    "ALLOWED_STAR_AMOUNTS",
    "ErrorCode",
    "NeonPayError",
    "PaymentError",
    "ConfigurationError",
    "AdapterError",
    "ValidationError",
    "PaymentValidationError",
    "StarsPaymentError",
    "raise_error",
]
