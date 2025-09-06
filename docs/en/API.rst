# NEONPAY API Reference

Complete API documentation for NEONPAY library.

## Quick Start

### Factory Function

\`\`\`python
from neonpay.factory import create_neonpay

# Automatic adapter detection
neonpay = create_neonpay(bot_instance=your_bot_instance)
\`\`\`

**Parameters:**
- `bot_instance`: Your bot instance (Bot, Client, TeleBot, etc.)
- `dispatcher`: Dispatcher instance (for Aiogram)
- `thank_you_message`: Custom thank you message

**Returns:** Configured NeonPayCore instance

## Core Classes

### NeonPayCore

Main payment processing class.

\`\`\`python
class NeonPayCore:
    def __init__(self, adapter: PaymentAdapter, thank_you_message: str = "Thank you for your payment!")
\`\`\`

#### Methods

##### `async setup() -> None`
Initialize the payment system. Called automatically when needed.

##### `create_payment_stage(stage_id: str, stage: PaymentStage) -> None`
Create a new payment stage.

**Parameters:**
- `stage_id`: Unique identifier for the payment stage
- `stage`: PaymentStage configuration object

**Raises:**
- `ValidationError`: If stage_id already exists or stage is invalid

##### `get_payment_stage(stage_id: str) -> Optional[PaymentStage]`
Retrieve a payment stage by ID.

**Returns:** PaymentStage object or None if not found

##### `list_payment_stages() -> Dict[str, PaymentStage]`
Get all payment stages.

**Returns:** Dictionary mapping stage IDs to PaymentStage objects

##### `remove_payment_stage(stage_id: str) -> bool`
Remove a payment stage.

**Returns:** True if stage was removed, False if not found

##### `async send_payment(user_id: int, stage_id: str) -> bool`
Send payment invoice to user.

**Parameters:**
- `user_id`: Telegram user ID
- `stage_id`: Payment stage identifier

**Returns:** True if invoice sent successfully

**Raises:**
- `PaymentError`: If stage not found or sending fails

##### `on_payment(callback: Callable[[PaymentResult], None]) -> None`
Register payment completion callback.

**Parameters:**
- `callback`: Function to call when payment completes

##### `get_stats() -> Dict[str, Any]`
Get payment system statistics.

**Returns:** Dictionary with system information

### PaymentStage

Payment configuration class.

\`\`\`python
@dataclass
class PaymentStage:
    title: str
    description: str
    price: int
    label: str = "Payment"
    photo_url: Optional[str] = None
    payload: Optional[Dict[str, Any]] = field(default_factory=dict)
    provider_token: str = ""
    start_parameter: str = "neonpay"
\`\`\`

**Validation:**
- `price` must be positive
- `title` and `description` cannot be empty

### PaymentResult

Payment completion result.

\`\`\`python
@dataclass
class PaymentResult:
    user_id: int
    amount: int
    currency: str = "XTR"
    status: PaymentStatus = PaymentStatus.COMPLETED
    stage: Optional[PaymentStage] = None
    transaction_id: Optional[str] = None
    timestamp: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
\`\`\`

### PaymentStatus

Payment status enumeration.

\`\`\`python
class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    REFUNDED = "refunded"
\`\`\`

## Adapters

### PaymentAdapter

Abstract base class for bot library adapters.

\`\`\`python
class PaymentAdapter(ABC):
    @abstractmethod
    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool
    
    @abstractmethod
    async def setup_handlers(self, payment_callback: Callable[[PaymentResult], None]) -> None
    
    @abstractmethod
    def get_library_info(self) -> Dict[str, str]
\`\`\`

### PyrogramAdapter

Pyrogram library adapter.

\`\`\`python
class PyrogramAdapter(PaymentAdapter):
    def __init__(self, app: Client)
\`\`\`

### AiogramAdapter

Aiogram library adapter.

\`\`\`python
class AiogramAdapter(PaymentAdapter):
    def __init__(self, bot: Bot, dispatcher: Optional[Dispatcher] = None)
\`\`\`

### PythonTelegramBotAdapter

python-telegram-bot library adapter.

\`\`\`python
class PythonTelegramBotAdapter(PaymentAdapter):
    def __init__(self, application: Application)
\`\`\`

### TelebotAdapter

pyTelegramBotAPI library adapter.

\`\`\`python
class TelebotAdapter(PaymentAdapter):
    def __init__(self, bot: TeleBot)
\`\`\`

### RawAPIAdapter

Raw Telegram Bot API adapter.

\`\`\`python
class RawAPIAdapter(PaymentAdapter):
    def __init__(self, bot_token: str, webhook_url: Optional[str] = None)
    
    async def handle_webhook_update(self, update_data: Dict[str, Any])
    async def close()
\`\`\`

## Factory Functions

### create_neonpay

Convenience function for automatic adapter creation.

\`\`\`python
def create_neonpay(
    bot_instance: Any,
    thank_you_message: str = "Thank you for your payment!"
) -> NeonPayCore
\`\`\`

**Parameters:**
- `bot_instance`: Bot instance from any supported library
- `thank_you_message`: Thank you message for payments

**Returns:** Configured NeonPayCore instance

**Raises:**
- `ConfigurationError`: If bot library is not supported

### AdapterFactory.create_adapter

Create appropriate adapter for bot instance.

\`\`\`python
@staticmethod
def create_adapter(bot_instance: Any) -> PaymentAdapter
\`\`\`

## Error Classes

### NeonPayError

Base exception class.

\`\`\`python
class NeonPayError(Exception):
    pass
\`\`\`

### PaymentError

Payment processing error.

\`\`\`python
class PaymentError(NeonPayError):
    pass
\`\`\`

### ConfigurationError

Configuration or setup error.

\`\`\`python
class ConfigurationError(NeonPayError):
    pass
\`\`\`

### AdapterError

Bot library adapter error.

\`\`\`python
class AdapterError(NeonPayError):
    pass
\`\`\`

### ValidationError

Data validation error.

\`\`\`python
class ValidationError(NeonPayError):
    pass
\`\`\`

## Usage Examples

### Basic Usage

\`\`\`python
from neonpay import create_neonpay, PaymentStage

# Initialize
neonpay = create_neonpay(bot)

# Create stage
stage = PaymentStage("Product", "Description", 100)
neonpay.create_payment_stage("product1", stage)

# Send payment
await neonpay.send_payment(user_id, "product1")

# Handle payments
@neonpay.on_payment
async def handle_payment(result):
    print(f"Payment: {result.amount} from {result.user_id}")
\`\`\`

### Advanced Usage

\`\`\`python
from neonpay import NeonPayCore, PyrogramAdapter, PaymentStage, PaymentStatus

# Manual adapter creation
adapter = PyrogramAdapter(pyrogram_client)
neonpay = NeonPayCore(adapter, "Thanks for your purchase!")

# Complex payment stage
stage = PaymentStage(
    title="Premium Subscription",
    description="Monthly premium access",
    price=500,
    label="Subscribe Now",
    photo_url="https://example.com/premium.png",
    payload={"plan": "premium", "duration": "monthly"},
    start_parameter="premium_ref"
)

neonpay.create_payment_stage("premium_monthly", stage)

# Advanced payment handling
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        plan = result.metadata.get("plan")
        duration = result.metadata.get("duration")
        
        # Business logic
        await activate_subscription(result.user_id, plan, duration)
        
        # Send confirmation
        await send_confirmation(result.user_id, result.amount)
\`\`\`

### Error Handling

\`\`\`python
from neonpay import NeonPayError, PaymentError, ValidationError

try:
    # Create stage with validation
    stage = PaymentStage("", "Description", -100)  # Invalid
    neonpay.create_payment_stage("invalid", stage)
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    # Send payment
    await neonpay.send_payment(user_id, "nonexistent")
except PaymentError as e:
    print(f"Payment error: {e}")
except NeonPayError as e:
    print(f"General error: {e}")
\`\`\`

---

[← Back to Documentation](README.md)
