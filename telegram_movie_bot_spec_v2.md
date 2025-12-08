# Telegram Movie Bot — Enhanced Specification v2.0

## Project Overview

Build a feature-rich Telegram bot for distributing movies/videos stored in a private Telegram channel. Users request movies by numeric code or search by title, bot delivers the video. Includes comprehensive admin panel for management.

**Language:** Uzbek (all user-facing text)  
**Tech Stack:** Python 3.11+, aiogram 3.x (async), PostgreSQL (recommended) / SQLite, python-dotenv, aiofiles

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
└────────┬────────┘           series, requests
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│      Bot        │ ◀─────▶ │     Users       │
└─────────────────┘         └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Backup System   │ ──exports──▶ JSON/SQL dumps
└─────────────────┘
```

---

## Database Schema (Enhanced)

### Tables

```sql
-- Series table (for multi-part movies/serials)
CREATE TABLE series (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    total_parts INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Movies table (ENHANCED)
CREATE TABLE movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    file_id TEXT NOT NULL,
    series_id INTEGER,
    part_number INTEGER,
    quality TEXT DEFAULT 'HD',
    year INTEGER,
    duration_minutes INTEGER,
    description TEXT,
    added_by INTEGER NOT NULL,
    download_count INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (series_id) REFERENCES series(id)
);

-- Users table (ENHANCED)
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    language_code TEXT DEFAULT 'uz',
    is_banned INTEGER DEFAULT 0,
    ban_reason TEXT,
    total_downloads INTEGER DEFAULT 0,
    last_active_at TIMESTAMP,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User movie requests/suggestions
CREATE TABLE requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'added')),
    admin_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Admins table
CREATE TABLE admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    role TEXT NOT NULL CHECK (role IN ('super_admin', 'admin')),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Downloads table (ENHANCED)
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    source TEXT DEFAULT 'code', -- 'code', 'search'
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

-- Broadcast queue (for async broadcasting)
CREATE TABLE broadcast_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type TEXT NOT NULL, -- 'text', 'photo', 'video'
    content TEXT NOT NULL,
    file_id TEXT,
    total_users INTEGER DEFAULT 0,
    sent_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending', -- 'pending', 'running', 'completed', 'cancelled'
    started_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (started_by) REFERENCES admins(id)
);

-- Default settings
INSERT INTO settings (key, value) VALUES 
    ('required_channel', ''),
    ('channel_check_enabled', 'false'),
    ('maintenance_mode', 'false'),
    ('maintenance_message', 'Texnik ishlar olib borilmoqda. Iltimos, keyinroq urinib ko''ring.'),
    ('movies_per_page', '10'),
    ('daily_download_limit', '0'), -- 0 = unlimited
    ('auto_backup_enabled', 'false'),
    ('search_enabled', 'true');
```

### Indexes

```sql
CREATE INDEX idx_movies_code ON movies(code);
CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_series ON movies(series_id);
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_admins_telegram_id ON admins(telegram_id);
CREATE INDEX idx_downloads_downloaded_at ON downloads(downloaded_at);
CREATE INDEX idx_admin_logs_created_at ON admin_logs(created_at);
```

---

## Project Structure (Enhanced)

```
movie_bot/
├── bot.py                  # Entry point
├── config.py               # Configuration & environment variables
├── requirements.txt
├── .env.example
├── backups/                # Database backup storage
│
├── database/
│   ├── __init__.py
│   ├── db.py               # Database connection & initialization
│   ├── models.py           # Database operations (CRUD)
│   └── backup.py           # Backup/restore functionality
│
├── handlers/
│   ├── __init__.py
│   ├── user.py             # User commands (/start, /help, movie codes)
│   ├── search.py           # Search functionality
│   ├── requests.py         # Movie requests
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
│   ├── throttling.py       # Rate limiting
│   └── activity.py         # User activity tracking
│
├── services/
│   ├── __init__.py
│   ├── broadcast.py        # Async broadcast service
│   ├── backup.py           # Scheduled backup service
│   └── analytics.py        # Advanced analytics
│
├── utils/
│   ├── __init__.py
│   ├── helpers.py          # Helper functions
│   ├── statistics.py       # Statistics calculation
│   ├── search.py           # Search algorithms
│   └── export.py           # Data export utilities
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
DATABASE_URL=postgresql://user:pass@localhost/moviebot
# or sqlite:///bot.db for SQLite

# Optional
BACKUP_CHANNEL_ID=-100xxxxxxxxxx  # Channel to send backups
BACKUP_INTERVAL_HOURS=24
MAX_CONCURRENT_BROADCASTS=30
```

---

## Feature Specifications

### 1. User Features (Original + Enhanced)

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

🔍 Qidirish: /search

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

🔍 Qidirish: /search kino nomi
📩 So'rov: /request

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
   - Send enhanced movie card with info
   - Send video file
   - Increment download_count
   - Log download in downloads table
7. If not found:
   - Show smart error message with suggestions

**Enhanced Movie Card:**
```
🎬 {title}

🔢 Kod: {code}
📅 Yili: {year}
⏱ Davomiyligi: {duration} daqiqa
📥 Yuklanishlar: {downloads} ta

⏳ Video yuklanmoqda...
```

---

### 2. Search Feature (NEW)

#### 2.1 /search Command

**Trigger:** `/search` or `/qidirish` or `/search {query}`

**Flow:**
```
Step 1: Bot shows search prompt (if no query provided)
        "🔍 Kino nomini yozing:
        
        Masalan: Avatar"
        [🔙 Bekor qilish]

Step 2: User sends search query
        - Minimum 2 characters required
        - Search in movie titles (case-insensitive, partial match)
        
        If found (max 10 results):
        "🔍 Natijalar: {query}
        
        1. 🎬 {title} (kod: {code})
        2. 🎬 {title} (kod: {code})
        3. 🎬 {title} (kod: {code})
        ...
        
        📥 Yuklab olish uchun kodni bosing:"
        
        [Inline buttons with codes]
        
        If not found:
        "❌ '{query}' bo'yicha hech narsa topilmadi
        
        💡 Maslahat:
        • Boshqacha yozing
        • Qisqaroq so'z ishlating
        
        📋 Barcha kodlar: @YourChannel"
```

**Smart Search Features:**
- Fuzzy matching (e.g., "avtar" finds "Avatar")
- Search by year: "2023" shows all 2023 movies
- Inline search: `/search avatar` works directly

---

### 3. Movie Request Feature (NEW)

#### 3.1 /request or /sorov Command

**Trigger:** `/request`, `/sorov`

**Flow:**
```
Step 1: "🎬 Qaysi kinoni qo'shishni xohlaysiz?
        
        Kino nomini yozing:
        (To'liq nom, yil qo'shsangiz yaxshi)"
        
        [🔙 Bekor qilish]

Step 2: User sends movie title
        "✅ So'rovingiz qabul qilindi!
        
        📽 {title}
        
        Adminlar ko'rib chiqadi.
        
        📊 Sizning so'rovlaringiz: /myrequest"
```

#### 3.2 /myrequest — View Own Requests

```
📋 Sizning so'rovlaringiz

1. 📽 {title}
   📅 {date} — ⏳ Kutilmoqda
   
2. 📽 {title}
   📅 {date} — ✅ Qo'shildi (kod: {code})
   
3. 📽 {title}
   📅 {date} — ❌ Rad etildi
   └── Sabab: {admin_response}
```

---

### 4. Series/Multi-Part Movies (NEW)

#### 4.1 Series Display

When user requests a movie that is part of a series:
```
🎬 {series_name}

📺 {part_number}-qism: {episode_title}

🔢 Kod: {code}
📥 Yuklanishlar: {count} ta

📺 Barcha qismlar:
├── 1-qism: kod {code1} ✅
├── 2-qism: kod {code2} ✅
├── 3-qism: kod {code3} ✅
└── 4-qism: kod {code4} (bu)

⏳ Video yuklanmoqda...
```

---

### 5. Admin Panel

#### 5.1 Access

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
[📺 Seriallar] [📊 Statistika]
[📋 Loglar] [📢 Xabar yuborish]
[🔧 Texnik rejim] [📩 So'rovlar]
[💾 Backup] [👥 Adminlar]
[⚙️ Sozlamalar]
```

Note: "👥 Adminlar" button only visible to super_admin role.

---

#### 5.2 Add Movie (➕ Kino qo'shish)

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
        "📅 Yilini kiriting (ixtiyoriy, o'tkazish uchun /skip):"

Step 5: User sends year or /skip
        "⏱ Davomiyligini kiriting (daqiqada, ixtiyoriy):"

Step 6: User sends duration or /skip
        "📺 Serial qismimi? (Ha/Yo'q)"
        [Ha] [Yo'q]

Step 7: If "Ha" - show series selection or create new
        If "Yo'q" - save directly

Confirmation:
        "✅ Kino qo'shildi!

        📽 {title}
        🔢 Kod: {code}
        📅 Yil: {year}

        [📢 E'lon qilish] [🔙 Admin panel]"
```

---

#### 5.3 Series Management (📺 Seriallar)

```
📺 Seriallar boshqaruvi

Hozirgi seriallar:
• Squid Game — 9 qism
• Money Heist — 41 qism
...

[➕ Yangi serial] [📋 Qismlar qo'shish]
[🔙 Admin panel]
```

---

#### 5.4 User Requests (📩 So'rovlar)

```
📩 Foydalanuvchi so'rovlari

⏳ Kutilmoqda: 5 ta

1. 📽 "Inception 2010"
   👤 @username — 2 kun oldin
   [✅ Qabul] [❌ Rad etish]

2. 📽 "Dune Part 2"
   👤 @username — 1 kun oldin
   [✅ Qabul] [❌ Rad etish]

[⬅️ Oldingi] [Keyingi ➡️]
[📋 Arxiv] [🔙 Admin panel]
```

**Approve flow:**
- Mark as "approved"
- Notify user: "✅ So'rovingiz qabul qilindi: {title}"

**Reject flow:**
- Ask for reason
- Mark as "rejected" with admin_response
- Notify user: "❌ So'rovingiz rad etildi: {title}\nSabab: {reason}"

---

#### 5.5 Database Backup (💾 Backup)

```
💾 Backup boshqaruvi

📊 Ma'lumotlar:
├── Kinolar: 150 ta
├── Foydalanuvchilar: 2,500 ta
├── Yuklanishlar: 15,000 ta
└── Hajmi: ~2.5 MB

📅 Oxirgi backup: {date_time}

[📤 Hozir backup] [📥 Restore]
[🔄 Auto-backup: {ON/OFF}]
[🔙 Admin panel]
```

**Backup creates:**
- JSON export of all data
- Sent to specified backup channel
- Includes restore instructions

---

#### 5.6 Enhanced Broadcasting with Progress

```
📢 Xabar yuborilmoqda...

📊 Progress: [████████░░] 80%

📤 Yuborildi: 2,000 / 2,500
❌ Xatolik: 12
⏱ Qolgan vaqt: ~30 soniya

[⏸ Pauza] [❌ Bekor qilish]
```

**Features:**
- Chunked sending (30 users per second)
- Real-time progress updates
- Pause/resume capability
- Automatic retry for failed sends

---

#### 5.7 Enhanced Statistics

```
📊 Batafsil statistika

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

🎬 Kontent:
├── Kinolar: {total_movies} ta
├── Seriallar: {total_series} ta
└── Yangi (bu hafta): {new_movies} ta

🔥 Top 5 (barcha vaqt):
{top_all_time}

🔥 Top 5 (bu hafta):
{top_week}

[🔄 Yangilash] [📤 Export CSV] [🔙 Admin panel]
```

---

### 6. Middleware Specifications

#### 6.1 Subscription Check Middleware
(Same as original)

#### 6.2 Maintenance Check Middleware
(Same as original)

#### 6.3 Ban Check Middleware
(Same as original)

#### 6.4 Throttling Middleware
**Config:** Max 5 requests per 60 seconds per user

#### 6.5 Activity Tracking Middleware (NEW)
- Updates `last_active_at` on every user interaction
- Tracks total_downloads per user

---

## New Messages (texts/messages.py additions)

```python
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

# Series
SERIES_INFO = """📺 {series_name}

📺 Barcha qismlar:
{parts_list}"""

# Enhanced movie card
MOVIE_CARD_ENHANCED = """🎬 {title}

🔢 Kod: {code}
📅 Yili: {year}
⏱ Davomiyligi: {duration} daqiqa
📥 Yuklanishlar: {downloads} ta

⏳ Video yuklanmoqda..."""

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

# Broadcast progress
BROADCAST_PROGRESS = """📢 Xabar yuborilmoqda...

📊 Progress: {progress_bar} {percent}%

📤 Yuborildi: {sent} / {total}
❌ Xatolik: {failed}
⏱ Qolgan vaqt: ~{remaining}"""
BROADCAST_PAUSED = "⏸ Xabar yuborish to'xtatildi"
BROADCAST_CANCELLED = "❌ Xabar yuborish bekor qilindi"
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
3. Add movie feature (with metadata)
4. Movie list feature
5. Edit movie feature
6. Delete movie feature

### Phase 3: Search Feature
1. Search functionality with fuzzy matching
2. Search by title, year
3. Inline search results with buttons
4. Search history (optional)

### Phase 4: Series Support
1. Series management for admins
2. Add parts to series
3. Series display for users
4. Navigation between parts

### Phase 5: User Engagement
1. Movie request system
2. Request management for admins
3. User notifications on request status
4. User activity tracking

### Phase 6: Advanced Admin
1. Statistics panel (enhanced)
2. Admin action logging
3. Admin logs viewer
4. Broadcast with progress tracking
5. Chunked async broadcasting

### Phase 7: Security & Settings
1. Maintenance mode
2. Channel subscription check
3. Ban check middleware
4. Throttling middleware
5. Settings panel
6. Admin management

### Phase 8: Backup & Export
1. Database backup system
2. Auto-backup scheduling
3. Backup to channel
4. Restore functionality
5. CSV export for statistics

### Phase 9: Polish & Testing
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

### Search
- [ ] /search shows prompt
- [ ] Search with results displays correctly
- [ ] No results message shown
- [ ] Fuzzy matching works
- [ ] Search by year works
- [ ] Minimum character validation
- [ ] Inline /search {query} works

### Requests
- [ ] /request flow works
- [ ] /myrequest shows history
- [ ] Admin can approve/reject
- [ ] User notified on status change

### Series
- [ ] Series movies show all parts
- [ ] Navigation between parts
- [ ] Correct part numbering

### Admin Flow
- [ ] /admin accessible only to admins
- [ ] Add movie with metadata → saves correctly
- [ ] Duplicate code rejected
- [ ] Edit movie (all fields)
- [ ] Delete movie with confirmation
- [ ] Movie list pagination works
- [ ] Statistics accurate
- [ ] Admin logs recorded and displayed
- [ ] Broadcast with progress works
- [ ] Pause/resume broadcast
- [ ] Weekly report auto-generates correctly
- [ ] Maintenance toggle works
- [ ] Channel settings work
- [ ] Admin add/remove (super_admin only)

### Series Management
- [ ] Add series
- [ ] Add parts to series
- [ ] Edit series

### Backup
- [ ] Manual backup creates file
- [ ] Backup sent to channel
- [ ] Auto-backup scheduling
- [ ] Restore from backup
- [ ] CSV export works

### Edge Cases
- [ ] Empty database (no movies)
- [ ] Single user
- [ ] Large numbers (1000+ movies, users)
- [ ] Concurrent requests
- [ ] Network errors handled gracefully
- [ ] Search with special characters
- [ ] Very long movie titles

---

## Comparison: Original vs Enhanced v2.0

| Feature | Original | Enhanced v2.0 |
|---------|----------|---------------|
| Movie search | ❌ | ✅ Fuzzy search |
| Series support | ❌ | ✅ Multi-part |
| User requests | ❌ | ✅ Full workflow |
| Broadcast | Basic | ✅ Async + progress |
| Backup | ❌ | ✅ Auto + manual |
| Movie metadata | Basic | ✅ Year, duration, description |
| Statistics | Basic | ✅ Enhanced + export |
| Activity tracking | ❌ | ✅ Last active, trends |

---

## Notes for Agent

1. **Use FSM (Finite State Machine)** for multi-step flows
2. **Always validate user input** before database operations
3. **Use inline keyboards** for admin panel navigation
4. **Handle all exceptions** gracefully with user-friendly messages
5. **Use transactions** for critical database operations
6. **Cache settings** to avoid frequent DB queries
7. **Paginate** movie lists and logs (10 items per page)
8. **Log all admin actions** immediately after execution
9. **Test each feature** before moving to next phase
10. **Use fuzzy search** library (e.g., `rapidfuzz`) for search
11. **Implement chunked broadcasting** (30/sec) to avoid rate limits
12. **Schedule backups** using `aioschedule` or background tasks

---

End of enhanced specification v2.0.
