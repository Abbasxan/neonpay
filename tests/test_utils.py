import pytest

from neonpay.errors import PaymentValidationError, ALLOWED_STAR_AMOUNTS
from neonpay.utils import NeonPayLogger, PaymentHelper, PaymentValidator


class TestPaymentValidator:
    def test_validate_amount_success(self):
        # все допустимые суммы должны пройти валидацию
        for amount in ALLOWED_STAR_AMOUNTS:
            assert PaymentValidator.validate_amount(amount)

    def test_validate_amount_failure(self):
        # явно некорректные значения
        invalid_amounts = [0, -1, 2501, 1.5, "100"]

        for amt in invalid_amounts:
            with pytest.raises(PaymentValidationError):
                PaymentValidator.validate_amount(amt)

        # значение, не входящее в ALLOWED_STAR_AMOUNTS
        not_allowed = max(ALLOWED_STAR_AMOUNTS) + 1
        with pytest.raises(PaymentValidationError):
            PaymentValidator.validate_amount(not_allowed)

    def test_validate_stage_id_success(self):
        assert PaymentValidator.validate_stage_id("test_stage")
        assert PaymentValidator.validate_stage_id("stage-123")
        assert PaymentValidator.validate_stage_id("STAGE_ID")

    def test_validate_stage_id_failure(self):
        invalid_ids = ["", "stage with spaces", "stage@invalid", "a" * 65]
        for sid in invalid_ids:
            with pytest.raises(PaymentValidationError):
                PaymentValidator.validate_stage_id(sid)

    def test_validate_title_success(self):
        assert PaymentValidator.validate_title("Test Product")
        assert PaymentValidator.validate_title("A")

    def test_validate_title_failure(self):
        invalid_titles = ["", "A" * 33]
        for t in invalid_titles:
            with pytest.raises(PaymentValidationError):
                PaymentValidator.validate_title(t)

    def test_validate_logo_url_success(self):
        assert PaymentValidator.validate_logo_url(None)
        assert PaymentValidator.validate_logo_url("https://example.com/logo.png")
        assert PaymentValidator.validate_logo_url("http://localhost:8000/logo.jpg")

    def test_validate_logo_url_failure(self):
        invalid_urls = ["invalid-url", "ftp://example.com/logo.png"]
        for url in invalid_urls:
            with pytest.raises(PaymentValidationError):
                PaymentValidator.validate_logo_url(url)


class TestPaymentHelper:
    def test_format_stars_amount(self):
        assert PaymentHelper.format_stars_amount(1) == "1 ⭐"
        assert PaymentHelper.format_stars_amount(100) == "100 ⭐"
        assert PaymentHelper.format_stars_amount(2500) == "2500 ⭐"

    def test_calculate_fee(self):
        assert PaymentHelper.calculate_fee(100, 5.0) == pytest.approx(5.0)
        assert PaymentHelper.calculate_fee(100, 0.0) == pytest.approx(0.0)
        assert PaymentHelper.calculate_fee(1000, 2.5) == pytest.approx(25.0)

    def test_generate_payment_description(self):
        result = PaymentHelper.generate_payment_description("Test Product", 100)
        assert result == "Test Product - 100 ⭐"

    def test_extract_user_data(self):
        payment_data = {
            "user_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "other_field": "ignored",
        }

        result = PaymentHelper.extract_user_data(payment_data)
        expected = {
            "user_id": 12345,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
        }

        assert result == expected

    def test_is_test_payment(self):
        assert PaymentHelper.is_test_payment({"is_test": True})
        assert not PaymentHelper.is_test_payment({"is_test": False})
        assert not PaymentHelper.is_test_payment({})


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
