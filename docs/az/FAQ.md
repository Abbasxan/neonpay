# NEONPAY Tez-tez Verilən Suallar

## Ümumi Suallar

### NEONPAY nədir?

NEONPAY Telegram botları üçün müasir, universal ödəniş emalı kitabxanasıdır. Telegram Stars ödənişlərini inteqrasiya etməyi inanılmaz dərəcədə sadə edir.

### Hansı bot kitabxanalarına dəstək verir?

NEONPAY aşağıdakı bot kitabxanalarına dəstək verir:
- Pyrogram
- Aiogram
- python-telegram-bot
- pyTelegramBotAPI
- Raw Bot API

### Telegram Stars nədir?

Telegram Stars Telegram-ın rəsmi virtual valyutasıdır. İstifadəçilər Telegram-da müxtəlif xidmətlər və məhsullar üçün Stars istifadə edə bilərlər.

## Quraşdırma və Konfiqurasiya

### NEONPAY-i necə quraşdırım?

```bash
pip install neonpay
```

### Minimum tələblər nələrdir?

- Python 3.9+
- Dəstəklənən bot kitabxanalarından biri
- Telegram bot token

### Hansı əlavə paketlər lazımdır?

NEONPAY özü minimal asılılıqlara malikdir. Yalnız seçdiyiniz bot kitabxanasını quraşdırmaq lazımdır.

## İstifadə

### Əsas istifadə necədir?

```python
from neonpay import create_neonpay, PaymentStage

neonpay = create_neonpay(your_bot_instance)
stage = PaymentStage("Premium", "Premium xüsusiyyətlər", 100)
neonpay.create_payment_stage("premium", stage)
await neonpay.send_payment(user_id, "premium")
```

### Ödənişləri necə idarə edim?

```python
@neonpay.on_payment
async def handle_payment(result):
    if result.status == PaymentStatus.COMPLETED:
        print(f"Ödəniş alındı: {result.amount} stars")
```

### Çoxlu ödəniş mərhələləri yarada bilərəm?

Bəli, istədiyiniz qədər ödəniş mərhələsi yarada bilərsiniz:

```python
neonpay.create_payment_stage("basic", basic_stage)
neonpay.create_payment_stage("premium", premium_stage)
neonpay.create_payment_stage("enterprise", enterprise_stage)
```

## Xətalar və Problemlər

### "PaymentError" xətası alıram

Bu xəta adətən ödəniş mərhələsinin mövcud olmaması və ya yanlış konfiqurasiya ilə bağlıdır. Ödəniş mərhələsinin düzgün yaradıldığından əmin olun.

### Bot ödənişləri qəbul etmir

Aşağıdakıları yoxlayın:
1. Bot token düzgündür
2. Ödəniş mərhələsi yaradılıb
3. Bot Telegram-da aktivdir
4. İstifadəçi Telegram Stars-a malikdir

### Async/sync problemi

NEONPAY həm async, həm də sync istifadəni dəstəkləyir. Bot kitabxananızın async dəstəyini yoxlayın.

## Performans və Optimallaşdırma

### NEONPAY performansı necədir?

NEONPAY yüksək performans üçün optimallaşdırılıb. Minimal yaddaş istifadəsi və sürətli emal təmin edir.

### Çoxlu istifadəçi dəstəyi

Bəli, NEONPAY çoxlu istifadəçi ilə işləmək üçün nəzərdə tutulub. Async arxitektura sayəsində yüksək yüklənməni idarə edə bilir.

### Yaddaş istifadəsi

NEONPAY minimal yaddaş istifadə edir. Ödəniş mərhələləri və metadata yaddaşda saxlanılır.

## Təhlükəsizlik

### NEONPAY təhlükəsizdir?

Bəli, NEONPAY təhlükəsizlik üçün müxtəlif tədbirlər tətbiq edib:
- Input validasiya
- Webhook imza yoxlanması
- Xəta idarəetməsi
- Təhlükəsiz API inteqrasiyası

### Webhook təhlükəsizliyi

NEONPAY webhook imza yoxlanması təmin edir. Bu, webhook-ların həqiqətən Telegram-dan gəldiyini təsdiqləyir.

## Dəstək və İnkişaf

### Dəstək haradan ala bilərəm?

- GitHub Issues: https://github.com/Abbasxan/neonpay/issues
- Telegram: @neonsahib
- Email: sultanov.abas@outlook.com

### NEONPAY açıq mənbəlidir?

Bəli, NEONPAY MIT lisenziyası altında açıq mənbəlidir.

### Töhfə verə bilərəm?

Bəli, töhfələr xoş gəlinir! GitHub-da Pull Request göndərin.

## Gələcək Planlar

### Hansı xüsusiyyətlər planlaşdırılır?

- Daha çox bot kitabxanası dəstəyi
- Təkmilləşdirilmiş analitika
- Çoxlu valyuta dəstəyi
- Təkmilləşdirilmiş webhook funksionallığı

### Versiya yeniləmələri nə qədər tez-tez olur?

NEONPAY aktiv inkişaf edir. Əsas yeniləmələr hər 2-3 ayda bir, kiçik düzəlişlər isə daha tez-tez buraxılır.

