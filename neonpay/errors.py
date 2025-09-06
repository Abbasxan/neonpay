"""
NEONPAY Error Classes
Comprehensive error handling for payment processing
"""


class NeonPayError(Exception):
    """
    Base exception class for NEONPAY library

    All NEONPAY-specific exceptions inherit from this class.
    """

    def __init__(self, message: str = "An unknown NeonPay error occurred") -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"[{self.__class__.__name__}] {self.message}"


class PaymentError(NeonPayError):
    """Payment processing error"""

    pass


class ConfigurationError(NeonPayError):
    """Configuration or setup error"""

    pass


class AdapterError(NeonPayError):
    """Bot library adapter error"""

    pass


class ValidationError(NeonPayError):
    """General data validation error"""

    pass


class PaymentValidationError(ValidationError):
    """Raised when payment-specific validation fails"""

    pass


# Legacy compatibility
StarsPaymentError = PaymentError


__all__ = [
    "NeonPayError",
    "PaymentError",
    "ConfigurationError",
    "AdapterError",
    "ValidationError",
    "PaymentValidationError",
    "StarsPaymentError",
]
