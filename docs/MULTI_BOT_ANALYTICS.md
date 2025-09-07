# 📊 NEONPAY Multi-Bot Analytics

**Автоматическое отслеживание всех событий для ботов** - это революционная система аналитики, которая собирает данные со всех синхронизированных ботов в едином центре.

## 🚀 Что это дает?

### **До мульти-бот аналитики:**
```python
# Пользователю нужно было:
# 1. Настроить аналитику в боте A (50+ строк)
# 2. Настроить аналитику в боте B (50+ строк)
# 3. Настроить аналитику в боте C (50+ строк)
# 4. Собирать данные из каждого бота отдельно
# 5. Анализировать данные вручную
# ИТОГО: ~200+ строк кода + ручная работа
```

### **После мульти-бот аналитики:**
```python
# Теперь достаточно:
from neonpay import MultiBotAnalyticsManager, MultiBotEventCollector, EventCollectorConfig

# Инициализировать аналитику
multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

# Зарегистрировать боты
multi_analytics.register_bot("store_bot", "Main Store Bot")
multi_analytics.register_bot("support_bot", "Support Bot")

# Настроить сбор событий
collector_config = EventCollectorConfig(
    central_analytics_url="http://localhost:8081",
    enable_real_time=True,
    enable_batch_collection=True
)
event_collector = MultiBotEventCollector(collector_config)

# Автоматически собираются ВСЕ события со ВСЕХ ботов!
# ИТОГО: ~10 строк кода!
```

## 🎯 Реальные преимущества

### **1. Централизованная аналитика**
```python
# Получить аналитику всей сети ботов
network_analytics = multi_analytics.get_network_analytics(days=30)

print(f"Общая выручка: {network_analytics.total_revenue} stars")
print(f"Общее количество пользователей: {network_analytics.total_users}")
print(f"Конверсия сети: {network_analytics.network_conversion_rate:.1f}%")

# Топ-боты по выручке
for bot in network_analytics.top_performing_bots:
    print(f"{bot['bot_name']}: {bot['revenue']} stars")
```

### **2. Автоматическое отслеживание событий**
```python
# События автоматически отслеживаются:
# - Просмотры продуктов
# - Покупки
# - Использование промокодов
# - Подписки
# - Ошибки ботов
# - Синхронизация между ботами

# Все события собираются в реальном времени!
```

### **3. Детальная аналитика по ботам**
```python
# Аналитика для конкретного бота
bot_analytics = multi_analytics.get_bot_analytics("store_bot", days=30)

print(f"События: {bot_analytics.total_events}")
print(f"Пользователи: {bot_analytics.total_users}")
print(f"Выручка: {bot_analytics.total_revenue} stars")
print(f"Конверсия: {bot_analytics.conversion_rate:.1f}%")

# События по типам
for event_type, count in bot_analytics.events_by_type.items():
    print(f"{event_type}: {count}")
```

## 🔧 Настройка за 2 минуты

### **Шаг 1: Установка**
```bash
pip install neonpay[analytics,sync]
```

### **Шаг 2: Настройка аналитики**
```python
from neonpay import (
    MultiBotAnalyticsManager, 
    MultiBotEventCollector, 
    EventCollectorConfig
)

# Инициализировать аналитику
multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

# Зарегистрировать боты
multi_analytics.register_bot("main_bot", "Main Store Bot")
multi_analytics.register_bot("support_bot", "Support Bot")
multi_analytics.register_bot("analytics_bot", "Analytics Bot")
```

### **Шаг 3: Настройка сбора событий**
```python
# Конфигурация сбора событий
collector_config = EventCollectorConfig(
    central_analytics_url="http://localhost:8081",
    collection_interval_seconds=30,
    enable_real_time=True,
    enable_batch_collection=True
)

# Инициализировать сборщик
event_collector = MultiBotEventCollector(collector_config)

# Добавить боты для сбора
event_collector.add_bot("main_bot", "Main Store Bot", "https://main-bot.com")
event_collector.add_bot("support_bot", "Support Bot", "https://support-bot.com")
```

### **Шаг 4: Запуск**
```python
# Запустить сбор событий
await event_collector.start()

# Отслеживать события
multi_analytics.track_event(
    event_type="payment_completed",
    bot_id="main_bot",
    user_id=12345,
    amount=100,
    product_id="premium_access"
)
```

## 📊 Что отслеживается?

### **✅ Пользовательские события**
- `user_started` - пользователь запустил бота
- `user_message` - пользователь отправил сообщение
- `user_callback` - пользователь нажал кнопку

### **✅ Продуктовые события**
- `product_view` - просмотр продукта
- `product_click` - клик по продукту
- `product_share` - поделился продуктом

### **✅ Платежные события**
- `payment_started` - начат платеж
- `payment_completed` - платеж завершен
- `payment_failed` - платеж не удался
- `payment_cancelled` - платеж отменен

### **✅ Промо события**
- `promo_code_used` - использован промокод
- `promo_code_invalid` - неверный промокод

### **✅ Подписочные события**
- `subscription_created` - создана подписка
- `subscription_renewed` - продлена подписка
- `subscription_expired` - истекла подписка
- `subscription_cancelled` - отменена подписка

### **✅ Бот события**
- `bot_started` - бот запущен
- `bot_sync` - синхронизация бота
- `bot_error` - ошибка бота

## 🔄 Real-time мониторинг

### **Автоматический сбор событий**
```python
# События собираются автоматически каждые 30 секунд
collector_config = EventCollectorConfig(
    collection_interval_seconds=30,
    enable_real_time=True
)

# Real-time события обрабатываются мгновенно
await event_collector.receive_realtime_event({
    "event_type": "payment_completed",
    "bot_id": "store_bot",
    "user_id": 12345,
    "amount": 100,
    "timestamp": time.time()
})
```

### **Мониторинг в реальном времени**
```python
# Получить текущую статистику
stats = multi_analytics.get_stats()

print(f"Зарегистрированных ботов: {stats['registered_bots']}")
print(f"Всего событий: {stats['total_events']}")
print(f"Всего пользователей: {stats['total_users']}")
```

## 📈 Готовые отчеты

### **Сетевой отчет**
```python
# Получить полный отчет по сети
report = multi_analytics.get_network_report(days=30)

print("📊 Сетевой отчет:")
print(f"Ботов: {report['network']['total_bots']}")
print(f"Событий: {report['network']['total_events']}")
print(f"Пользователей: {report['network']['total_users']}")
print(f"Выручка: {report['network']['total_revenue']} stars")
print(f"Транзакций: {report['network']['total_transactions']}")
print(f"Конверсия: {report['network']['network_conversion_rate']:.1f}%")
```

### **Отчет по ботам**
```python
# Отчет по каждому боту
for bot_id, bot_data in report['bots'].items():
    print(f"\n🤖 {bot_data['bot_name']}:")
    print(f"  События: {bot_data['total_events']}")
    print(f"  Пользователи: {bot_data['total_users']}")
    print(f"  Выручка: {bot_data['total_revenue']} stars")
    print(f"  Конверсия: {bot_data['conversion_rate']:.1f}%")
```

## 📤 Экспорт данных

### **JSON экспорт**
```python
# Экспорт в JSON
json_data = multi_analytics.export_network_analytics(
    format_type="json",
    days=30
)

with open("analytics.json", "w") as f:
    f.write(json_data)
```

### **CSV экспорт**
```python
# Экспорт в CSV
csv_data = multi_analytics.export_network_analytics(
    format_type="csv",
    days=30
)

with open("analytics.csv", "w") as f:
    f.write(csv_data)
```

## 🛠️ CLI команды

```bash
# Сетевой аналитика
neonpay multi-analytics network --period 30days --format table

# Аналитика конкретного бота
neonpay multi-analytics bot store_bot --period 7days --format json

# Экспорт данных
neonpay multi-analytics export --format csv --period 30days --output analytics.csv

# Статус аналитики
neonpay multi-analytics status
```

## 🌐 Веб-интерфейс

### **Запуск веб-сервера аналитики**
```python
from neonpay.web_analytics import run_analytics_server

# Запустить сервер аналитики
await run_analytics_server(
    multi_analytics,
    event_collector,
    host="0.0.0.0",
    port=8081
)
```

### **Доступные endpoints**
- `POST /analytics/collect` - сбор событий от ботов
- `POST /analytics/realtime` - real-time события
- `GET /analytics/query` - запросы аналитики
- `GET /analytics/export` - экспорт данных
- `GET /analytics/status` - статус системы

## 📊 Статистика улучшений

### **Экономия времени:**
- **Настройка аналитики**: с 200+ строк до 10 строк (**95% экономии**)
- **Сбор данных**: с ручного до автоматического
- **Анализ данных**: с ручного до готовых отчетов
- **Мониторинг**: с разрозненного до централизованного

### **Преимущества:**
- **Централизация**: все данные в одном месте
- **Real-time**: события в реальном времени
- **Автоматизация**: никакой ручной работы
- **Масштабируемость**: легко добавлять новые боты
- **Экспорт**: данные в любом формате

## 🎯 Реальные примеры использования

### **1. Сеть магазинов**
```python
# Главный магазин + 5 филиалов
# Автоматически отслеживаются:
# - Общая выручка сети
# - Популярные продукты
# - Конверсия по филиалам
# - Поведение пользователей
```

### **2. Партнерская программа**
```python
# Ваш бот + боты партнеров
# Автоматически отслеживаются:
# - Продажи партнеров
# - Комиссионные
# - Эффективность партнеров
# - Общая статистика
```

### **3. A/B тестирование**
```python
# Бот A (тестовая версия) + Бот B (контрольная версия)
# Автоматически отслеживаются:
# - Конверсия по версиям
# - Популярность функций
# - Поведение пользователей
# - Результаты тестов
```

## 🚀 Начните прямо сейчас!

```python
# 1. Установите NEONPAY
pip install neonpay[analytics,sync]

# 2. Скопируйте этот код
from neonpay import MultiBotAnalyticsManager, MultiBotEventCollector, EventCollectorConfig

# 3. Инициализируйте аналитику
multi_analytics = MultiBotAnalyticsManager(enable_analytics=True)

# 4. Зарегистрируйте боты
multi_analytics.register_bot("main_bot", "Main Store Bot")
multi_analytics.register_bot("support_bot", "Support Bot")

# 5. Настройте сбор событий
collector_config = EventCollectorConfig(central_analytics_url="http://localhost:8081")
event_collector = MultiBotEventCollector(collector_config)

# 6. Запустите сбор
await event_collector.start()

# Готово! Теперь все события автоматически отслеживаются! 🎉
```

**Мульти-бот аналитика** - это не просто отслеживание событий, это **полноценная система управления данными** для целых экосистем Telegram ботов!

Больше никакого ручного сбора данных, никакого разрозненного анализа, никаких проблем с масштабированием.

**Все события → автоматически → в едином центре!** 🚀
