"""
Tests for NEONPAY validation and security features
"""

import pytest
import json
import hmac
import hashlib
import time
from unittest.mock import Mock, AsyncMock
from neonpay.core import (
    PaymentStage, PaymentResult, PaymentStatus, 
    validate_url, validate_json_payload, NeonPayCore
)
from neonpay.errors import NeonPayError
from neonpay.webhooks import WebhookVerifier, WebhookHandler
from neonpay.localization import Language


class TestValidation:
    """Test validation functions"""
    
    def test_validate_url(self):
        """Test URL validation"""
        # Valid URLs
        assert validate_url("https://example.com") == True
        assert validate_url("http://example.com") == True
        assert validate_url("https://sub.example.com/path?param=value") == True
        
        # Invalid URLs
        assert validate_url("") == False
        assert validate_url("not-a-url") == False
        assert validate_url("ftp://example.com") == False
        
        # HTTPS required
        assert validate_url("https://example.com", require_https=True) == True
        assert validate_url("http://example.com", require_https=True) == False
    
    def test_validate_json_payload(self):
        """Test JSON payload validation"""
        # Valid payloads
        assert validate_json_payload({}) == True
        assert validate_json_payload({"key": "value"}) == True
        assert validate_json_payload({"nested": {"key": "value"}}) == True
        
        # Invalid payloads
        assert validate_json_payload("not-a-dict") == False
        assert validate_json_payload(None) == False
        
        # Large payload (over 1024 bytes)
        large_payload = {"data": "x" * 1000}
        assert validate_json_payload(large_payload) == False


class TestPaymentStageValidation:
    """Test PaymentStage validation"""
    
    def test_valid_payment_stage(self):
        """Test valid payment stage creation"""
        stage = PaymentStage(
            title="Test Product",
            description="Test Description",
            price=100
        )
        assert stage.title == "Test Product"
        assert stage.price == 100
    
    def test_invalid_price(self):
        """Test price validation"""
        # Too low
        with pytest.raises(ValueError, match="between 1 and 2500"):
            PaymentStage(
                title="Test",
                description="Test",
                price=0
            )
        
        # Too high
        with pytest.raises(ValueError, match="between 1 and 2500"):
            PaymentStage(
                title="Test",
                description="Test",
                price=3000
            )
        
        # Wrong type
        with pytest.raises(ValueError, match="must be an integer"):
            PaymentStage(
                title="Test",
                description="Test",
                price="100"
            )
    
    def test_invalid_title(self):
        """Test title validation"""
        # Empty title
        with pytest.raises(ValueError, match="non-empty string"):
            PaymentStage(
                title="",
                description="Test",
                price=100
            )
        
        # Title too long
        with pytest.raises(ValueError, match="32 characters or less"):
            PaymentStage(
                title="A" * 33,
                description="Test",
                price=100
            )
    
    def test_invalid_description(self):
        """Test description validation"""
        # Empty description
        with pytest.raises(ValueError, match="non-empty string"):
            PaymentStage(
                title="Test",
                description="",
                price=100
            )
        
        # Description too long
        with pytest.raises(ValueError, match="255 characters or less"):
            PaymentStage(
                title="Test",
                description="A" * 256,
                price=100
            )
    
    def test_invalid_photo_url(self):
        """Test photo URL validation"""
        with pytest.raises(ValueError, match="valid URL"):
            PaymentStage(
                title="Test",
                description="Test",
                price=100,
                photo_url="not-a-url"
            )
    
    def test_invalid_start_parameter(self):
        """Test start parameter validation"""
        # Invalid characters
        with pytest.raises(ValueError, match="letters, numbers, and underscores"):
            PaymentStage(
                title="Test",
                description="Test",
                price=100,
                start_parameter="invalid-parameter"
            )
        
        # Too long
        with pytest.raises(ValueError, match="64 characters or less"):
            PaymentStage(
                title="Test",
                description="Test",
                price=100,
                start_parameter="A" * 65
            )


class TestPaymentResultValidation:
    """Test PaymentResult validation"""
    
    def test_valid_payment_result(self):
        """Test valid payment result creation"""
        result = PaymentResult(
            user_id=12345,
            amount=100
        )
        assert result.user_id == 12345
        assert result.amount == 100
        assert result.currency == "XTR"
    
    def test_invalid_user_id(self):
        """Test user ID validation"""
        with pytest.raises(ValueError, match="positive integer"):
            PaymentResult(
                user_id=0,
                amount=100
            )
        
        with pytest.raises(ValueError, match="positive integer"):
            PaymentResult(
                user_id=-1,
                amount=100
            )
    
    def test_invalid_amount(self):
        """Test amount validation"""
        with pytest.raises(ValueError, match="positive integer"):
            PaymentResult(
                user_id=12345,
                amount=0
            )
    
    def test_invalid_currency(self):
        """Test currency validation"""
        with pytest.raises(ValueError, match="must be 'XTR'"):
            PaymentResult(
                user_id=12345,
                amount=100,
                currency="USD"
            )


class TestNeonPayCoreValidation:
    """Test NeonPayCore validation"""
    
    @pytest.fixture
    def mock_adapter(self):
        """Create mock adapter"""
        adapter = Mock()
        adapter.send_invoice = AsyncMock(return_value=True)
        adapter.setup_handlers = AsyncMock()
        adapter.get_library_info = Mock(return_value={"library": "test"})
        return adapter
    
    @pytest.fixture
    def core(self, mock_adapter):
        """Create NeonPayCore instance"""
        return NeonPayCore(mock_adapter)
    
    def test_create_payment_stage_validation(self, core):
        """Test payment stage creation validation"""
        stage = PaymentStage(
            title="Test",
            description="Test",
            price=100
        )
        
        # Valid stage ID
        core.create_payment_stage("test_id", stage)
        assert "test_id" in core.list_payment_stages()
        
        # Invalid stage ID
        with pytest.raises(ValueError, match="Stage ID must be a string"):
            core.create_payment_stage(123, stage)
        
        # Empty stage ID
        with pytest.raises(ValueError, match="Stage ID is required"):
            core.create_payment_stage("", stage)
        
        # Duplicate stage ID
        with pytest.raises(ValueError, match="already exists"):
            core.create_payment_stage("test_id", stage)
    
    def test_send_payment_validation(self, core):
        """Test send payment validation"""
        stage = PaymentStage(
            title="Test",
            description="Test",
            price=100
        )
        core.create_payment_stage("test_id", stage)
        
        # Valid parameters
        assert core.send_payment(12345, "test_id") == True
        
        # Invalid user ID
        with pytest.raises(ValueError, match="positive integer"):
            core.send_payment(0, "test_id")
        
        # Invalid stage ID
        with pytest.raises(ValueError, match="Stage ID is required"):
            core.send_payment(12345, "")
    
    def test_on_payment_validation(self, core):
        """Test payment callback validation"""
        # Valid callback
        def valid_callback(result):
            pass
        
        core.on_payment(valid_callback)
        assert len(core._payment_callbacks) == 1
        
        # Invalid callback
        with pytest.raises(ValueError, match="must be callable"):
            core.on_payment("not-a-function")


class TestWebhookSecurity:
    """Test webhook security features"""
    
    @pytest.fixture
    def verifier(self):
        """Create webhook verifier"""
        return WebhookVerifier("secret_token", max_age=300)
    
    @pytest.fixture
    def handler(self, verifier):
        """Create webhook handler"""
        return WebhookHandler(verifier)
    
    def test_signature_verification(self, verifier):
        """Test signature verification"""
        payload = '{"test": "data"}'
        
        # Valid signature
        valid_signature = hmac.new(
            b"secret_token",
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        assert verifier.verify_signature(payload, valid_signature) == True
        
        # Invalid signature
        assert verifier.verify_signature(payload, "invalid") == False
        
        # Empty signature
        assert verifier.verify_signature(payload, "") == False
    
    def test_timestamp_verification(self, verifier):
        """Test timestamp verification"""
        current_time = int(time.time())
        
        # Valid timestamp
        assert verifier.verify_timestamp(str(current_time)) == True
        
        # Too old timestamp
        old_timestamp = str(current_time - 400)  # 400 seconds old
        assert verifier.verify_timestamp(old_timestamp) == False
        
        # Future timestamp (with small tolerance)
        future_timestamp = str(current_time + 30)  # 30 seconds in future
        assert verifier.verify_timestamp(future_timestamp) == True
        
        # Too far in future
        far_future = str(current_time + 100)  # 100 seconds in future
        assert verifier.verify_timestamp(far_future) == False
    
    def test_webhook_verification(self, verifier):
        """Test complete webhook verification"""
        payload = '{"test": "data"}'
        current_time = str(int(time.time()))
        
        # Valid webhook
        valid_signature = hmac.new(
            b"secret_token",
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        assert verifier.verify_webhook(payload, valid_signature, current_time) == True
        
        # Invalid signature
        assert verifier.verify_webhook(payload, "invalid", current_time) == False
        
        # Invalid timestamp
        assert verifier.verify_webhook(payload, valid_signature, "invalid") == False


class TestWebhookHandler:
    """Test webhook handler functionality"""
    
    @pytest.fixture
    def handler(self):
        """Create webhook handler"""
        verifier = WebhookVerifier("secret_token")
        return WebhookHandler(verifier)
    
    def test_event_handler_registration(self, handler):
        """Test event handler registration"""
        def test_handler(event_type, data, headers):
            return {"processed": True}
        
        handler.on_event("test_event", test_handler)
        assert "test_event" in handler._event_handlers
        assert len(handler._event_handlers["test_event"]) == 1
    
    def test_default_handler_registration(self, handler):
        """Test default handler registration"""
        def default_handler(event_type, data, headers):
            return {"default": True}
        
        handler.on_default(default_handler)
        assert handler._default_handler == default_handler
    
    def test_invalid_handler_registration(self, handler):
        """Test invalid handler registration"""
        with pytest.raises(ValueError, match="must be callable"):
            handler.on_event("test", "not-a-function")
        
        with pytest.raises(ValueError, match="must be callable"):
            handler.on_default("not-a-function")
    
    def test_event_type_extraction(self, handler):
        """Test event type extraction"""
        # Payment success
        payment_data = {"message": {"successful_payment": {"amount": 100}}}
        assert handler._extract_event_type(payment_data) == "payment_success"
        
        # Regular message
        message_data = {"message": {"text": "hello"}}
        assert handler._extract_event_type(message_data) == "message"
        
        # Pre-checkout
        checkout_data = {"pre_checkout_query": {"id": "123"}}
        assert handler._extract_event_type(checkout_data) == "pre_checkout"
        
        # Unknown
        unknown_data = {"unknown": "data"}
        assert handler._extract_event_type(unknown_data) == "unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
