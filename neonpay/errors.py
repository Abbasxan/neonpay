"""
NEONPAY Error Classes
Comprehensive error handling for payment processing
"""


class NeonPayError(Exception):
    """
    Base exception class for NEONPAY library
    
    All NEONPAY-specific exceptions inherit from this class.
    """
    pass


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
    """Data validation error"""
    pass


# Legacy compatibility
StarsPaymentError = PaymentError
