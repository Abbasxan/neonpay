# Tez-tez Verilən Suallar (FAQ) - NEONPAY

NEONPAY kitabxanası haqqında tez-tez verilən suallar və cavablar.

## Mündəricat

1. [Ümumi Suallar](#ümumi-suallar)
2. [Quraşdırma və Quraşdırma](#quraşdırma-və-quraşdırma)
3. [Ödəniş Emalı](#ödəniş-emalı)
4. [Xəta İdarəetməsi](#xəta-idarəetməsi)
5. [Təhlükəsizlik](#təhlükəsizlik)
6. [İstehsal Yerləşdirilməsi](#istehsal-yerləşdirilməsi)
7. [Problem Həlli](#problem-həlli)

## Ümumi Suallar

### NEONPAY nədir?

NEONPAY bot developerləri üçün Telegram Stars ödənişlərinin inteqrasiyasını sadələşdirən Python kitabxanasıdır. O, çoxlu bot kitabxanaları (Aiogram, Pyrogram, pyTelegramBotAPI və s.) üçün vahid API təmin edir və ödənişləri avtomatik olaraq idarə edir.

### Hansı bot kitabxanaları dəstəklənir?

NEONPAY dəstəkləyir:
- **Aiogram** (Tövsiyə olunur) - Müasir async kitabxana
- **Pyrogram** - Məşhur MTProto kitabxana
- **pyTelegramBotAPI** - Sadə sinxron kitabxana
- **python-telegram-bot** - Hərtərəfli kitabxana
- **Raw Telegram Bot API** - Birbaşa HTTP sorğuları

### Telegram Stars nədir?

Telegram Stars istifadəçilərin ala biləcəyi və botlarda rəqəmsal mallar və xidmətlər üçün ödəniş etmək üçün istifadə edə biləcəyi Telegram-ın daxili virtual valyutasıdır. O, Telegram tərəfindən rəsmi olaraq dəstəklənir və problemsiz ödəniş təcrübəsi təmin edir.

### NEONPAY istifadə etmək pulsuzdur?

Bəli, NEONPAY tamamilə pulsuz və açıq mənbədir. Siz yalnız Telegram-ın Stars ödənişlərinin emalı üçün komissiyasını ödəyirsiniz (adətən əməliyyat məbləğinin 5%).

## Quraşdırma və Quraşdırma

### NEONPAY-ı necə quraşdırmaq olar?

```bash
# Əsas quraşdırma
pip install neonpay

# Xüsusi bot kitabxanası ilə
pip install neonpay aiogram  # Aiogram üçün
pip install neonpay pyrogram  # Pyrogram üçün
```

### Necə tez başlamaq olar?

```python
from neonpay.factory import create_neonpay
from neonpay.core import PaymentStage, PaymentStatus

# İnitializasiya
neonpay = create_neonpay(bot_instance=sizin_bot)

# Ödəniş mərhələsi yaratmaq
stage = PaymentStage(
    title="Premium Giriş",
    description="Premium funksiyaları açmaq",
    price=25,  # 25 Telegram Stars
)
neonpay.create_payment_stage("premium", stage)

# Ödənişləri idarə etmək
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Ödəniş alındı: {result.amount} ulduz")
```

### Webhook quraşdırmaq lazımdır?

Xeyr, NEONPAY dəstəklənən kitabxanalar üçün webhook konfiqurasiyasını avtomatik olaraq idarə edir. Raw API üçün webhook-u əl ilə quraşdırmaq lazımdır.

### Düzgün bot kitabxanasını necə seçmək olar?

**Yeni layihələr üçün:** **Aiogram** istifadə edin - o müasirdir, yaxşı sənədləşdirilmişdir və əla async dəstəyi var.

**Mövcud layihələr üçün:** Artıq istifadə etdiyiniz kitabxanadan istifadə edin. NEONPAY bütün əsas kitabxanalarla işləyir.

## Ödəniş Emalı

### Müxtəlif ödəniş variantlarını necə yaratmaq olar?

```python
# Donasiya variantları
donation_stages = [
    PaymentStage("Dəstək 1⭐", "Botun işləməsinə kömək et", 1),
    PaymentStage("Dəstək 10⭐", "İnkişafa dəstək", 10),
    PaymentStage("Dəstək 50⭐", "Böyük dəstək", 50),
]

# Rəqəmsal məhsullar
product_stages = [
    PaymentStage("Premium Giriş", "30 gün premium", 25),
    PaymentStage("Xüsusi Tema", "Fərdiləşdirilmiş tema", 15),
]

# Bütün mərhələləri əlavə et
for i, stage in enumerate(donation_stages):
    neonpay.create_payment_stage(f"donate_{i}", stage)

for i, stage in enumerate(product_stages):
    neonpay.create_payment_stage(f"product_{i}", stage)
```

### Müxtəlif ödəniş növlərini necə idarə etmək olar?

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        if result.stage_id.startswith("donate_"):
            # Donasiyanı idarə et
            await handle_donation(result)
        elif result.stage_id.startswith("product_"):
            # Məhsul alışını idarə et
            await handle_product_purchase(result)
        else:
            # Digər ödənişləri idarə et
            await handle_other_payment(result)
```

### Ödəniş mesajlarını fərdiləşdirmək olarmı?

Bəli, təşəkkür mesajını fərdiləşdirə bilərsiniz:

```python
neonpay = create_neonpay(
    bot_instance=bot,
    thank_you_message="🎉 Alışınız üçün təşəkkürlər! Məhsulunuz indi aktivdir."
)
```

### Ödəniş məbləğlərini necə doğrulamaq olar?

```python
@neonpay.on_payment
async def handle_payment(result):
    # Bu mərhələ üçün gözlənilən məbləği al
    stage = neonpay.get_payment_stage(result.stage_id)
    expected_amount = stage.price
    
    if result.amount != expected_amount:
        logger.warning(f"Məbləğ uyğunsuzluğu: gözlənilən {expected_amount}, alınan {result.amount}")
        return
    
    # Ödənişi emal et
    await process_payment(result)
```

## Xəta İdarəetməsi

### Ödəniş uğursuz olsa nə baş verir?

NEONPAY avtomatik olaraq uğursuz ödənişləri idarə edir və ətraflı xəta məlumatı təmin edir:

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        # Ödəniş uğurlu
        await process_successful_payment(result)
    elif result.status == PaymentStatus.FAILED:
        # Ödəniş uğursuz
        await handle_payment_failure(result)
    elif result.status == PaymentStatus.PENDING:
        # Ödəniş gözləyir
        await handle_pending_payment(result)
```

### Şəbəkə xətalarını necə idarə etmək olar?

```python
async def safe_send_payment(user_id: int, stage_id: str):
    try:
        await neonpay.send_payment(user_id, stage_id)
    except PaymentError as e:
        logger.error(f"Ödəniş xətası: {e}")
        await bot.send_message(user_id, "Ödəniş uğursuz oldu. Zəhmət olmasa yenidən cəhd edin.")
    except Exception as e:
        logger.error(f"Gözlənilməz xəta: {e}")
        await bot.send_message(user_id, "Nəsə səhv getdi. Zəhmət olmasa sonra cəhd edin.")
```

### Bot token etibarsızdırsa nə baş verir?

NEONPAY bot token etibarsızdırsa `ConfigurationError` yaradacaq:

```python
try:
    neonpay = create_neonpay(bot_instance=bot)
except ConfigurationError as e:
    print(f"Konfiqurasiya xətası: {e}")
    # Bot tokenınızı yoxlayın
```

## Təhlükəsizlik

### Bot tokenımı necə qorumaq olar?

Heç vaxt tokenları mənbə kodunda hardcode etməyin:

```python
# ❌ Yanlış
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"

# ✅ Düzgün
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
```

### İstifadəçi icazələrini necə doğrulamaq olar?

```python
async def safe_send_payment(user_id: int, stage_id: str):
    # İstifadəçinin ödəniş edə biləcəyini yoxlayın
    if not await user_can_pay(user_id):
        await bot.send_message(user_id, "Ödəniş etmək üçün icazəniz yoxdur.")
        return
    
    # İstifadəçinin ödəniş limitinə çatıb-çatmadığını yoxlayın
    if await user_payment_limit_reached(user_id):
        await bot.send_message(user_id, "Ödəniş limitinizə çatdınız.")
        return
    
    # Ödənişi göndərin
    await neonpay.send_payment(user_id, stage_id)
```

### Ödəniş dolandırıcılığını necə qarşısını almaq olar?

```python
class PaymentValidator:
    def __init__(self):
        self.user_payments = defaultdict(list)
        self.max_payments_per_hour = 5
    
    async def validate_payment(self, user_id: int, stage_id: str) -> bool:
        # Ödəniş tezliyini yoxlayın
        now = time.time()
        recent_payments = [
            t for t in self.user_payments[user_id] 
            if now - t < 3600  # Son saat
        ]
        
        if len(recent_payments) >= self.max_payments_per_hour:
            return False
        
        # Şübhəli nümunələri yoxlayın
        if await self.is_suspicious_user(user_id):
            return False
        
        return True
    
    async def record_payment(self, user_id: int):
        self.user_payments[user_id].append(time.time())
```

## İstehsal Yerləşdirilməsi

### İstehsala necə yerləşdirmək olar?

1. **Mühit dəyişənlərini istifadə edin:**
```python
import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
```

2. **Düzgün log quraşdırın:**
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

3. **İstehsal verilənlər bazası istifadə edin:**
```python
# Yaddaşda saxlanılanı verilənlər bazası ilə əvəz edin
import asyncpg

async def store_payment(payment_data):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO payments (user_id, amount, stage_id, created_at) VALUES ($1, $2, $3, NOW())",
        payment_data['user_id'], payment_data['amount'], payment_data['stage_id']
    )
    await conn.close()
```

### Ödənişləri necə monitor etmək olar?

```python
class PaymentMonitor:
    def __init__(self):
        self.payment_stats = defaultdict(int)
    
    async def log_payment(self, result):
        self.payment_stats['total_payments'] += 1
        self.payment_stats['total_amount'] += result.amount
        
        # Verilənlər bazasına log
        await self.store_payment_log(result)
        
        # Yüksək həcm üçün xəbərdarlıq göndərin
        if self.payment_stats['total_payments'] % 100 == 0:
            await self.send_volume_alert()
    
    async def get_stats(self):
        return dict(self.payment_stats)
```

### Yüksək trafiki necə idarə etmək olar?

```python
# Əlaqə hovuzu istifadə edin
import asyncpg

class DatabasePool:
    def __init__(self, database_url: str):
        self.pool = None
        self.database_url = database_url
    
    async def initialize(self):
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=10,
            max_size=20
        )
    
    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)
```

## Problem Həlli

### Ödəniş göndərilmir

**Yoxlayın:**
1. Bot token etibarlıdır
2. İstifadəçi botu başlatıb
3. Ödəniş mərhələsi mövcuddur
4. İstifadəçi ID düzgündür

```python
# Ödəniş göndərməni debug et
async def debug_send_payment(user_id: int, stage_id: str):
    # Mərhələnin mövcud olduğunu yoxlayın
    stage = neonpay.get_payment_stage(stage_id)
    if not stage:
        print(f"Mərhələ {stage_id} tapılmadı")
        return
    
    # İstifadəçinin mövcud olduğunu yoxlayın
    try:
        user = await bot.get_chat(user_id)
        print(f"İstifadəçi tapıldı: {user.first_name}")
    except Exception as e:
        print(f"İstifadəçi tapılmadı: {e}")
        return
    
    # Ödənişi göndərin
    try:
        await neonpay.send_payment(user_id, stage_id)
        print("Ödəniş uğurla göndərildi")
    except Exception as e:
        print(f"Ödəniş uğursuz oldu: {e}")
```

### Ödəniş callback işləmir

**Yoxlayın:**
1. `@neonpay.on_payment` dekoratoru düzgün tətbiq edilib
2. Funksiya async-dir
3. Bot işləyir və yeniləmələri alır

```python
# Ödəniş callback testi
@neonpay.on_payment
async def test_payment_handler(result):
    print(f"Ödəniş callback işə düşdü: {result}")
    # Debug üçün burada breakpoint əlavə edin
```

### Bot əmrlərə cavab vermir

**Yoxlayın:**
1. Bot token düzgündür
2. Bot işləyir
3. Əmrlər düzgün qeydiyyatdan keçib
4. Şəbəkə bağlantısı

```python
# Bot bağlantısını test et
async def test_bot():
    try:
        me = await bot.get_me()
        print(f"Bot işləyir: {me.first_name}")
    except Exception as e:
        print(f"Bot bağlantısı uğursuz oldu: {e}")
```

### Verilənlər bazası bağlantı problemləri

```python
# Verilənlər bazası bağlantısını test et
async def test_database():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        result = await conn.fetchval("SELECT 1")
        print(f"Verilənlər bazası bağlandı: {result}")
        await conn.close()
    except Exception as e:
        print(f"Verilənlər bazası bağlantısı uğursuz oldu: {e}")
```

## Ümumi Problemlər

### "Ödəniş mərhələsi tapılmadı"

Bu, mövcud olmayan mərhələ üçün ödəniş göndərməyə çalışdığınızda baş verir:

```python
# Mövcud mərhələləri yoxlayın
stages = neonpay.list_payment_stages()
print(f"Mövcud mərhələlər: {list(stages.keys())}")

# Əgər çatışmırsa mərhələ yaradın
if "premium" not in stages:
    stage = PaymentStage("Premium", "Premium giriş", 25)
    neonpay.create_payment_stage("premium", stage)
```

### "İnvoice göndərmək uğursuz oldu"

Bu adətən deməkdir:
1. Bot token etibarsızdır
2. İstifadəçi botu başlatmayıb
3. İstifadəçi ID yanlışdır

```python
# Invoice göndərməni debug et
async def debug_invoice(user_id: int, stage_id: str):
    try:
        # Bot məlumatlarını yoxlayın
        me = await bot.get_me()
        print(f"Bot: {me.first_name} (@{me.username})")
        
        # İstifadəçini yoxlayın
        user = await bot.get_chat(user_id)
        print(f"İstifadəçi: {user.first_name} (@{user.username})")
        
        # Ödənişi göndərin
        await neonpay.send_payment(user_id, stage_id)
    except Exception as e:
        print(f"Xəta: {e}")
```

### "Ödəniş callback işə düşmür"

Əmin olun ki:
1. Funksiya `@neonpay.on_payment` ilə dekorasiya edilib
2. Funksiya async-dir
3. Bot yeniləmələri alır

```python
# Callback qeydiyyatını test et
stats = neonpay.get_stats()
print(f"Callbacks qeydiyyatdan keçib: {stats['registered_callbacks']}")
```

## Kömək Almaq

### Haradan kömək ala bilərəm?

1. **Sənədləşmə**: [examples](../../examples/) qovluğunu yoxlayın
2. **İcma**: [Telegram icmamıza](https://t.me/neonpay_community) qoşulun
3. **Problemlər**: [GitHub-da](https://github.com/Abbasxan/neonpay/issues) issue açın
4. **Email**: [support@neonpay.com](mailto:support@neonpay.com) ünvanından dəstəklə əlaqə saxlayın

### Xətaları necə bildirmək olar?

Xətaları bildirərkən, zəhmət olmasa daxil edin:
1. Python versiyası
2. NEONPAY versiyası
3. Bot kitabxanası və versiyası
4. Xəta mesajı və stack trace
5. Təkrar etmək üçün addımlar

### Funksiyaları necə tələb etmək olar?

Funksiya tələbləri xoş gəlinir! Zəhmət olmasa:
1. Funksiyanın artıq mövcud olub-olmadığını yoxlayın
2. İstifadə halını təsvir edin
3. Mümkünsə nümunə kod təqdim edin
4. GitHub-da issue açın

---

**Hələ də suallarınız var? [examples](../../examples/) qovluğunu yoxlayın və ya dəstəklə əlaqə saxlayın!**
