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
        }

        if enable_notifications:
            logger.info("Notification system initialized")

        # Mapping notification type -> notifier method name
        self._notifier_methods = {
            NotificationType.EMAIL: "send_email",
            NotificationType.TELEGRAM: "send_telegram",
            NotificationType.SMS: "send_sms",
            NotificationType.WEBHOOK: "send_webhook",
            NotificationType.SLACK: "send_slack",
        }

    async def send_notification(self, message: NotificationMessage) -> bool:
        """Send notification using specified type"""
        if not self.enabled:
            return False

        notifier = self._notifiers.get(message.notification_type)
        if not notifier:
            logger.error(f"No notifier found for type: {message.notification_type}")
            return False

        method_name = self._notifier_methods.get(message.notification_type)
        if not method_name:
            logger.error(f"No method mapping found for type: {message.notification_type}")
            return False

        send_method = getattr(notifier, method_name, None)
        if not callable(send_method):
            logger.error(f"{message.notification_type.value} notifier does not have {method_name} method")
            return False

        try:
            return bool(await send_method(message))
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
        }

