# Руководство по безопасности - NEONPAY

Этот документ описывает лучшие практики безопасности для использования NEONPAY в продакшн среде.

## Содержание

1. [Безопасность токенов](#безопасность-токенов)
2. [Валидация платежей](#валидация-платежей)
3. [Защита данных](#защита-данных)
4. [Обработка ошибок](#обработка-ошибок)
5. [Безопасность логирования](#безопасность-логирования)
6. [Чек-лист для продакшена](#чек-лист-для-продакшена)

## Безопасность токенов

### Защита токена бота

**❌ Никогда не делайте так:**
```python
# НЕ ДЕЛАЙТЕ: Хардкод токенов в исходном коде
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**✅ Делайте так:**
```python
import os

# ДЕЛАЙТЕ: Используйте переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Переменная окружения BOT_TOKEN обязательна")
```

### Переменные окружения

Создайте файл `.env` (никогда не коммитьте в систему контроля версий):
```bash
# .env
BOT_TOKEN=ваш_токен_бота_здесь
API_ID=ваш_api_id_здесь
API_HASH=ваш_api_hash_здесь
DATABASE_URL=postgresql://user:pass@localhost/db
```

Загрузите с помощью python-dotenv:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Валидация платежей

### Проверка сумм платежей

```python
@neonpay.on_payment
async def handle_payment(result):
    # Всегда проверяйте сумму платежа
    expected_amount = get_expected_amount(result.stage_id)
    
    if result.amount != expected_amount:
        logger.warning(
            f"Несоответствие суммы платежа: ожидалось {expected_amount}, "
            f"получено {result.amount} от пользователя {result.user_id}"
        )
        return
    
    # Обрабатывайте платеж только после валидации
    await process_payment(result)
```

### Валидация ID этапов

```python
async def safe_send_payment(user_id: int, stage_id: str):
    # Проверьте, что этап существует
    stage = neonpay.get_payment_stage(stage_id)
    if not stage:
        logger.error(f"Неверный stage_id: {stage_id}")
        await bot.send_message(user_id, "Вариант оплаты недоступен.")
        return
    
    # Проверьте права пользователя
    if not await user_can_purchase(user_id, stage_id):
        await bot.send_message(user_id, "У вас нет прав на покупку этого товара.")
        return
    
    # Отправьте платеж
    await neonpay.send_payment(user_id, stage_id)
```

## Защита данных

### Обработка данных пользователей

```python
import hashlib

def hash_user_id(user_id: int) -> str:
    """Хеширование ID пользователя для логирования (одностороннее)"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:8]

@neonpay.on_payment
async def handle_payment(result):
    # Логируйте с хешированным ID пользователя
    hashed_id = hash_user_id(result.user_id)
    logger.info(f"Платеж получен от пользователя {hashed_id}: {result.amount} звезд")
    
    # Сохраняйте в базе данных с правильным шифрованием
    await store_payment_securely(result)
```

### Безопасность базы данных

```python
import asyncpg
from cryptography.fernet import Fernet

class SecurePaymentStorage:
    def __init__(self, db_url: str, encryption_key: str):
        self.db_url = db_url
        self.cipher = Fernet(encryption_key.encode())
    
    async def store_payment(self, payment_data: dict):
        # Шифруйте чувствительные данные
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

## Обработка ошибок

### Безопасные сообщения об ошибках

```python
async def handle_payment_error(user_id: int, error: Exception):
    # Логируйте полные детали ошибки
    logger.error(f"Ошибка платежа для пользователя {user_id}: {error}", exc_info=True)
    
    # Отправьте общее сообщение пользователю
    await bot.send_message(
        user_id, 
        "Что-то пошло не так с вашим платежом. Попробуйте позже."
    )
    
    # Не раскрывайте внутренние детали
    # ❌ НЕ ДЕЛАЙТЕ: await bot.send_message(user_id, f"Ошибка: {str(error)}")
```

### Валидация входных данных

```python
def validate_user_input(user_id: int, stage_id: str) -> bool:
    """Валидация входных данных пользователя перед обработкой"""
    
    # Проверьте, что user_id валиден
    if not isinstance(user_id, int) or user_id <= 0:
        return False
    
    # Проверьте формат stage_id
    if not isinstance(stage_id, str) or len(stage_id) > 100:
        return False
    
    # Проверьте на подозрительные паттерны
    if any(char in stage_id for char in ['<', '>', '&', '"', "'"]):
        return False
    
    return True
```

## Безопасность логирования

### Конфигурация безопасного логирования

```python
import logging
import logging.handlers
from datetime import datetime

def setup_secure_logging():
    """Настройка конфигурации безопасного логирования"""
    
    # Создайте форматтер, исключающий чувствительные данные
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Обработчик файлов с ротацией
    file_handler = logging.handlers.RotatingFileHandler(
        'bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Обработчик консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Настройте логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Отключите отладку в продакшене
    if os.getenv("ENVIRONMENT") == "production":
        logger.setLevel(logging.WARNING)
```

### Фильтрация чувствительных данных

```python
class SensitiveDataFilter(logging.Filter):
    """Фильтр для удаления чувствительных данных из логов"""
    
    def filter(self, record):
        # Удалите токены из сообщений лога
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Замените паттерны токенов
            import re
            record.msg = re.sub(
                r'\b\d{10}:[A-Za-z0-9_-]{35}\b',
                '[TOKEN_REDACTED]',
                msg
            )
        return True

# Примените фильтр
logger.addFilter(SensitiveDataFilter())
```

## Чек-лист для продакшена

### Проверка безопасности перед развертыванием

- [ ] **Переменные окружения**: Все чувствительные данные в переменных окружения
- [ ] **Защита токенов**: Токены ботов не в исходном коде
- [ ] **Безопасность базы данных**: Зашифрованные соединения и данные
- [ ] **Валидация входных данных**: Все входные данные пользователей валидированы
- [ ] **Обработка ошибок**: Общие сообщения об ошибках для пользователей
- [ ] **Логирование**: Чувствительные данные отфильтрованы из логов
- [ ] **HTTPS**: Все webhook используют HTTPS
- [ ] **Ограничение скорости**: Реализовано ограничение скорости для платежей
- [ ] **Мониторинг**: Настроен мониторинг платежей и оповещения
- [ ] **Резервное копирование**: Регулярные резервные копии базы данных

### Ограничение скорости

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
        
        # Удалите старые платежи вне окна
        user_payments[:] = [t for t in user_payments if now - t < self.window]
        
        # Проверьте, что под лимитом
        return len(user_payments) < self.max_payments
    
    def record_payment(self, user_id: int):
        self.user_payments[user_id].append(time.time())

# Использование
rate_limiter = PaymentRateLimiter()

async def safe_send_payment(user_id: int, stage_id: str):
    if not rate_limiter.can_make_payment(user_id):
        await bot.send_message(
            user_id, 
            "Слишком много попыток оплаты. Попробуйте позже."
        )
        return
    
    await neonpay.send_payment(user_id, stage_id)
    rate_limiter.record_payment(user_id)
```

### Мониторинг и оповещения

```python
import asyncio
from datetime import datetime, timedelta

class PaymentMonitor:
    def __init__(self):
        self.payment_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    async def monitor_payments(self):
        """Мониторинг паттернов платежей на предмет аномалий"""
        while True:
            await asyncio.sleep(300)  # Проверяйте каждые 5 минут
            
            # Проверьте на необычные паттерны платежей
            recent_payments = self.get_recent_payments()
            
            if len(recent_payments) > 100:  # Порог
                await send_alert(f"Высокий объем платежей: {len(recent_payments)} платежей")
            
            # Проверьте на ошибки
            recent_errors = self.get_recent_errors()
            if len(recent_errors) > 10:  # Порог
                await send_alert(f"Высокий уровень ошибок: {len(recent_errors)} ошибок")
    
    async def send_alert(self, message: str):
        """Отправка оповещения о безопасности"""
        # Отправьте в систему мониторинга
        logger.critical(f"ОПОВЕЩЕНИЕ О БЕЗОПАСНОСТИ: {message}")
```

## Частые ошибки безопасности

### 1. Раскрытие внутренних ошибок

**❌ Неправильно:**
```python
except Exception as e:
    await bot.send_message(user_id, f"Ошибка: {str(e)}")
```

**✅ Правильно:**
```python
except Exception as e:
    logger.error(f"Ошибка платежа: {e}")
    await bot.send_message(user_id, "Платеж не удался. Попробуйте еще раз.")
```

### 2. Хранение чувствительных данных в логах

**❌ Неправильно:**
```python
logger.info(f"Пользователь {user_id} заплатил с токеном {bot_token}")
```

**✅ Правильно:**
```python
logger.info(f"Пользователь {hash_user_id(user_id)} завершил платеж")
```

### 3. Отсутствие валидации входных данных

**❌ Неправильно:**
```python
await neonpay.send_payment(user_id, stage_id)  # Нет валидации
```

**✅ Правильно:**
```python
if validate_user_input(user_id, stage_id):
    await neonpay.send_payment(user_id, stage_id)
else:
    await bot.send_message(user_id, "Неверный запрос.")
```

## Реагирование на инциденты

### Чек-лист инцидентов безопасности

1. **Немедленное реагирование**
   - [ ] Отключите затронутого бота при необходимости
   - [ ] Просмотрите логи на предмет подозрительной активности
   - [ ] Смените токен бота, если он скомпрометирован
   - [ ] Уведомите пользователей в случае утечки данных

2. **Расследование**
   - [ ] Проанализируйте вектор атаки
   - [ ] Определите затронутых пользователей
   - [ ] Задокументируйте детали инцидента
   - [ ] Сохраните доказательства

3. **Восстановление**
   - [ ] Исправьте уязвимости безопасности
   - [ ] Обновите меры безопасности
   - [ ] Тщательно протестируйте систему
   - [ ] Мониторьте на предмет продолжения атак

4. **Постинцидентные действия**
   - [ ] Обновите документацию по безопасности
   - [ ] Проведите обзор безопасности
   - [ ] Внедрите дополнительные защитные меры
   - [ ] Обучите команду на основе извлеченных уроков

## Ресурсы

- [Безопасность Telegram Bot](https://core.telegram.org/bots/security)
- [Руководства по безопасности OWASP](https://owasp.org/)
- [Лучшие практики безопасности Python](https://python-security.readthedocs.io/)

---

**Помните: Безопасность - это непрерывный процесс, а не разовая настройка. Регулярно пересматривайте и обновляйте ваши меры безопасности.**
