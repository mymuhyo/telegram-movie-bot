# Telegram Movie Bot — Complete Specification

## Project Overview

Build a Telegram bot for distributing movies/videos stored in a private Telegram channel. Users request movies by numeric code, bot delivers the video. Includes admin panel for management.

**Language:** Uzbek (all user-facing text)
**Tech Stack:** Python 3.11+, aiogram 3.x (async), SQLite (or PostgreSQL), python-dotenv

---

## Architecture

```
┌─────────────────┐
│ Private Channel │ ──stores──▶ Videos (file_id saved)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Database     │ ──maps──▶ code → file_id + metadata
└────────┬────────┘
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│      Bot        │ ◀─────▶ │     Users       │
└─────────────────┘         └─────────────────┘
```

---

## Database Schema

### Tables

```sql
-- Movies table
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    file_id TEXT NOT NULL,
    added_by INTEGER NOT NULL,
    download_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    is_banned INTEGER DEFAULT 0,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admins table
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    role TEXT NOT NULL CHECK (role IN ('super_admin', 'admin')),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Downloads table (for statistics)
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (movie_id) REFERENCES movies(id)
);

-- Admin action logs
CREATE TABLE admin_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    action_type TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admins(id)
);

-- Settings table
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Default settings to insert
INSERT INTO settings (key, value) VALUES ('required_channel', '');
INSERT INTO settings (key, value) VALUES ('channel_check_enabled', 'false');
INSERT INTO settings (key, value) VALUES ('maintenance_mode', 'false');
INSERT INTO settings (key, value) VALUES ('maintenance_message', 'Texnik ishlar olib borilmoqda. Iltimos, keyinroq urinib ko''ring.');
```

### Indexes

```sql
CREATE INDEX idx_movies_code ON movies(code);
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_admins_telegram_id ON admins(telegram_id);
CREATE INDEX idx_downloads_downloaded_at ON downloads(downloaded_at);
CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at);
```

---

## Project Structure

```
movie_bot/
├── bot.py                  # Entry point
├── config.py               # Configuration & environment variables
├── requirements.txt
├── .env.example
│
├── database/
│   ├── __init__.py
│   ├── db.py               # Database connection & initialization
│   └── models.py           # Database operations (CRUD)
│
├── handlers/
│   ├── __init__.py
│   ├── user.py             # User commands (/start, /help, movie codes)
│   └── admin.py            # Admin panel & all admin operations
│
├── keyboards/
│   ├── __init__.py
│   ├── user_kb.py          # User keyboards
│   └── admin_kb.py         # Admin panel keyboards
│
├── middlewares/
│   ├── __init__.py
│   ├── subscription.py     # Channel subscription check
│   ├── maintenance.py      # Maintenance mode check
│   ├── ban_check.py        # Banned user check
│   └── throttling.py       # Rate limiting
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py          # Helper functions
│   └── statistics.py       # Statistics calculation functions
│
└── texts/
    ├── __init__.py
    └── messages.py         # All bot messages (Uzbek)
```

---

## Environment Variables (.env)

```env
BOT_TOKEN=your_bot_token_here
PRIVATE_CHANNEL_ID=-100xxxxxxxxxx
SUPER_ADMIN_ID=123456789
DATABASE_URL=sqlite:///bot.db
```

---

## Feature Specifications

### 1. User Features

#### 1.1 /start Command

**Trigger:** `/start`

**Flow:**
1. Check if maintenance mode → show maintenance message, stop
2. Check if user banned → show banned message, stop
3. Check channel subscription (if enabled) → show subscription prompt if not subscribed
4. Register user in database (if new)
5. Show welcome message

**Welcome Message:**
```
🎬 Kino Botga xush kelibsiz!

📥 Kino olish uchun kod yuboring.
Masalan: 47

📋 Kodlar ro'yxati: @YourChannel

❓ Yordam: /help
```

#### 1.2 /help Command

**Trigger:** `/help`

**Message:**
```
📖 Botdan foydalanish

1️⃣ Kino kodini yuboring (masalan: 47)
2️⃣ Bot sizga kinoni yuboradi

📋 Kodlar ro'yxati: @YourChannel

❓ Savollar bo'lsa: @AdminUsername
```

#### 1.3 Movie Request (Code)

**Trigger:** Any numeric message (e.g., `47`)

**Flow:**
1. Check maintenance mode
2. Check if user banned
3. Check channel subscription
4. Validate input (must be numeric)
5. Query database for movie with that code
6. If found:
   - Send movie card with info
   - Send video file
   - Increment download_count
   - Log download in downloads table
7. If not found:
   - Show smart error message with suggestions

**Movie Card (send before video):**
```
🎬 {title}

🔢 Kod: {code}
📥 Yuklanishlar: {download_count} ta

⏳ Video yuklanmoqda...
```

**Smart Error Message (movie not found):**
```
❌ Kod {code} topilmadi

💡 Tekshiring:
• Kod to'g'ri yozilganmi?
• Faqat raqam yuboring

🔥 Mashhur kinolar:
├── {code1} — {title1}
├── {code2} — {title2}
└── {code3} — {title3}

📋 Barcha kodlar: @YourChannel
```

**Invalid Input Message:**
```
❌ Noto'g'ri format

Faqat raqam yuboring.
Masalan: 47
```

---

### 2. Admin Panel

#### 2.1 Access

**Trigger:** `/admin`

**Check:** User must be in admins table

**Main Menu:**
```
🎬 Admin Panel

Tanlang:
```

**Inline Keyboard:**
```
[➕ Kino qo'shish] [📋 Kinolar]
[✏️ Tahrirlash] [🗑 O'chirish]
[📊 Statistika] [📋 Loglar]
[📢 Xabar yuborish] [🔧 Texnik rejim]
[👥 Adminlar] [⚙️ Sozlamalar]
```

Note: "👥 Adminlar" button only visible to super_admin role.

---

#### 2.2 Add Movie (➕ Kino qo'shish)

**Flow:**
```
Step 1: Bot asks for video
        "📤 Video yuboring:"
        [🔙 Bekor qilish]

Step 2: User sends video → Bot saves file_id temporarily
        "✅ Video qabul qilindi"
        "📝 Kino nomini kiriting:"

Step 3: User sends title
        "🔢 Kodni kiriting (faqat raqam):"

Step 4: User sends code
        - Validate: must be numeric
        - Validate: must be unique (not exist in DB)
        
        If code exists:
        "❌ Bu kod band: {existing_title}"
        "Boshqa kod kiriting:"
        
        If valid:
        - Save to database
        - Log action
        - Show confirmation

Confirmation:
        "✅ Kino qo'shildi!

        📽 {title}
        🔢 Kod: {code}

        [📢 E'lon qilish] [🔙 Admin panel]"
```

**"📢 E'lon qilish" button:** Broadcasts new movie announcement to all users (optional).

---

#### 2.3 Movie List (📋 Kinolar)

**Display:**
```
📋 Kinolar ro'yxati

Jami: {total_count} ta

1. {title} — kod: {code}
2. {title} — kod: {code}
3. {title} — kod: {code}
...

[⬅️ Oldingi] Sahifa 1/5 [Keyingi ➡️]
[🔙 Admin panel]
```

Paginate: 10 movies per page.

---

#### 2.4 Edit Movie (✏️ Tahrirlash)

**Flow:**
```
Step 1: "🔢 Tahrirlash uchun kodni kiriting:"

Step 2: User sends code
        If not found: "❌ Kod topilmadi"
        
        If found, show movie info:
        "📽 {title}
        🔢 Kod: {code}
        📥 Yuklanishlar: {count}
        
        Nimani o'zgartirmoqchisiz?"
        
        [📝 Nom] [🔢 Kod] [🎬 Video]
        [🔙 Bekor qilish]

Step 3a: If "📝 Nom" selected
         "Yangi nomni kiriting:"
         User sends new title → Update DB → Log action → Confirm

Step 3b: If "🔢 Kod" selected
         "Yangi kodni kiriting:"
         User sends new code → Validate unique → Update DB → Log action → Confirm

Step 3c: If "🎬 Video" selected
         "Yangi videoni yuboring:"
         User sends video → Update file_id → Log action → Confirm
```

---

#### 2.5 Delete Movie (🗑 O'chirish)

**Flow:**
```
Step 1: "🔢 O'chirish uchun kodni kiriting:"

Step 2: User sends code
        If not found: "❌ Kod topilmadi"
        
        If found:
        "📽 {title}
        🔢 Kod: {code}
        
        ⚠️ O'chirishni tasdiqlaysizmi?"
        
        [✅ Ha, o'chirish] [❌ Yo'q]

Step 3: If confirmed
        - Delete from database
        - Log action
        - "✅ Kino o'chirildi"
```

---

#### 2.6 Statistics (📊 Statistika)

**Display:**
```
📊 Batafsil statistika

👥 Foydalanuvchilar:
├── Jami: {total_users}
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
1. {title} ({code}) — {count} ta
2. {title} ({code}) — {count} ta
3. {title} ({code}) — {count} ta
4. {title} ({code}) — {count} ta
5. {title} ({code}) — {count} ta

🔥 Top 5 (bu hafta):
1. {title} ({code}) — {count} ta
2. {title} ({code}) — {count} ta
3. {title} ({code}) — {count} ta
4. {title} ({code}) — {count} ta
5. {title} ({code}) — {count} ta

[🔄 Yangilash] [🔙 Admin panel]
```

---

#### 2.7 Admin Logs (📋 Loglar)

**Display:**
```
📋 So'nggi harakatlar

{timestamp} — @{username}
└── {action_description}

{timestamp} — @{username}
└── {action_description}

{timestamp} — @{username}
└── {action_description}

...

[⬅️ Oldingi] [Keyingi ➡️]
[🔙 Admin panel]
```

Show 10 logs per page, newest first.

**Action type formats:**
- add_movie: "Kino qo'shdi: {title} (kod: {code})"
- edit_movie: "Kino tahrirladi: {title} — {field}"
- delete_movie: "Kino o'chirdi: {title} (kod: {code})"
- add_admin: "Admin qo'shdi: @{username}"
- remove_admin: "Admin o'chirdi: @{username}"
- maintenance_on: "Texnik rejim yoqdi"
- maintenance_off: "Texnik rejim o'chirdi"
- broadcast: "Xabar yubordi ({count} ta foydalanuvchi)"
- settings_change: "Sozlama o'zgartirdi: {setting}"

---

#### 2.8 Broadcast (📢 Xabar yuborish)

**Menu:**
```
📢 Xabar yuborish

Turini tanlang:

[✍️ Oddiy xabar]
[📊 Haftalik hisobot]
[🔙 Admin panel]
```

**2.8.1 Custom Message (✍️ Oddiy xabar):**
```
Step 1: "Xabarni yuboring (matn, rasm, video):"
        [🔙 Bekor qilish]

Step 2: User sends content
        "📤 Xabar yuborilsinmi?
        
        Foydalanuvchilar: {total_users} ta"
        
        [✅ Yuborish] [❌ Bekor qilish]

Step 3: If confirmed
        - Send to all non-banned users
        - Log action
        - Show result:
        "✅ Xabar yuborildi!
        
        📤 Yuborildi: {success_count}
        ❌ Xatolik: {fail_count}"
```

**2.8.2 Weekly Report (📊 Haftalik hisobot):**

Auto-generates and sends:
```
📊 Haftalik yangiliklar!

🎬 Yangi kinolar: {new_movies_count} ta
🔢 Yangi kodlar: {new_codes_list}

🔥 Hafta mashhuri:
└── {top_movie_title} (kod: {code}) — {count} ta yuklash

👥 Jamiyatimiz: {total_users} ta obunachi

📥 Kinolar uchun: @YourChannel
```

---

#### 2.9 Maintenance Mode (🔧 Texnik rejim)

**Display:**
```
🔧 Texnik rejim

Holati: {✅ Yoqilgan / ❌ O'chirilgan}

Xabar: "{current_message}"

[🔄 {Yoqish/O'chirish}] [✏️ Xabarni o'zgartirish]
[🔙 Admin panel]
```

**Toggle flow:**
```
If currently OFF and admin clicks "🔴 Yoqish":
- Update setting maintenance_mode = true
- Log action
- "✅ Texnik rejim yoqildi"

If currently ON and admin clicks "🟢 O'chirish":
- Update setting maintenance_mode = false
- Log action
- "✅ Texnik rejim o'chirildi"
```

**Edit message flow:**
```
"Yangi xabarni kiriting:"
User sends message
- Update setting maintenance_message
- Log action
- "✅ Xabar yangilandi"
```

**User experience when maintenance ON:**
```
🔧 Bot vaqtincha ishlamayapti

{maintenance_message}

Uzr so'raymiz!
```

**Important:** Admins bypass maintenance mode — they can use bot normally.

---

#### 2.10 Admin Management (👥 Adminlar) — Super Admin Only

**Display:**
```
👥 Adminlar boshqaruvi

Hozirgi adminlar:
• @{username} — 👑 super_admin
• @{username} — admin
• @{username} — admin

[➕ Admin qo'shish] [➖ Adminni o'chirish]
[🔙 Admin panel]
```

**Add admin flow:**
```
Step 1: "Yangi admin Telegram ID sini kiriting:
        (yoki xabarini forward qiling)"

Step 2: User sends ID or forwards message
        - Extract telegram_id
        - Check if already admin
        
        If already admin: "❌ Bu foydalanuvchi allaqachon admin"
        
        If valid:
        - Add to admins table with role='admin'
        - Log action
        - "✅ Admin qo'shildi: {telegram_id}"
```

**Remove admin flow:**
```
Step 1: Show list of removable admins (not super_admin)
        
        "Adminni tanlang:"
        [Inline buttons with admin usernames]

Step 2: Admin selected
        "⚠️ @{username} ni o'chirishni tasdiqlaysizmi?"
        [✅ Ha] [❌ Yo'q]

Step 3: If confirmed
        - Remove from admins table
        - Log action
        - "✅ Admin o'chirildi"
```

---

#### 2.11 Settings (⚙️ Sozlamalar)

**Display:**
```
⚙️ Sozlamalar

📢 Majburiy kanal: {channel_username or "O'rnatilmagan"}
   Holati: {✅ Yoqilgan / ❌ O'chirilgan}

[✏️ Kanalni o'zgartirish]
[🔄 {Yoqish/O'chirish}]
[🔙 Admin panel]
```

**Change channel flow:**
```
"Kanal username ni kiriting (@bilan):"
User sends: @channelname
- Validate format (starts with @)
- Update setting
- Log action
- "✅ Kanal yangilandi: @channelname"
```

---

### 3. Middleware Specifications

#### 3.1 Subscription Check Middleware

**Logic:**
```python
async def check_subscription(user_id):
    # Check if feature enabled
    enabled = get_setting('channel_check_enabled')
    if enabled != 'true':
        return True
    
    channel = get_setting('required_channel')
    if not channel:
        return True
    
    # Check membership via Telegram API
    try:
        member = await bot.get_chat_member(channel, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True  # If error, allow (don't block users due to API issues)
```

**Subscription prompt:**
```
🔐 Botdan foydalanish uchun kanalga obuna bo'ling:

👉 {channel_username}

Obuna bo'lgach, tugmani bosing:

[✅ Obuna bo'ldim]
```

**After button click:**
- Re-check subscription
- If subscribed: "✅ Rahmat! Endi botdan foydalanishingiz mumkin."
- If not: "❌ Siz hali obuna bo'lmagansiz."

#### 3.2 Maintenance Check Middleware

**Logic:**
```python
async def check_maintenance(user_id):
    # Admins bypass maintenance
    if is_admin(user_id):
        return True
    
    maintenance = get_setting('maintenance_mode')
    return maintenance != 'true'
```

#### 3.3 Ban Check Middleware

**Logic:**
```python
async def check_ban(user_id):
    user = get_user(user_id)
    if user and user.is_banned:
        return False
    return True
```

**Banned message:**
```
🚫 Sizga bot bloklangan.

Sabab bo'yicha: @AdminUsername
```

#### 3.4 Throttling Middleware

**Config:** Max 5 requests per 60 seconds per user

**Throttled message:**
```
⏳ Juda ko'p so'rov!

Iltimos, {seconds} soniya kuting.
```

---

### 4. Helper Functions

#### 4.1 Statistics Functions

```python
def get_total_users():
    """Return count of all users"""

def get_users_by_period(period):
    """Return count of users joined in period (today/week/month)"""

def get_total_downloads():
    """Return total download count"""

def get_downloads_by_period(period):
    """Return downloads in period"""

def get_top_movies(limit=5, period=None):
    """Return top movies by download count
    period: None=all time, 'week', 'month'
    """

def get_new_movies_this_week():
    """Return movies added this week"""
```

#### 4.2 Admin Log Function

```python
def log_admin_action(admin_id, action_type, details):
    """Insert into admin_logs table"""
```

#### 4.3 Broadcast Function

```python
async def broadcast_message(content, content_type='text'):
    """Send message to all non-banned users
    Returns: (success_count, fail_count)
    """
```

---

## Development Phases

### Phase 1: Foundation
1. Set up project structure
2. Configure database and create tables
3. Implement basic user handlers (/start, /help)
4. Implement movie code handler (send video by code)
5. Test with manual database entries

### Phase 2: Admin Panel Core
1. Admin authentication check
2. Admin panel main menu
3. Add movie feature
4. Movie list feature
5. Edit movie feature
6. Delete movie feature

### Phase 3: Advanced Features
1. Statistics panel
2. Admin action logging
3. Admin logs viewer
4. Broadcast feature (custom + weekly report)

### Phase 4: Security & Settings
1. Maintenance mode
2. Channel subscription check
3. Ban check middleware
4. Throttling middleware
5. Settings panel
6. Admin management (super_admin)

### Phase 5: Polish & Testing
1. Smart error messages
2. Input validation everywhere
3. Error handling
4. Test all flows
5. Edge case handling

---

## Testing Checklist

### User Flow
- [ ] /start shows welcome (new user registered)
- [ ] /help shows instructions
- [ ] Valid code → movie sent, download logged
- [ ] Invalid code → smart error with suggestions
- [ ] Non-numeric input → error message
- [ ] Banned user → blocked message
- [ ] Maintenance mode → maintenance message
- [ ] Channel not subscribed → subscription prompt

### Admin Flow
- [ ] /admin accessible only to admins
- [ ] Add movie → saves correctly
- [ ] Duplicate code rejected
- [ ] Edit movie (all fields)
- [ ] Delete movie with confirmation
- [ ] Movie list pagination works
- [ ] Statistics accurate
- [ ] Admin logs recorded and displayed
- [ ] Broadcast sends to all users
- [ ] Weekly report auto-generates correctly
- [ ] Maintenance toggle works
- [ ] Channel settings work
- [ ] Admin add/remove (super_admin only)

### Edge Cases
- [ ] Empty database (no movies)
- [ ] Single user
- [ ] Large numbers (1000+ movies, users)
- [ ] Concurrent requests
- [ ] Network errors handled gracefully

---

## Messages Reference (texts/messages.py)

```python
# Welcome & Help
WELCOME = """🎬 Kino Botga xush kelibsiz!

📥 Kino olish uchun kod yuboring.
Masalan: 47

📋 Kodlar ro'yxati: {channel}

❓ Yordam: /help"""

HELP = """📖 Botdan foydalanish

1️⃣ Kino kodini yuboring (masalan: 47)
2️⃣ Bot sizga kinoni yuboradi

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

# Admin messages
ADMIN_PANEL = "🎬 Admin Panel\n\nTanlang:"
ADMIN_ONLY = "❌ Bu buyruq faqat adminlar uchun."

# Add movie
ADD_MOVIE_VIDEO = "📤 Video yuboring:"
ADD_MOVIE_TITLE = "📝 Kino nomini kiriting:"
ADD_MOVIE_CODE = "🔢 Kodni kiriting (faqat raqam):"
ADD_MOVIE_CODE_EXISTS = "❌ Bu kod band: {title}\nBoshqa kod kiriting:"
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

# Statistics
STATISTICS = """📊 Batafsil statistika

👥 Foydalanuvchilar:
├── Jami: {total_users}
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

# Common
CANCEL = "🔙 Bekor qilish"
BACK = "🔙 Orqaga"
CANCELLED = "❌ Bekor qilindi"
NOT_FOUND = "❌ Topilmadi"
YES = "✅ Ha"
NO = "❌ Yo'q"
```

---

## Notes for Agent

1. **Use FSM (Finite State Machine)** for multi-step flows like adding/editing movies
2. **Always validate user input** before database operations
3. **Use inline keyboards** for admin panel navigation
4. **Handle all exceptions** gracefully with user-friendly messages
5. **Use transactions** for critical database operations
6. **Cache settings** to avoid frequent DB queries
7. **Paginate** movie lists and logs (10 items per page)
8. **Log all admin actions** immediately after execution
9. **Test each feature** before moving to next phase

---

## Example Code Snippets

### Aiogram 3.x Router Setup

```python
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

user_router = Router()
admin_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: Message):
    # Handler code

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    # Check if admin first
```

### FSM States Example

```python
from aiogram.fsm.state import State, StatesGroup

class AddMovieStates(StatesGroup):
    waiting_for_video = State()
    waiting_for_title = State()
    waiting_for_code = State()
```

### Middleware Example

```python
from aiogram import BaseMiddleware

class MaintenanceMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        if not await check_maintenance(user_id):
            return await event.answer(MAINTENANCE_MESSAGE)
        return await handler(event, data)
```

---

End of specification.
