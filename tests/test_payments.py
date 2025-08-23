import pytest
from neon_stars_payments.errors import StarsPaymentError

def test_error_message():
    with pytest.raises(StarsPaymentError):
        raise StarsPaymentError("Тестовая ошибка")

  
