# Təhlükəsizlik Təlimatı - NEONPAY

Bu sənəd NEONPAY-ın istehsal mühitlərində istifadəsi üçün təhlükəsizlik ən yaxşı təcrübələrini təsvir edir.

## Mündəricat

1. [Token Təhlükəsizliyi](#token-təhlükəsizliyi)
2. [Ödəniş Doğrulaması](#ödəniş-doğrulaması)
3. [Məlumat Qorunması](#məlumat-qorunması)
4. [Xəta İdarəetməsi](#xəta-idarəetməsi)
5. [Log Təhlükəsizliyi](#log-təhlükəsizliyi)
6. [İstehsal Çeklisti](#istehsal-çeklisti)

## Token Təhlükəsizliyi

### Bot Token Qorunması

**❌ Heç vaxt belə etməyin:**
```python
# ETMƏYİN: Tokenları mənbə kodunda hardcode edin
BOT_TOKEN = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
```

**✅ Bunun əvəzinə belə edin:**
```python
import os

# EDİN: Mühit dəyişənlərini istifadə edin
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN mühit dəyişəni tələb olunur")
```

### Mühit Dəyişənləri

`.env` faylı yaradın (heç vaxt versiya nəzarətinə commit etməyin):
```bash
# .env
BOT_TOKEN=bot_tokenunuz_burada
API_ID=api_id_niz_burada
API_HASH=api_hash_niz_burada
DATABASE_URL=postgresql://user:pass@localhost/db
```

python-dotenv ilə yükləyin:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Ödəniş Doğrulaması

### Ödəniş Məbləğlərini Yoxlama

```python
@neonpay.on_payment
async def handle_payment(result):
    # Həmişə ödəniş məbləğini yoxlayın
    expected_amount = get_expected_amount(result.stage_id)
    
    if result.amount != expected_amount:
        logger.warning(
            f"Ödəniş məbləği uyğunsuzluğu: gözlənilən {expected_amount}, "
            f"alınan {result.amount} istifadəçidən {result.user_id}"
        )
        return
    
    # Yoxlama sonrası ödənişi emal edin
    await process_payment(result)
```

### Stage ID Doğrulaması

```python
async def safe_send_payment(user_id: int, stage_id: str):
    # Stage-in mövcud olduğunu yoxlayın
    stage = neonpay.get_payment_stage(stage_id)
    if not stage:
        logger.error(f"Yanlış stage_id: {stage_id}")
        await bot.send_message(user_id, "Ödəniş seçimi mövcud deyil.")
        return
    
    # İstifadəçi icazələrini yoxlayın
    if not await user_can_purchase(user_id, stage_id):
        await bot.send_message(user_id, "Bu məhsulu almaq üçün icazəniz yoxdur.")
        return
    
    # Ödənişi göndərin
    await neonpay.send_payment(user_id, stage_id)
```

## Məlumat Qorunması

### İstifadəçi Məlumatlarının İdarəsi

```python
import hashlib

def hash_user_id(user_id: int) -> str:
    """Log üçün istifadəçi ID-ni hash etmək (bir istiqamətli)"""
    return hashlib.sha256(str(user_id).encode()).hexdigest()[:8]

@neonpay.on_payment
async def handle_payment(result):
    # Hash edilmiş istifadəçi ID ilə log
    hashed_id = hash_user_id(result.user_id)
    logger.info(f"İstifadəçidən ödəniş alındı {hashed_id}: {result.amount} ulduz")
    
    # Verilənlər bazasında düzgün şifrələmə ilə saxlayın
    await store_payment_securely(result)
```

### Verilənlər Bazası Təhlükəsizliyi

```python
import asyncpg
from cryptography.fernet import Fernet

class SecurePaymentStorage:
    def __init__(self, db_url: str, encryption_key: str):
        self.db_url = db_url
        self.cipher = Fernet(encryption_key.encode())
    
    async def store_payment(self, payment_data: dict):
        # Həssas məlumatları şifrələyin
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

## Xəta İdarəetməsi

### Təhlükəsiz Xəta Mesajları

```python
async def handle_payment_error(user_id: int, error: Exception):
    # Tam xəta təfərrüatlarını log edin
    logger.error(f"İstifadəçi üçün ödəniş xətası {user_id}: {error}", exc_info=True)
    
    # İstifadəçiyə ümumi mesaj göndərin
    await bot.send_message(
        user_id, 
        "Ödənişinizlə bağlı bir problem yarandı. Zəhmət olmasa sonra cəhd edin."
    )
    
    # Daxili təfərrüatları açıqlamayın
    # ❌ ETMƏYİN: await bot.send_message(user_id, f"Xəta: {str(error)}")
```

### Giriş Doğrulaması

```python
def validate_user_input(user_id: int, stage_id: str) -> bool:
    """Emal etməzdən əvvəl istifadəçi girişini doğrulayın"""
    
    # user_id-nin etibarlı olduğunu yoxlayın
    if not isinstance(user_id, int) or user_id <= 0:
        return False
    
    # stage_id formatını yoxlayın
    if not isinstance(stage_id, str) or len(stage_id) > 100:
        return False
    
    # Şübhəli nümunələri yoxlayın
    if any(char in stage_id for char in ['<', '>', '&', '"', "'"]):
        return False
    
    return True
```

## Log Təhlükəsizliyi

### Təhlükəsiz Log Konfiqurasiyası

```python
import logging
import logging.handlers
from datetime import datetime

def setup_secure_logging():
    """Təhlükəsiz log konfiqurasiyasını quraşdırın"""
    
    # Həssas məlumatları istisna edən formatör yaradın
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Fırlanma ilə fayl işləyicisi
    file_handler = logging.handlers.RotatingFileHandler(
        'bot.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Konsol işləyicisi
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Logger quraşdırın
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # İstehsalda debug-u söndürün
    if os.getenv("ENVIRONMENT") == "production":
        logger.setLevel(logging.WARNING)
```

### Həssas Məlumat Filtrasiyası

```python
class SensitiveDataFilter(logging.Filter):
    """Loglardan həssas məlumatları filtrləyin"""
    
    def filter(self, record):
        # Log mesajlarından tokenları silin
        if hasattr(record, 'msg'):
            msg = str(record.msg)
            # Token nümunələrini əvəz edin
            import re
            record.msg = re.sub(
                r'\b\d{10}:[A-Za-z0-9_-]{35}\b',
                '[TOKEN_REDACTED]',
                msg
            )
        return True

# Filtr tətbiq edin
logger.addFilter(SensitiveDataFilter())
```

## İstehsal Çeklisti

### Yerləşdirmədən əvvəl Təhlükəsizlik Yoxlaması

- [ ] **Mühit Dəyişənləri**: Bütün həssas məlumatlar mühit dəyişənlərində
- [ ] **Token Qorunması**: Bot tokenları mənbə kodunda deyil
- [ ] **Verilənlər Bazası Təhlükəsizliyi**: Şifrələnmiş əlaqələr və məlumatlar
- [ ] **Giriş Doğrulaması**: Bütün istifadəçi girişləri doğrulanıb
- [ ] **Xəta İdarəetməsi**: İstifadəçilər üçün ümumi xəta mesajları
- [ ] **Log**: Həssas məlumatlar loglardan filtrelənib
- [ ] **HTTPS**: Bütün webhooklar HTTPS istifadə edir
- [ ] **Sürət Məhdudiyyəti**: Ödənişlər üçün sürət məhdudiyyəti tətbiq edilib
- [ ] **Monitorinq**: Ödəniş monitorinqi və xəbərdarlıqlar quraşdırılıb
- [ ] **Yedəkləmə**: Müntəzəm verilənlər bazası yedəkləmələri

### Sürət Məhdudiyyəti

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
        
        # Pəncərədən kənar köhnə ödənişləri silin
        user_payments[:] = [t for t in user_payments if now - t < self.window]
        
        # Limit altında olduğunu yoxlayın
        return len(user_payments) < self.max_payments
    
    def record_payment(self, user_id: int):
        self.user_payments[user_id].append(time.time())

# İstifadə
rate_limiter = PaymentRateLimiter()

async def safe_send_payment(user_id: int, stage_id: str):
    if not rate_limiter.can_make_payment(user_id):
        await bot.send_message(
            user_id, 
            "Çox çox ödəniş cəhdi. Zəhmət olmasa sonra cəhd edin."
        )
        return
    
    await neonpay.send_payment(user_id, stage_id)
    rate_limiter.record_payment(user_id)
```

### Monitorinq və Xəbərdarlıqlar

```python
import asyncio
from datetime import datetime, timedelta

class PaymentMonitor:
    def __init__(self):
        self.payment_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
    
    async def monitor_payments(self):
        """Anomaliyalar üçün ödəniş nümunələrini monitor edin"""
        while True:
            await asyncio.sleep(300)  # Hər 5 dəqiqədə yoxlayın
            
            # Qeyri-adi ödəniş nümunələrini yoxlayın
            recent_payments = self.get_recent_payments()
            
            if len(recent_payments) > 100:  # Hədd
                await send_alert(f"Yüksək ödəniş həcmi: {len(recent_payments)} ödəniş")
            
            # Xətaları yoxlayın
            recent_errors = self.get_recent_errors()
            if len(recent_errors) > 10:  # Hədd
                await send_alert(f"Yüksək xəta dərəcəsi: {len(recent_errors)} xəta")
    
    async def send_alert(self, message: str):
        """Təhlükəsizlik xəbərdarlığı göndərin"""
        # Monitorinq sisteminə göndərin
        logger.critical(f"TƏHLÜKƏSİZLİK XƏBƏRDARLIĞI: {message}")
```

## Ümumi Təhlükəsizlik Səhvləri

### 1. Daxili Xətaları Açıqlama

**❌ Yanlış:**
```python
except Exception as e:
    await bot.send_message(user_id, f"Xəta: {str(e)}")
```

**✅ Düzgün:**
```python
except Exception as e:
    logger.error(f"Ödəniş xətası: {e}")
    await bot.send_message(user_id, "Ödəniş uğursuz oldu. Zəhmət olmasa yenidən cəhd edin.")
```

### 2. Loglarda Həssas Məlumat Saxlama

**❌ Yanlış:**
```python
logger.info(f"İstifadəçi {user_id} token {bot_token} ilə ödədi")
```

**✅ Düzgün:**
```python
logger.info(f"İstifadəçi {hash_user_id(user_id)} ödənişi tamamladı")
```

### 3. Giriş Doğrulaması Olmadan

**❌ Yanlış:**
```python
await neonpay.send_payment(user_id, stage_id)  # Doğrulama yoxdur
```

**✅ Düzgün:**
```python
if validate_user_input(user_id, stage_id):
    await neonpay.send_payment(user_id, stage_id)
else:
    await bot.send_message(user_id, "Yanlış sorğu.")
```

## Hadisə Cavabı

### Təhlükəsizlik Hadisəsi Çeklisti

1. **Dərhal Cavab**
   - [ ] Lazım olduqda təsirlənən botu söndürün
   - [ ] Şübhəli fəaliyyət üçün logları nəzərdən keçirin
   - [ ] Kompromisə düşdüyü halda bot tokenını dəyişdirin
   - [ ] Məlumat sızması halında istifadəçiləri bildirin

2. **Araşdırma**
   - [ ] Hücum vektorunu təhlil edin
   - [ ] Təsirlənən istifadəçiləri müəyyən edin
   - [ ] Hadisə təfərrüatlarını sənədləşdirin
   - [ ] Sübutları qoruyun

3. **Bərpa**
   - [ ] Təhlükəsizlik zəifliklərini yamalayın
   - [ ] Təhlükəsizlik tədbirlərini yeniləyin
   - [ ] Sistemi hərtərəfli test edin
   - [ ] Davam edən hücumlar üçün monitor edin

4. **Hadisə sonrası**
   - [ ] Təhlükəsizlik sənədlərini yeniləyin
   - [ ] Təhlükəsizlik nəzərdən keçirməsi keçirin
   - [ ] Əlavə qoruyucu tədbirlər tətbiq edin
   - [ ] Komandaya öyrənilən dərslər üzrə təlim verin

## Resurslar

- [Telegram Bot Təhlükəsizliyi](https://core.telegram.org/bots/security)
- [OWASP Təhlükəsizlik Təlimatları](https://owasp.org/)
- [Python Təhlükəsizlik Ən Yaxşı Təcrübələri](https://python-security.readthedocs.io/)

---

**Xatırlayın: Təhlükəsizlik davamlı prosesdir, bir dəfəlik quraşdırma deyil. Təhlükəsizlik tədbirlərinizi müntəzəm nəzərdən keçirin və yeniləyin.**
