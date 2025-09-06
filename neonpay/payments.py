"""
Pyrogram NeonStars Adapter for NEONPAY
Handles Telegram Stars payments via raw updates.

Requires Pyrogram (v2.0+ recommended).

Features:
- Send donation invoices to users
- Automatic pre-checkout handling
- Process successful payments with callback registration
"""

import json
import random
import logging
import asyncio
from typing import Any, Callable, Optional

# Legacy compatibility - only import if pyrogram is available
try:
    from pyrogram.raw.types import (
        LabeledPrice,
        Invoice,
        InputWebDocument,
        InputMediaInvoice,
        DataJSON,
        UpdateBotPrecheckoutQuery,
        MessageActionPaymentSentMe,
    )
    from pyrogram.raw.functions.messages import SendMedia, SetBotPrecheckoutResults

    PYROGRAM_AVAILABLE = True
except ImportError:
    PYROGRAM_AVAILABLE = False

from .errors import StarsPaymentError

logger = logging.getLogger(__name__)


class NeonStars:
    def __init__(self, app: Any, thank_you: str = "Спасибо за поддержку!") -> None:
        """
        :param app: pyrogram.Client
        :param thank_you: сообщение благодарности пользователю
        """
        self.logger = logging.getLogger(__name__)
        if not PYROGRAM_AVAILABLE:
            raise ImportError(
                "Pyrogram is not installed. Install with: pip install pyrogram"
            )

        self.app = app
        self.thank_you = thank_you
        self._payment_callback: Optional[Callable[[int, int], None]] = None

        # Подписка на raw обновления
        app.add_handler(self._on_raw_update, group=-1)

    def on_payment(self, callback: Callable[[int, int], Any]) -> None:
        """
        Регистрирует callback, который будет вызван при успешной оплате.
        callback(user_id: int, amount: int)
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
        """Отправить пользователю инвойс"""
        try:
            peer = await self.app.resolve_peer(user_id)
        except Exception:
            raise StarsPaymentError("Пользователь не найден")

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
                    random_id=random.getrandbits(64),
                )
            )
        except Exception as e:
            raise StarsPaymentError(f"Ошибка отправки счета: {e}")

    async def _on_raw_update(
        self, client: Any, update: Any, users: Any, chats: Any
    ) -> None:
        """Автоматическая обработка pre_checkout и успешной оплаты"""
        try:
            # Pre-checkout запрос
            if isinstance(update, UpdateBotPrecheckoutQuery):
                await client.invoke(
                    SetBotPrecheckoutResults(query_id=update.query_id, success=True)
                )
                return

            # Успешная оплата Stars
            if (
                hasattr(update, "message")
                and isinstance(update.message.action, MessageActionPaymentSentMe)
                and hasattr(update.message, "from_id")
                and hasattr(update.message.from_id, "user_id")
            ):
                user_id = update.message.from_id.user_id
                amount = update.message.action.total_amount
                if self._payment_callback:
                    callback_result = self._payment_callback(user_id, amount)
                    if asyncio.iscoroutine(callback_result):
                        await callback_result

        except Exception as e:
            self.logger.error(f"Error in _on_raw_update: {e}")
