class StarsPaymentError(Exception):
    """
    Базовый класс ошибок для библиотеки NeonPay.

    Используется для всех исключений, связанных с оплатой звёздами (XTR) в Telegram-ботах.

    Примеры использования:

        raise StarsPaymentError("Пользователь не найден")
        raise StarsPaymentError("Ошибка отправки счета")
    """
    pass
