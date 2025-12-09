"""All bot texts in Uzbek language."""

# Welcome & Help
WELCOME = """🎬 Kino Botga xush kelibsiz!

📥 Kino olish uchun kod yuboring.
Masalan: 47

🔍 Qidirish: /search

📋 Kodlar ro'yxati: {channel}

❓ Yordam: /help"""

HELP = """📖 Botdan foydalanish

1️⃣ Kino kodini yuboring (masalan: 47)
2️⃣ Bot sizga kinoni yuboradi

🔍 Qidirish: /search kino nomi
📩 So'rov: /request

📋 Kodlar ro'yxati: {channel}

❓ Savollar bo'lsa: {admin}"""

# Errors
MOVIE_NOT_FOUND = """❌ Kod {code} topilmadi

💡 Tekshiring:
• Kod to'g'ri yozilganmi?
• Faqat raqam yuboring

🔥 Mashhur kinolar:
{suggestions}

📋 Barcha kodlar: {channel}"""

INVALID_INPUT = """❌ Noto'g'ri format

Faqat raqam yuboring.
Masalan: 47"""

USER_BANNED = """🚫 Sizga bot bloklangan.

Sabab bo'yicha: {admin}"""

MAINTENANCE = """🔧 Bot vaqtincha ishlamayapti

{message}

Uzr so'raymiz!"""

THROTTLED = """⏳ Juda ko'p so'rov!

Iltimos, {seconds} soniya kuting."""

# Subscription
SUBSCRIBE_REQUIRED = """🔐 Botdan foydalanish uchun kanalga obuna bo'ling:

👉 {channel}

Obuna bo'lgach, tugmani bosing:"""

SUBSCRIBE_SUCCESS = "✅ Rahmat! Endi botdan foydalanishingiz mumkin."
SUBSCRIBE_FAIL = "❌ Siz hali obuna bo'lmagansiz."

# Movie card
MOVIE_CARD = """🎬 {title}

🔢 Kod: {code}
📥 Yuklanishlar: {downloads} ta

⏳ Video yuklanmoqda..."""

MOVIE_CARD_ENHANCED = """🎬 {title}

🔢 Kod: {code}
📅 Yili: {year}
⏱ Davomiyligi: {duration} daqiqa
📥 Yuklanishlar: {downloads} ta

⏳ Video yuklanmoqda..."""

MOVIE_CARD_RICH = """🎬 {title}

🔢 Kod: {code}
📅 Yili: {year}
⏱ Davomiyligi: {duration} daqiqa
📥 Yuklanishlar: {downloads} ta

📝 {description}"""

# Series
SERIES_INFO = """📺 {series_name}

📺 Barcha qismlar:
{parts_list}"""

# Search
SEARCH_PROMPT = "🔍 Kino nomini yozing:\n\nMasalan: Avatar"
SEARCH_RESULTS = """🔍 Natijalar: {query}

{results}

📥 Yuklab olish uchun kodni bosing:"""
SEARCH_NOT_FOUND = """❌ '{query}' bo'yicha hech narsa topilmadi

💡 Maslahat:
• Boshqacha yozing
• Qisqaroq so'z ishlating

📋 Barcha kodlar: {channel}"""
SEARCH_TOO_SHORT = "❌ Kamida 2 ta belgi kiriting"

# Requests
REQUEST_PROMPT = """🎬 Qaysi kinoni qo'shishni xohlaysiz?

Kino nomini yozing:
(To'liq nom, yil qo'shsangiz yaxshi)"""
REQUEST_SUBMITTED = """✅ So'rovingiz qabul qilindi!

📽 {title}

Adminlar ko'rib chiqadi.

📊 Sizning so'rovlaringiz: /myrequest"""
MY_REQUESTS = """📋 Sizning so'rovlaringiz

{requests}"""
NO_REQUESTS = "📋 Sizda hali so'rovlar yo'q"
REQUEST_APPROVED = "✅ So'rovingiz qabul qilindi: {title}"
REQUEST_REJECTED = "❌ So'rovingiz rad etildi: {title}\nSabab: {reason}"

# Admin
ADMIN_PANEL = "🎬 Admin Panel\n\nTanlang:"
ADMIN_ONLY = "❌ Bu buyruq faqat adminlar uchun."
SUPER_ADMIN_ONLY = "❌ Bu buyruq faqat bosh admin uchun."

# Add movie
ADD_MOVIE_VIDEO = "📤 Video yuboring:"
ADD_MOVIE_TITLE = "📝 Kino nomini kiriting:"
ADD_MOVIE_CODE = "🔢 Kodni kiriting (faqat raqam):"
ADD_MOVIE_CODE_EXISTS = "❌ Bu kod band: {title}\nBoshqa kod kiriting:"
ADD_MOVIE_YEAR = "📅 Yilini kiriting (ixtiyoriy, o'tkazish uchun /skip):"
ADD_MOVIE_DURATION = "⏱ Davomiyligini kiriting (daqiqada, ixtiyoriy):"
ADD_MOVIE_SUCCESS = """✅ Kino qo'shildi!

📽 {title}
🔢 Kod: {code}"""

# Edit movie
EDIT_MOVIE_ASK_CODE = "🔢 Tahrirlash uchun kodni kiriting:"
EDIT_MOVIE_INFO = """📽 {title}
🔢 Kod: {code}
📥 Yuklanishlar: {downloads}

Nimani o'zgartirmoqchisiz?"""
EDIT_MOVIE_SUCCESS = "✅ O'zgarishlar saqlandi!"

# Delete movie
DELETE_MOVIE_ASK_CODE = "🔢 O'chirish uchun kodni kiriting:"
DELETE_MOVIE_CONFIRM = """📽 {title}
🔢 Kod: {code}

⚠️ O'chirishni tasdiqlaysizmi?"""
DELETE_MOVIE_SUCCESS = "✅ Kino o'chirildi"

# Movie list
MOVIE_LIST = """📋 Kinolar ro'yxati

Jami: {total} ta

{movies}"""

# Statistics
STATISTICS = """📊 Batafsil statistika

👥 Foydalanuvchilar:
├── Jami: {total_users}
├── Aktiv (7 kun): {active_users}
├── Bugun: +{today_users}
├── Hafta: +{week_users}
└── Oy: +{month_users}

📥 Yuklanishlar:
├── Jami: {total_downloads}
├── Bugun: {today_downloads}
├── Hafta: {week_downloads}
└── Oy: {month_downloads}

🎬 Kinolar: {total_movies} ta

🔥 Top 5 (barcha vaqt):
{top_all_time}

🔥 Top 5 (bu hafta):
{top_week}"""

# Broadcast
BROADCAST_MENU = "📢 Xabar yuborish\n\nTurini tanlang:"
BROADCAST_ASK_CONTENT = "Xabarni yuboring (matn, rasm, video):"
BROADCAST_CONFIRM = """📤 Xabar yuborilsinmi?

Foydalanuvchilar: {count} ta"""
BROADCAST_SUCCESS = """✅ Xabar yuborildi!

📤 Yuborildi: {success}
❌ Xatolik: {fail}"""
BROADCAST_PROGRESS = """📢 Xabar yuborilmoqda...

📊 Progress: {progress_bar} {percent}%

📤 Yuborildi: {sent} / {total}
❌ Xatolik: {failed}
⏱ Qolgan vaqt: ~{remaining}"""
BROADCAST_PAUSED = "⏸ Xabar yuborish to'xtatildi"
BROADCAST_CANCELLED = "❌ Xabar yuborish bekor qilindi"

# Weekly report
WEEKLY_REPORT = """📊 Haftalik yangiliklar!

🎬 Yangi kinolar: {new_count} ta
🔢 Yangi kodlar: {new_codes}

🔥 Hafta mashhuri:
└── {top_title} (kod: {top_code}) — {top_downloads} ta yuklash

👥 Jamiyatimiz: {total_users} ta obunachi

📥 Kinolar uchun: {channel}"""

# Maintenance
MAINTENANCE_STATUS = """🔧 Texnik rejim

Holati: {status}

Xabar: "{message}"
"""
MAINTENANCE_ON = "✅ Texnik rejim yoqildi"
MAINTENANCE_OFF = "✅ Texnik rejim o'chirildi"
MAINTENANCE_MSG_UPDATED = "✅ Xabar yangilandi"

# Admin management
ADMIN_LIST = """👥 Adminlar boshqaruvi

Hozirgi adminlar:
{admin_list}"""
ADMIN_ASK_ID = """Yangi admin Telegram ID sini kiriting:
(yoki xabarini forward qiling)"""
ADMIN_EXISTS = "❌ Bu foydalanuvchi allaqachon admin"
ADMIN_ADDED = "✅ Admin qo'shildi: {username}"
ADMIN_REMOVE_CONFIRM = "⚠️ @{username} ni o'chirishni tasdiqlaysizmi?"
ADMIN_REMOVED = "✅ Admin o'chirildi"

# Settings
SETTINGS = """⚙️ Sozlamalar

📢 Majburiy kanal: {channel}
   Holati: {status}"""
SETTINGS_ASK_CHANNEL = "Kanal username ni kiriting (@bilan):"
SETTINGS_CHANNEL_UPDATED = "✅ Kanal yangilandi: {channel}"

# Backup
BACKUP_MENU = """💾 Backup boshqaruvi

📊 Ma'lumotlar:
├── Kinolar: {movies} ta
├── Foydalanuvchilar: {users} ta
├── Yuklanishlar: {downloads} ta
└── Hajmi: ~{size}

📅 Oxirgi backup: {last_backup}"""
BACKUP_STARTED = "⏳ Backup yaratilmoqda..."
BACKUP_SUCCESS = """✅ Backup tayyor!

📁 Fayl: {filename}
📊 Hajmi: {size}
📅 Sana: {date}"""
BACKUP_SENT = "✅ Backup kanalga yuborildi"

# Common
CANCEL = "🔙 Bekor qilish"
BACK = "🔙 Orqaga"
CANCELLED = "❌ Bekor qilindi"
NOT_FOUND = "❌ Topilmadi"
YES = "✅ Ha"
NO = "❌ Yo'q"
SKIP = "⏭ O'tkazish"

# Rating
RATING_PROMPT = """⭐ *{title}* ni baholang

1-5 orasida tanlang:"""
RATING_SUCCESS = "✅ Rahmat! *{title}* uchun bahongiz: {stars}"
RATING_UPDATED = "✅ Bahongiz yangilandi: {stars}"
RATING_CANCELLED = "❌ Baholash bekor qilindi"

# Favorites
FAVORITES_TITLE = "❤️ *Sevimli kinolar*"
FAVORITES_EMPTY = """📭 Sevimlilar ro'yxati bo'sh

Kino kartasidagi ❤️ tugmasini bosib qo'shishingiz mumkin."""
FAVORITE_ADDED = "❤️ Sevimlilarga qo'shildi!"
FAVORITE_REMOVED = "💔 Sevimlilardan olib tashlandi"
FAVORITE_EXISTS = "Allaqachon sevimlilarda"

# Series
SERIES_TITLE = "📺 *{name}*"
SERIES_PROGRESS = "Ko'rilgan: {watched}/{total} qism ({percent}%)"
SERIES_CONTINUE = "▶️ Davom etish: {part}-qism"
SERIES_COMPLETED = "✅ Serial to'liq ko'rilgan!"
SERIES_PARTS_LIST = """📺 *{name}*

Qismlar:
{parts}"""

# Recommendations
RECOMMENDATIONS_TITLE = "🎯 *Sizga tavsiya*"
RECOMMENDATIONS_EMPTY = "Tavsiyalar uchun bir nechta kino ko'ring yoki baholang."
SIMILAR_MOVIES_TITLE = "🎬 O'xshash kinolar"

# Requests
REQUEST_START = """📝 Kino so'rovi

Iltimos, kino nomini aniq yozing.
Masalan: "Qasoskorlar", "Hayot go'zal", va h.k.

🔙 Bekor qilish uchun: /cancel"""
REQUEST_SUBMITTED = """✅ So'rovingiz qabul qilindi!

Adminlar ko'rib chiqib, javob berishadi.
Holatini /myrequest orqali tekshirishingiz mumkin."""
REQUEST_EMPTY = "📝 Sizda hali so'rovlar yo'q."
REQUEST_LIST = """📝 Sizning so'rovlaringiz:

{requests}"""
