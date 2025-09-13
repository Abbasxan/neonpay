# 🤖 QƏDDAR Bot - Güclü Qrup İdarəetmə Botu

**QƏDDAR Bot** - Telegram qrupları üçün ən güclü və çoxfunksiyalı moderasiya botudur. Bot qrupunuzda nizamı qoruyur, spam və reklamları avtomatik olaraq aşkar edib silir, üzvləri idarə edir və bir çox faydalı funksiyalar təqdim edir.

## 🌟 Əsas Xüsusiyyətlər

### 🛡️ Təhlükəsizlik və Moderasiya
- **Anti-Spam Sistemi** - Spam mesajları avtomatik aşkar edib silir
- **Anti-Reklam Sistemi** - Reklam və kanal reklamlarını bloklar
- **Anti-Vulgar Sistemi** - Kobud sözləri filtrləyir və xəbərdarlıq verir
- **Captcha Sistemi** - Yeni üzvlər üçün riyazi tapşırıqlar
- **Flood Qoruma** - Mesaj spamını qarşısını alır

### 👥 İstifadəçi İdarəetməsi
- **Avtomatik Mute/Ban** - Qaydaları pozanlara avtomatik cəza
- **Xəbərdarlıq Sistemi** - Üzvlərə xəbərdarlıq verilməsi
- **Top Bad Boy** - Ən çox xəbərdarlıq alan üzvlərin siyahısı
- **İstifadəçi Statistikası** - Detallı aktivlik hesabatları

### 🎮 Əyləncə Modulu
- **Daş-Kağız-Qayçı** - Klassik oyun
- **Sevgi Ölçən** - İki şəxs arasında sevgi faizi
- **Test Oyunu** - Müxtəlif testlər və suallar
- **Qəddar Söz** - Gündəlik motivasiya sözləri

### ⚙️ İdarəetmə və Tənzimləmələr
- **Modul Tənzimləmələri** - Hər modulu ayrıca aktiv/deaktiv etmək
- **Dil Dəstəyi** - Azərbaycan, İngilis və Rus dilləri
- **Broadcast Sistemi** - Bütün qruplara mesaj göndərmək
- **Yardım Sistemi** - Detallı kömək və təlimatlar

## 🚀 Quraşdırma

### Tələblər
- Python 3.8+
- MongoDB
- Telegram Bot Token
- Userbot hesabı (əlavə funksiyalar üçün)

### Addımlar
1. Repozitoriyanı klonlayın
2. Tələb olunan paketləri quraşdırın
3. `.env` faylını yaradın və tənzimləyin
4. Botu işə salın

## 📋 Əsas Komandalar

### 👑 Admin Komandaları
- `/settings` - Bot tənzimləmələri
- `/broadcast` - Bütün qruplara mesaj göndərmək
- `/topbadder` - Ən çox xəbərdarlıq alanlar
- `/captcha on/off` - Captcha sistemini idarə etmək

### 👤 İstifadəçi Komandaları
- `/start` - Botu başlatmaq
- `/help` - Yardım menyusu
- `/ping` - Bot cavab müddətini yoxlamaq
- `/uptime` - Sistem məlumatları
- `/noarqo` - Arxa fon rəsmini dəyişmək

### 🎮 Oyun Komandaları
- `/kagizqaycidas` - Daş-Kağız-Qayçı oyunu
- `/lovemeter` - Sevgi ölçən
- `/test` - Test oyunu
- `/qeddarsoz` - Gündəlik söz

## 🔧 Modul Sistemi

Bot modulyar quruluşa malikdir və hər modul müstəqil olaraq idarə oluna bilər:

### Mövcud Modullar
- **start.py** - Başlanğıc və qeydiyyat
- **help.py** - Yardım sistemi
- **settings.py** - Tənzimləmələr
- **antispam.py** - Spam əleyhinə
- **antireklam.py** - Reklam əleyhinə
- **antivulgar.py** - Kobud söz filteri
- **captcha.py** - Captcha sistemi
- **broadcast.py** - Kütləvi mesaj göndərmə
- **topbadboy.py** - Statistika və reytinqlər
- **ping.py** - Ping yoxlaması

## 🗄️ Verilənlər Bazası

Bot MongoDB istifadə edir və aşağıdakı kolleksiyaları saxlayır:
- `users` - İstifadəçi məlumatları
- `groups` - Qrup tənzimləmələri
- `warnings` - Xəbərdarlıq sistemi
- `bad_word_stats` - Kobud söz statistikası
- `deleted_messages` - Silinmiş mesaj logları

## 🌍 Dil Dəstəyi

Bot 3 dili dəstəkləyir:
- 🇦🇿 **Azərbaycan dili** (əsas)
- 🇺🇸 **İngilis dili**
- 🇷🇺 **Rus dili**

Dil faylları `langs/` qovluğunda yerləşir və YAML formatında saxlanılır.

## 🔒 Təhlükəsizlik

- Bütün admin əməliyyatları icazə yoxlaması ilə qorunur
- Rate limiting sistemi spam hücumlarını qarşısını alır
- Userbot inteqrasiyası əlavə təhlükəsizlik təmin edir
- Avtomatik log sistemi bütün fəaliyyətləri izləyir

## 📊 Statistika və Monitorinq

- Real vaxt aktivlik izləməsi
- Detallı istifadə statistikaları
- Xəta izləmə və hesabat sistemi
- Log kanalı inteqrasiyası

## 🤝 Töhfə Vermək

1. Repozitoriyanı fork edin
2. Yeni branch yaradın
3. Dəyişikliklərinizi commit edin
4. Branch-ı push edin
5. Pull Request yaradın

## 📞 Dəstək

- **Telegram Kanalı**: [@qeddarbot_news](https://t.me/qeddarbot_news)
- **Dəstək Qrupu**: [@qeddarbot_support](https://t.me/qeddarbot_support)
- **Developer**: [@neonsahib](https://t.me/neonsahib)

## 📄 Lisenziya

Bu layihə MIT lisenziyası altında paylanır. Ətraflı məlumat üçün `LICENSE` faylına baxın.

## 🙏 Təşəkkürlər

- Pyrogram kitabxanası üçün
- MongoDB komandası üçün

---

**QƏDDAR Bot** - Qrupunuzun ən etibarlı qoruyucusu! 🛡️
