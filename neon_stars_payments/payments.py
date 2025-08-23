import json
import random
from pyrogram import errors
from pyrogram.raw.types import LabeledPrice, Invoice, InputWebDocument
from pyrogram.raw.functions.messages import SendMedia
from pyrogram.raw.types import InputMediaInvoice, DataJSON

from .errors import StarsPaymentError


async def send_invoice(
    client,
    user_id: int,
    amount: int,
    label: str,
    title: str,
    description: str,
    photo_url: str = "https://telegram.org/img/t_logo.png"
):
    """
    Отправляет пользователю счёт на оплату звёздами ⭐

    :param client: pyrogram.Client
    :param user_id: ID пользователя
    :param amount: Сумма в звёздах (XTR)
    :param label: Текст метки (например, "☕ 10 ⭐")
    :param title: Заголовок счёта
    :param description: Описание
    :param photo_url: Картинка для инвойса
    """
    invoice = Invoice(
        currency="XTR",
        prices=[LabeledPrice(label=label, amount=amount)],
    )

    payload = json.dumps({"user_id": user_id, "amount": amount}).encode()

    try:
        peer = await client.resolve_peer(user_id)
    except errors.PeerIdInvalid:
        raise StarsPaymentError("Пользователь не найден")

    try:
        await client.invoke(
            SendMedia(
                peer=peer,
                media=InputMediaInvoice(
                    title=title,
                    description=description,
                    invoice=invoice,
                    payload=payload,
                    provider="",
                    provider_data=DataJSON(data=r"{}"),
                    photo=InputWebDocument(
                        url=photo_url,
                        size=0,
                        mime_type="image/png",
                        attributes=[],
                    ),
                    start_param="stars_payment",
                ),
                message=f"⭐ {label}\n\nСпасибо за поддержку!",
                random_id=random.randint(100000, 999999),
            )
        )
    except errors.RPCError as e:
        raise StarsPaymentError(f"Ошибка отправки счёта: {e}")
