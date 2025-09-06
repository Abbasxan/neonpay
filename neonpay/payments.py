"""
Pyrogram NeonStars Adapter for NEONPAY
Handles Telegram Stars payments via raw updates.

Requires Pyrogram (v2.0+ recommended).

Features:
- Send donation invoices to users
- Automatic pre-checkout handling
- Process successful payments with callback registration
"""

import asyncio
import json
import logging
import secrets
from typing import Any, Callable, Optional

from .errors import StarsPaymentError

# Pyrogram imports will be loaded lazily when needed
PYROGRAM_AVAILABLE = None

# Initialize Pyrogram types as None - will be loaded when needed
LabeledPrice: Any = None
Invoice: Any = None
InputWebDocument: Any = None
InputMediaInvoice: Any = None
DataJSON: Any = None
UpdateBotPrecheckoutQuery: Any = None
MessageActionPaymentSentMe: Any = None
SendMedia: Any = None
SetBotPrecheckoutResults: Any = None


def _load_pyrogram() -> bool:
    """Lazy load Pyrogram types and functions"""
    global PYROGRAM_AVAILABLE
    global LabeledPrice
    global Invoice
    global InputWebDocument
    global InputMediaInvoice
    global DataJSON
    global UpdateBotPrecheckoutQuery
    global MessageActionPaymentSentMe
    global SendMedia
    global SetBotPrecheckoutResults

    if PYROGRAM_AVAILABLE is None:
        try:
            from pyrogram.raw.functions.messages import SendMedia as _SendMedia
            from pyrogram.raw.functions.messages import (
                SetBotPrecheckoutResults as _SetBotPrecheckoutResults,
            )
            from pyrogram.raw.types import DataJSON as _DataJSON
            from pyrogram.raw.types import InputMediaInvoice as _InputMediaInvoice
            from pyrogram.raw.types import InputWebDocument as _InputWebDocument
            from pyrogram.raw.types import Invoice as _Invoice
            from pyrogram.raw.types import LabeledPrice as _LabeledPrice
            from pyrogram.raw.types import (
                MessageActionPaymentSentMe as _MessageActionPaymentSentMe,
            )
            from pyrogram.raw.types import (
                UpdateBotPrecheckoutQuery as _UpdateBotPrecheckoutQuery,
            )

            # Update global variables
            LabeledPrice = _LabeledPrice
            Invoice = _Invoice
            InputWebDocument = _InputWebDocument
            InputMediaInvoice = _InputMediaInvoice
            DataJSON = _DataJSON
            UpdateBotPrecheckoutQuery = _UpdateBotPrecheckoutQuery
            MessageActionPaymentSentMe = _MessageActionPaymentSentMe
            SendMedia = _SendMedia
            SetBotPrecheckoutResults = _SetBotPrecheckoutResults

            PYROGRAM_AVAILABLE = True
        except ImportError:
            PYROGRAM_AVAILABLE = False
    return PYROGRAM_AVAILABLE


logger = logging.getLogger(__name__)


class NeonStars:
    def __init__(
        self, app: Any, thank_you: str = "Thank you for your support!"
    ) -> None:
        """
        :param app: pyrogram.Client instance
        :param thank_you: message of appreciation to send along with invoices
        """
        self.logger = logging.getLogger(__name__)
        if not PYROGRAM_AVAILABLE:
            raise ImportError(
                "Pyrogram is not installed. Install with: pip install pyrogram"
            )

        self.app = app
        self.thank_you = thank_you
        self._payment_callback: Optional[Callable[[int, int], Any]] = None

        # Subscribe to raw updates
        app.add_handler(self._on_raw_update, group=-1)

    def on_payment(self, callback: Callable[[int, int], Any]) -> None:
        """
        Register a callback to be called after a successful payment.

        The callback may be:
        - sync function: callback(user_id: int, amount: int) -> Any
        - async function: async callback(user_id: int, amount: int) -> Any

        If the callback is synchronous and returns a value, it will be logged.
        """
        self._payment_callback = callback

    async def send_donate(
        self,
        user_id: int,
        amount: int,
        label: str,
        title: str,
        description: str,
        photo_url: str = "https://telegram.org/img/t_logo.png",
    ) -> None:
        """Send an invoice (Telegram Stars donation request) to the user."""
        if not _load_pyrogram():
            raise ImportError(
                "Pyrogram is not installed. Install with: pip install pyrogram"
            )

        try:
            peer = await self.app.resolve_peer(user_id)
        except Exception:
            raise StarsPaymentError("User not found")

        # Ensure Pyrogram types are loaded
        if Invoice is None or LabeledPrice is None or InputMediaInvoice is None:
            raise StarsPaymentError("Pyrogram types not loaded")

        invoice = Invoice(
            currency="XTR",
            prices=[LabeledPrice(label=label, amount=amount)],
        )

        media = InputMediaInvoice(
            title=title,
            description=description,
            invoice=invoice,
            payload=json.dumps({"user_id": user_id, "amount": amount}).encode(),
            provider="",
            provider_data=DataJSON(data="{}"),
            photo=InputWebDocument(
                url=photo_url, size=0, mime_type="image/png", attributes=[]
            ),
            start_param="stars_donate",
        )

        try:
            await self.app.invoke(
                SendMedia(
                    peer=peer,
                    media=media,
                    message=f"{label}\n\n{description}\n\n{self.thank_you}",
                    random_id=secrets.randbits(64),
                )
            )
        except Exception as e:
            raise StarsPaymentError(f"Failed to send invoice: {e}")

    async def _on_raw_update(
        self, client: Any, update: Any, users: Any, chats: Any
    ) -> None:
        """
        Automatically handle pre-checkout requests and successful payments.
        """
        if not _load_pyrogram():
            return  # Skip processing if Pyrogram is not available

        try:
            # Pre-checkout query
            if UpdateBotPrecheckoutQuery is not None and isinstance(
                update, UpdateBotPrecheckoutQuery
            ):
                await client.invoke(
                    SetBotPrecheckoutResults(query_id=update.query_id, success=True)
                )
                return

            # Successful payment
            if (
                hasattr(update, "message")
                and MessageActionPaymentSentMe is not None
                and isinstance(update.message.action, MessageActionPaymentSentMe)
                and hasattr(update.message, "from_id")
                and hasattr(update.message.from_id, "user_id")
            ):
                user_id = update.message.from_id.user_id
                amount = update.message.action.total_amount

                if self._payment_callback:
                    result = self._payment_callback(user_id, amount)

                    if asyncio.iscoroutine(result):
                        await result
                    else:
                        # For sync callbacks we log the return value (if any)
                        if result is not None:
                            self.logger.debug(
                                f"Synchronous payment callback returned: {result}"
                            )

        except Exception as e:
            self.logger.error(f"Error in _on_raw_update: {e}")
