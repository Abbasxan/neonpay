"""
NEONPAY Notifications - Comprehensive notification system
Supports email, Telegram, SMS, and webhook notifications
"""

import asyncio
import logging
import smtplib
import time
from dataclasses import dataclass, field
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of notifications"""

    EMAIL = "email"
    TELEGRAM = "telegram"
    SMS = "sms"
    WEBHOOK = "webhook"
    SLACK = "slack"
    DISCORD = "discord"


class NotificationPriority(Enum):
    """Notification priority levels"""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationTemplate:
    """Notification template configuration"""

    name: str
    notification_type: NotificationType
    subject: str
    body: str
    variables: List[str] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.NORMAL
    enabled: bool = True


@dataclass
class NotificationConfig:
    """Notification configuration"""

    # Email settings
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True

    # Telegram settings
    telegram_bot_token: Optional[str] = None
    telegram_admin_chat_id: Optional[str] = None

    # SMS settings
    sms_provider: Optional[str] = None
    sms_api_key: Optional[str] = None
    sms_api_secret: Optional[str] = None

    # Webhook settings
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None

    # Slack settings
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None

    # Discord settings
    discord_webhook_url: Optional[str] = None


@dataclass
class NotificationMessage:
    """Notification message to send"""

    notification_type: NotificationType
    recipient: str
    subject: Optional[str] = None
    body: str = ""
    priority: NotificationPriority = NotificationPriority.NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    template_name: Optional[str] = None
    variables: Dict[str, Any] = field(default_factory=dict)


class EmailNotifier:
    """Email notification handler"""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config

    async def send_email(self, message: NotificationMessage) -> bool:
        """Send email notification"""
        if not self.config.smtp_host or not self.config.smtp_username:
            logger.warning("Email configuration not provided")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.config.smtp_username
            msg["To"] = message.recipient
            msg["Subject"] = message.subject or "NEONPAY Notification"

            # Add body
            msg.attach(MIMEText(message.body, "html"))

            # Send email
            server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
            if self.config.smtp_use_tls:
                server.starttls()
            if self.config.smtp_password is None:
                raise ValueError("SMTP password is required")
            server.login(self.config.smtp_username, self.config.smtp_password)
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent to {message.recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False


class TelegramNotifier:
    """Telegram notification handler"""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config

    async def send_telegram(self, message: NotificationMessage) -> bool:
        """Send Telegram notification"""
        if not self.config.telegram_bot_token or not self.config.telegram_admin_chat_id:
            logger.warning("Telegram configuration not provided")
            return False

        try:
            url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"

            # Format message
            text = f"🔔 *{message.subject or 'NEONPAY Notification'}*\n\n{message.body}"

            payload = {
                "chat_id": self.config.telegram_admin_chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram notification sent")
                        return True
                    else:
                        logger.error(f"Telegram API error: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False


class SMSNotifier:
    """SMS notification handler"""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config

    async def send_sms(self, message: NotificationMessage) -> bool:
        """Send SMS notification"""
        if not self.config.sms_provider or not self.config.sms_api_key:
            logger.warning("SMS configuration not provided")
            return False

        try:
            # This is a placeholder implementation
            # In real implementation, you would integrate with SMS providers like Twilio, AWS SNS, etc.
            logger.info(f"SMS would be sent to {message.recipient}: {message.body}")
            return True

        except Exception as e:
            logger.error(f"Failed to send SMS: {e}")
            return False


class WebhookNotifier:
    """Webhook notification handler"""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config

    async def send_webhook(self, message: NotificationMessage) -> bool:
        """Send webhook notification"""
        if not self.config.webhook_url:
            logger.warning("Webhook URL not configured")
            return False

        try:
            payload = {
                "type": message.notification_type.value,
                "recipient": message.recipient,
                "subject": message.subject,
                "body": message.body,
                "priority": message.priority.value,
                "metadata": message.metadata,
                "timestamp": time.time(),
            }

            headers = {"Content-Type": "application/json"}
            if self.config.webhook_secret:
                headers["X-Webhook-Secret"] = self.config.webhook_secret

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url, json=payload, headers=headers
                ) as response:
                    if response.status in [200, 201]:
                        logger.info("Webhook notification sent")
                        return True
                    else:
                        logger.error(f"Webhook error: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False


class SlackNotifier:
    """Slack notification handler"""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config

    async def send_slack(self, message: NotificationMessage) -> bool:
        """Send Slack notification"""
        if not self.config.slack_webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False

        try:
            # Format message for Slack
            slack_message = {
                "text": f"🔔 {message.subject or 'NEONPAY Notification'}",
                "attachments": [
                    {
                        "color": self._get_color_for_priority(message.priority),
                        "fields": [
                            {"title": "Message", "value": message.body, "short": False}
                        ],
                    }
                ],
            }

            if self.config.slack_channel:
                slack_message["channel"] = self.config.slack_channel

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.slack_webhook_url, json=slack_message
                ) as response:
                    if response.status == 200:
                        logger.info("Slack notification sent")
                        return True
                    else:
                        logger.error(f"Slack API error: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

    def _get_color_for_priority(self, priority: NotificationPriority) -> str:
        """Get Slack color based on priority"""
        colors = {
            NotificationPriority.LOW: "good",
            NotificationPriority.NORMAL: "#36a64f",
            NotificationPriority.HIGH: "warning",
            NotificationPriority.CRITICAL: "danger",
        }
        return colors.get(priority, "#36a64f")


class DiscordNotifier:
    """Discord notification handler"""

    def __init__(self, config: NotificationConfig) -> None:
        self.config = config

    async def send_discord(self, message: NotificationMessage) -> bool:
        """Send Discord notification"""
        if not self.config.discord_webhook_url:
            logger.warning("Discord webhook URL not configured")
            return False

        try:
            # Format message for Discord
            discord_message = {
                "embeds": [
                    {
                        "title": message.subject or "NEONPAY Notification",
                        "description": message.body,
                        "color": self._get_color_for_priority(message.priority),
                        "timestamp": time.time(),
                        "footer": {"text": f"Priority: {message.priority.value}"},
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.discord_webhook_url, json=discord_message
                ) as response:
                    if response.status in [200, 204]:
                        logger.info("Discord notification sent")
                        return True
                    else:
                        logger.error(f"Discord API error: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Failed to send Discord notification: {e}")
            return False

    def _get_color_for_priority(self, priority: NotificationPriority) -> int:
        """Get Discord color based on priority"""
        colors = {
            NotificationPriority.LOW: 0x00FF00,  # Green
            NotificationPriority.NORMAL: 0x0099FF,  # Blue
            NotificationPriority.HIGH: 0xFF9900,  # Orange
            NotificationPriority.CRITICAL: 0xFF0000,  # Red
        }
        return colors.get(priority, 0x0099FF)


class NotificationTemplateManager:
    """Manages notification templates"""

    def __init__(self) -> None:
        self._templates: Dict[str, NotificationTemplate] = {}
        self._load_default_templates()

    def _load_default_templates(self) -> None:
        """Load default notification templates"""
        default_templates = [
            NotificationTemplate(
                name="payment_completed",
                notification_type=NotificationType.TELEGRAM,
                subject="💰 Payment Completed",
                body="User {user_id} completed payment of {amount} stars for {product_name}",
                variables=["user_id", "amount", "product_name"],
                priority=NotificationPriority.NORMAL,
            ),
            NotificationTemplate(
                name="payment_failed",
                notification_type=NotificationType.TELEGRAM,
                subject="❌ Payment Failed",
                body="Payment failed for user {user_id}. Amount: {amount} stars. Reason: {reason}",
                variables=["user_id", "amount", "reason"],
                priority=NotificationPriority.HIGH,
            ),
            NotificationTemplate(
                name="new_subscription",
                notification_type=NotificationType.EMAIL,
                subject="🎉 New Subscription",
                body="User {user_id} subscribed to {plan_name} for {duration} days",
                variables=["user_id", "plan_name", "duration"],
                priority=NotificationPriority.NORMAL,
            ),
            NotificationTemplate(
                name="subscription_expired",
                notification_type=NotificationType.EMAIL,
                subject="⚠️ Subscription Expired",
                body="Subscription expired for user {user_id}. Plan: {plan_name}",
                variables=["user_id", "plan_name"],
                priority=NotificationPriority.HIGH,
            ),
            NotificationTemplate(
                name="security_alert",
                notification_type=NotificationType.TELEGRAM,
                subject="🚨 Security Alert",
                body="Security alert: {alert_type} for user {user_id}. Details: {details}",
                variables=["alert_type", "user_id", "details"],
                priority=NotificationPriority.CRITICAL,
            ),
            NotificationTemplate(
                name="system_error",
                notification_type=NotificationType.WEBHOOK,
                subject="🔧 System Error",
                body="System error occurred: {error_type}. Message: {error_message}",
                variables=["error_type", "error_message"],
                priority=NotificationPriority.HIGH,
            ),
        ]

        for template in default_templates:
            self._templates[template.name] = template

    def get_template(self, name: str) -> Optional[NotificationTemplate]:
        """Get notification template by name"""
        return self._templates.get(name)

    def add_template(self, template: NotificationTemplate) -> None:
        """Add new notification template"""
        self._templates[template.name] = template

    def list_templates(self) -> List[NotificationTemplate]:
        """List all available templates"""
        return list(self._templates.values())

    def render_template(
        self, template_name: str, variables: Dict[str, Any]
    ) -> Optional[NotificationMessage]:
        """Render template with variables"""
        template = self.get_template(template_name)
        if not template:
            return None

        # Replace variables in subject and body
        subject = template.subject
        body = template.body

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            subject = subject.replace(placeholder, str(value))
            body = body.replace(placeholder, str(value))

        return NotificationMessage(
            notification_type=template.notification_type,
            recipient="",  # Will be set by caller
            subject=subject,
            body=body,
            priority=template.priority,
            template_name=template_name,
            variables=variables,
        )


class NotificationManager:
    """Main notification manager for NEONPAY"""

    def __init__(
        self, config: NotificationConfig, enable_notifications: bool = True
    ) -> None:
        self.enabled = enable_notifications
        self.config = config
        self.template_manager = NotificationTemplateManager()

        # Initialize notifiers
        self._notifiers = {
            NotificationType.EMAIL: EmailNotifier(config),
            NotificationType.TELEGRAM: TelegramNotifier(config),
            NotificationType.SMS: SMSNotifier(config),
            NotificationType.WEBHOOK: WebhookNotifier(config),
            NotificationType.SLACK: SlackNotifier(config),
            NotificationType.DISCORD: DiscordNotifier(config),
        }

        if enable_notifications:
            logger.info("Notification system initialized")

    async def send_notification(self, message: NotificationMessage) -> bool:
        """Send notification using specified type"""
        if not self.enabled:
            return False

        notifier = self._notifiers.get(message.notification_type)
        if not notifier:
            logger.error(f"No notifier found for type: {message.notification_type}")
            return False

        try:
            if message.notification_type == NotificationType.EMAIL:
                if hasattr(notifier, "send_email"):
                    return bool(await notifier.send_email(message))
                else:
                    logger.error("Email notifier does not have send_email method")
                    return False
            elif message.notification_type == NotificationType.TELEGRAM:
                if hasattr(notifier, "send_telegram"):
                    return bool(await notifier.send_telegram(message))
                else:
                    logger.error("Telegram notifier does not have send_telegram method")
                    return False
            elif message.notification_type == NotificationType.SMS:
                if hasattr(notifier, "send_sms"):
                    return bool(await notifier.send_sms(message))
                else:
                    logger.error("SMS notifier does not have send_sms method")
                    return False
            elif message.notification_type == NotificationType.WEBHOOK:
                if hasattr(notifier, "send_webhook"):
                    return bool(await notifier.send_webhook(message))
                else:
                    logger.error("Webhook notifier does not have send_webhook method")
                    return False
            elif message.notification_type == NotificationType.SLACK:
                if hasattr(notifier, "send_slack"):
                    return bool(await notifier.send_slack(message))
                else:
                    logger.error("Slack notifier does not have send_slack method")
                    return False
            elif message.notification_type == NotificationType.DISCORD:
                if hasattr(notifier, "send_discord"):
                    return bool(await notifier.send_discord(message))
                else:
                    logger.error("Discord notifier does not have send_discord method")
                    return False
            else:
                logger.error(
                    f"Unsupported notification type: {message.notification_type}"
                )
                return False

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def send_template_notification(
        self,
        template_name: str,
        recipient: str,
        variables: Dict[str, Any],
        notification_type: Optional[NotificationType] = None,
    ) -> bool:
        """Send notification using template"""
        if not self.enabled:
            return False

        # Render template
        message = self.template_manager.render_template(template_name, variables)
        if not message:
            logger.error(f"Template not found: {template_name}")
            return False

        # Override notification type if specified
        if notification_type:
            message.notification_type = notification_type

        # Set recipient
        message.recipient = recipient

        return await self.send_notification(message)

    async def send_multiple_notifications(
        self, messages: List[NotificationMessage]
    ) -> Dict[str, bool]:
        """Send multiple notifications concurrently"""
        if not self.enabled:
            return {}

        tasks = [self.send_notification(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        return {
            f"{msg.notification_type.value}_{i}": (
                bool(result) if not isinstance(result, Exception) else False
            )
            for i, (msg, result) in enumerate(zip(messages, results))
        }

    def add_custom_template(
        self,
        name: str,
        notification_type: NotificationType,
        subject: str,
        body: str,
        variables: List[str],
        priority: NotificationPriority = NotificationPriority.NORMAL,
    ) -> None:
        """Add custom notification template"""
        template = NotificationTemplate(
            name=name,
            notification_type=notification_type,
            subject=subject,
            body=body,
            variables=variables,
            priority=priority,
        )
        self.template_manager.add_template(template)

    def get_available_templates(self) -> List[str]:
        """Get list of available template names"""
        return [template.name for template in self.template_manager.list_templates()]

    def get_stats(self) -> Dict[str, Any]:
        """Get notification system statistics"""
        return {
            "enabled": self.enabled,
            "available_templates": len(self.template_manager.list_templates()),
            "configured_notifiers": len([n for n in self._notifiers.values() if n]),
            "email_configured": bool(self.config.smtp_host),
            "telegram_configured": bool(self.config.telegram_bot_token),
            "webhook_configured": bool(self.config.webhook_url),
            "slack_configured": bool(self.config.slack_webhook_url),
            "discord_configured": bool(self.config.discord_webhook_url),
        }
"""
NEONPAY Sync - Multi-bot synchronization system
Allows synchronization of payment stages, analytics, and settings between multiple bots
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class SyncDirection(Enum):
    """Synchronization direction"""

    PUSH = "push"  # Send data to target
    PULL = "pull"  # Get data from target
    BIDIRECTIONAL = "bidirectional"  # Sync both ways


class SyncStatus(Enum):
    """Synchronization status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class ConflictResolution(Enum):
    """Conflict resolution strategy"""

    ASK_USER = "ask_user"  # Ask user to choose
    SOURCE_WINS = "source_wins"  # Source data overwrites target
    TARGET_WINS = "target_wins"  # Target data overwrites source
    MERGE = "merge"  # Try to merge data
    SKIP = "skip"  # Skip conflicting items


@dataclass
class SyncConfig:
    """Synchronization configuration"""

    target_bot_token: str
    target_bot_name: str = "Target Bot"
    sync_payment_stages: bool = True
    sync_promo_codes: bool = True
    sync_subscriptions: bool = True
    sync_analytics: bool = False  # Usually disabled for privacy
    sync_templates: bool = True
    sync_settings: bool = True
    direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    conflict_resolution: ConflictResolution = ConflictResolution.ASK_USER
    auto_sync: bool = False
    sync_interval_minutes: int = 60
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None


@dataclass
class SyncResult:
    """Synchronization result"""

    sync_id: str
    status: SyncStatus
    start_time: float
    end_time: Optional[float] = None
    items_synced: Dict[str, int] = field(default_factory=dict)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SyncConflict:
    """Synchronization conflict"""

    item_type: str
    item_id: str
    source_data: Dict[str, Any]
    target_data: Dict[str, Any]
    conflict_reason: str
    resolution: Optional[ConflictResolution] = None


class BotConnector:
    """Connects to remote bots for synchronization"""

    def __init__(self, bot_token: str, bot_name: str = "Remote Bot") -> None:
        self.bot_token = bot_token
        self.bot_name = bot_name
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def get_bot_info(self) -> Dict[str, Any]:
        """Get bot information"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/getMe") as response:
                    if response.status == 200:
                        data = await response.json()
                        result = data.get("result", {})
                        return result if isinstance(result, dict) else {}
                    else:
                        raise Exception(f"Failed to get bot info: {response.status}")
        except Exception as e:
            logger.error(f"Failed to get bot info for {self.bot_name}: {e}")
            return {}

    async def send_data(self, endpoint: str, data: Dict[str, Any]) -> bool:
        """Send data to bot webhook endpoint"""
        if not endpoint:
            return False

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=data) as response:
                    return response.status in [200, 201]
        except Exception as e:
            logger.error(f"Failed to send data to {endpoint}: {e}")
            return False

    async def receive_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Receive data from bot webhook endpoint"""
        if not endpoint:
            return None

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data if isinstance(data, dict) else None
                    else:
                        return None
        except Exception as e:
            logger.error(f"Failed to receive data from {endpoint}: {e}")
            return None


class DataSerializer:
    """Serializes and deserializes data for synchronization"""

    @staticmethod
    def serialize_payment_stages(stages: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize payment stages for sync"""
        serialized = {}
        for stage_id, stage in stages.items():
            if hasattr(stage, "__dict__"):
                serialized[stage_id] = {
                    "title": stage.title,
                    "description": stage.description,
                    "price": stage.price,
                    "label": stage.label,
                    "photo_url": stage.photo_url,
                    "payload": stage.payload,
                    "start_parameter": stage.start_parameter,
                    "created_at": getattr(stage, "created_at", time.time()),
                }
            else:
                serialized[stage_id] = stage
        return serialized

    @staticmethod
    def deserialize_payment_stages(data: Dict[str, Any]) -> Dict[str, Any]:
        """Deserialize payment stages from sync"""
        return data  # Already in correct format

    @staticmethod
    def serialize_promo_codes(promo_codes: List[Any]) -> List[Dict[str, Any]]:
        """Serialize promo codes for sync"""
        serialized = []
        for promo in promo_codes:
            if hasattr(promo, "__dict__"):
                serialized.append(
                    {
                        "code": promo.code,
                        "discount_type": (
                            promo.discount_type.value
                            if hasattr(promo.discount_type, "value")
                            else str(promo.discount_type)
                        ),
                        "discount_value": promo.discount_value,
                        "max_uses": promo.max_uses,
                        "expires_at": promo.expires_at,
                        "min_amount": promo.min_amount,
                        "max_discount": promo.max_discount,
                        "user_limit": promo.user_limit,
                        "active": promo.active,
                        "description": promo.description,
                        "created_at": getattr(promo, "created_at", time.time()),
                    }
                )
            else:
                serialized.append(promo)
        return serialized

    @staticmethod
    def serialize_subscriptions(subscriptions: List[Any]) -> List[Dict[str, Any]]:
        """Serialize subscriptions for sync"""
        serialized = []
        for sub in subscriptions:
            if hasattr(sub, "__dict__"):
                serialized.append(
                    {
                        "user_id": sub.user_id,
                        "plan_id": sub.plan_id,
                        "status": (
                            sub.status.value
                            if hasattr(sub.status, "value")
                            else str(sub.status)
                        ),
                        "start_date": sub.start_date,
                        "end_date": sub.end_date,
                        "auto_renew": sub.auto_renew,
                        "created_at": getattr(sub, "created_at", time.time()),
                    }
                )
            else:
                serialized.append(sub)
        return serialized


class ConflictResolver:
    """Resolves conflicts during synchronization"""

    def __init__(
        self, strategy: ConflictResolution = ConflictResolution.ASK_USER
    ) -> None:
        self.strategy = strategy

    def resolve_conflict(self, conflict: SyncConflict) -> Optional[Dict[str, Any]]:
        """Resolve a synchronization conflict"""
        if self.strategy == ConflictResolution.SOURCE_WINS:
            return conflict.source_data
        elif self.strategy == ConflictResolution.TARGET_WINS:
            return conflict.target_data
        elif self.strategy == ConflictResolution.MERGE:
            return self._merge_data(conflict.source_data, conflict.target_data)
        elif self.strategy == ConflictResolution.SKIP:
            return None  # Skip this item
        else:  # ASK_USER
            return self._ask_user_resolution(conflict)

    def _merge_data(
        self, source: Dict[str, Any], target: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge source and target data"""
        merged = target.copy()

        # Merge non-conflicting fields
        for key, value in source.items():
            if key not in target or target[key] == value:
                merged[key] = value
            elif isinstance(value, dict) and isinstance(target.get(key), dict):
                merged[key] = self._merge_data(value, target[key])
            else:
                # Conflict - use source value
                merged[key] = value

        return merged

    def _ask_user_resolution(self, conflict: SyncConflict) -> Dict[str, Any]:
        """Ask user to resolve conflict (placeholder implementation)"""
        logger.warning(
            f"Conflict resolution needed for {conflict.item_type}:{conflict.item_id}"
        )
        logger.warning(f"Source: {conflict.source_data}")
        logger.warning(f"Target: {conflict.target_data}")
        logger.warning(f"Reason: {conflict.conflict_reason}")

        # For now, default to source wins
        return conflict.source_data


class SyncManager:
    """Main synchronization manager"""

    def __init__(self, neonpay_instance: Any, config: SyncConfig) -> None:
        self.neonpay = neonpay_instance
        self.config = config
        self.connector = BotConnector(config.target_bot_token, config.target_bot_name)
        self.serializer = DataSerializer()
        self.conflict_resolver = ConflictResolver(config.conflict_resolution)
        self._sync_history: List[SyncResult] = []
        self._running = False
        self._sync_task: Optional[asyncio.Task] = None

    async def start_auto_sync(self) -> None:
        """Start automatic synchronization"""
        if not self.config.auto_sync:
            return

        if self._running:
            return

        self._running = True
        self._sync_task = asyncio.create_task(self._auto_sync_loop())
        logger.info(f"Auto-sync started for {self.config.target_bot_name}")

    async def stop_auto_sync(self) -> None:
        """Stop automatic synchronization"""
        self._running = False
        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        logger.info(f"Auto-sync stopped for {self.config.target_bot_name}")

    async def _auto_sync_loop(self) -> None:
        """Main auto-sync loop"""
        while self._running:
            try:
                await asyncio.sleep(self.config.sync_interval_minutes * 60)
                if self._running:
                    await self.sync_all()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Auto-sync error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying

    async def sync_all(self) -> SyncResult:
        """Synchronize all configured data"""
        sync_id = f"sync_{int(time.time())}"
        result = SyncResult(
            sync_id=sync_id, status=SyncStatus.IN_PROGRESS, start_time=time.time()
        )

        try:
            logger.info(f"Starting sync {sync_id} with {self.config.target_bot_name}")

            # Sync payment stages
            if self.config.sync_payment_stages:
                stages_result = await self.sync_payment_stages()
                result.items_synced["payment_stages"] = stages_result.get("synced", 0)
                result.conflicts.extend(stages_result.get("conflicts", []))

            # Sync promo codes
            if self.config.sync_promo_codes:
                promo_result = await self.sync_promo_codes()
                result.items_synced["promo_codes"] = promo_result.get("synced", 0)
                result.conflicts.extend(promo_result.get("conflicts", []))

            # Sync subscriptions
            if self.config.sync_subscriptions:
                sub_result = await self.sync_subscriptions()
                result.items_synced["subscriptions"] = sub_result.get("synced", 0)
                result.conflicts.extend(sub_result.get("conflicts", []))

            # Sync templates
            if self.config.sync_templates:
                template_result = await self.sync_templates()
                result.items_synced["templates"] = template_result.get("synced", 0)
                result.conflicts.extend(template_result.get("conflicts", []))

            # Sync settings
            if self.config.sync_settings:
                settings_result = await self.sync_settings()
                result.items_synced["settings"] = settings_result.get("synced", 0)
                result.conflicts.extend(settings_result.get("conflicts", []))

            result.status = SyncStatus.COMPLETED
            result.end_time = time.time()

            logger.info(f"Sync {sync_id} completed successfully")

        except Exception as e:
            result.status = SyncStatus.FAILED
            result.end_time = time.time()
            result.errors.append(str(e))
            logger.error(f"Sync {sync_id} failed: {e}")

        self._sync_history.append(result)
        return result

    async def sync_payment_stages(self) -> Dict[str, Any]:
        """Synchronize payment stages"""
        logger.info("Syncing payment stages...")

        # Get local stages
        local_stages = self.neonpay.list_payment_stages()
        local_data = self.serializer.serialize_payment_stages(local_stages)

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/payment_stages",
                {"action": "sync", "data": local_data},
            )
            if not success:
                logger.warning("Failed to send payment stages to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/payment_stages"
            )

        # Process conflicts and apply changes
        conflicts: List[Dict[str, Any]] = []
        synced_count = 0

        if target_data:
            for stage_id, stage_data in target_data.items():
                if stage_id in local_stages:
                    # Check for conflicts
                    local_stage = local_stages[stage_id]
                    if self._has_conflict(local_stage, stage_data):
                        conflict = SyncConflict(
                            item_type="payment_stage",
                            item_id=stage_id,
                            source_data=local_data.get(stage_id, {}),
                            target_data=stage_data,
                            conflict_reason="Data mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            # Apply resolved data
                            from .core import PaymentStage

                            stage = PaymentStage(
                                title=resolved_data["title"],
                                description=resolved_data["description"],
                                price=resolved_data["price"],
                                label=resolved_data["label"],
                                photo_url=resolved_data["photo_url"],
                                payload=resolved_data["payload"],
                                start_parameter=resolved_data["start_parameter"],
                            )
                            self.neonpay.create_payment_stage(stage_id, stage)
                            synced_count += 1
                    else:
                        # No conflict, update if needed
                        synced_count += 1
                else:
                    # New stage from target
                    from .core import PaymentStage

                    stage = PaymentStage(
                        title=stage_data["title"],
                        description=stage_data["description"],
                        price=stage_data["price"],
                        label=stage_data["label"],
                        photo_url=stage_data["photo_url"],
                        payload=stage_data["payload"],
                        start_parameter=stage_data["start_parameter"],
                    )
                    self.neonpay.create_payment_stage(stage_id, stage)
                    synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    async def sync_promo_codes(self) -> Dict[str, Any]:
        """Synchronize promo codes"""
        logger.info("Syncing promo codes...")

        # Get local promo codes
        local_promos = []
        if hasattr(self.neonpay, "promotions") and self.neonpay.promotions:
            local_promos = self.neonpay.promotions.list_promo_codes(active_only=False)

        local_data = self.serializer.serialize_promo_codes(local_promos)

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/promo_codes",
                {"action": "sync", "data": local_data},
            )
            if not success:
                logger.warning("Failed to send promo codes to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/promo_codes"
            )

        # Process conflicts and apply changes
        conflicts: List[Dict[str, Any]] = []
        synced_count = 0

        if (
            target_data
            and hasattr(self.neonpay, "promotions")
            and self.neonpay.promotions
        ):
            promo_system = self.neonpay.promotions

            # target_data should be a list of promo codes
            if isinstance(target_data, list):
                promo_list = target_data
            elif isinstance(target_data, dict):
                # If it's a dict, convert to list
                promo_list = list(target_data.values())
            else:
                logger.warning(f"Invalid target_data format: {type(target_data)}")
                return {"synced": 0, "conflicts": []}

            for promo_data in promo_list:
                if not isinstance(promo_data, dict):
                    logger.warning(f"Invalid promo data format: {promo_data}")
                    continue
                code = promo_data["code"]
                existing_promo = promo_system.get_promo_code(code)

                if existing_promo:
                    # Check for conflicts
                    if self._has_conflict(existing_promo, promo_data):
                        conflict = SyncConflict(
                            item_type="promo_code",
                            item_id=code,
                            source_data=self.serializer.serialize_promo_codes(
                                [existing_promo]
                            )[0],
                            target_data=promo_data,
                            conflict_reason="Data mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            # Update promo code
                            from .promotions import DiscountType

                            promo_system.create_promo_code(
                                code=resolved_data["code"],
                                discount_type=DiscountType(
                                    resolved_data["discount_type"]
                                ),
                                discount_value=resolved_data["discount_value"],
                                **{
                                    k: v
                                    for k, v in resolved_data.items()
                                    if k
                                    not in ["code", "discount_type", "discount_value"]
                                },
                            )
                            synced_count += 1
                    else:
                        synced_count += 1
                else:
                    # New promo code from target
                    from .promotions import DiscountType

                    promo_system.create_promo_code(
                        code=promo_data["code"],
                        discount_type=DiscountType(promo_data["discount_type"]),
                        discount_value=promo_data["discount_value"],
                        **{
                            k: v
                            for k, v in promo_data.items()
                            if k not in ["code", "discount_type", "discount_value"]
                        },
                    )
                    synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    async def sync_subscriptions(self) -> Dict[str, Any]:
        """Synchronize subscriptions"""
        logger.info("Syncing subscriptions...")

        # Get local subscriptions
        # local_subs = []  # Not used
        if hasattr(self.neonpay, "subscriptions") and self.neonpay.subscriptions:
            # This would need to be implemented in the subscription manager
            pass

        # local_data = self.serializer.serialize_subscriptions(local_subs)  # Not used

        # Similar implementation to promo codes...
        return {"synced": 0, "conflicts": []}

    async def sync_templates(self) -> Dict[str, Any]:
        """Synchronize templates"""
        logger.info("Syncing templates...")

        # Get local templates
        local_templates = {}
        if hasattr(self.neonpay, "templates") and self.neonpay.templates:
            template_manager = self.neonpay.templates
            templates = template_manager.list_templates()
            for template in templates:
                local_templates[template.name] = template_manager.export_template(
                    template, "json"
                )

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/templates",
                {"action": "sync", "data": local_templates},
            )
            if not success:
                logger.warning("Failed to send templates to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/templates"
            )

        # Process conflicts and apply changes
        conflicts: List[Dict[str, Any]] = []
        synced_count = 0

        if (
            target_data
            and hasattr(self.neonpay, "templates")
            and self.neonpay.templates
        ):
            template_manager = self.neonpay.templates

            for template_name, template_data in target_data.items():
                existing_template = template_manager.get_template(template_name)

                if existing_template:
                    # Check for conflicts
                    existing_json = template_manager.export_template(
                        existing_template, "json"
                    )
                    if existing_json != template_data:
                        conflict = SyncConflict(
                            item_type="template",
                            item_id=template_name,
                            source_data=json.loads(existing_json),
                            target_data=json.loads(template_data),
                            conflict_reason="Template data mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            # Import resolved template
                            template_manager.import_template(json.dumps(resolved_data))
                            synced_count += 1
                    else:
                        synced_count += 1
                else:
                    # New template from target
                    template_manager.import_template(template_data)
                    synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    async def sync_settings(self) -> Dict[str, Any]:
        """Synchronize bot settings"""
        logger.info("Syncing settings...")

        # Get local settings
        local_settings = {
            "thank_you_message": getattr(self.neonpay, "thank_you_message", ""),
            "max_stages": getattr(self.neonpay, "_max_stages", 100),
            "logging_enabled": getattr(self.neonpay, "_enable_logging", True),
        }

        # Send to target bot
        if self.config.direction in [SyncDirection.PUSH, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            success = await self.connector.send_data(
                self.config.webhook_url + "/sync/settings",
                {"action": "sync", "data": local_settings},
            )
            if not success:
                logger.warning("Failed to send settings to target bot")

        # Get from target bot
        target_data = None
        if self.config.direction in [SyncDirection.PULL, SyncDirection.BIDIRECTIONAL]:
            if self.config.webhook_url is None:
                logger.error("Webhook URL is required for sync")
                return {"error": "Webhook URL is required for sync", "synced_count": 0}
            target_data = await self.connector.receive_data(
                self.config.webhook_url + "/sync/settings"
            )

        # Apply target settings
        synced_count = 0
        conflicts: List[Dict[str, Any]] = []

        if target_data:
            for key, value in target_data.items():
                if hasattr(self.neonpay, key):
                    current_value = getattr(self.neonpay, key)
                    if current_value != value:
                        # Conflict detected
                        conflict = SyncConflict(
                            item_type="setting",
                            item_id=key,
                            source_data={key: current_value},
                            target_data={key: value},
                            conflict_reason="Setting value mismatch",
                        )
                        conflicts.append(conflict.__dict__)

                        # Resolve conflict
                        resolved_data = self.conflict_resolver.resolve_conflict(
                            conflict
                        )
                        if resolved_data:
                            setattr(self.neonpay, key, resolved_data[key])
                            synced_count += 1
                    else:
                        synced_count += 1

        return {"synced": synced_count, "conflicts": conflicts}

    def _has_conflict(self, local_item: Any, target_item: Dict[str, Any]) -> bool:
        """Check if there's a conflict between local and target items"""
        if isinstance(local_item, dict):
            local_dict = local_item
        else:
            local_dict = local_item.__dict__ if hasattr(local_item, "__dict__") else {}

        # Compare key fields
        key_fields = ["title", "description", "price", "code", "name"]
        for field_name in key_fields:
            if field_name in local_dict and field_name in target_item:
                if local_dict[field_name] != target_item[field_name]:
                    return True

        return False

    def get_sync_history(self) -> List[SyncResult]:
        """Get synchronization history"""
        return self._sync_history.copy()

    def get_last_sync(self) -> Optional[SyncResult]:
        """Get last synchronization result"""
        return self._sync_history[-1] if self._sync_history else None

    def get_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics"""
        if not self._sync_history:
            return {"total_syncs": 0}

        total_syncs = len(self._sync_history)
        successful_syncs = len(
            [s for s in self._sync_history if s.status == SyncStatus.COMPLETED]
        )
        failed_syncs = len(
            [s for s in self._sync_history if s.status == SyncStatus.FAILED]
        )

        total_items_synced = sum(
            sum(s.items_synced.values()) for s in self._sync_history
        )

        total_conflicts = sum(len(s.conflicts) for s in self._sync_history)

        return {
            "total_syncs": total_syncs,
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "success_rate": (
                (successful_syncs / total_syncs * 100) if total_syncs > 0 else 0
            ),
            "total_items_synced": total_items_synced,
            "total_conflicts": total_conflicts,
            "last_sync": (
                self._sync_history[-1].start_time if self._sync_history else None
            ),
            "auto_sync_enabled": self.config.auto_sync,
            "sync_interval_minutes": self.config.sync_interval_minutes,
        }


class MultiBotSyncManager:
    """Manages synchronization between multiple bots"""

    def __init__(self, neonpay_instance: Any) -> None:
        self.neonpay = neonpay_instance
        self._sync_managers: Dict[str, SyncManager] = {}

    def add_bot(self, config: SyncConfig) -> SyncManager:
        """Add a bot for synchronization"""
        sync_manager = SyncManager(self.neonpay, config)
        self._sync_managers[config.target_bot_name] = sync_manager
        return sync_manager

    def remove_bot(self, bot_name: str) -> bool:
        """Remove a bot from synchronization"""
        if bot_name in self._sync_managers:
            sync_manager = self._sync_managers[bot_name]
            asyncio.create_task(sync_manager.stop_auto_sync())
            del self._sync_managers[bot_name]
            return True
        return False

    async def sync_all_bots(self) -> Dict[str, SyncResult]:
        """Synchronize with all configured bots"""
        results = {}

        for bot_name, sync_manager in self._sync_managers.items():
            try:
                result = await sync_manager.sync_all()
                results[bot_name] = result
            except Exception as e:
                logger.error(f"Failed to sync with {bot_name}: {e}")
                results[bot_name] = SyncResult(
                    sync_id=f"failed_{int(time.time())}",
                    status=SyncStatus.FAILED,
                    start_time=time.time(),
                    end_time=time.time(),
                    errors=[str(e)],
                )

        return results

    async def start_auto_sync_all(self) -> None:
        """Start automatic synchronization for all bots"""
        for sync_manager in self._sync_managers.values():
            await sync_manager.start_auto_sync()

    async def stop_auto_sync_all(self) -> None:
        """Stop automatic synchronization for all bots"""
        for sync_manager in self._sync_managers.values():
            await sync_manager.stop_auto_sync()

    def get_all_sync_stats(self) -> Dict[str, Any]:
        """Get synchronization statistics for all bots"""
        stats = {}
        for bot_name, sync_manager in self._sync_managers.items():
            stats[bot_name] = sync_manager.get_sync_stats()
        return stats

    def list_configured_bots(self) -> List[str]:
        """List all configured bots"""
        return list(self._sync_managers.keys())

