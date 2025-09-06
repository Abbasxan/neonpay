"""
Raw Telegram Bot API adapter for NEONPAY
Direct API integration without external bot libraries
"""

import asyncio
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Optional, Union

import aiohttp

from ..core import PaymentAdapter, PaymentStage
from ..errors import NeonPayError

logger = logging.getLogger(__name__)


class RawAPIAdapter(PaymentAdapter):
    """Raw Telegram Bot API adapter with enhanced error handling"""

    def __init__(
        self, bot_token: str, webhook_url: Optional[str] = None, timeout: int = 30
    ) -> None:
        """
        Initialize Raw API adapter

        Args:
            bot_token: Telegram bot token
            webhook_url: Optional webhook URL for payment notifications
            timeout: HTTP request timeout in seconds
        """
        self.bot_token = bot_token
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self._session: Optional[aiohttp.ClientSession] = None
        self._payment_callback: Optional[
            Callable[[Any], Union[None, Awaitable[None]]]
        ] = None

        # Configure timeout
        self._timeout = aiohttp.ClientTimeout(total=timeout)

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)
        return self._session

    async def _make_api_request(
        self, method: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make API request with enhanced error handling"""
        session = await self._get_session()

        try:
            async with session.post(f"{self.api_url}/{method}", data=data) as response:
                if response.status != 200:
                    raise NeonPayError(f"HTTP {response.status}: {response.reason}")

                result = await response.json()

                if not result.get("ok"):
                    error_msg = result.get("description", "Unknown API error")
                    raise NeonPayError(f"Telegram API error: {error_msg}")

                result_data = result.get("result", {})
                if isinstance(result_data, dict):
                    return result_data
                else:
                    return {}

        except asyncio.TimeoutError:
            raise NeonPayError("Request timeout. Please try again.")
        except aiohttp.ClientError as e:
            raise NeonPayError(f"Network error. Please check your connection: {e}")
        except Exception as e:
            raise NeonPayError(f"API error: {e}")

    async def send_invoice(self, user_id: int, stage: PaymentStage) -> bool:
        """
        Send payment invoice using Telegram Bot API

        Args:
            user_id: Telegram user ID
            stage: Payment stage configuration

        Returns:
            True if invoice was sent successfully
        """
        try:
            # Prepare invoice data
            invoice_data = {
                "chat_id": user_id,
                "title": stage.title,
                "description": stage.description,
                "payload": json.dumps(stage.payload),
                "provider_token": stage.provider_token,
                "currency": "XTR",
                "prices": json.dumps(
                    [{"label": stage.label, "amount": stage.price * 100}]
                ),
                "start_parameter": stage.start_parameter,
            }

            # Add photo if provided
            if stage.photo_url:
                invoice_data["photo_url"] = stage.photo_url

            # Send invoice
            result = await self._make_api_request("sendInvoice", invoice_data)

            if result:
                logger.info(f"Invoice sent to user {user_id}: {stage.price} Stars")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to send invoice: {e}")
            return False

    async def setup_handlers(
        self, payment_callback: Callable[[Any], Union[None, Awaitable[None]]]
    ) -> None:
        """
        Setup payment event handlers

        Args:
            payment_callback: Function to call when payment is completed
        """
        self._payment_callback = payment_callback
        logger.info("Raw API adapter handlers configured")

    def get_library_info(self) -> Dict[str, Any]:
        """Get information about the bot library"""
        return {
            "library": "Raw Telegram Bot API",
            "version": "2.0.0",
            "features": [
                "Direct API integration",
                "Webhook support",
                "Enhanced error handling",
            ],
        }

    async def close(self) -> None:
        """Close aiohttp session"""
        if self._session and not self._session.closed:
            await self._session.close()
            logger.info("Raw API adapter session closed")

    def __del__(self) -> None:
        """Cleanup on deletion"""
        if hasattr(self, "_session") and self._session and not self._session.closed:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.close())
                else:
                    loop.run_until_complete(self.close())
            except RuntimeError:
                # No event loop in this context
                pass
