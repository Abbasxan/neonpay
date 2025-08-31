import pytest
from neonpay.utils import PaymentValidator, NeonPayLogger, PaymentHelper
from neonpay.errors import PaymentValidationError


class TestPaymentValidator:
    def test_validate_amount_success(self):
        assert PaymentValidator.validate_amount(1) is True
        assert PaymentValidator.validate_amount(100) is True
        assert PaymentValidator.validate_amount(2500) is True
    
    def test_validate_amount_failure(self):
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_amount(0)
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_amount(-1)
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_amount(2501)
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_amount("100")
    
    def test_validate_stage_id_success(self):
        assert PaymentValidator.validate_stage_id("test_stage") is True
        assert PaymentValidator.validate_stage_id("stage-123") is True
        assert PaymentValidator.validate_stage_id("STAGE_ID") is True
    
    def test_validate_stage_id_failure(self):
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_stage_id("")
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_stage_id("stage with spaces")
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_stage_id("stage@invalid")
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_stage_id("a" * 65)  # Too long
    
    def test_validate_title_success(self):
        assert PaymentValidator.validate_title("Test Product") is True
        assert PaymentValidator.validate_title("A") is True
    
    def test_validate_title_failure(self):
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_title("")
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_title("A" * 33)  # Too long
    
    def test_validate_logo_url_success(self):
        assert PaymentValidator.validate_logo_url(None) is True
        assert PaymentValidator.validate_logo_url("https://example.com/logo.png") is True
        assert PaymentValidator.validate_logo_url("http://localhost:8000/logo.jpg") is True
    
    def test_validate_logo_url_failure(self):
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_logo_url("invalid-url")
        
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_logo_url("ftp://example.com/logo.png")


class TestPaymentHelper:
    def test_format_stars_amount(self):
        assert PaymentHelper.format_stars_amount(1) == "1 ⭐"
        assert PaymentHelper.format_stars_amount(100) == "100 ⭐"
        assert PaymentHelper.format_stars_amount(2500) == "2500 ⭐"
    
    def test_calculate_fee(self):
        assert PaymentHelper.calculate_fee(100, 5.0) == 5
        assert PaymentHelper.calculate_fee(100, 0.0) == 0
        assert PaymentHelper.calculate_fee(1000, 2.5) == 25
    
    def test_generate_payment_description(self):
        result = PaymentHelper.generate_payment_description("Test Product", 100)
        assert result == "Test Product - 100 ⭐"
    
    def test_extract_user_data(self):
        payment_data = {
            "user_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "other_field": "ignored"
        }
        
        result = PaymentHelper.extract_user_data(payment_data)
        expected = {
            "user_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User"
        }
        
        assert result == expected
    
    def test_is_test_payment(self):
        assert PaymentHelper.is_test_payment({"is_test": True}) is True
        assert PaymentHelper.is_test_payment({"is_test": False}) is False
        assert PaymentHelper.is_test_payment({}) is False


class TestNeonPayLogger:
    def test_logger_creation(self):
        logger = NeonPayLogger("test_logger")
        assert logger.logger.name == "test_logger"
    
    def test_payment_logging_methods(self):
        logger = NeonPayLogger("test_logger")
        
        # Эти методы не должны вызывать ошибок
        logger.payment_sent(12345, "test_stage", 100)
        logger.payment_completed("pay_123", 12345, 100)
        logger.payment_failed(12345, "test_stage", "Test error")
