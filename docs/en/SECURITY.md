# NEONPAY Security Guide

## 🔒 Security Overview

NEONPAY is designed with security as a top priority. This document outlines the security features, best practices, and recommendations for secure deployment.

## 🛡️ Security Features

### 1. Input Validation

NEONPAY implements comprehensive input validation to prevent injection attacks and ensure data integrity:

```python
from neonpay import PaymentStage

# All inputs are validated automatically
stage = PaymentStage(
    title="Product Name",           # Max 32 chars, non-empty
    description="Description",      # Max 255 chars, non-empty
    price=100,                     # 1-2500 Telegram Stars only
    photo_url="https://example.com/image.jpg",  # Valid URL required
    start_parameter="valid_param"  # Alphanumeric + underscore only
)
```

**Validation Rules:**
- **Title**: 1-32 characters, non-empty string
- **Description**: 1-255 characters, non-empty string
- **Price**: Integer between 1-2500 Telegram Stars
- **Photo URL**: Valid HTTP/HTTPS URL format
- **Start Parameter**: Alphanumeric characters and underscores only
- **Payload**: JSON dictionary under 1024 bytes

### 2. Webhook Security

NEONPAY provides secure webhook handling with signature verification and timestamp validation:

```python
from neonpay import create_secure_webhook_handler

# Create secure webhook handler
handler = create_secure_webhook_handler(
    secret_token="your_secret_token",
    max_age=300,  # 5 minutes
    language="en"
)

# Register event handlers
@handler.on_event("payment_success")
async def handle_payment_success(event_type, data, headers):
    # Verify webhook authenticity is automatic
    return {"processed": True}

# Process incoming webhook
result = await handler.process_webhook(
    payload=raw_payload,
    signature=telegram_signature,
    timestamp=telegram_timestamp
)
```

**Security Features:**
- **HMAC-SHA256 Signature Verification**: Ensures webhook authenticity
- **Timestamp Validation**: Prevents replay attacks (configurable max age)
- **Automatic Validation**: All webhooks are verified before processing
- **Secure Headers**: Validates Telegram Bot API headers

### 3. Rate Limiting and Limits

NEONPAY implements configurable limits to prevent abuse:

```python
from neonpay import NeonPayCore

# Configure limits
core = NeonPayCore(
    adapter=adapter,
    max_stages=100,        # Maximum payment stages
    enable_logging=True     # Security logging
)
```

**Built-in Limits:**
- **Payment Stages**: Configurable maximum (default: 100)
- **Payload Size**: Maximum 1024 bytes for JSON payloads
- **URL Validation**: Only HTTP/HTTPS URLs accepted
- **Character Limits**: Enforced on all text fields

### 4. Secure Logging

NEONPAY provides secure logging without exposing sensitive information:

```python
# Logging is automatically sanitized
core = NeonPayCore(
    adapter=adapter,
    enable_logging=True  # Secure logging enabled
)

# Sensitive data is never logged
# Only metadata and status information is recorded
```

**Logging Security:**
- **No Sensitive Data**: Tokens, user IDs, and payment details are never logged
- **Structured Logs**: Consistent format for security monitoring
- **Configurable**: Logging can be disabled for production if needed

## 🚨 Security Best Practices

### 1. Bot Token Security

```python
# ❌ NEVER do this
bot_token = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# ✅ Use environment variables
import os
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

# ✅ Use secure configuration management
from dotenv import load_dotenv
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
```

### 2. Webhook Secret Management

```python
# ❌ Hardcoded secrets
webhook_secret = "my_secret_123"

# ✅ Use secure secret management
webhook_secret = os.getenv("WEBHOOK_SECRET")
if not webhook_secret:
    raise ValueError("WEBHOOK_SECRET environment variable required")
```

### 3. Input Sanitization

```python
# ❌ Trusting user input
user_title = user_input  # Could be malicious

# ✅ Always validate through NEONPAY
try:
    stage = PaymentStage(
        title=user_title,      # Automatically validated
        description=user_desc, # Automatically validated
        price=user_price       # Automatically validated
    )
except ValueError as e:
    # Handle validation errors securely
    logger.warning(f"Invalid input: {e}")
    return {"error": "Invalid input"}
```

### 4. Error Handling

```python
# ❌ Exposing internal errors
except Exception as e:
    return {"error": str(e)}  # Could expose sensitive info

# ✅ Use NEONPAY's secure error handling
from neonpay import NeonPayError

try:
    result = await core.send_payment(user_id, stage_id)
except NeonPayError as e:
    # NEONPAY errors are safe to expose
    return {"error": str(e)}
except Exception as e:
    # Log internal errors, return generic message
    logger.error(f"Internal error: {e}")
    return {"error": "Internal server error"}
```

## 🔐 Deployment Security

### 1. Environment Configuration

```bash
# .env file (never commit to version control)
TELEGRAM_BOT_TOKEN=your_bot_token_here
WEBHOOK_SECRET=your_webhook_secret_here
NEONPAY_LOG_LEVEL=INFO
NEONPAY_MAX_STAGES=50
```

### 2. HTTPS Requirements

```python
# Webhook URLs must use HTTPS in production
webhook_url = "https://yourdomain.com/webhook"

# Local development can use HTTP
if os.getenv("ENVIRONMENT") == "production":
    assert webhook_url.startswith("https://")
```

### 3. Network Security

```python
# Use secure HTTP client settings
from neonpay import RawAPIAdapter

adapter = RawAPIAdapter(
    bot_token=bot_token,
    timeout=30,  # Prevent hanging connections
    webhook_url=webhook_url
)
```

## 🧪 Security Testing

### 1. Validation Tests

```python
import pytest
from neonpay import PaymentStage

def test_security_validation():
    # Test malicious inputs
    with pytest.raises(ValueError):
        PaymentStage(
            title="A" * 33,  # Too long
            description="Test",
            price=100
        )
    
    with pytest.raises(ValueError):
        PaymentStage(
            title="Test",
            description="Test",
            price=3000  # Too high
        )
```

### 2. Webhook Security Tests

```python
def test_webhook_security():
    from neonpay import WebhookVerifier
    
    verifier = WebhookVerifier("secret", max_age=300)
    
    # Test invalid signature
    assert not verifier.verify_signature("payload", "invalid")
    
    # Test expired timestamp
    old_timestamp = str(int(time.time()) - 400)
    assert not verifier.verify_timestamp(old_timestamp)
```

## 📊 Security Monitoring

### 1. Log Analysis

Monitor NEONPAY logs for security events:

```python
# Enable security logging
core = NeonPayCore(
    adapter=adapter,
    enable_logging=True
)

# Monitor for:
# - Failed webhook verifications
# - Validation errors
# - Rate limit violations
# - Suspicious input patterns
```

### 2. Metrics Collection

```python
# Get security statistics
stats = core.get_stats()
webhook_stats = handler.get_stats()

# Monitor:
# - Total payment stages
# - Webhook verification success rate
# - Validation error frequency
# - Resource usage
```

## 🚨 Incident Response

### 1. Security Breach Checklist

If you suspect a security breach:

1. **Immediate Actions:**
   - Rotate bot token
   - Change webhook secret
   - Disable webhook temporarily
   - Review logs for suspicious activity

2. **Investigation:**
   - Check webhook verification logs
   - Review input validation failures
   - Analyze rate limiting violations
   - Check for unauthorized access

3. **Recovery:**
   - Update security configurations
   - Implement additional monitoring
   - Review and update access controls
   - Document incident and lessons learned

### 2. Contact Information

For security issues:
- **Email**: security@neonpay.dev
- **GitHub**: Create security advisory
- **Response Time**: Within 24 hours for critical issues

## 📚 Additional Resources

- [Telegram Bot API Security](https://core.telegram.org/bots/api#security-considerations)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)

## 🔄 Security Updates

NEONPAY is regularly updated with security improvements:

- **Automatic Updates**: Security patches are released promptly
- **Vulnerability Reporting**: Security issues are addressed within 24 hours
- **Backward Compatibility**: Security updates maintain API compatibility
- **Transparency**: All security changes are documented and announced

---

**Remember**: Security is a shared responsibility. Always follow security best practices and keep your NEONPAY installation updated.
