import logging
import re
from typing import Any, Dict, Optional

from .errors import PaymentValidationError, ALLOWED_STAR_AMOUNTS


class PaymentValidator:
    """Утилиты для валидации платежных данных"""

    @staticmethod
    def validate_amount(amount: int) -> bool:
        """Валидация суммы платежа в Telegram Stars"""
        if not isinstance(amount, int):
            raise PaymentValidationError("Amount must be an integer")

        if amount < 1:
            raise PaymentValidationError("Amount must be at least 1 star")

        if amount > 2500:
            raise PaymentValidationError("Amount cannot exceed 2500 stars")

        if amount not in ALLOWED_STAR_AMOUNTS:
            raise PaymentValidationError(f"Amount {amount} is not in allowed amounts: {ALLOWED_STAR_AMOUNTS}")

        return True

    @staticmethod
    def validate_stage_id(stage_id: str) -> bool:
        """Валидация ID этапа платежа"""
        if not isinstance(stage_id, str):
            raise PaymentValidationError("Stage ID must be a string")

        if not stage_id.strip():
            raise PaymentValidationError("Stage ID cannot be empty")

        if len(stage_id) > 64:
            raise PaymentValidationError("Stage ID cannot exceed 64 characters")

        # Проверка на допустимые символы
        if not re.match(r"^[a-zA-Z0-9_-]+$", stage_id):
            raise PaymentValidationError(
                "Stage ID can only contain letters, numbers, underscores, and hyphens"
            )

        return True

    @staticmethod
    def validate_title(title: str) -> bool:
        """Валидация заголовка продукта"""
        if not isinstance(title, str):
            raise PaymentValidationError("Title must be a string")

        if not title.strip():
            raise PaymentValidationError("Title cannot be empty")

        if len(title) > 32:
            raise PaymentValidationError("Title cannot exceed 32 characters")

        return True

    @staticmethod
    def validate_description(description: str) -> bool:
        """Валидация описания продукта"""
        if not isinstance(description, str):
            raise PaymentValidationError("Description must be a string")

        if not description.strip():
            raise PaymentValidationError("Description cannot be empty")

        if len(description) > 255:
            raise PaymentValidationError("Description cannot exceed 255 characters")

        return True

    @staticmethod
    def validate_user_id(user_id: int) -> bool:
        """Валидация ID пользователя Telegram"""
        if not isinstance(user_id, int):
            raise PaymentValidationError("User ID must be an integer")

        if user_id <= 0:
            raise PaymentValidationError("User ID must be positive")

        return True

    @staticmethod
    def validate_logo_url(logo_url: Optional[str]) -> bool:
        """Валидация URL логотипа"""
        if logo_url is None:
            return True

        if not isinstance(logo_url, str):
            raise PaymentValidationError("Logo URL must be a string")

        # Простая проверка URL
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        if not url_pattern.match(logo_url):
            raise PaymentValidationError("Invalid logo URL format")

        return True


class NeonPayLogger:
    """Система логирования для NEONPAY"""

    def __init__(self, name: str = "neonpay", level: int = logging.INFO) -> None:
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Создаем handler только если его еще нет
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def info(self, message: str, **kwargs: Any) -> None:
        """Логирование информационных сообщений"""
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Логирование ошибок"""
        self.logger.error(message, extra=kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Логирование предупреждений"""
        self.logger.warning(message, extra=kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Логирование отладочной информации"""
        self.logger.debug(message, extra=kwargs)

    def payment_sent(self, user_id: int, stage_id: str, amount: int) -> None:
        """Логирование отправки платежа"""
        self.info(
            f"Payment request sent to user {user_id} for stage '{stage_id}' amount {amount} stars"
        )

    def payment_completed(self, payment_id: str, user_id: int, amount: int) -> None:
        """Логирование завершения платежа"""
        self.info(
            f"Payment completed: {payment_id} from user {user_id} amount {amount} stars"
        )

    def payment_failed(self, user_id: int, stage_id: str, error: str) -> None:
        """Логирование неудачного платежа"""
        self.error(f"Payment failed for user {user_id} stage '{stage_id}': {error}")


class PaymentHelper:
    """Вспомогательные утилиты для работы с платежами"""

    @staticmethod
    def format_stars_amount(amount: int) -> str:
        """Форматирование суммы в звездах для отображения"""
        if amount == 1:
            return "1 ⭐"
        return f"{amount} ⭐"

    @staticmethod
    def calculate_fee(amount: int, fee_percentage: float = 0.0) -> int:
        """Расчет комиссии (если потребуется в будущем)"""
        return int(amount * fee_percentage / 100)

    @staticmethod
    def generate_payment_description(title: str, amount: int) -> str:
        """Генерация описания платежа"""
        return f"{title} - {PaymentHelper.format_stars_amount(amount)}"

    @staticmethod
    def extract_user_data(payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Извлечение пользовательских данных из платежа"""
        return {
            "user_id": payment_data.get("user_id"),
            "username": payment_data.get("username"),
            "first_name": payment_data.get("first_name"),
            "last_name": payment_data.get("last_name"),
        }

    @staticmethod
    def is_test_payment(payment_data: Dict[str, Any]) -> bool:
        """Проверка, является ли платеж тестовым"""
        return bool(payment_data.get("is_test", False))
