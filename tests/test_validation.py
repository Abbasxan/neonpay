"""
Tests for NEONPAY validation and security features
"""

import hashlib
import hmac
import time
from unittest.mock import AsyncMock, Mock

import pytest

from neonpay.core import (
    NeonPayCore,
    PaymentResult,
    PaymentStage,
    validate_json_payload,
    validate_url,
)
from neonpay.webhooks import WebhookHandler, WebhookVerifier


class TestValidation:
    """Test validation functions"""

    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        assert validate_url("https://example.com")
        assert validate_url("http://example.com")
        assert validate_url("https://sub.example.com/path?param=value")

        # Invalid URLs
        assert not validate_url("")
        assert not validate_url("not-a-url")
        # FTP URLs are valid according to the current implementation
        assert validate_url("ftp://example.com")

        # HTTPS required
        assert validate_url("https://example.com", require_https=True)
        assert not validate_url("http://example.com", require_https=True)

    def test_validate_json_payload(self):
        """Test JSON payload validation"""
        # Valid payloads
        assert validate_json_payload({})
        assert validate_json_payload({"key": "value"})
        assert validate_json_payload({"nested": {"key": "value"}})

        # Invalid payloads
        assert not validate_json_payload("not-a-dict")
        assert not validate_json_payload(None)

        # Large payload (over 1024 bytes)
        large_payload = {"data": "x" * 1200}
        assert not validate_json_payload(large_payload)


class TestPaymentStageValidation:
    """Test PaymentStage validation"""

    def test_valid_payment_stage(self):
        stage = PaymentStage(
            title="Test Product", description="Test Description", price=100
        )
        assert stage.title == "Test Product"
        assert stage.price == 100

    def test_invalid_price(self):
        # Too low
        with pytest.raises(ValueError, match="between 1 and 2500"):
            PaymentStage(title="Test", description="Test", price=0)
        # Too high
        with pytest.raises(ValueError, match="between 1 and 2500"):
            PaymentStage(title="Test", description="Test", price=3000)
        # Wrong type
        with pytest.raises(ValueError, match="must be an integer"):
            PaymentStage(title="Test", description="Test", price="100")

    def test_invalid_title(self):
        with pytest.raises(ValueError, match="non-empty string"):
            PaymentStage(title="", description="Test", price=100)
        with pytest.raises(ValueError, match="32 characters or less"):
            PaymentStage(title="A" * 33, description="Test", price=100)

    def test_invalid_description(self):
        with pytest.raises(ValueError, match="non-empty string"):
            PaymentStage(title="Test", description="", price=100)
        with pytest.raises(ValueError, match="255 characters or less"):
            PaymentStage(title="Test", description="A" * 256, price=100)

    def test_invalid_photo_url(self):
        with pytest.raises(ValueError, match="valid URL"):
            PaymentStage(
                title="Test", description="Test", price=100, photo_url="not-a-url"
            )

    def test_invalid_start_parameter(self):
        with pytest.raises(ValueError, match="letters, numbers, and underscores"):
            PaymentStage(
                title="Test",
                description="Test",
                price=100,
                start_parameter="invalid-parameter",
            )
        with pytest.raises(ValueError, match="64 characters or less"):
            PaymentStage(
                title="Test", description="Test", price=100, start_parameter="A" * 65
            )


class TestPaymentResultValidation:
    """Test PaymentResult validation"""

    def test_valid_payment_result(self):
        result = PaymentResult(user_id=12345, amount=100)
        assert result.user_id == 12345
        assert result.amount == 100
        assert result.currency == "XTR"

    def test_invalid_user_id(self):
        with pytest.raises(ValueError, match="positive integer"):
            PaymentResult(user_id=0, amount=100)
        with pytest.raises(ValueError, match="positive integer"):
            PaymentResult(user_id=-1, amount=100)

    def test_invalid_amount(self):
        with pytest.raises(ValueError, match="positive integer"):
            PaymentResult(user_id=12345, amount=0)

    def test_invalid_currency(self):
        with pytest.raises(ValueError, match="must be 'XTR'"):
            PaymentResult(user_id=12345, amount=100, currency="USD")


class TestNeonPayCoreValidation:
    """Test NeonPayCore validation"""

    @pytest.fixture
    def mock_adapter(self):
        adapter = Mock()
        adapter.send_invoice = AsyncMock(return_value=True)
        adapter.setup_handlers = AsyncMock()
        adapter.get_library_info = Mock(return_value={"library": "test"})
        return adapter

    @pytest.fixture
    def core(self, mock_adapter):
        return NeonPayCore(mock_adapter)

    def test_create_payment_stage_validation(self, core):
        stage = PaymentStage(title="Test", description="Test", price=100)
        core.create_payment_stage("test_id", stage)
        assert "test_id" in core.list_payment_stages()
        # Invalid stage ID
        with pytest.raises(ValueError, match="Stage ID is required"):
            core.create_payment_stage(123, stage)
        with pytest.raises(ValueError, match="Stage ID is required"):
            core.create_payment_stage("", stage)
        with pytest.raises(ValueError, match="already exists"):
            core.create_payment_stage("test_id", stage)

    @pytest.mark.asyncio
    async def test_send_payment_validation(self, core):
        stage = PaymentStage(title="Test", description="Test", price=100)
        core.create_payment_stage("test_id", stage)
        # Valid parameters
        result = await core.send_payment(12345, "test_id")
        assert result is True  # Will be True because adapter is mocked
        # Invalid user ID
        with pytest.raises(ValueError, match="User ID must be a positive integer"):
            await core.send_payment(0, "test_id")
        # Invalid stage ID
        with pytest.raises(ValueError, match="Stage ID is required"):
            await core.send_payment(12345, "")

    def test_on_payment_validation(self, core):
        def valid_callback(result):
            pass

        core.on_payment(valid_callback)
        assert len(core._payment_callbacks) == 1
        with pytest.raises(ValueError, match="must be callable"):
            core.on_payment("not-a-function")


class TestWebhookSecurity:
    """Test webhook security features"""

    @pytest.fixture
    def verifier(self):
        return WebhookVerifier("secret_token", max_age=300)

    @pytest.fixture
    def handler(self, verifier):
        return WebhookHandler(verifier)

    def test_signature_verification(self, verifier):
        payload = '{"test": "data"}'
        valid_signature = hmac.new(
            b"secret_token", payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        assert verifier.verify_signature(payload, valid_signature)
        assert not verifier.verify_signature(payload, "invalid")
        assert not verifier.verify_signature(payload, "")

    def test_timestamp_verification(self, verifier):
        current_time = int(time.time())
        assert verifier.verify_timestamp(str(current_time))
        old_timestamp = str(current_time - 400)
        assert not verifier.verify_timestamp(old_timestamp)
        future_timestamp = str(current_time + 30)
        assert verifier.verify_timestamp(future_timestamp)
        far_future = str(current_time + 400)
        assert not verifier.verify_timestamp(far_future)

    def test_webhook_verification(self, verifier):
        payload = '{"test": "data"}'
        current_time = str(int(time.time()))
        valid_signature = hmac.new(
            b"secret_token", payload.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        assert verifier.verify_webhook(payload, valid_signature, current_time)
        assert not verifier.verify_webhook(payload, "invalid", current_time)
        assert not verifier.verify_webhook(payload, valid_signature, "invalid")


class TestWebhookHandler:
    """Test webhook handler functionality"""

    @pytest.fixture
    def handler(self):
        verifier = WebhookVerifier("secret_token")
        return WebhookHandler(verifier)

    def test_event_handler_registration(self, handler):
        def test_handler(event_type, data, headers):
            return {"processed": True}

        handler.on_event("test_event", test_handler)
        assert "test_event" in handler._event_handlers
        assert len(handler._event_handlers["test_event"]) == 1

    def test_default_handler_registration(self, handler):
        def default_handler(event_type, data, headers):
            return {"default": True}

        handler.on_default(default_handler)
        assert handler._default_handler == default_handler

    def test_invalid_handler_registration(self, handler):
        with pytest.raises(ValueError, match="must be callable"):
            handler.on_event("test", "not-a-function")
        with pytest.raises(ValueError, match="must be callable"):
            handler.on_default("not-a-function")

    def test_event_type_extraction(self, handler):
        payment_data = {"message": {"successful_payment": {"amount": 100}}}
        assert handler._extract_event_type(payment_data) == "payment_success"
        message_data = {"message": {"text": "hello"}}
        assert handler._extract_event_type(message_data) == "message"
        checkout_data = {"pre_checkout_query": {"id": "123"}}
        assert handler._extract_event_type(checkout_data) == "pre_checkout"
        unknown_data = {"unknown": "data"}
        assert handler._extract_event_type(unknown_data) == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
