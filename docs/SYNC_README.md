# 🔄 NEONPAY Multi-Bot Synchronization

**Синхронизация между несколькими ботами** - это революционная функция NEONPAY, которая позволяет управлять несколькими Telegram ботами как единой экосистемой.

## 🚀 Что это дает?

### **До синхронизации:**
```python
# Пользователю нужно было:
# 1. Создать продукт в боте A (50+ строк)
# 2. Создать тот же продукт в боте B (50+ строк)
# 3. Создать тот же продукт в боте C (50+ строк)
# 4. Обновлять цены в каждом боте отдельно
# 5. Следить за промокодами в каждом боте
# ИТОГО: ~200+ строк кода + постоянное дублирование работы
```

### **После синхронизации:**
```python
# Теперь достаточно:
from neonpay import MultiBotSyncManager, BotSyncConfig, SyncDirection

multi_sync = MultiBotSyncManager(neonpay)

# Настроить синхронизацию с другими ботами
config = BotSyncConfig(
    target_bot_token="OTHER_BOT_TOKEN",
    target_bot_name="Store Bot",
    direction=SyncDirection.BIDIRECTIONAL,
    auto_sync=True
)

multi_sync.add_bot(config)

# Создать продукт ОДИН РАЗ
neonpay.create_payment_stage("premium", PaymentStage(
    title="Premium Access",
    description="Unlock all features",
    price=100
))

# Автоматически синхронизируется со ВСЕМИ ботами!
# ИТОГО: ~10 строк кода!
```

## 🎯 Реальные преимущества

### **1. Управление несколькими магазинами**
```python
# Главный бот - управляет всеми продуктами
main_store = BotSyncConfig(
    target_bot_token="MAIN_STORE_TOKEN",
    direction=SyncDirection.PUSH  # Отправляет данные
)

# Филиалы - получают продукты автоматически
branch1 = BotSyncConfig(
    target_bot_token="BRANCH1_TOKEN", 
    direction=SyncDirection.PULL  # Получает данные
)

branch2 = BotSyncConfig(
    target_bot_token="BRANCH2_TOKEN",
    direction=SyncDirection.PULL
)

multi_sync.add_bot(main_store)
multi_sync.add_bot(branch1) 
multi_sync.add_bot(branch2)

# Создал продукт в главном боте - автоматически появился во всех филиалах!
```

### **2. A/B тестирование**
```python
# Бот A - тестирует новые цены
bot_a = BotSyncConfig(
    target_bot_token="BOT_A_TOKEN",
    direction=SyncDirection.PUSH
)

# Бот B - получает результаты тестов
bot_b = BotSyncConfig(
    target_bot_token="BOT_B_TOKEN", 
    direction=SyncDirection.PULL
)

# Автоматически сравниваете результаты между ботами!
```

### **3. Резервное копирование**
```python
# Основной бот
main_bot = BotSyncConfig(
    target_bot_token="MAIN_BOT_TOKEN",
    direction=SyncDirection.PUSH
)

# Резервный бот
backup_bot = BotSyncConfig(
    target_bot_token="BACKUP_BOT_TOKEN",
    direction=SyncDirection.PULL
)

# Если основной бот упал - резервный автоматически получил все данные!
```

## 🔧 Настройка за 3 минуты

### **Шаг 1: Установка**
```bash
pip install neonpay[sync]
```

### **Шаг 2: Настройка**
```python
from neonpay import create_neonpay, MultiBotSyncManager, BotSyncConfig

# Ваш основной бот
neonpay = create_neonpay(bot_instance=your_bot)
multi_sync = MultiBotSyncManager(neonpay)

# Добавить бота для синхронизации
config = BotSyncConfig(
    target_bot_token="OTHER_BOT_TOKEN",
    target_bot_name="Partner Bot",
    direction=SyncDirection.BIDIRECTIONAL,
    auto_sync=True,
    sync_interval_minutes=30
)

multi_sync.add_bot(config)
```

### **Шаг 3: Запуск**
```python
# Запустить автоматическую синхронизацию
await multi_sync.start_auto_sync_all()

# Или синхронизировать вручную
await multi_sync.sync_all_bots()
```

## 📊 Что синхронизируется?

### **✅ Payment Stages (Продукты)**
- Названия и описания товаров
- Цены и настройки платежей
- Фотографии и параметры

### **✅ Promo Codes (Промокоды)**
- Коды скидок
- Размеры скидок
- Ограничения использования

### **✅ Templates (Шаблоны)**
- Готовые конфигурации ботов
- Темы оформления
- Каталоги продуктов

### **✅ Settings (Настройки)**
- Сообщения благодарности
- Лимиты и ограничения
- Конфигурации бота

## 🔄 Направления синхронизации

### **Push (Отправка)**
```python
# Отправляете данные в другой бот
direction=SyncDirection.PUSH
```

### **Pull (Получение)**
```python
# Получаете данные из другого бота
direction=SyncDirection.PULL
```

### **Bidirectional (Двусторонняя)**
```python
# Обмениваетесь данными в обе стороны
direction=SyncDirection.BIDIRECTIONAL
```

## ⚔️ Разрешение конфликтов

### **Source Wins (Источник побеждает)**
```python
# Ваши данные перезаписывают чужие
conflict_resolution=ConflictResolution.SOURCE_WINS
```

### **Target Wins (Цель побеждает)**
```python
# Чужие данные перезаписывают ваши
conflict_resolution=ConflictResolution.TARGET_WINS
```

### **Merge (Слияние)**
```python
# Пытается объединить данные
conflict_resolution=ConflictResolution.MERGE
```

## 🛠️ CLI команды

```bash
# Добавить бота для синхронизации
neonpay sync add-bot --token "BOT_TOKEN" --name "Store Bot" \
  --direction bidirectional --auto-sync

# Синхронизировать со всеми ботами
neonpay sync sync-all

# Показать статистику
neonpay sync stats

# Список настроенных ботов
neonpay sync list-bots
```

## 📈 Статистика использования

### **Экономия времени:**
- **Создание продуктов**: с 200+ строк до 10 строк (**95% экономии**)
- **Обновление цен**: с ручного обновления в каждом боте до автоматического
- **Управление промокодами**: с дублирования до централизованного управления

### **Преимущества:**
- **Масштабируемость**: легко добавлять новые боты
- **Надежность**: автоматическое резервное копирование
- **Гибкость**: разные стратегии синхронизации
- **Мониторинг**: детальная статистика синхронизации

## 🌐 Веб-интерфейс

```python
from neonpay.web_sync import run_sync_server

# Запустить веб-сервер для синхронизации
await run_sync_server(
    neonpay, 
    host="0.0.0.0", 
    port=8080,
    webhook_secret="your_secret"
)
```

**Доступные endpoints:**
- `POST /sync/payment_stages` - синхронизация продуктов
- `POST /sync/promo_codes` - синхронизация промокодов
- `GET /sync/status` - статус синхронизации
- `GET /health` - проверка здоровья

## 🎉 Реальные примеры использования

### **1. Сеть магазинов**
```python
# Главный магазин управляет всеми продуктами
# Филиалы автоматически получают обновления
# Изменение цены в главном магазине → автоматически во всех филиалах
```

### **2. Партнерская программа**
```python
# Вы создаете продукты
# Партнеры получают их автоматически
# Вы получаете комиссию с продаж партнеров
```

### **3. Тестирование**
```python
# Бот A - тестирует новые функции
# Бот B - стабильная версия
# Автоматическое сравнение результатов
```

### **4. Резервное копирование**
```python
# Основной бот работает
# Резервный бот получает все данные
# При падении основного - переключаетесь на резервный
```

## 🚀 Начните прямо сейчас!

```python
# 1. Установите NEONPAY
pip install neonpay[sync]

# 2. Скопируйте этот код
from neonpay import create_neonpay, MultiBotSyncManager, BotSyncConfig, SyncDirection

neonpay = create_neonpay(bot_instance=your_bot)
multi_sync = MultiBotSyncManager(neonpay)

# 3. Добавьте бота для синхронизации
config = BotSyncConfig(
    target_bot_token="YOUR_OTHER_BOT_TOKEN",
    target_bot_name="Partner Bot",
    direction=SyncDirection.BIDIRECTIONAL,
    auto_sync=True
)

multi_sync.add_bot(config)

# 4. Запустите синхронизацию
await multi_sync.start_auto_sync_all()

# Готово! Теперь ваши боты синхронизируются автоматически! 🎉
```

**Синхронизация между ботами** - это не просто функция, это **революция в управлении Telegram ботами**! 

Больше никакого дублирования кода, никакой ручной синхронизации, никаких ошибок при обновлении данных в нескольких ботах.

**Один продукт → все боты автоматически!** 🚀
