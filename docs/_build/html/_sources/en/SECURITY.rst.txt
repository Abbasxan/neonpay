# Security Guide - NEONPAY

This document outlines security best practices for using NEONPAY in production environments.

## Table of Contents

1. [Token Security](#token-security)
2. [Payment Validation](#payment-validation)
3. [Data Protection](#data-protection)
4. [Error Handling](#error-handling)
5. [Logging Security](#logging-security)
6. [Production Checklist](#production-checklist)

## Token Security

### Bot Token Protection

**❌ Never do this:**
```python
# DON'T: Hardcode tokens in source code
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**✅ Do this instead:**
```python
import os

# DO: Use environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
```

### Environment Variables

Create a `.env` file (never commit to version control):
```bash
# .env
BOT_TOKEN=your_bot_token_here
API_ID=your_api_id_here
API_HASH=your_api_hash_here
DATABASE_URL=postgresql://user:pass@localhost/db
```

Load with python-dotenv:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Payment Validation

### Verify Payment Amounts

```python
@neonpay.on_payment
async def handle_payment(result):
    # Always verify the payment amount
    expected_amount = get_expected_amount(result.stage_id)
    
    if result.amount != expected_amount:
        logger.warning(
            f"Payment amount mismatch: expected {expected_amount}, "
            f"got {result.amount} from user {result.user_id}"
        )
        return
    
    # Process payment only after validation
    await process_payment(result)
```

### Validate Stage IDs

```python
async def safe_send_payment(user_id: int, stage_id: str):
    # Validate stage exists
    stage = neonpay.get_payment_stage(stage_id)
    if not stage:
        logger.error(f"Invalid stage_id: {stage_id}")
        await bot.send_message(user_id, "Payment option not available.")
        return
    
    # Validate user permissions
    if not await user_can_purchase(user_id, stage_id):
        await bot.send_message(user_id, "You don't have permission to purchase this item.")
        return
    
    # Send payment
    await neonpay.send_payment(user_id, stage_id)
```

## Data Protection

### User Data Handling

```python
import hashlib

def hash_user_id(user_id: int) -> str:
    """Hash user ID for logging (one-way)"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:8]

@neonpay.on_payment
async def handle_payment(result):
    # Log with hashed user ID
    hashed_id = hash_user_id(result.user_id)
    logger.info(f"Payment received from user {hashed_id}: {result.amount} stars")
    
    # Store in database with proper encryption
    await store_payment_securely(result)
```

### Database Security

```python
import asyncpg
from cryptography.fernet import Fernet

class SecurePaymentStorage:
    def __init__(self, db_url: str, encryption_key: str):
        self.db_url = db_url
        self.cipher = Fernet(encryption_key.encode())
    
    async def store_payment(self, payment_data: dict):
        # Encrypt sensitive data
        encrypted_data = self.cipher.encrypt(
            json.dumps(payment_data).encode()
        )
        
        conn = await asyncpg.connect(self.db_url)
        await conn.execute(
            "INSERT INTO payments (encrypted_data, created_at) VALUES ($1, NOW())",
            encrypted_data
        )
        await conn.close()
```

## Error Handling

### Secure Error Messages

```python
async def handle_payment_error(user_id: int, error: Exception):
    # Log full error details
    logger.error(f"Payment error for user {user_id}: {error}", exc_info=True)
    
    # Send generic message to user
    await bot.send_message(
        user_id, 
        "Something went wrong with your payment. Please try again later."
    )
    
    # Don't expose internal details
    # ❌ DON'T: await bot.send_message(user_id, f"Error: {str(error)}")
```

### Input Validation

```python
def validate_user_input(user_id: int, stage_id: str) -> bool:
    """Validate user input before processing"""
    
    # Check user_id is valid
    if not isinstance(user_id, int) or user_id <= 0:
        return False
    
    # Check stage_id format
    if not isinstance(stage_id, str) or len(stage_id) > 100:
        return False
    
    # Check for suspicious patterns
    if any(char in stage_id for char in ['<', '>', '&', '"', "'"]):
        return False
    
    return True
```

## Logging Security

### Secure Logging Configuration

```python
import logging
import logging.handlers
from datetime import datetime

def setup_secure_logging():
    """Setup secure logging configuration"""
    
    # Create formatter that excludes sensitive data
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Setup logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Disable debug in production
if os.getenv("ENVIRONMENT") == "production":
        logger.setLevel(logging.WARNING)
```

### Sensitive Data Filtering

```python
class SensitiveDataFilter(logging.Filter):
    """Filter out sensitive data from logs"""
    
    def filter(self, record):
        # Remove tokens from log messages
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Replace token patterns
            import re
            record.msg = re.sub(
                r'\b\d{10}:[A-Za-z0-9_-]{35}\b',
                '[TOKEN_REDACTED]',
                msg
            )
        return True

# Apply filter
logger.addFilter(SensitiveDataFilter())
```

## Production Checklist

### Pre-deployment Security Check

- [ ] **Environment Variables**: All sensitive data in environment variables
- [ ] **Token Protection**: Bot tokens not in source code
- [ ] **Database Security**: Encrypted connections and data
- [ ] **Input Validation**: All user inputs validated
- [ ] **Error Handling**: Generic error messages for users
- [ ] **Logging**: Sensitive data filtered from logs
- [ ] **HTTPS**: All webhooks use HTTPS
- [ ] **Rate Limiting**: Implement rate limiting for payments
- [ ] **Monitoring**: Set up payment monitoring and alerts
- [ ] **Backup**: Regular database backups

### Rate Limiting

```python
from collections import defaultdict
import time

class PaymentRateLimiter:
    def __init__(self, max_payments: int = 5, window: int = 3600):
        self.max_payments = max_payments
        self.window = window
        self.user_payments = defaultdict(list)
    
    def can_make_payment(self, user_id: int) -> bool:
        now = time.time()
        user_payments = self.user_payments[user_id]
        
        # Remove old payments outside window
        user_payments[:] = [t for t in user_payments if now - t < self.window]
        
        # Check if under limit
        return len(user_payments) < self.max_payments
    
    def record_payment(self, user_id: int):
        self.user_payments[user_id].append(time.time())

# Usage
rate_limiter = PaymentRateLimiter()

async def safe_send_payment(user_id: int, stage_id: str):
    if not rate_limiter.can_make_payment(user_id):
        await bot.send_message(
            user_id, 
            "Too many payment attempts. Please try again later."
        )
        return
    
    await neonpay.send_payment(user_id, stage_id)
    rate_limiter.record_payment(user_id)
```

### Monitoring and Alerts

```python
import asyncio
from datetime import datetime, timedelta

class PaymentMonitor:
    def __init__(self):
        self.payment_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    async def monitor_payments(self):
        """Monitor payment patterns for anomalies"""
        while True:
            await asyncio.sleep(300)  # Check every 5 minutes
            
            # Check for unusual payment patterns
            recent_payments = self.get_recent_payments()
            
            if len(recent_payments) > 100:  # Threshold
                await send_alert(f"High payment volume: {len(recent_payments)} payments")
            
            # Check for errors
            recent_errors = self.get_recent_errors()
            if len(recent_errors) > 10:  # Threshold
                await send_alert(f"High error rate: {len(recent_errors)} errors")
    
    async def send_alert(self, message: str):
        """Send security alert"""
        # Send to monitoring system
        logger.critical(f"SECURITY ALERT: {message}")
```

## Common Security Mistakes

### 1. Exposing Internal Errors

**❌ Wrong:**
```python
except Exception as e:
    await bot.send_message(user_id, f"Error: {str(e)}")
```

**✅ Correct:**
```python
except Exception as e:
    logger.error(f"Payment error: {e}")
    await bot.send_message(user_id, "Payment failed. Please try again.")
```

### 2. Storing Sensitive Data in Logs

**❌ Wrong:**
```python
logger.info(f"User {user_id} paid with token {bot_token}")
```

**✅ Correct:**
```python
logger.info(f"User {hash_user_id(user_id)} completed payment")
```

### 3. No Input Validation

**❌ Wrong:**
```python
await neonpay.send_payment(user_id, stage_id)  # No validation
```

**✅ Correct:**
```python
if validate_user_input(user_id, stage_id):
    await neonpay.send_payment(user_id, stage_id)
else:
    await bot.send_message(user_id, "Invalid request.")
```

## Incident Response

### Security Incident Checklist

1. **Immediate Response**
   - [ ] Disable affected bot if necessary
   - [ ] Review logs for suspicious activity
   - [ ] Change bot token if compromised
   - [ ] Notify users if data breach

2. **Investigation**
   - [ ] Analyze attack vector
   - [ ] Identify affected users
   - [ ] Document incident details
   - [ ] Preserve evidence

3. **Recovery**
   - [ ] Patch security vulnerabilities
   - [ ] Update security measures
   - [ ] Test system thoroughly
   - [ ] Monitor for continued attacks

4. **Post-incident**
   - [ ] Update security documentation
   - [ ] Conduct security review
   - [ ] Implement additional safeguards
   - [ ] Train team on lessons learned

## Resources

- [Telegram Bot Security](https://core.telegram.org/bots/security)
- [OWASP Security Guidelines](https://owasp.org/)
- [Python Security Best Practices](https://python-security.readthedocs.io/)

---

**Remember: Security is an ongoing process, not a one-time setup. Regularly review and update your security measures.**